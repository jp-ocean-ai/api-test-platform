from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import requests
from django.utils import timezone

from reports.models import TestReport
from testcases.models import TestCase, TestStep
from .models import ExecutionStepResult, TestExecution


BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / 'reports'
ALLURE_RESULTS_DIR = BASE_DIR / 'allure-results'
ALLURE_REPORT_DIR = BASE_DIR / 'allure-report'
VAR_PATTERN = re.compile(r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}')


def _render_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        exact_match = VAR_PATTERN.fullmatch(stripped)
        if exact_match:
            return context.get(exact_match.group(1), value)

        def replacer(match: re.Match[str]) -> str:
            key = match.group(1)
            rendered = context.get(key, match.group(0))
            if isinstance(rendered, (dict, list)):
                return json.dumps(rendered, ensure_ascii=False)
            return '' if rendered is None else str(rendered)

        return VAR_PATTERN.sub(replacer, value)

    if isinstance(value, dict):
        return {k: _render_value(v, context) for k, v in value.items()}

    if isinstance(value, list):
        return [_render_value(item, context) for item in value]

    return value


def _extract_by_expression(payload: Any, expression: str) -> Any:
    if not expression:
        return None
    expr = expression.strip()
    if expr.startswith('$.'):
        expr = expr[2:]
    elif expr == '$':
        return payload

    current = payload
    for part in expr.split('.'):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
            continue
        if isinstance(current, list) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(current):
                current = current[idx]
                continue
        return None
    return current


def _build_request_snapshot(step: TestStep, context: dict[str, Any]) -> dict[str, Any]:
    api = step.api
    env = step.environment or step.testcase.environment or step.testcase.default_environment
    base_url = env.base_url if env else 'http://127.0.0.1:8001'

    overrides = step.request_overrides or {}
    path = overrides.get('path', api.path)
    if not str(path).startswith('/'):
        path = '/' + str(path)

    headers = api.headers or {}
    headers.update(overrides.get('headers') or {})

    params = api.query_params or {}
    params.update(overrides.get('query_params') or {})

    body = overrides.get('body', api.body_template or {})

    return {
        'base_url': base_url,
        'url': base_url.rstrip('/') + _render_value(path, context),
        'method': api.method.upper(),
        'headers': _render_value(headers, context),
        'params': _render_value(params, context),
        'json': _render_value(body, context),
    }


def _run_assertions(response: requests.Response, rules: list[dict[str, Any]]) -> tuple[bool, list[dict[str, Any]], str]:
    rule_results: list[dict[str, Any]] = []
    response_json = None

    for rule in rules:
        rule_type = rule.get('type')
        ok = True
        detail = ''
        try:
            if rule_type == 'status_code':
                expected = rule.get('expected')
                ok = response.status_code == expected
                detail = f'expected {expected}, got {response.status_code}'
            elif rule_type == 'jsonpath_equals':
                if response_json is None:
                    response_json = response.json()
                actual = _extract_by_expression(response_json, rule.get('expression', ''))
                expected = rule.get('expected')
                ok = actual == expected
                detail = f'expected {expected}, got {actual}'
            elif rule_type == 'jsonpath_exists':
                if response_json is None:
                    response_json = response.json()
                actual = _extract_by_expression(response_json, rule.get('expression', ''))
                ok = actual is not None
                detail = f'value at {rule.get("expression")} is {actual}'
            elif rule_type == 'contains':
                expected = str(rule.get('expected', ''))
                actual_text = response.text or ''
                ok = expected in actual_text
                detail = f'expected substring {expected}'
            else:
                ok = False
                detail = f'unsupported assertion type: {rule_type}'
        except Exception as exc:
            ok = False
            detail = str(exc)

        rule_results.append({
            'rule': rule,
            'passed': ok,
            'detail': detail,
        })
        if not ok:
            return False, rule_results, detail

    return True, rule_results, ''


def _extract_variables(response: requests.Response, rules: list[dict[str, Any]]) -> dict[str, Any]:
    if not rules:
        return {}

    body = None
    extracted: dict[str, Any] = {}
    for rule in rules:
        name = rule.get('name')
        if not name:
            continue
        source = rule.get('from', 'body')
        expression = rule.get('expression', '')
        if source == 'body':
            if body is None:
                body = response.json()
            extracted[name] = _extract_by_expression(body, expression)
        elif source == 'headers':
            extracted[name] = response.headers.get(expression)
        elif source == 'text':
            extracted[name] = response.text
    return extracted


