import logging
import json
import os
import asyncio
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    function_tool,
    RunContext
)
from livekit.plugins import murf, deepgram, google, silero

load_dotenv(".env.local")
logger = logging.getLogger("voice-game-master")

# -------------------------------
# GAME STATE ENGINE
# -------------------------------

GAME_STATE = {
    "player_name": None,
    "health": 100,
    "inventory": ["Old Map"],
    "location": "Ancient Forest Entrance",
    "chapter": 1,
    "game_active": False
}

# -------------------------------
# GAME TOOLS
# -------------------------------

@function_tool
async def start_game(
    ctx: RunContext,
    player_name: Annotated[str, "Your name for the adventure"],
):
    """Start the adventure."""
    GAME_STATE["player_name"] = player_name
    GAME_STATE["health"] = 100
    GAME_STATE["inventory"] = ["Old Map"]
    GAME_STATE["location"] = "Ancient Forest Entrance"
    GAME_STATE["chapter"] = 1
    GAME_STATE["game_active"] = True

    return (
        f"Welcome, {player_name}. Your journey begins at the Ancient Forest Entrance. "
        "Mist swirls around you… and something is watching."
    )


@function_tool
async def game_action(
    ctx: RunContext,
    action: Annotated[str, "The action the player performs"],
):
    """Perform an action in the game."""

    if not GAME_STATE["game_active"]:
        return "Your story hasn't started yet. Tell me your name to begin."

    action = action.lower()

    # MOVEMENT
    if "move" in action or "walk" in action or "forward" in action:
        GAME_STATE["location"] = "Deep Forest Path"
        return "You step deeper into the dark woods. The trees whisper… something follows you."

    # ATTACK
    if "attack" in action or "fight" in action:
        GAME_STATE["health"] -= 15
        return (
            "You swing your weapon! The shadow screeches and retreats. "
            "But you are scratched. Health -15."
        )

    # CHECK STATUS
    if "status" in action or "health" in action:
        return (
            f"Health: {GAME_STATE['health']}. "
            f"Location: {GAME_STATE['location']}. "
            f"Chapter: {GAME_STATE['chapter']}."
        )

    # INVENTORY
    if "inventory" in action or "bag" in action:
        items = ", ".join(GAME_STATE["inventory"])
        return f"You check your bag: {items}"

    return "Your action echoes in the darkness, but nothing responds…"


@function_tool
async def end_game(
    ctx: RunContext
):
    """End the current adventure."""
    GAME_STATE["game_active"] = False
    return "Your adventure fades into darkness. Until we meet again…"


# -------------------------------
# GAME MASTER AGENT
# -------------------------------

class GameMasterAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a cinematic Voice Game Master.
            - Create immersive narration.
            - Continue the story.
            - When players give actions, call `game_action`.
            - When players introduce their name, call `start_game`.
            - If the user says stop or exit, call `end_game`.

            STYLE:
            - Dark fantasy
            - Cinematic storytelling
            - Sounding like a narrator
            """
        )

    async def on_start(self, session: AgentSession):
        await session.say(
            "Welcome, traveler. Tell me your name to begin your adventure.",
            allow_interruptions=True
        )

    async def on_message(self, session: AgentSession, message: str):
        msg = message.lower()

        # Detect name
        if "my name is" in msg:
            name = message.split("is")[-1].strip()
            await session.invoke_tool(start_game, {"player_name": name})
            return
        
        # Start game
        if "start game" in msg:
            await session.invoke_tool(start_game, {"player_name": "Player"})
            return

        # End game
        if "end game" in msg or "stop" in msg or "exit" in msg:
            await session.invoke_tool(end_game, {})
            return

        # Active gameplay
        if GAME_STATE["game_active"]:
            await session.invoke_tool(game_action, {"action": message})
            return

        await session.say("Tell me your name to begin the story.")


# -------------------------------
# ENTRYPOINT + PREWARM
# -------------------------------

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    try:
        await ctx.connect()

        session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=google.LLM(model="gemini-2.5-flash"),
            tts=murf.TTS(
                voice="en-US-alicia",
                style="Narration",
                text_pacing=True
            ),
            vad=ctx.proc.userdata["vad"]
        )

        agent = GameMasterAgent()
        await session.start(agent=agent, room=ctx.room)

        # INTRO VOICE
        await session.say(
            "The forest stirs… and your adventure awaits. What is your name, traveler?",
            allow_interruptions=True
        )

    except Exception as e:
        logger.error(f"CRITICAL GAME ERROR: {e}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
