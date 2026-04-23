from rest_framework import viewsets

from .models import ApiDefinition
from .serializers import ApiDefinitionSerializer


class ApiDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ApiDefinition.objects.select_related('project').all()
    serializer_class = ApiDefinitionSerializer
