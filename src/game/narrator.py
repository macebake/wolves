from src.llms.base_client import BaseLLMClient
from src.game.conversation import GameMessage
from typing import List

class Narrator:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm = llm_client
        
    def announce_deaths(self, deaths: set) -> str:
        system = f"""
        You are the narrator in a game of Werewolves. Announce the deaths concisely, with slight dramatic flair. Make sure to call for the players to deliberate about who they think is responsible, and should be exiled. That is their task!

        Tonight's victim(s): {deaths}
        """
        messages= [{"role": "user", "content": system}]
        return self.llm.get_response(messages)

    def should_start_vote(self, conversation_history: List[GameMessage]) -> bool:        
        # Add safety check - max 3 rounds of discussion
        discussion_rounds = sum(1 for msg in conversation_history if msg.phase == "discussion")
        if discussion_rounds >= 5:
            print("Max discussion rounds reached, forcing vote")
            return True
            
        system = """You are the narrator in a game of Werewolves. Analyze the recent discussion to decide if it's time to call for a vote.
        Return EXACTLY one of these two responses:
        - "TRUE" if discussion seems complete (repeating/circular, no new info, clear consensus, or many turns)
        - "FALSE" if more discussion would be valuable"""
        
        # Only look at discussion messages from the last round
        discussion_messages = [
            msg for msg in conversation_history[-10:]
            if msg.phase == "discussion"
        ]
        
        if not discussion_messages:
            return False
            
        discussion = "\n".join([f"{msg.player}: {msg.content}" for msg in discussion_messages])
        messages = [
            {"role": "user", "content": discussion},
            {"role": "user", "content": system}
        ]
        
        response = self.llm.get_response(messages)
        response = response.strip().upper()
        
        # Force a decision
        if response not in ["TRUE", "FALSE"]:
            print(f"Invalid narrator response: {response}, defaulting to continue discussion")
            return False
            
        return response == "TRUE"
    
    def announce_vote(self) -> str:
        system = "You are the narrator. Call for a vote dramatically but briefly."
        return self.llm.get_response(system)

    def announce_night(self) -> str:
        system = "You are the narrator. Announce that night has fallen, dramatically but briefly."
        return self.llm.get_response(system)

    def announce_dawn(self) -> str:
        system = "You are the narrator. Announce that dawn has arrived, dramatically but briefly."
        return self.llm.get_response(system)