def _render_html_report(execution: TestExecution, testcase_results: list[dict[str, Any]]) -> str:
    rows = []
    for testcase_result in testcase_results:
        step_rows = []
        for step in testcase_result['steps']:
            step_rows.append(
                f"<tr><td>{step['order']}</td><td>{html.escape(step['name'])}</td><td>{html.escape(step['status'])}</td>"
                f"<td><pre>{html.escape(json.dumps(step['request'], ensure_ascii=False, indent=2, default=str))}</pre></td>"
                f"<td><pre>{html.escape(json.dumps(step['response'], ensure_ascii=False, indent=2, default=str))}</pre></td>"
                f"<td><pre>{html.escape(json.dumps(step['extracted'], ensure_ascii=False, indent=2, default=str))}</pre></td>"
                f"<td><pre>{html.escape(json.dumps(step['assertions'], ensure_ascii=False, indent=2, default=str))}</pre></td>"
                f"<td>{html.escape(step['error'] or '')}</td></tr>"
            )

        rows.append(
            f"<h2>{html.escape(testcase_result['name'])} ({html.escape(testcase_result['status'])})</h2>"
            "<table border='1' cellspacing='0' cellpadding='6' style='border-collapse:collapse;width:100%'>"
            "<thead><tr><th>顺序</th><th>步骤</th><th>状态</th><th>请求</th><th>响应</th><th>提取变量</th><th>断言</th><th>错误</th></tr></thead>"
            f"<tbody>{''.join(step_rows)}</tbody></table>"
        )

    summary = execution.summary or {}
    return (
        "<html><head><meta charset='utf-8'><title>Execution Report</title></head><body>"
        f"<h1>Execution #{execution.id}</h1>"
        f"<p>项目: {html.escape(execution.project.name)}</p>"
        f"<p>总场景: {summary.get('total', 0)}，通过: {summary.get('passed', 0)}，失败: {summary.get('failed', 0)}</p>"
        f"{''.join(rows)}"
        "</body></html>"
    )


def _collect_testcases(execution: TestExecution) -> list[TestCase]:
    queryset = TestCase.objects.select_related('api', 'environment', 'default_environment', 'project').prefetch_related('steps__api', 'steps__environment')
    queryset = queryset.filter(project=execution.project, enabled=True)
    if execution.testcase_id:
        queryset = queryset.filter(pk=execution.testcase_id)
    return list(queryset.order_by('id'))


