from rest_framework import viewsets

from .models import TestCase
from .serializers import TestCaseSerializer


class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.select_related('project', 'environment', 'api').all()
    serializer_class = TestCaseSerializer
