from django.db import models

from core.models import TimeStampedModel
from projects.models import Project


class Environment(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='environments')
    name = models.CharField(max_length=100)
    base_url = models.URLField(max_length=255)
    variables = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('project', 'name')
        ordering = ['-id']

    def __str__(self):
        return f'{self.project.name} - {self.name}'