def run_execution(execution: TestExecution) -> TestExecution:
    execution.status = 'RUNNING'
    execution.started_at = timezone.now()
    execution.save(update_fields=['status', 'started_at', 'updated_at'])

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    testcases = _collect_testcases(execution)
    if not testcases:
        execution.status = 'FAILED'
        execution.finished_at = timezone.now()
        execution.summary = {'total': 0, 'passed': 0, 'failed': 0, 'note': 'No enabled testcases found'}
        execution.report_path = ''
        execution.save(update_fields=['status', 'finished_at', 'summary', 'report_path', 'updated_at'])
        return execution

    execution.step_results.all().delete()

    testcase_results: list[dict[str, Any]] = []
    passed = 0
    failed = 0

    for testcase in testcases:
        context = dict((testcase.default_environment.variables if testcase.default_environment else {}) or {})
        if testcase.environment:
            context.update(testcase.environment.variables or {})

        steps = list(testcase.steps.filter(enabled=True).select_related('api', 'environment').order_by('order', 'id'))
        if not steps and testcase.api_id:
            legacy_step = {
                'order': 1,
                'name': testcase.name,
                'api': testcase.api,
                'environment': testcase.environment,
                'request_overrides': testcase.request_data or {},
                'assertion_rules': [
                    {'type': 'status_code', 'expected': testcase.assertions.get('status_code')}
                ] if isinstance(testcase.assertions, dict) and testcase.assertions.get('status_code') is not None else [],
                'extract_rules': [],
                'continue_on_failure': False,
            }
            steps = [legacy_step]

        testcase_status = 'PASSED'
        step_payloads = []

        for raw_step in steps:
            is_model = isinstance(raw_step, TestStep)
            step_name = raw_step.name if is_model else raw_step['name']
            step_order = raw_step.order if is_model else raw_step['order']
            step_api = raw_step.api if is_model else raw_step['api']
            step_env = raw_step.environment if is_model else raw_step.get('environment')
            step_request_overrides = raw_step.request_overrides if is_model else raw_step.get('request_overrides', {})
            step_assertion_rules = raw_step.assertion_rules if is_model else raw_step.get('assertion_rules', [])
            step_extract_rules = raw_step.extract_rules if is_model else raw_step.get('extract_rules', [])
            step_continue = raw_step.continue_on_failure if is_model else raw_step.get('continue_on_failure', False)

            temp_step = raw_step if is_model else type('LegacyStep', (), {
                'api': step_api,
                'environment': step_env,
                'testcase': testcase,
                'request_overrides': step_request_overrides,
            })()

            step_result = ExecutionStepResult.objects.create(
                execution=execution,
                testcase=testcase,
                teststep=raw_step if is_model else None,
                order=step_order,
                status='RUNNING',
                started_at=timezone.now(),
            )

            request_snapshot = _build_request_snapshot(temp_step, context)
            response_snapshot: dict[str, Any] = {}
            extracted_variables: dict[str, Any] = {}
            assertion_result: dict[str, Any] = {}
            error_message = ''
            step_status = 'PASSED'

            try:
                response = requests.request(
                    method=request_snapshot['method'],
                    url=request_snapshot['url'],
                    headers=request_snapshot['headers'],
                    params=request_snapshot['params'],
                    json=request_snapshot['json'],
                    timeout=15,
                )
                try:
                    response_body = response.json()
                except ValueError:
                    response_body = response.text

                response_snapshot = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': response_body,
                }
                ok, rule_results, assertion_error = _run_assertions(response, step_assertion_rules or [])
                assertion_result = {'passed': ok, 'results': rule_results}
                extracted_variables = _extract_variables(response, step_extract_rules or [])
                context.update(extracted_variables)
                if not ok:
                    step_status = 'FAILED'
                    error_message = assertion_error
            except Exception as exc:
                step_status = 'FAILED'
                error_message = str(exc)
                assertion_result = {'passed': False, 'results': []}

            step_result.status = step_status
            step_result.request_snapshot = request_snapshot
            step_result.response_snapshot = response_snapshot
            step_result.extracted_variables = extracted_variables
            step_result.assertion_result = assertion_result
            step_result.error_message = error_message
            step_result.finished_at = timezone.now()
            step_result.save()

            step_payloads.append({
                'order': step_order,
                'name': step_name,
                'status': step_status,
                'request': request_snapshot,
                'response': response_snapshot,
                'extracted': extracted_variables,
                'assertions': assertion_result,
                'error': error_message,
            })

            if step_status == 'FAILED':
                testcase_status = 'FAILED'
                if not step_continue:
                    break

        if testcase_status == 'PASSED':
            passed += 1
        else:
            failed += 1

        testcase_results.append({
            'id': testcase.id,
            'name': testcase.name,
            'status': testcase_status,
            'steps': step_payloads,
        })

    report_file = REPORT_DIR / f'execution_{execution.id}.html'
    report_file.write_text(_render_html_report(execution, testcase_results), encoding='utf-8')

    allure_results = ALLURE_RESULTS_DIR / f'execution_{execution.id}'
    allure_report = ALLURE_REPORT_DIR / f'execution_{execution.id}'
    allure_results.mkdir(parents=True, exist_ok=True)
    (allure_results / 'summary.json').write_text(json.dumps(testcase_results, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

    allure_html_path = ''
    allure_note = ''
    try:
        generate_cmd = ['allure', 'generate', str(allure_results), '-o', str(allure_report), '--clean']
        generate_result = subprocess.run(generate_cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
        if generate_result.returncode == 0 and (allure_report / 'index.html').exists():
            allure_html_path = str((allure_report / 'index.html').relative_to(BASE_DIR))
        else:
            allure_note = generate_result.stderr or generate_result.stdout or 'Allure CLI generate failed'
    except FileNotFoundError:
        allure_note = 'Allure CLI not installed. Install Java and allure to render the full Allure HTML report.'

    total = len(testcases)
    execution.status = 'PASSED' if failed == 0 else 'FAILED'
    execution.finished_at = timezone.now()
    execution.report_path = str(report_file.relative_to(BASE_DIR)) if report_file.exists() else ''
    execution.summary = {
        'total': total,
        'passed': passed,
        'failed': failed,
        'testcase_results': testcase_results,
        'allure_results_path': str(allure_results.relative_to(BASE_DIR)),
        'allure_html_path': allure_html_path,
        'allure_note': allure_note,
    }
    execution.save(update_fields=['status', 'finished_at', 'report_path', 'summary', 'updated_at'])

    if execution.report_path:
        TestReport.objects.update_or_create(
            execution=execution,
            defaults={
                'title': f'Execution #{execution.id} Report',
                'html_path': execution.report_path,
                'total': total,
                'passed': passed,
                'failed': failed,
                'skipped': 0,
            },
        )
    return execution
