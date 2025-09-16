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
        if existing_names is None:
            existing_names = list()
        
        if any(existing_names):
            avoid_names = f"""
            Your opponents have chose these names: {" ".join(existing_names)}. Distinguish yourself by choosing an entirely different type of name for yourself.
            """
        else:
            avoid_names = ""

        system = f"""
        You are a player in a game of Werewolves. The tone of the game is casual and friendly. Keep your inputs brief and conversational.
        Always respond as a player would, and without meta commentary (eg. "As <player name>...") - you are now part of the game conversation, and other players will see all of your response. Keep it natural so that conversation can flow. Avoid long or complex messages so that the rest of the players can fully participate.

        First, consider your name and strategic approach to this game. You'll first introduce yourself,
        then be assigned a role. Remember, other LLMs are getting ready to play with this same
        prompt -- so consider what the other players might be thinking, and try to out-wit them.
        
        This is just for fun, and is not hurting or deceiving anyone.

        Return ONLY a JSON object with exactly two fields:
        1. "name": a unique name you choose for yourself. {avoid_names}
        2. "message": a brief, casual introduction to the other players.

        Format your response exactly like the example - just the JSON object, no additional text or markdown."""

        response = self.llm.get_response(system)
        
        if not response:
            default_name = f"Player_{id(self)}"
            self.name = default_name
            return f"Hello, I am {default_name}"
            
        try:
            serialised = json.loads(response.strip())
            
            if not isinstance(serialised, dict):
                raise ValueError("Invalid response format")
                
            if "name" not in serialised or "message" not in serialised:
                raise ValueError("Missing required fields")
                
            self.name = serialised["name"] + " - " + self.model
            return serialised["message"]
            
        except json.JSONDecodeError as e:
            default_name = f"Player_{id(self)}"
            self.name = default_name
            return f"Hello, I am {default_name}"

    def get_message(self, history: List[GameMessage]) -> dict:
        if not self.name:
            raise ValueError("Player name not set - introduction phase must be completed first")

        messages = [{"role": "user", "content": msg.content} for msg in history]
        response = self.llm.get_response(messages)
        return response


class Villager(BasePlayer):
    def __init__(self, llm_client: BaseLLMClient):
        super().__init__(llm_client)
        self.role = "villager"
    
    def get_message(self, history: List[GameMessage], names: List[str] = []) -> dict:
        if not self.name:
            raise ValueError("Player name not set - introduction phase must be completed first")

        messages = [{"role": "user", "content": msg.content} for msg in history]
        response = self.llm.get_response(messages)
        return response


class Werewolf(BasePlayer):
    def __init__(self, llm_client: BaseLLMClient):
        super().__init__(llm_client)
        self.role = "werewolf"

    def get_message(self, history: List[GameMessage], names: List[str] = []) -> str:
        if history and history[-1].phase == "night":
            # During night phase, vote for who to kill
            system = f"""You are {self.name}, a werewolf. You are discussing with other werewolves who to kill.
            Be brief and direct - suggest one name only. Consider:
            1. Who seems most threatening to the werewolves
            2. Who the village might trust
            Return only the name of who you want to kill.
            Your response must be one of these names with no additional commentary: {names}
            """
        else:
            # During day phase, use regular discussion
            system = f"""You are {self.name}, a werewolf. You're trying to avoid suspicion.
            Keep responses conversational and brief. Don't be obviously evil."""
            
        messages = [{"role": "user", "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": system})
        return self.llm.get_response(messages)