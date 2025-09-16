# Werewolves
This is a game of werewolves designed to be played by various LLMs.

## Running the game

`main.py` contains all of the core game logic. This is where you can adjust core parameters of the game if needed.

Populate `.env`, and run the game with `python main.py`.

Game logs will be written to `game_logs` in jsonl format. All events will be logged here, whether or not the LLM players can "see" them (eg. voting events).

## LLM Providers
As-is, this game supports:

all OpenAI models from OpenAI directly
Sonnet through AWS Bedrock
Deepseek R1 + Llama-405b via Fireworks
You may want to adjust or expand these.
