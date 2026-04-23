from django.db import models

from core.models import TimeStampedModel
from projects.models import Project


class ApiDefinition(TimeStampedModel):
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='apis')
    name = models.CharField(max_length=120)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='GET')
    path = models.CharField(max_length=255)
    headers = models.JSONField(default=dict, blank=True)
    query_params = models.JSONField(default=dict, blank=True)
    body_template = models.JSONField(default=dict, blank=True)
    expected_result = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']
        unique_together = ('project', 'name')

    def __str__(self):
        return f'{self.project.name} - {self.name}'
