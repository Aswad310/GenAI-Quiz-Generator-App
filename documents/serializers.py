from rest_framework import serializers, status
from .models import Document
from django.db import transaction


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


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

        document = Document.objects.create(
            user=user,
            title=title,
            file=file
        )

        data = DocumentSerializer(document).data
        return data, "Document uploaded successfully.", status.HTTP_201_CREATED
