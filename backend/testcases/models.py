from django.db import models

from apis.models import ApiDefinition
from core.models import TimeStampedModel
from environments.models import Environment
from projects.models import Project


class TestCase(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testcases')
    environment = models.ForeignKey(Environment, on_delete=models.SET_NULL, null=True, blank=True, related_name='testcases')
    api = models.ForeignKey(ApiDefinition, on_delete=models.CASCADE, related_name='testcases')
    name = models.CharField(max_length=120)
    request_data = models.JSONField(default=dict, blank=True)
    assertions = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']
        unique_together = ('project', 'name')

    def __str__(self):
        return f'{self.project.name} - {self.name}'
