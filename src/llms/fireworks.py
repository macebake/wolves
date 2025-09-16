import requests
import os
import json
from dotenv import load_dotenv
from src.llms.base_client import BaseLLMClient

load_dotenv()


class FireworksClient(BaseLLMClient):
    def __init__(self, model_alias, model_snapshot):
        super().__init__()
        self.model = model_snapshot
        self.model_alias = model_alias

    def get_response(self, messages, temperature=0.7):
        url = "https://api.fireworks.ai/inference/v1/chat/completions"
        messages = [{"role": "user", "content": message} for message in messages]
        payload = {
            "model": self.model,
            "top_p": 1,
            "top_k": 40,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "temperature": temperature,
            "messages": messages,
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('FIREWORKS_API_KEY')}"
        }
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        text = json.loads(response.text)
        message = text['choices'][0]['message']['content']

        if "deepseek-r1" in self.model:
            return self.remove_thinking(message)
        else:
            return message

    def vote(self, messages):
        return self.get_response(messages)

    def remove_thinking(self, message):
        split_thinking = message.split("</think>")[1]
        stripped_newlines = split_thinking.replace("\n", "")
        return stripped_newlines
