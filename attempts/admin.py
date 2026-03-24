from django.contrib import admin
from .models import QuizAttempt, UserAnswer

admin.site.register(QuizAttempt)
admin.site.register(UserAnswer)
