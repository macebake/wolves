import boto3
import os
from dotenv import load_dotenv
from src.llms.base_client import BaseLLMClient


load_dotenv()

class BedrockClient(BaseLLMClient):
    def __init__(self, model_alias, model_snapshot):
        print("Initialising bedrock")
        super().__init__()
        self.client = self.instantiate_client()
        self.model = model_snapshot
        self.model_alias = model_alias

    def instantiate_client(self):
        print("Initialising bedrock client")
        session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"))
        return session.client(service_name="bedrock-runtime")

    def get_response(self, messages):
        print("bedrock get_Response")
        # Wrap string prompts into a list of message objects.
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        fixed_messages = self.fix_messages(messages)

        response = self.client.converse(
            modelId=self.model,
            messages=fixed_messages,
        )

        return response["output"]["message"]["content"][0]["text"]

    def vote(self, messages):
        return self.get_response(messages)
    
    def fix_messages(self, messages):
        if isinstance(messages, dict):
            messages = [messages]
        
        # This is horrific, but is easier to deal with here as Anthropic is the only standout
        for message in messages:
            if not isinstance(message["content"], list):
                message["content"] = [{"text": message["content"]}]
        
        return messages
