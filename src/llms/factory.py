from src.llms.openai import OpenAIClient
# from src.llms.anthropic import AnthropicClient
import os

class LLMFactory:
   def create_client(self, provider: str = None):
       if not provider:
           provider = os.getenv("DEFAULT_LLM", "openai")
           
       if provider == "openai":
           return OpenAIClient()
       elif provider == "anthropic":
           raise ValueError("Anthropic is not yet implemented")
        #    return AnthropicClient()
       else:
           raise ValueError(f"Unknown LLM provider: {provider}")