from src.llms.base_client import BaseLLMClient
from openai import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()

class OpenAIClient(BaseLLMClient):
    def __init__(self, model_alias, model_snapshot):
        super().__init__()
        self.client = self.instantiate_client()
        self.model = model_snapshot
        self.model_alias = model_alias
    
    def instantiate_client(self):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_response(self, prompt):
        # If prompt is a string, wrap it in a message object.
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        message_text = response.choices[0].message.content
        return message_text