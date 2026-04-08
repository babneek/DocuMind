import os
from dotenv import load_dotenv
import openai
import time

load_dotenv()

class LLMService:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.extra_body = None
        
        if nvidia_api_key and "your" not in nvidia_api_key:
            self.model_name = os.getenv("NVIDIA_MODEL", "deepseek-ai/deepseek-v3.2")
            print(f"[LLMService] Using NVIDIA Integrate with model {self.model_name}")
            self.client = openai.OpenAI(
                api_key=nvidia_api_key,
                base_url="https://integrate.api.nvidia.com/v1"
            )
            self.extra_body = {"chat_template_kwargs": {"thinking": True}}
        elif groq_api_key and "your" not in groq_api_key:
            print(f"[LLMService] Using Groq API with model {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')}")
            self.client = openai.OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        elif openai_api_key and "your" not in openai_api_key:
            print(f"[LLMService] Using OpenRouter/OpenAI with model {os.getenv('OPENROUTER_MODEL', 'mistralai/mistral-7b-instruct')}")
            self.client = openai.OpenAI(
                api_key=openai_api_key,
                base_url="https://openrouter.ai/api/v1/"
            )
            self.model_name = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
        else:
            print("[LLMService] WARNING: No valid API key found in .env")
            self.client = None
            self.model_name = None
    
    @staticmethod
    def get_groq_client():
        """Get a Groq-specific client for faster responses"""
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key and "your" not in groq_api_key:
            client = openai.OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            return client, model_name
        return None, None

    def generate_summary(self, text: str) -> str:
        prompt = (
            "Please provide a comprehensive, detailed, and multi-paragraph summary of the following text. The summary should cover all key points, main ideas, and important details. Write at least 3 paragraphs.\n\n"
            f"{text}\n\nLong, Detailed Summary:"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to generate summary: {e}"

    def answer_question(self, question: str, context: str) -> str:
        prompt = f"""
        You are an intelligent assistant. Based ONLY on the context provided below, answer the user's question.
        If the answer is not in the context, say "I don't have enough information in the documents to answer that."

        Context:
        ---
        {context}
        ---

        Question: {question}
        Answer:
        """
        try:
            request_args = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 1000,
            }
            if self.extra_body:
                request_args["extra_body"] = self.extra_body

            response = self.client.chat.completions.create(**request_args)
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to answer question: {e}"

    def extract_structured_data(self, text: str, schema_description: str) -> str:
        prompt = f"""
        Extract structured information from the following text based on this description: {schema_description}.
        Provide the output in valid JSON format ONLY.

        Text:
        ---
        {text}
        ---

        JSON Output:
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to extract data: {e}"

    def generate_response(self, prompt: str) -> str:
        try:
            request_args = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000,
            }
            if self.extra_body:
                request_args["extra_body"] = self.extra_body

            response = self.client.chat.completions.create(**request_args)
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error] Failed to generate response: {e}"
