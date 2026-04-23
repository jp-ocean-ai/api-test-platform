from rest_framework import serializers

from .models import TestExecution


class TestExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestExecution
        fields = '__all__'
