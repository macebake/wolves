from src.game.game_state import GameState
from src.game.narrator import Narrator
from src.utils.logger import GameLogger
from typing import List
from src.players.base_player import BasePlayer
import asyncio
import json

class GameOrchestrator:
   def __init__(self, game_state: GameState, players: List[BasePlayer], 
                narrator: Narrator, logger: GameLogger):
       self.game_state = game_state
       self.players = players
       self.narrator = narrator
       self.logger = logger
       self.conversation_history = []
       
   async def run(self):
       await self.introduction_phase()
       while not self.game_state.is_game_over():
           await self.night_phase()
           if self.game_state.is_game_over():
               break
           await self.day_phase()
           
       await self.end_game()
           
   async def introduction_phase(self):
       # Have each player introduce themselves
       for player in self.players:
           intro = await player.introduce()
           self.conversation_history.append({
               "phase": "intro",
               "player": player.name,
               "content": intro
           })
           
   async def night_phase(self):
       # Werewolves choose victim
       werewolves = [p for p in self.players if p.role == "werewolf" and p.is_alive]
       if werewolves:
           victim = await self._conduct_werewolf_vote(werewolves)
           self.game_state.kill_player(victim)
           
   async def day_phase(self):
       # Announce deaths
       deaths = await self.narrator.announce_deaths(self.game_state.last_deaths)
       self.conversation_history.append({
           "phase": "day",
           "player": "narrator",
           "content": deaths
       })
       
       # Discussion
       await self._conduct_discussion()
       
       # Voting
       if self.game_state.living_players():
           exile = await self._conduct_vote()
           self.game_state.exile_player(exile)
           
   async def _conduct_discussion(self):
       alive_players = [p for p in self.players if p.is_alive]
       for player in alive_players:
           response = await player.get_message(self.conversation_history)
           if response["wants_to_speak"]:
               self.conversation_history.append({
                   "phase": "discussion",
                   "player": player.name,
                   "content": response["message"],
                   "action": response["action"]
               })