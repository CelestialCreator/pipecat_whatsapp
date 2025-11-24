#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#
import os

from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

from prompt import AGENT_INSTRUCTION, SESSION_INSTRUCTION

# Import MCP modules if available
try:
    from pipecat.services.mcp import MCPService
    from pipecat.services.mcp.http import MCPHttpTransport
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPHttpTransport = None

load_dotenv(override=True)

SYSTEM_INSTRUCTION = SESSION_INSTRUCTION


async def run_bot(webrtc_connection):
    pipecat_transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            audio_out_10ms_chunks=2,
        ),
    )

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="f8f5f1b2-f02d-4d8e-a40d-fd850a487b3d",  # British Reading Lady
    )

    # Check if MCP URL is provided in environment variables
    mcp_url = os.getenv("MCP_HTTP_URL")

    if mcp_url and MCP_AVAILABLE:
        # Use MCP service for LLM
        logger.info(f"Using MCP service at URL: {mcp_url}")
        mcp_http_transport = MCPHttpTransport(mcp_url)
        # MCP services handle their own system instructions based on tool definitions and configuration
        llm = MCPService(mcp_http_transport)
    else:
        # Use OpenAI service by default
        llm = OpenAILLMService(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            model="google/gemini-2.0-flash-lite-001",  # Using a free model from OpenRouter
            system_prompt=AGENT_INSTRUCTION,
        )

    # Create initial context with session instructions
    initial_messages = [
        {
            "role": "system",
            "content": SESSION_INSTRUCTION,
        }
    ]
    context = LLMContext(initial_messages)
    context_aggregator = LLMContextAggregatorPair(context)

    pipeline = Pipeline(
        [
            pipecat_transport.input(),
            stt,  # Speech-to-Text
            context_aggregator.user(),
            llm,  # LLM
            tts,  # Text-to-Speech
            pipecat_transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    @pipecat_transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Pipecat Client connected")
        # Add a greeting message to the context and kick off the conversation
        greeting_message = "Hi, this is Reva from Doolally Taproom, your WhatsApp assistant. Greet the user warmly, introduce yourself, and ask how you can help them today."
        context.add_message({"role": "user", "content": greeting_message})
        await task.queue_frames([LLMRunFrame()])

    @pipecat_transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Pipecat Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)
