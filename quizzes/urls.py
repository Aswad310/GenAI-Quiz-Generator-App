from django.urls import path
from .views import (
    GenerateQuizAPIView,
    QuizListAPIView,
    QuizDetailAPIView,
    GenerationConfigAPIView,
    LLMModelListAPIView
)

urlpatterns = [
    path('generate/', GenerateQuizAPIView.as_view(), name='quiz-generate'),
    path('settings/', GenerationConfigAPIView.as_view(), name='quiz-settings'),
    path('models/', LLMModelListAPIView.as_view(), name='llm-models'),
    path('', QuizListAPIView.as_view(), name='quiz-list'),
    path('<uuid:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
]
