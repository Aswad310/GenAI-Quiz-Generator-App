from rest_framework import serializers, status
from .models import GenerationConfig, Quiz, Question, Option
from documents.models import Document
from django.shortcuts import get_object_or_404
from django.db import transaction
from .pipeline import QuizGenerationPipeline
from .constants import QuizDifficultyChoicesClass


class GenerationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationConfig
        fields = '__all__'


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


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    total_questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_total_questions(self, obj):
        return obj.questions.count()


class GenerateQuizAPIViewSerializer(serializers.Serializer):
    document_id = serializers.UUIDField()
    generation_config = GenerationConfigSerializer()
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
        config_data = validated_data.get('generation_config')
        title = validated_data.get('title')
        difficulty = validated_data.get('difficulty_level')

        document = get_object_or_404(Document, id=document_id, user=request.user)

        config = GenerationConfig.objects.create(**config_data)

        try:
            pipeline = QuizGenerationPipeline(document.file.path, config, difficulty)
            result = pipeline.run()
        except Exception as e:
            raise serializers.ValidationError({"message": f"LLM generation failed: {str(e)}"})

        quiz = Quiz.objects.create(
            user=request.user,
            document=document,
            generation_config=config,
            title=title,
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
