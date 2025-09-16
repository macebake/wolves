from src.game.game_state import GameState
from src.game.narrator import Narrator
from src.game.logger import GameLogger
from src.game.conversation import GameMessage
from src.game.conversation import ConversationManager
from src.game.role_manager import RoleManager
from typing import List
from src.game.roles import BasePlayer, Villager, Werewolf

import random


class GameOrchestrator:
    def __init__(self, players: List[BasePlayer], narrator: Narrator, logger: GameLogger):
        self.players = players
        self.narrator = narrator
        self.logger = logger
        self.conversation = ConversationManager()
        self.role_manager = None  # Will be initialized after introductions
        self.game_state = None

    def run(self):
        self.logger.log({"event": "game_start"})
        self.introduction_phase()
        self.role_assignment_phase()
        
        while not self.game_state.is_game_over():
            self.logger.log({"event": "night_phase_start"})
            self.night_phase()
            if self.game_state.is_game_over():
                break
            
            self.logger.log({"event": "day_phase_start"})
            self.day_phase()
            
        self.end_game()

    def introduction_phase(self):
        self.logger.log({"event": "introduction_phase_start"})
        for player in self.players:
            intro = player.introduce(existing_names=[p.name for p in self.players if p.name])
            message = {
                "phase": "intro",
                "player": player.name,
                "content": intro
            }
            self.conversation.add_message(GameMessage(**message))
            self.logger.log({
                "event": "player_introduction",
                "data": message
            })
        # Initialize role manager after all players have introduced themselves
        self.role_manager = RoleManager([p.name for p in self.players])
        self.logger.log({"event": "introduction_phase_end"})

    def role_assignment_phase(self):
        if not self.role_manager:
            raise ValueError("Role manager not initialized - introduction phase must be completed first")
            
        roles = self.role_manager.assign_roles()
        for player in self.players:
            role = roles[player.name]
            # Create new player instance of correct type
            if role == "werewolf":
                new_player = Werewolf(player.llm)
            else:
                new_player = Villager(player.llm)
            
            # Transfer existing player state
            new_player.name = player.name
            new_player.is_alive = player.is_alive
            
            # Replace player in list
            self.players[self.players.index(player)] = new_player
            
            # Assign role and log
            self.conversation.assign_role(player.name, role)
            self.logger.log({
                "event": "role_assigned",
                "data": {"player": player.name, "role": role}
            })
        
        self.game_state = GameState(roles)

    def get_message(self, history: List[GameMessage]) -> dict:
        system = f"You are {self.name}, a {self.role}. Given the game state, share your thoughts about who might be a werewolf and why."
        messages = [{"content": msg.content} for msg in history]
        messages.append({"content": system})
        response = self.llm.get_response(messages)
        return {"wants_to_speak": True, "message": response}

    def night_phase(self):
        # Announce night falling
        night_start = self.narrator.announce_night()
        self.conversation.add_message(GameMessage(
            phase="night",
            player="narrator",
            content=night_start,
            visibility="public"
        ))
        self.logger.log({
            "event": "night_start",
            "data": {"message": night_start}
        })

        # Werewolves choose victim
        werewolves = [p for p in self.players if p.role == "werewolf" and p.is_alive]
        if werewolves:
            # Let werewolves deliberate
            for wolf in werewolves:
                decision = wolf.get_message(self.conversation.get_player_history(wolf.name), [p.name for p in self.players if p.is_alive])
                self.conversation.add_message(GameMessage(
                    phase="night",
                    player=wolf.name,
                    content=decision,
                    visibility="private"  # Only other werewolves can see
                ))
                self.logger.log({
                    "event": "werewolf_deliberation",
                    "data": {
                        "player": wolf.name,
                        "message": decision
                    }
                })

            victim = self._conduct_werewolf_vote(werewolves)
            self.game_state.kill_player(victim)
            self.logger.log({
                "event": "werewolf_kill",
                "data": {"victim": victim.name}
            })

        # Announce night ending
        night_end = self.narrator.announce_dawn()
        self.conversation.add_message(GameMessage(
            phase="night",
            player="narrator",
            content=night_end,
            visibility="public"
        ))
    
    def _conduct_werewolf_vote(self, werewolves: List[BasePlayer]) -> BasePlayer:
        """Conducts vote among werewolves to choose victim"""
        if not werewolves:
            return None
            
        votes = {}
        # Each werewolf submits their vote
        for werewolf in werewolves:
            vote = werewolf.get_message(self.conversation.get_player_history(werewolf.name), [p.name for p in self.players if p.is_alive])
            # Remove any whitespace and standardize case
            vote = vote.strip().lower()
            votes[vote] = votes.get(vote, 0) + 1
            
            self.logger.log({
                "event": "werewolf_vote",
                "data": {"voter": werewolf.name, "vote": vote}
            })
        
        # Find the candidate with most votes
        if not votes:
            return None
            
        max_votes = max(votes.values())
        candidates = [name for name, count in votes.items() if count == max_votes]
        
        # Break ties randomly
        chosen_name = random.choice(candidates)

        # Find closest matching player name
        for player in self.players:
            if chosen_name in player.name.lower():
                return player

        # Fallback to random living non-werewolf if no match
        return random.choice([p for p in self.players if p.is_alive and p.role != "werewolf"])

    def _conduct_vote(self) -> BasePlayer:
        """Conducts village vote to exile a player"""
        votes = {}
        living_players = [p for p in self.players if p.is_alive]
        
        # Each living player submits their vote
        for player in living_players:
            # Add special voting prompt to history
            vote_prompt = GameMessage(
                phase="voting",
                player="narrator",
                content=f"""
                    Cast your vote for who to exile. Your only options are {", ".join([p.name for p in living_players])}.
                    You must respond only with their name, and no additional commentary whatsoever.
                """,
                visibility="public"
            )
            history = self.conversation.get_player_history(player.name)
            history.append(vote_prompt)
            vote = player.get_message(history, names=[p.name for p in self.players if p.is_alive])
            # Remove any whitespace and standardize case
            vote = vote.strip().lower()
            votes[vote] = votes.get(vote, 0) + 1
            
            self.logger.log({
                "event": "village_vote",
                "data": {"voter": player.name, "vote": vote}
            })
        
        # Find candidate with most votes
        if not votes:
            return None
        
        print("votes:", votes)

        max_votes = max(votes.values())
        candidates = [name for name, count in votes.items() if count == max_votes]

         # Break ties randomly
        chosen_name = random.choice(candidates)

        # Find closest matching player name
        for player in self.players:
            if chosen_name in player.name.lower():
                return player

        # Fallback to random living non-werewolf if no match
        return random.choice([p for p in self.players if p.is_alive and p.role != "werewolf"])

    def day_phase(self):
        # Announce deaths
        deaths = self.narrator.announce_deaths(self.game_state.last_deaths)
        message = GameMessage(phase="day", player="narrator", content=deaths)
        self.conversation.add_message(message)
        self.logger.log({
            "event": "day_start",
            "data": {"deaths": list(self.game_state.last_deaths), "message": deaths}
        })

        discussion_ended = False
        while not discussion_ended:
            alive_players = [p for p in self.players if p.is_alive]
            for player in alive_players:
                response = player.get_message(self.conversation.get_player_history(player.name))
                message = GameMessage(
                    phase="discussion",
                    player=player.name,
                    content=response,
                    visibility="public"
                )
                self.conversation.add_message(message)
                self.logger.log({
                    "event": "player_discussion",
                    "data": {"player": player.name, "message": response}
                })
            
            discussion_ended = self.narrator.should_start_vote(
                self.conversation.get_player_history("narrator")
            )
        
        vote_announcement = self.narrator.announce_vote()
        self.conversation.add_message(GameMessage(
            phase="voting",
            player="narrator",
            content=vote_announcement
        ))

        self.logger.log({
            "event": "voting_start",
            "data": {"message": vote_announcement}
        })

        exile = self._conduct_vote()
        self.game_state.kill_player(exile)
        self.logger.log({
            "event": "player_exiled",
            "data": {"player": exile.name}
        })

    def _conduct_discussion(self):
        alive_players = [p for p in self.game_state.living_players]
        for player in alive_players:
            response = player.get_message(self.conversation.get_player_history(player.name))
            message = GameMessage(
                phase="discussion",
                player=player.name,
                content=response,
                visibility="public"
            )
            self.conversation.add_message(message)
            self.logger.log({
                "event": "player_discussion",
                "data": {"player": player.name, "message": response}
            })

    def end_game(self):
        """End the game and log final state."""
        
        # Count surviving werewolves
        werewolves = sum(1 for p in self.game_state.living_players 
                        if self.game_state.players[p] == "werewolf")
        villagers = len(self.game_state.living_players) - werewolves
        
        # Determine winner
        winner = "Villagers" if werewolves == 0 else "Werewolves"
        
        # Group players by role with status indicators
        player_roles = {
            "Werewolves": [p for p, r in self.game_state.players.items() if r == "werewolf"],
            "Villagers": [p for p, r in self.game_state.players.items() if r == "villager"]
        }
        
        player_statuses = {
            player: "🪦" if player in self.game_state.dead_players else "✨"
            for player in self.game_state.players
        }
        
        final_state = {
            role: [f"{player} {player_statuses[player]}" for player in players]
            for role, players in player_roles.items()
        }
        
        # Create detailed game over message
        game_over_msg = f"Game Over! The {winner} have won!"
        
        final_message = GameMessage(
            phase="end",
            player="narrator",
            content=game_over_msg,
            visibility="public"
        )

        self.conversation.add_message(final_message)
        self.logger.log({
            "event": "game_end",
            "data": {
                "winner": winner,
                "message": game_over_msg,
                "werewolves": final_state['Werewolves'],
                "villagers": final_state['Villagers'],
            }
        })
