from django.contrib import admin
from .models import GenerationConfig, Quiz, Question, Option, LLMModel


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    search_fields = ('name',)


@admin.register(GenerationConfig)
class GenerationConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'model', 'temp', 'created_at')
    search_fields = ('user__username', 'model__name')
    list_filter = ('created_at',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'number_of_mcqs', 'difficulty_level', 'created_at')
    search_fields = ('title', 'user__username', 'user__email')
    list_filter = ('difficulty_level', 'status', 'created_at')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'order_index', 'status')
    search_fields = ('question_text', 'quiz__title')
    list_filter = ('quiz', 'status')
    inlines = [OptionInline]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_text', 'question', 'is_correct', 'status')
    search_fields = ('option_text', 'question__question_text')
    list_filter = ('is_correct', 'status')
