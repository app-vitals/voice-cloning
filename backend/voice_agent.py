import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Union, AsyncIterable, Optional, List
from uuid import uuid4
from pathlib import Path
import os

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    ChatContext,
    ChatMessage,
    JobContext,
    FunctionTool,
    ModelSettings,
    RoomInputOptions,
    RoomOutputOptions,
    WorkerOptions,
    UserStateChangedEvent,
    cli,
    stt,
    llm,
)
from livekit.agents.llm import ImageContent, AudioContent
from livekit.plugins import resemble, deepgram, openai, silero
from livekit.plugins.turn_detector.english import EnglishModel

from config import get_settings
from langfuse import Langfuse
from langfuse.client import StatefulClient

logger = logging.getLogger("voice-cloning-agent")
logger.setLevel(logging.INFO)

_langfuse = Langfuse()

def load_instructions_from_env() -> str:
    """Load agent instructions from configuration."""
    settings = get_settings()
    instructions_file = settings.voice.instructions_file
    instructions_path = Path(instructions_file)
    
    if not instructions_path.exists():
        raise FileNotFoundError(f"Instructions file not found: {instructions_file}")
    
    with open(instructions_path, 'r', encoding='utf-8') as f:
        instructions = f.read().strip()
    
    logger.info(f"Loaded instructions from: {instructions_file}")
    return instructions

def load_intro_template_from_env() -> str:
    """Load intro prompt template from configuration."""
    settings = get_settings()
    intro_file = settings.voice.intro_file
    intro_path = Path(intro_file)
    
    if not intro_path.exists():
        raise FileNotFoundError(f"Intro template file not found: {intro_file}")
    
    with open(intro_path, 'r', encoding='utf-8') as f:
        intro_template = f.read().strip()
    
    logger.info(f"Loaded intro template from: {intro_file}")
    return intro_template

def intro_prompt(name: str, intro_template: str) -> str:
    """Generate intro prompt using template with user name substitution."""
    return intro_template.format(name=name)

class VoiceCloningAgent(Agent):
    def __init__(self, instructions: str, intro_template: str, user_name: str) -> None:
        settings = get_settings()
        
        super().__init__(
            instructions=instructions,
            llm=openai.LLM(model=settings.openai.model),
            stt=deepgram.STT(),
            tts=resemble.TTS(
                voice_uuid=settings.resemble.voice_uuid,
            ),
            vad=silero.VAD.load(),
            turn_detection=EnglishModel(),
        )
        self.user_name = user_name
        self.intro_template = intro_template
        self.session_id = str(uuid4())
        self.current_trace = None

    def close(self) -> None:
        if self.current_trace:
            self.current_trace = None
        _langfuse.flush()

    async def on_enter(self) -> None:
        # Start with a natural greeting using the loaded template
        await self.session.generate_reply(
            instructions=intro_prompt(self.user_name, self.intro_template),
        )

    async def on_exit(self) -> None:
        self.close()

    def get_current_trace(self) -> StatefulClient:
        if self.current_trace:
            return self.current_trace
        self.current_trace = _langfuse.trace(name="voice_cloning_agent", session_id=self.session_id)
        return self.current_trace

    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage,
    ) -> None:
        # Reset the span when a new user turn is completed
        if self.current_trace:
            self.current_trace = None
        self.current_trace = _langfuse.trace(name="voice_cloning_agent", session_id=self.session_id)
        trace = self.get_current_trace()
        logger.info(f"User turn completed {trace.trace_id}")

    async def stt_node(
        self, audio: AsyncIterable[rtc.AudioFrame], model_settings: ModelSettings
    ) -> Optional[AsyncIterable[stt.SpeechEvent]]:
        trace = self.get_current_trace()
        logger.info(f"STT node called {trace.trace_id}")
        async for event in Agent.default.stt_node(self, audio, model_settings):
            logger.info(f"STT event: {event.type} {event.request_id}")
            yield event

    async def llm_node(
        self,
        chat_ctx: llm.ChatContext,
        tools: List[FunctionTool],
        model_settings: ModelSettings
    ) -> AsyncIterable[llm.ChatChunk]:
        trace = self.get_current_trace()
        logger.info(f"LLM node called {trace.trace_id}")

        settings = get_settings()
        generation = trace.generation(
            name="voice_clone_llm_generation",
            model=settings.openai.model,
            input=chat_ctx.to_provider_format("openai"),
        )
        output = ""
        set_completion_start_time = False
        try:
            async for chunk in Agent.default.llm_node(self, chat_ctx, tools, model_settings):
                if not set_completion_start_time:
                    generation.update(
                        completion_start_time=datetime.now(UTC),
                    )
                    set_completion_start_time = True
                if chunk.delta and chunk.delta.content:
                    output += chunk.delta.content
                yield chunk
        except Exception as e:
            generation.update(level="ERROR")
            logger.error(f"LLM error: {e}")
            raise
        finally:
            generation.end(output=output)

    async def tts_node(
        self, text: AsyncIterable[str], model_settings: ModelSettings
    ) -> AsyncIterable[rtc.AudioFrame]:
        trace = self.get_current_trace()
        logger.info(f"TTS node called {trace.trace_id}")
        span = trace.span(name="voice_clone_tts_node", metadata={"model": "resemble"})
        try:
            async for event in Agent.default.tts_node(self, text, model_settings):
                yield event
        except Exception as e:
            span.update(level="ERROR")
            logger.error(f"TTS error: {e}")
            raise
        finally:
            span.end()


async def entrypoint(ctx: JobContext) -> None:
    # Load instructions and intro template from environment variables
    try:
        instructions = load_instructions_from_env()
        intro_template = load_intro_template_from_env()
    except FileNotFoundError as e:
        logger.error(f"Failed to load files: {e}")
        print(f"Error: {e}")
        return

    # Connect to the room
    await ctx.connect()

    print(f"VOICE CLONING AGENT CONNECTED TO ROOM: {ctx.room.name}")
    print(f"LOCAL PARTICIPANT: {ctx.room.local_participant.identity}")

    if len(ctx.room.remote_participants) == 0:
        print("EXITING: No participants in the room for voice cloning demo")
        return

    print(f"REMOTE PARTICIPANTS: {len(ctx.room.remote_participants)}")
    
    # Create agent session
    session = AgentSession()

    # Configure voice cloning agent
    participant = list(ctx.room.remote_participants.values())[0]
    
    agent = VoiceCloningAgent(
        instructions=instructions,
        intro_template=intro_template,
        user_name=participant.name
    )
    
    # Set up room input/output - enable audio and transcripts
    room_input = RoomInputOptions(
        audio_enabled=True
    )
    
    room_output = RoomOutputOptions(
        audio_enabled=True,
        transcription_enabled=True
    )

    # Start voice cloning agent with all capabilities
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=room_input,
        room_output_options=room_output,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
