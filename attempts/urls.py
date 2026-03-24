from django.urls import path
from .views import StartAttemptAPIView, SubmitAnswerAPIView, FinishAttemptAPIView, AttemptDetailAPIView

urlpatterns = [
  path('start/', StartAttemptAPIView.as_view(), name='attempt-start'),
  path('<uuid:attempt_id>/submit-answer/', SubmitAnswerAPIView.as_view(), name='attempt-submit-answer'),
  path('<uuid:attempt_id>/finish/', FinishAttemptAPIView.as_view(), name='attempt-finish'),
  path('<uuid:pk>/', AttemptDetailAPIView.as_view(), name='attempt-detail'),
]
