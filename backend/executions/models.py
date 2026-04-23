from django.db import models

from core.models import TimeStampedModel
from projects.models import Project
from testcases.models import TestCase, TestStep


class TestExecution(TimeStampedModel):
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('RUNNING', 'RUNNING'),
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='executions')
    testcase = models.ForeignKey(TestCase, on_delete=models.SET_NULL, null=True, blank=True, related_name='executions')
    trigger_user = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    report_path = models.CharField(max_length=255, blank=True)
    summary = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.project.name} - {self.status}'


class ExecutionStepResult(TimeStampedModel):
    execution = models.ForeignKey(TestExecution, on_delete=models.CASCADE, related_name='step_results')
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='step_results')
    teststep = models.ForeignKey(TestStep, on_delete=models.CASCADE, related_name='execution_results', null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, default='PENDING')
    request_snapshot = models.JSONField(default=dict, blank=True)
    response_snapshot = models.JSONField(default=dict, blank=True)
    extracted_variables = models.JSONField(default=dict, blank=True)
    assertion_result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['execution_id', 'order', 'id']

    def __str__(self):
        return f'Execution {self.execution_id} Step {self.order} - {self.status}'
