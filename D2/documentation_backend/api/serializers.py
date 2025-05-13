from rest_framework import serializers
from .models import CodeDocumentation, APIDocumentation, DatabaseSchema

class CodeDocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeDocumentation
        fields = '__all__'

class APIDocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIDocumentation
        fields = '__all__'

class DatabaseSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseSchema
        fields = '__all__'