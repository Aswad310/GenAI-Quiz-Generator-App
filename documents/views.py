from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.responses import BaseResponse
from core.pagination import StandardPagination
from django.db import transaction
from .models import Document
from .serializers import DocumentSerializer, DocumentCreateAPIViewSerializer


class DocumentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(user=request.user).order_by('-created_at')
        paginator = StandardPagination()
        paginated_documents = paginator.paginate_queryset(documents, request)
        serializer = DocumentSerializer(paginated_documents, many=True)
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic()
    def post(self, request):
        serializer = DocumentCreateAPIViewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data, message, status_code = serializer.save()
        return BaseResponse(data, message=message, status_code=status_code)


class DocumentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk, user=request.user)
        serializer = DocumentSerializer(document)
        return BaseResponse(serializer.data, message="Document fetched successfully.")

    @transaction.atomic()
    def delete(self, request, pk):
        document = get_object_or_404(Document, pk=pk, user=request.user)
        document.delete()
        return BaseResponse(message="Document deleted successfully.")
