from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from django.utils import timezone

from reports.models import TestReport
from testcases.models import TestCase
from .models import TestExecution


BASE_DIR = Path(__file__).resolve().parent.parent
RUNTIME_TEST_DIR = BASE_DIR / 'runtime_tests'
REPORT_DIR = BASE_DIR / 'reports'
ALLURE_RESULTS_DIR = BASE_DIR / 'allure-results'
ALLURE_REPORT_DIR = BASE_DIR / 'allure-report'


def _to_python_literal(value: Any) -> str:
    return repr(value)


def build_pytest_file(testcase: TestCase, report_file: Path) -> Path:
    api = testcase.api
    env = testcase.environment
    base_url = env.base_url if env else 'http://127.0.0.1:8001'
    path = api.path
    if not path.startswith('/'):
        path = '/' + path

    test_file = RUNTIME_TEST_DIR / f'test_execution_{testcase.id}.py'
    content = f'''import requests


def test_case_{testcase.id}():
    base_url = {_to_python_literal(base_url)}
    url = base_url.rstrip('/') + {_to_python_literal(path)}
    method = {_to_python_literal(api.method.lower())}
    headers = {_to_python_literal(api.headers or {})}
    params = {_to_python_literal(api.query_params or {})}
    json_body = {_to_python_literal(testcase.request_data or api.body_template or {})}
    assertions = {_to_python_literal(testcase.assertions or {})}

    response = requests.request(method=method, url=url, headers=headers, params=params, json=json_body, timeout=15)

    expected_status = assertions.get('status_code')
    if expected_status is not None:
        assert response.status_code == expected_status

    expected_json = assertions.get('json')
    if expected_json is not None:
        data = response.json()
        for key, value in expected_json.items():
            assert data.get(key) == value
'''
    test_file.write_text(content, encoding='utf-8')
    return test_file


def run_execution(execution: TestExecution) -> TestExecution:
    execution.status = 'RUNNING'
    execution.started_at = timezone.now()
    execution.save(update_fields=['status', 'started_at', 'updated_at'])

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_TEST_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    testcases = list(
        TestCase.objects.select_related('api', 'environment', 'project')
        .filter(project=execution.project, enabled=True)
        .order_by('id')
    )

    if not testcases:
        execution.status = 'FAILED'
        execution.finished_at = timezone.now()
        execution.summary = {'total': 0, 'passed': 0, 'failed': 0, 'note': 'No enabled testcases found'}
        execution.report_path = ''
        execution.save(update_fields=['status', 'finished_at', 'summary', 'report_path', 'updated_at'])
        return execution

    test_files = []
    report_file = REPORT_DIR / f'execution_{execution.id}.html'
    allure_results = ALLURE_RESULTS_DIR / f'execution_{execution.id}'
    allure_report = ALLURE_REPORT_DIR / f'execution_{execution.id}'
    allure_results.mkdir(parents=True, exist_ok=True)
    for testcase in testcases:
        test_files.append(str(build_pytest_file(testcase, report_file)))

    cmd = [
        str(BASE_DIR / '.venv' / 'bin' / 'python'),
        '-m',
        'pytest',
        *test_files,
        f'--html={report_file}',
        '--self-contained-html',
        f'--alluredir={allure_results}',
        '-q',
    ]

    result = subprocess.run(
        cmd,
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
    )

    stdout = result.stdout or ''
    stderr = result.stderr or ''
    passed = 0
    failed = 0
    total = len(testcases)

    if ' passed' in stdout:
        import re
        m = re.search(r'(\d+) passed', stdout)
        if m:
            passed = int(m.group(1))
    if ' failed' in stdout:
        import re
        m = re.search(r'(\d+) failed', stdout)
        if m:
            failed = int(m.group(1))

    if passed == 0 and failed == 0:
        failed = total if result.returncode != 0 else 0
        passed = total if result.returncode == 0 else 0

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

    execution.status = 'PASSED' if result.returncode == 0 else 'FAILED'
    execution.finished_at = timezone.now()
    execution.report_path = str(report_file.relative_to(BASE_DIR)) if report_file.exists() else ''
    execution.summary = {
        'total': total,
        'passed': passed,
        'failed': failed,
        'return_code': result.returncode,
        'stdout': stdout,
        'stderr': stderr,
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
