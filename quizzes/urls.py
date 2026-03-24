from django.urls import path
from .views import GenerateQuizAPIView, QuizListAPIView, QuizDetailAPIView

urlpatterns = [
  path('', QuizListAPIView.as_view(), name='quiz-list'),
  path('<uuid:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
  path('generate/', GenerateQuizAPIView.as_view(), name='quiz-generate'),
]
