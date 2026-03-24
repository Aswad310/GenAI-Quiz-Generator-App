from django.urls import path
from .views import DocumentListCreateAPIView, DocumentDetailAPIView

urlpatterns = [
  path('', DocumentListCreateAPIView.as_view(), name='document-list-create'),
  path('<uuid:pk>/', DocumentDetailAPIView.as_view(), name='document-detail'),
]
