from rest_framework import viewsets

from .models import TestCase, TestStep
from .serializers import TestCaseSerializer, TestStepSerializer


class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.select_related('project', 'environment', 'default_environment', 'api').prefetch_related('steps').all()
    serializer_class = TestCaseSerializer


class TestStepViewSet(viewsets.ModelViewSet):
    queryset = TestStep.objects.select_related('project', 'testcase', 'environment', 'api').all()
    serializer_class = TestStepSerializer
