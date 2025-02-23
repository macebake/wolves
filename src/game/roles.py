from src.llms.base_client import BaseLLMClient
from src.game.conversation import GameMessage

from typing import List
import json


class BasePlayer:
    def __init__(self, llm_client: BaseLLMClient):
        self.name = None  # Will be set during introduction
        self.llm = llm_client
        self.is_alive = True
        self.role = None
        self.model = llm_client.model_alias

    def introduce(self, existing_names: list = None) -> str:
        print("\n=== Starting player introduction ===")
        print(f"LLM client type: {type(self.llm)}")
        print(f"LLM client: {self.llm}")
        
        if existing_names is None:
            existing_names = list()

        system = """You are a player in a game of Werewolves.
        Return ONLY a JSON object like this, no other text:
        {"name": "choose a name", "message": "brief introduction"}"""
        
        print("\nSending prompt to LLM...")
        response = self.llm.get_response(system)
        print(f"Raw LLM response: '{response}'")
        print(f"Response type: {type(response)}")
        print(f"Response length: {len(response) if response else 0}")
        
        if not response:
            print("Got empty response from LLM")
            default_name = f"Player_{id(self)}"
            self.name = default_name
            return f"Hello, I am {default_name}"
            
        try:
            print("Attempting to parse response as JSON...")
            serialised = json.loads(response.strip())
            print(f"Parsed JSON: {serialised}")
            
            if not isinstance(serialised, dict):
                print(f"Response not a dict: {type(serialised)}")
                raise ValueError("Invalid response format")
                
            if "name" not in serialised or "message" not in serialised:
                print(f"Missing required fields. Got: {list(serialised.keys())}")
                raise ValueError("Missing required fields")
                
            print("Successfully parsed response")
            self.name = serialised["name"]
            return serialised["message"]
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {str(e)}")
            print(f"Failed to parse: '{response}'")
            default_name = f"Player_{id(self)}"
            self.name = default_name
            return f"Hello, I am {default_name}"

    def get_message(self, history: List[GameMessage]) -> dict:
        print("Getting message")
        if not self.name:
            raise ValueError("Player name not set - introduction phase must be completed first")

        system = f"You are {self.name}, a {self.role}. Decide if you want to speak."
        messages = [{"role": "user", "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": system})
        response = self.llm.get_response(messages)
        return response


class Villager(BasePlayer):
    def __init__(self, llm_client: BaseLLMClient):
        print("Villager created")
        super().__init__(llm_client)
        self.role = "villager"


class Werewolf(BasePlayer):
    def __init__(self, llm_client: BaseLLMClient):
        super().__init__(llm_client)
        self.role = "werewolf"

    def get_message(self, history: List[GameMessage]) -> str:
        print("Getting message for werewolf")
        if history and history[-1].phase == "night":
            # During night phase, vote for who to kill
            system = f"""You are {self.name}, a werewolf. You are discussing with other werewolves who to kill.
            Be brief and direct - suggest one name only. Consider:
            1. Who seems most threatening to the werewolves
            2. Who the village might trust
            Return only the name of who you want to kill."""
        else:
            # During day phase, use regular discussion
            system = f"""You are {self.name}, a werewolf. You're trying to avoid suspicion.
            Keep responses conversational and brief. Don't be obviously evil."""
            
        messages = [{"role": "user", "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": system})
        return self.llm.get_response(messages)