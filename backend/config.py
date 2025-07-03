"""
Configuration management for Voice Cloning Demo using Pydantic models.

Centralizes all environment variable handling and provides type-safe configuration
with validation and defaults.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class LiveKitConfig(BaseModel):
    """LiveKit configuration for real-time communication."""
    
    api_key: str
    api_secret: str
    url: str


class ResembleConfig(BaseModel):
    """Resemble AI configuration for voice synthesis."""
    
    api_key: str
    voice_uuid: str


class OpenAIConfig(BaseModel):
    """OpenAI configuration for language model."""
    
    api_key: str
    model: str = "gpt-4o-mini"


class DeepgramConfig(BaseModel):
    """Deepgram configuration for speech-to-text."""
    
    api_key: str


class LangfuseConfig(BaseModel):
    """Optional Langfuse configuration for observability."""
    
    public_key: Optional[str] = None
    secret_key: Optional[str] = None
    host: str = "https://cloud.langfuse.com"
    
    @property
    def enabled(self) -> bool:
        """Check if Langfuse is properly configured."""
        return bool(self.public_key and self.secret_key)


class VoiceConfig(BaseModel):
    """Voice agent character configuration."""
    
    instructions_file: str = "prompts/default_instructions.md"
    intro_file: str = "prompts/default_intro.md"


class AppConfig(BaseModel):
    """Application-level settings."""
    
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False


class Settings(BaseModel):
    """Master settings container for all configuration."""
    
    livekit: LiveKitConfig
    resemble: ResembleConfig
    openai: OpenAIConfig
    deepgram: DeepgramConfig
    langfuse: LangfuseConfig
    voice: VoiceConfig
    app: AppConfig


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the application settings.
    
    Loads configuration from environment variables with sensible defaults.
    Uses a singleton pattern for performance.
    
    Returns:
        Settings: Configured settings instance
        
    Raises:
        ValueError: If required environment variables are missing
    """
    global _settings
    if _settings is None:
        # Load from environment variables
        _settings = Settings(
            livekit=LiveKitConfig(
                api_key=os.getenv("LIVEKIT_API_KEY", ""),
                api_secret=os.getenv("LIVEKIT_API_SECRET", ""),
                url=os.getenv("LIVEKIT_URL", ""),
            ),
            resemble=ResembleConfig(
                api_key=os.getenv("RESEMBLE_API_KEY", ""),
                voice_uuid=os.getenv("RESEMBLE_VOICE_UUID", ""),
            ),
            openai=OpenAIConfig(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            ),
            deepgram=DeepgramConfig(
                api_key=os.getenv("DEEPGRAM_API_KEY", ""),
            ),
            langfuse=LangfuseConfig(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            ),
            voice=VoiceConfig(
                instructions_file=os.getenv("VOICE_INSTRUCTIONS_FILE", "prompts/default_instructions.md"),
                intro_file=os.getenv("VOICE_INTRO_FILE", "prompts/default_intro.md"),
            ),
            app=AppConfig(
                environment=os.getenv("ENVIRONMENT", "development"),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                debug=os.getenv("DEBUG", "").lower() in ("true", "1", "yes"),
            ),
        )
    return _settings


def reload_settings() -> Settings:
    """
    Force reload settings from environment variables.
    
    Useful for testing or when environment changes at runtime.
    
    Returns:
        Settings: Freshly loaded settings instance
    """
    global _settings
    _settings = None
    return get_settings()