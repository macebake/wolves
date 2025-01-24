import json
import os
from datetime import datetime

class GameLogger:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs/complete", exist_ok=True)
        
    def log(self, event: dict):
        event["timestamp"] = datetime.now().isoformat()
        with open(f"logs/complete/{self.timestamp}.jsonl", "a") as f:
            f.write(json.dumps(event) + "\n")