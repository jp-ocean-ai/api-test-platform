from rest_framework import serializers

from .models import ExecutionStepResult, TestExecution


class ExecutionStepResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionStepResult
        fields = '__all__'


class TestExecutionSerializer(serializers.ModelSerializer):
    step_results = ExecutionStepResultSerializer(many=True, read_only=True)

    class Meta:
        model = TestExecution
        fields = '__all__'
