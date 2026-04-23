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
    description = models.TextField(blank=True)
    default_environment = models.ForeignKey(
        Environment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_testcases',
    )
    request_data = models.JSONField(default=dict, blank=True)
    assertions = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']
        unique_together = ('project', 'name')

    def __str__(self):
        return f'{self.project.name} - {self.name}'


class TestStep(TimeStampedModel):
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='steps')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='teststeps')
    order = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=120)
    api = models.ForeignKey(ApiDefinition, on_delete=models.CASCADE, related_name='teststeps')
    environment = models.ForeignKey(
        Environment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teststeps',
    )
    request_overrides = models.JSONField(default=dict, blank=True)
    extract_rules = models.JSONField(default=list, blank=True)
    assertion_rules = models.JSONField(default=list, blank=True)
    continue_on_failure = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['testcase_id', 'order', 'id']
        unique_together = ('testcase', 'order')

    def __str__(self):
        return f'{self.testcase.name} - Step {self.order} - {self.name}'
