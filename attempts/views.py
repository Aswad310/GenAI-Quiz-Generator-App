from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.responses import BaseResponse
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
        return BaseResponse(data, message=message, status_code=status_code)


class SubmitAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request, attempt_id):
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        serializer = SubmitAnswerAPIViewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data, message, status_code = serializer.save(attempt=attempt)
        return BaseResponse(data, message=message, status_code=status_code)


class FinishAttemptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request, attempt_id):
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

        serializer = FinishAttemptAPIViewSerializer(instance=attempt, data={})
        serializer.is_valid(raise_exception=True)

        data, message, status_code = serializer.save()

        return BaseResponse(data, message=message, status_code=status_code)


class AttemptDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        attempt = get_object_or_404(QuizAttempt, pk=pk, user=request.user)

        serializer = QuizAttemptSerializer(attempt)
        return BaseResponse(serializer.data, message="Attempt fetched successfully.")
