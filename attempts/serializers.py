from rest_framework import serializers, status
from django.utils import timezone
from django.db import transaction
from .models import QuizAttempt, UserAnswer
from quizzes.models import Quiz, Question, Option


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'
        read_only_fields = ['attempt', 'is_correct']


class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = '__all__'
        read_only_fields = ['user', 'score', 'total_questions', 'started_at', 'completed_at']


class StartAttemptAPIViewSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()

    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get('request')
        quiz_id = validated_data.get('quiz_id')

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError({"message": "Quiz not found."})

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            total_questions=quiz.total_questions
        )

        data = QuizAttemptSerializer(attempt).data
        return data, "Quiz attempt started successfully.", status.HTTP_201_CREATED


class SubmitAnswerAPIViewSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    option_id = serializers.UUIDField()

    @transaction.atomic()
    def create(self, validated_data):
        attempt = validated_data.get('attempt')
        question_id = validated_data.get('question_id')
        option_id = validated_data.get('option_id')

        if attempt.completed_at:
            raise serializers.ValidationError({"message": "Attempt already completed."})

        try:
            question = Question.objects.get(id=question_id, quiz=attempt.quiz)
        except Question.DoesNotExist:
            raise serializers.ValidationError({"message": "Question not found in this quiz."})

        try:
            option = Option.objects.get(id=option_id, question=question)
        except Option.DoesNotExist:
            raise serializers.ValidationError({"message": "Option not found for this question."})

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


class FinishAttemptAPIViewSerializer(serializers.Serializer):

    @transaction.atomic()
    def create(self, validated_data):
        attempt = validated_data.get('attempt')
        if attempt.completed_at:
            raise serializers.ValidationError({"message": "Attempt already completed."})

        attempt.completed_at = timezone.now()
        correct_answers = UserAnswer.objects.filter(attempt=attempt, is_correct=True).count()
        attempt.score = correct_answers
        attempt.save()

        data = QuizAttemptSerializer(attempt).data
        return data, "Quiz attempt finished successfully.", status.HTTP_200_OK
