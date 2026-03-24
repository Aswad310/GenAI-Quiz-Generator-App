from rest_framework import serializers, status
from .models import Document
from django.db import transaction


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['user', 'file_size', 'file_type', 'created_at', 'updated_at']


class DocumentCreateAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'file']

    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        file = validated_data.get('file')
        title = validated_data.get('title')

        file_size = file.size
        file_type = file.name.split('.')[-1] if '.' in file.name else 'unknown'

        document = Document.objects.create(
            user=user,
            title=title,
            file=file,
            file_size=file_size,
            file_type=file_type
        )

        data = DocumentSerializer(document).data
        return data, "Document uploaded successfully.", status.HTTP_201_CREATED
