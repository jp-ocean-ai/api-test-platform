from django.db import models

from core.models import TimeStampedModel


class Project(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    owner = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name
