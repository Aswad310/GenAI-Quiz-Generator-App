from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.responses import BaseResponse
from core.pagination import StandardPagination
from django.db import transaction
from .models import Quiz, LLMModel, GenerationConfig
from .serializers import QuizListSerializer, QuizDetailSerializer, GenerateQuizAPIViewSerializer, \
    GenerationConfigSerializer, \
    LLMModelSerializer


class GenerateQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request):
        generate_serializer = GenerateQuizAPIViewSerializer(data=request.data, context={'request': request})
        generate_serializer.is_valid(raise_exception=True)
        data, message, status_code = generate_serializer.save()

        return BaseResponse(data, message=message, status_code=status_code)


class QuizListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = Quiz.objects.filter(user=request.user).order_by('-created_at')
        paginator = StandardPagination()
        paginated_quizzes = paginator.paginate_queryset(quizzes, request)
        serializer = QuizListSerializer(paginated_quizzes, many=True)
        return paginator.get_paginated_response(serializer.data)


class QuizDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
        serializer = QuizDetailSerializer(quiz)
        return BaseResponse(serializer.data, message="Quiz fetched successfully.")


class GenerationConfigAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        config, created = GenerationConfig.objects.get_or_create(
            user=request.user,
            defaults={
                'model': LLMModel.objects.filter(status=True).first(),
                'temp': 0.7
            }
        )
        serializer = GenerationConfigSerializer(config)
        return BaseResponse(serializer.data, message="Settings fetched successfully.")

    def patch(self, request):
        config, created = GenerationConfig.objects.get_or_create(user=request.user)
        serializer = GenerationConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return BaseResponse(serializer.data, message="Settings updated successfully.")


class LLMModelListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models = LLMModel.objects.filter(status=True).order_by('name')
        paginator = StandardPagination()
        paginated_models = paginator.paginate_queryset(models, request)
        serializer = LLMModelSerializer(paginated_models, many=True)
        return paginator.get_paginated_response(serializer.data)
