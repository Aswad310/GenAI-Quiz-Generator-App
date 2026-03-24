from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from .models import Quiz
from .serializers import QuizSerializer, GenerateQuizAPIViewSerializer


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
        serializer = QuizSerializer(quizzes, many=True)
        response = {
            "message": "Quizzes fetched successfully.",
            "status": True,
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)


class QuizDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            quiz = Quiz.objects.get(pk=pk, user=request.user)
        except Quiz.DoesNotExist:
            return Response({
                "message": "Quiz not found.",
                "status": False,
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizSerializer(quiz)
        response = {
            "message": "Quiz fetched successfully.",
            "status": True,
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)
