from django.contrib import admin
from .models import GenerationConfig, Quiz, Question, Option

admin.site.register(GenerationConfig)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
