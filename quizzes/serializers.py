from rest_framework import serializers, status
from .models import GenerationConfig, Quiz, Question, Option
from documents.models import Document
from django.shortcuts import get_object_or_404
from django.db import transaction


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

    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class GenerateQuizAPIViewSerializer(serializers.Serializer):
    document_id = serializers.UUIDField()
    generation_config = GenerationConfigSerializer()
    title = serializers.CharField(max_length=255, required=False, default='Generated Quiz')
    difficulty_level = serializers.CharField(max_length=50, required=False, default='Medium')

    @transaction.atomic()
    def create(self, validated_data):
        request = self.context.get('request')
        document_id = validated_data.get('document_id')
        config_data = validated_data.get('generation_config')
        title = validated_data.get('title')
        difficulty = validated_data.get('difficulty_level')

        try:
            document = Document.objects.get(id=document_id, user=request.user)
        except Document.DoesNotExist:
            raise serializers.ValidationError({"message": "Document not found."})

        config = GenerationConfig.objects.create(**config_data)

        file_path = document.file.path
        ext = file_path.split('.')[-1].lower()
        content = ""
        if ext == 'pdf':
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            content = "\\n".join([doc.page_content for doc in docs])
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        content = content[:15000]

        from langchain_ollama import ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser

        llm = ChatOllama(
            base_url="http://localhost:11434",
            model=config.model_name,
            temperature=config.temperature,
            format="json"
        )

        template = """
You are an expert quiz generator. Generate exactly {number_of_mcqs} multiple choice questions from the provided text.
The difficulty should be {difficulty}.

Respond with a JSON object containing a single key "questions" mapping to a list of question objects.
Each question object MUST have:
- "question_text": The question string
- "options": A list of exactly 4 strings representing the choices
- "correct_answer": The exact string from the options list that is the correct answer

Context text:
{context}
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | JsonOutputParser()

        try:
            result = chain.invoke({
                "number_of_mcqs": config.number_of_mcqs,
                "difficulty": difficulty,
                "context": content
            })
        except Exception as e:
            raise serializers.ValidationError({"message": f"LLM generation failed: {str(e)}"})

        quiz = Quiz.objects.create(
            user=request.user,
            document=document,
            generation_config=config,
            title=title,
            difficulty_level=difficulty,
            total_questions=len(result.get('questions', []))
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
