from rest_framework import serializers, status
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import QuizAttempt, UserAnswer
from quizzes.models import Quiz, Question, Option
from quizzes.serializers import QuizDetailSerializer


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'
        read_only_fields = ['attempt', 'is_correct']


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizDetailSerializer(read_only=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = '__all__'
        read_only_fields = ['user', 'score', 'started_at', 'completed_at']

    def get_answers(self, obj):
        return UserAnswerSerializer(obj.answers.all(), many=True).data


class StartAttemptAPIViewSerializer(serializers.ModelSerializer):
    quiz_id = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), source='quiz')

    class Meta:
        model = QuizAttempt
        fields = ['quiz_id']

    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get('request')
        quiz = validated_data.get('quiz')

        # Check for existing active attempt
        existing_attempt = QuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user,
            completed_at__isnull=True
        ).first()

        if existing_attempt:
            data = QuizAttemptSerializer(existing_attempt).data
            return data, "Existing quiz attempt resumed.", status.HTTP_200_OK

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
        )

        data = QuizAttemptSerializer(attempt).data
        return data, "Quiz attempt started successfully.", status.HTTP_201_CREATED


class SubmitAnswerAPIViewSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(), source='question')
    option_id = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), source='selected_option')

    class Meta:
        model = UserAnswer
        fields = ['question_id', 'option_id']

    @transaction.atomic()
    def create(self, validated_data):
        attempt = validated_data.get('attempt')
        question = validated_data.get('question')
        option = validated_data.get('selected_option')

        if attempt.completed_at:
            raise serializers.ValidationError({"message": "Attempt already completed."})

        # Ensure the question belongs to this quiz
        if question.quiz != attempt.quiz:
            raise serializers.ValidationError({"message": "Question does not belong to this quiz."})

        # Ensure the option belongs to this question
        if option.question != question:
            raise serializers.ValidationError({"message": "Option does not belong to this question."})

        user_answer, created = UserAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_option': option,
                'is_correct': option.is_correct
            }
        )

        data = UserAnswerSerializer(user_answer).data
        return data, "Answer submitted successfully.", status.HTTP_200_OK


class FinishAttemptAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = []

    @transaction.atomic()
    def update(self, instance, validated_data):
        if instance.completed_at:
            raise serializers.ValidationError({"message": "Attempt already completed."})

        instance.completed_at = timezone.now()
        correct_answers = UserAnswer.objects.filter(attempt=instance, is_correct=True).count()
        instance.score = correct_answers
        instance.save()

        data = QuizAttemptSerializer(instance).data
        return data, "Quiz attempt finished successfully.", status.HTTP_200_OK
