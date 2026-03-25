from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from .models import Document
from .serializers import DocumentSerializer, DocumentCreateAPIViewSerializer


class DocumentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(user=request.user)
        serializer = DocumentSerializer(documents, many=True)
        response = {
            "message": "Documents fetched successfully.",
            "status": True,
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    @transaction.atomic()
    def post(self, request):
        serializer = DocumentCreateAPIViewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data, message, status_code = serializer.save()
        response = {
            "message": message,
            "status": True,
            "data": data
        }
        return Response(response, status=status_code)


class DocumentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk, user=request.user)
        serializer = DocumentSerializer(document)
        response = {
            "message": "Document fetched successfully.",
            "status": True,
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    @transaction.atomic()
    def delete(self, request, pk):
        document = get_object_or_404(Document, pk=pk, user=request.user)
        document.delete()
        response = {
            "message": "Document deleted successfully.",
            "status": True,
            "data": {}
        }
        return Response(response, status=status.HTTP_200_OK)
