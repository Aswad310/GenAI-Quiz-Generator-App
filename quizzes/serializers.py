from rest_framework import serializers, status
from .models import GenerationConfig, Quiz, Question, Option, LLMModel
from documents.models import Document
from django.shortcuts import get_object_or_404
from django.db import transaction
from .pipeline import QuizGenerationPipeline
from .constants import QuizDifficultyChoicesClass


class LLMModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMModel
        fields = '__all__'


class GenerationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationConfig
        fields = ['id', 'model', 'temp', 'status']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'
        read_only_fields = ['question']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['quiz']


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        exclude = ('user', 'document')
        read_only_fields = ['created_at', 'updated_at']


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        exclude = ('user', 'document')
        read_only_fields = ['created_at', 'updated_at']


class GenerateQuizAPIViewSerializer(serializers.Serializer):
    document_id = serializers.UUIDField()
    number_of_mcqs = serializers.IntegerField(min_value=1, max_value=50)
    title = serializers.CharField(max_length=255, required=False, default='Generated Quiz')
    difficulty_level = serializers.CharField(
        max_length=50,
        required=False,
        default=QuizDifficultyChoicesClass.medium
    )

    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get('request')
        document_id = validated_data.get('document_id')
        number_of_mcqs = validated_data.get('number_of_mcqs')
        title = validated_data.get('title')
        difficulty = validated_data.get('difficulty_level')

        document = get_object_or_404(Document, id=document_id, user=request.user)

        # Get user's generation config
        try:
            config = request.user.generation_config
        except GenerationConfig.DoesNotExist:
            raise serializers.ValidationError({
                "message": "Generation configuration not found for the user. Please set up your generation settings first."
            })

        try:
            pipeline = QuizGenerationPipeline(document.file.path, config, difficulty, number_of_mcqs)
            result = pipeline.run()
        except Exception as e:
            raise serializers.ValidationError({"message": f"LLM generation failed: {str(e)}"})

        quiz = Quiz.objects.create(
            user=request.user,
            document=document,
            title=title,
            number_of_mcqs=number_of_mcqs,
            difficulty_level=difficulty,
        )

        for i, q_data in enumerate(result.get('questions', [])):
            question = Question.objects.create(
                quiz=quiz,
                question_text=q_data.get('question_text', ''),
                order_index=i
            )

            options = q_data.get('options', [])
            correct_answer = q_data.get('correct_answer', '')

            for opt_text in options:
                is_correct = (opt_text == correct_answer)
                Option.objects.create(
                    question=question,
                    option_text=opt_text,
                    is_correct=is_correct
                )

        data = QuizSerializer(quiz).data
        return data, "Quiz generated successfully.", status.HTTP_201_CREATED
