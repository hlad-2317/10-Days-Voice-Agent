import logging
import json
import os
from typing import Dict, Any, Optional, List 

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

LEAD_FILE_PATH = "captured_lead_data.json"

# --------------------------
# SAVE CHAT FUNCTION
# --------------------------
def save_chat(role: str, message: str):
    file_path = LEAD_FILE_PATH

    # Ensure file exists and is valid JSON array
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)

    with open(file_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    data.append({"role": role, "message": message})

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
# --------------------------

load_dotenv(".env.local")

COMPANY_NAME = "Tata Neu"
FAQ_CONTENT = {
    "what_it_does": "Tata Neu is a super-app that brings together the Tata Group's brand ecosystem—including shopping (e.g., BigBasket, Croma), travel (e.g., Air India), financial services, and payments—into a single platform.",
    "target_audience": "Our platform is primarily for consumers in India who want a unified loyalty and shopping experience across various retail, travel, and financial services under the trusted Tata brand.",
    "pricing_basics": "The Tata Neu app itself is free to download and use. Its value comes from earning and spending 'NeuCoins,' which are rewarded on purchases across all partner brands. Financial products offered through the app, like loans or credit cards, have their own specific pricing and fees.",
    "key_benefits": "The main benefit is the unified loyalty program (NeuPass) and seamless integration across all Tata brands, offering better rewards and a smoother checkout experience for users.",
    "free_tier": "There is no separate 'tier' since the app is free. The value is derived from user activity and rewards. We do offer promotional benefits that are effectively free perks."
}

LEAD_FIELDS = ["Name", "Company", "Email", "Role", "Use case", "Team size", "Timeline"]

class SDRSessionState:
    def __init__(self):
        self.lead_data: Dict[str, Any] = {field: None for field in LEAD_FIELDS}
        self.current_question: Optional[str] = None
        self.conversation_transcript: List[str] = []
        self.faq_hits: List[str] = []

    def get_missing_lead_fields(self) -> List[str]:
        return [field for field, value in self.lead_data.items() if value is None]


class SDRScriptAgent(Agent):
    def __init__(self, userdata: SDRSessionState) -> None:
        self.state = userdata
        
        # Instructions modified to ensure agent always asks for lead fields
        instructions = f"""You are the Sales Development Representative (SDR) for {COMPANY_NAME}.
Your primary goal is to qualify the visitor, answer their questions based *ONLY* on the provided FAQ, and capture lead information.

**SDR Persona Rules:**
1. Greet the user warmly when the conversation starts.
2. Use FAQ: If the user asks a product, pricing, or company question, use the `answer_faq` tool. DO NOT invent details.
3. ALWAYS collect lead data: After greeting the user, immediately call the `capture_lead_data` tool to ask for the first missing field.
4. During every turn, after responding to the user, call `capture_lead_data` again until all lead fields are completed.
5. Once all LEAD_FIELDS are filled and the user says "that's all", "bye", "thanks", or similar, call the `end_call_summary` tool.

**Available FAQ Keys:** {', '.join(FAQ_CONTENT.keys())}
"""
        super().__init__(instructions=instructions)

    @function_tool
    async def answer_faq(self, context: RunContext, topic: str) -> str:
        topic = topic.lower().replace(' ', '_').replace('-', '_')
        
        for key, answer in FAQ_CONTENT.items():
            if topic in key or key in topic:
                context.userdata.faq_hits.append(key)
                return f"Regarding {COMPANY_NAME}, {answer}"

        return "I'm sorry, I don't have a pre-approved answer for that specific topic in my FAQ. Can I try to answer another question, or can I get your contact details?"

    @function_tool
    async def capture_lead_data(self, context: RunContext, field_name: Optional[str] = None, value: Optional[str] = None) -> str:
        """
        Use this tool to naturally ask for missing lead information or store a piece of information provided by the user.
        If called with a field_name and value, store it. Otherwise, ask for the next missing field.
        """
        # If the LLM provides a field and a value, store it
        if field_name and value:
            field_name = field_name.title()
            if field_name in LEAD_FIELDS:
                context.userdata.lead_data[field_name] = value
                logger.info(f"Captured lead data: {field_name}={value}")
                # Also save to transcript file as structured lead update
                save_chat("lead_update", f"{field_name}={value}")
        
        # Determine remaining fields
        missing = context.userdata.get_missing_lead_fields()
        
        if not missing:
            return "Thank you! I believe I have all the key information I need to pass along to my team. How else can I help you today?"

        next_field = missing[0]
        context.userdata.current_question = next_field

        prompts = {
            "Name": "That's helpful! Before we go further, can I just get your name?",
            "Email": "And what would be the best email address to send our summary and follow-up resources to?",
            "Company": "Great. What company are you currently with?",
            "Role": "And what is your role or title at the company?",
            "Use case": "What specific problem are you hoping to solve or what feature of Tata Neu interests you most?",
            "Team size": "Roughly how many people are on the team that would be using our solution?",
            "Timeline": "And finally, what's your timeline for implementing a new solution: immediately, within the next three months, or later this year?"
        }

        return prompts.get(next_field, "I've updated the lead data. What is your next question?")

    @function_tool
    async def end_call_summary(self, context: RunContext) -> str:
        """
        Use this tool when the user signals the end of the conversation.
        It summarizes the lead data and saves it to a JSON file.
        """
        lead_data = context.userdata.lead_data
        
        # Build a summary text for the user
        name = lead_data.get("Name", "the visitor")
        company = lead_data.get("Company", "an interested party")
        use_case = lead_data.get("Use case", "a potential integration")
        timeline = lead_data.get("Timeline", "an undefined timeline")

        summary_text = (
            f"Thank you, {name}, for your time today. To summarize: you are interested in {COMPANY_NAME} for {use_case}. "
            f"You are currently with {company}, and your timeline is {timeline}. I will ensure a specialist follows up with you shortly."
        )

        # Save lead data persistently
        try:
            if os.path.exists(LEAD_FILE_PATH):
                with open(LEAD_FILE_PATH, 'r') as f:
                    try:
                        leads = json.load(f)
                    except json.JSONDecodeError:
                        leads = []
            else:
                leads = []
            
            leads.append(lead_data)
            
            with open(LEAD_FILE_PATH, 'w') as f:
                json.dump(leads, f, indent=4)
            
            logger.info(f"Successfully saved lead data to {LEAD_FILE_PATH}")
        except Exception as e:
            logger.error(f"Failed to save lead data: {e}")
            summary_text += " (Note: There was an issue recording the data internally, but I have the information.)"

        # Also save summary to transcript file
        save_chat("agent_summary", summary_text)

        return f"{summary_text} Thank you again and have a productive day!"


def prewarm(proc: JobProcess):
    """Prewarm models."""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Set up session state
    session_state = SDRSessionState()
    
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline
    session = AgentSession(
        userdata=session_state,
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Save user speech lines as they come in
    @session.on("transcript")
    def on_user_transcript(ev):
        try:
            if getattr(ev, "user_speaking", False) and getattr(ev, "text", None):
                save_chat("user", ev.text)
                # Also append to session_state transcript for in-memory history
                session_state.conversation_transcript.append(f"user: {ev.text}")
        except Exception as e:
            logger.error(f"Error saving user transcript: {e}")

    # Save agent responses
    @session.on("agent_response")
    def on_agent_response(ev):
        try:
            if getattr(ev, "text", None):
                save_chat("agent", ev.text)
                session_state.conversation_transcript.append(f"agent: {ev.text}")
                # After agent responds, we expect the LLM to call capture_lead_data per instruction.
                # (The instruction ensures the LLM uses the capture_lead_data tool repeatedly until done.)
        except Exception as e:
            logger.error(f"Error saving agent response: {e}")

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=SDRScriptAgent(userdata=session_state),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Connect to the room (join)
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
