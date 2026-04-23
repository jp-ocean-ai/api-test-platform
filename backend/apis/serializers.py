from rest_framework import serializers

from .models import ApiDefinition


class ApiDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiDefinition
        fields = '__all__'
