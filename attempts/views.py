from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import QuizAttempt
from .serializers import (
    QuizAttemptSerializer,
    StartAttemptAPIViewSerializer,
    SubmitAnswerAPIViewSerializer,
    FinishAttemptAPIViewSerializer
)


class StartAttemptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request):
        serializer = StartAttemptAPIViewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data, message, status_code = serializer.save()
        response = {
            "message": message,
            "status": True,
            "data": data
        }
        return Response(response, status=status_code)


class SubmitAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request, attempt_id):
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        serializer = SubmitAnswerAPIViewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data, message, status_code = serializer.save(attempt=attempt)
        response = {
            "message": message,
            "status": True,
            "data": data
        }
        return Response(response, status=status_code)


class FinishAttemptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request, attempt_id):
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

        # Use an empty dictionary to ensure validation runs successfully 
        # as there might be no fields passed directly into the body.
        data_input = request.data if request.data else {}
        serializer = FinishAttemptAPIViewSerializer(data=data_input, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data, message, status_code = serializer.save(attempt=attempt)
        response = {
            "message": message,
            "status": True,
            "data": data
        }
        return Response(response, status=status_code)


class AttemptDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        attempt = get_object_or_404(QuizAttempt, pk=pk, user=request.user)

        serializer = QuizAttemptSerializer(attempt)
        response = {
            "message": "Attempt fetched successfully.",
            "status": True,
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)
