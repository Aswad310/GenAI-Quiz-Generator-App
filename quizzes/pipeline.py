from typing import List
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class QuestionSchema(BaseModel):
    question_text: str = Field(description="The question string")
    options: List[str] = Field(description="A list of exactly 4 strings representing the choices")
    correct_answer: str = Field(description="The exact string from the options list that is the correct answer")


class QuizSchema(BaseModel):
    questions: List[QuestionSchema] = Field(description="A list of generated questions")


class QuizGenerationPipeline:

    def __init__(self, file_path, config, difficulty, number_of_mcqs):
        self.file_path = file_path
        self.config = config
        self.difficulty = difficulty
        self.number_of_mcqs = number_of_mcqs
        self.parser = JsonOutputParser(pydantic_object=QuizSchema)

    def load_content(self):
        ext = self.file_path.split('.')[-1].lower()
        content = ""
        if ext == 'pdf':
            loader = PyPDFLoader(self.file_path)
            docs = loader.load()
            content = "\n".join([doc.page_content for doc in docs])
        else:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        return content[:10000]

    def get_llm(self):
        return ChatOllama(
            model=self.config.model.name,
            temperature=self.config.temp,
            format="json",
            num_ctx=4096
        )

    def get_prompt_template(self):
        template = """
                    You are an expert quiz generator. Your task is to generate exactly {number_of_mcqs} multiple choice questions (MCQs) from the provided context.
                    Each question MUST have exactly 4 options.
                    Difficulty level: {difficulty}

                    DO NOT summarize the text. DO NOT provide sections or points unless they are part of a question.
                    Focus solely on generating the quiz questions.

                    Context text:
                    {context}

                    {format_instructions}
                    """
        return PromptTemplate(
            template=template,
            input_variables=["number_of_mcqs", "difficulty", "context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def run(self):
        content = self.load_content()
        llm = self.get_llm()
        prompt = self.get_prompt_template()
        chain = prompt | llm | self.parser

        result = chain.invoke({
            "number_of_mcqs": self.number_of_mcqs,
            "difficulty": self.difficulty,
            "context": content
        })

        return result
