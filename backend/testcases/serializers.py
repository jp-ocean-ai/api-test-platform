from rest_framework import serializers

from .models import TestCase, TestStep


class ProjectScopedValidationMixin:
    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = getattr(self, 'instance', None)

        project = attrs.get('project')
        if project is None and instance is not None:
            project = instance.project

        testcase = attrs.get('testcase')
        if testcase is None and instance is not None and hasattr(instance, 'testcase'):
            testcase = instance.testcase

        if testcase is not None:
            if project is None:
                project = testcase.project
            elif testcase.project_id != project.id:
                raise serializers.ValidationError({'testcase': 'testcase must belong to the selected project'})

        for field_name in ('environment', 'default_environment'):
            value = attrs.get(field_name)
            if value is None and instance is not None and hasattr(instance, field_name):
                value = getattr(instance, field_name)
            if value is not None and project is not None and value.project_id != project.id:
                raise serializers.ValidationError({field_name: f'{field_name} must belong to the selected project'})

        api = attrs.get('api')
        if api is None and instance is not None and hasattr(instance, 'api'):
            api = instance.api
        if api is not None and project is not None and api.project_id != project.id:
            raise serializers.ValidationError({'api': 'api must belong to the selected project'})

        return attrs


class TestStepSerializer(ProjectScopedValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = TestStep
        fields = '__all__'


class TestCaseSerializer(ProjectScopedValidationMixin, serializers.ModelSerializer):
    steps = TestStepSerializer(many=True, read_only=True)

    class Meta:
        model = TestCase
        fields = '__all__'
