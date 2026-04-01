from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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

        response = {
            "message": message,
            "status": True,
            "data": data
        }
        return Response(response, status=status_code)


class QuizListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizListSerializer(quizzes, many=True)

        return Response({
            "message": "Quizzes fetched successfully.",
            "status": True,
            "data": serializer.data
        })


class QuizDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
        serializer = QuizDetailSerializer(quiz)

        return Response({
            "message": "Quiz fetched successfully.",
            "status": True,
            "data": serializer.data
        })


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
        return Response({
            "message": "Settings fetched successfully.",
            "status": True,
            "data": serializer.data
        })

    def patch(self, request):
        config, created = GenerationConfig.objects.get_or_create(user=request.user)
        serializer = GenerationConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Settings updated successfully.",
            "status": True,
            "data": serializer.data
        })


class LLMModelListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models = LLMModel.objects.filter(status=True)
        serializer = LLMModelSerializer(models, many=True)
        return Response({
            "message": "Models fetched successfully.",
            "status": True,
            "data": serializer.data
        })
