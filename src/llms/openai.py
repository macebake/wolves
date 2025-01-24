from src.llms.base_client import BaseLLMClient
from openai import AsyncOpenAI
import os

class OpenAIClient(BaseLLMClient):
   def __init__(self):
       self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
       self.model = "gpt-4-turbo-preview"

   async def chat(self, messages: list, system: str) -> str:
       formatted_messages = [{"role": "system", "content": system}]
       formatted_messages.extend([
           {"role": "assistant" if msg["role"] == "assistant" else "user",
            "content": msg["content"]} 
           for msg in messages
       ])

       response = await self.client.chat.completions.create(
           model=self.model,
           messages=formatted_messages
       )
       
       return response.choices[0].message.content