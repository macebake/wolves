from datetime import datetime
import json
import os

class GameLogger:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("game_logs", exist_ok=True)
        
    def log(self, event: dict):
        event["timestamp"] = datetime.now().isoformat()
        with open(f"game_logs/{self.timestamp}.jsonl", "a") as f:
            f.write(json.dumps(event) + "\n")