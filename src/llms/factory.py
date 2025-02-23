from src.llms.openai import OpenAIClient
from src.llms.fireworks import FireworksClient
from src.llms.bedrock import BedrockClient

import os
import random

MODELS = {
    "OpenAI": [('o1-2024-12-17', 'o1'), ('gpt-4o-2024-08-06', '4o-aug'), ('gpt-4o-2024-11-20', '4o-nov'), ('o3-mini-2025-01-31', 'o3')],
    "Bedrock": [('eu.anthropic.claude-3-5-sonnet-20240620-v1:0', 'sonnet')],
    # "Fireworks": [('accounts/fireworks/models/llama-v3p1-405b-instruct', 'llama'), ('accounts/fireworks/models/deepseek-r1', 'r1')],
}

def choose_random_model():
    flattened = [i for s in list(MODELS.values()) for i in s]
    return random.choice(flattened)

class LLMFactory:
    def __init__(self):
        self.model_tuple = choose_random_model()
        self.model_snapshot = self.model_tuple[0]
        self.model_alias = self.model_tuple[1]

    def create_client(self):
        for provider, models in MODELS.items():
            model_snapshots = [m[0] for m in models]
            if self.model_snapshot in model_snapshots:
                if provider == "OpenAI":
                    return OpenAIClient(self.model_alias, self.model_snapshot)
                elif provider == "Fireworks":
                    return FireworksClient(self.model_alias, self.model_snapshot)
                elif provider == "Bedrock":
                    return BedrockClient(self.model_alias, self.model_snapshot)
                else:
                    raise ValueError(f"Unknown LLM provider: {provider}")