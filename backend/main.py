#!/usr/bin/env python3
"""
Voice Cloning Demo - Main Entry Point

This module provides entry points for running the voice cloning demo:
- Run the LiveKit agent worker for voice conversations
- Run the FastAPI server for token generation
"""

import asyncio
import sys
from typing import Optional

def main():
    """Main entry point with command selection"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    if command == "agent":
        run_agent()
    elif command == "api":
        run_api()
    elif command == "help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()

def print_usage():
    """Print usage information"""
    print("""
Voice Cloning Demo - LiveKit Voice AI

Usage:
    python main.py <command>

Commands:
    agent    Start the LiveKit agent worker (for voice conversations)
    api      Start the FastAPI server (for token generation)
    help     Show this help message

Examples:
    python main.py agent    # Start voice cloning agent worker
    python main.py api      # Start API server on port 8000

Environment Setup:
    Copy .env.example to .env and configure your API keys:
    - LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL
    - RESEMBLE_API_KEY, RESEMBLE_PROJECT_UUID
    - OPENAI_API_KEY, DEEPGRAM_API_KEY
    - LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY (optional)

For more information, see the README.md file.
""")

def run_agent():
    """Run the voice cloning LiveKit agent worker"""
    try:
        from voice_agent import cli, WorkerOptions, entrypoint
        print("🎤 Starting Voice Cloning Agent Worker...")
        print("Ready to demonstrate voice cloning...")
        # Pass remaining args to the LiveKit CLI (e.g., 'dev', 'download-files')
        agent_args = sys.argv[2:] if len(sys.argv) > 2 else ['dev']
        sys.argv = ['voice_agent'] + agent_args
        cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    except ImportError as e:
        print(f"Error importing agent modules: {e}")
        print("Make sure all dependencies are installed: uv sync")
    except Exception as e:
        print(f"Error starting agent: {e}")

def run_api():
    """Run the FastAPI server for token generation"""
    try:
        import uvicorn
        from api import app
        print("🚀 Starting Voice Cloning Demo API Server...")
        print("Ready to generate tokens for voice cloning demos...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except ImportError as e:
        print(f"Error importing API modules: {e}")
        print("Make sure all dependencies are installed: uv sync")
    except Exception as e:
        print(f"Error starting API server: {e}")

if __name__ == "__main__":
    main()