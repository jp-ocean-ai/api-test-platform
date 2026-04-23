from django.db import models

from core.models import TimeStampedModel
from projects.models import Project


class TestExecution(TimeStampedModel):
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('RUNNING', 'RUNNING'),
        ('PASSED', 'PASSED'),
        ('FAILED', 'FAILED'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='executions')
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
