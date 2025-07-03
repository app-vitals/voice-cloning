from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import LiveKitAPI, ListRoomsRequest, AccessToken, VideoGrants, CreateRoomRequest
from pydantic import BaseModel
import uvicorn

from config import get_settings

app = FastAPI(
    title="Voice Cloning Demo API",
    description="API for generating tokens and managing rooms for voice cloning demonstrations",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenResponse(BaseModel):
    token: str
    url: str
    room_name: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Voice Cloning Demo API - Ready to demonstrate voice cloning with LiveKit",
        "version": "0.1.0",
        "status": "ready"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Voice cloning demo is operational"}

@app.get("/api/get-token", response_model=TokenResponse)
async def get_token(participant: str = Query(..., description="Name of the participant")):
    """
    Generate a LiveKit token for a participant to join a voice cloning conversation.
    
    Args:
        participant: The name of the participant
        
    Returns:
        Token, URL, and room name for connecting to the conversation
    """
    settings = get_settings()
    
    if not settings.livekit.api_key or not settings.livekit.api_secret:
        raise HTTPException(
            status_code=500, 
            detail="LiveKit API credentials not configured"
        )

    if not settings.livekit.url:
        raise HTTPException(
            status_code=500,
            detail="LiveKit URL not configured"
        )

    # Create a unique room for this conversation
    room_name = f"voice-clone-demo-{uuid4().hex[:8]}"
    
    try:
        async with LiveKitAPI() as client:
            room = await client.room.create_room(
                CreateRoomRequest(
                    name=room_name,
                    departure_timeout=60,  # Room cleanup after participant leaves
                    max_participants=2,    # Participant and voice clone agent
                ),
            )
            room_name = room.name
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create room: {str(e)}"
        )
    
    # Generate access token
    try:
        token = AccessToken(settings.livekit.api_key, settings.livekit.api_secret) \
            .with_identity(participant) \
            .with_name(participant) \
            .with_grants(VideoGrants(
                room=room_name,
                room_join=True,
                can_subscribe=True,
                can_publish=True,
            ))
        
        return TokenResponse(
            token=token.to_jwt(),
            url=settings.livekit.url,
            room_name=room_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate token: {str(e)}"
        )

@app.get("/api/rooms")
async def list_rooms():
    """List active rooms (for debugging/monitoring)"""
    settings = get_settings()
    if not settings.livekit.api_key or not settings.livekit.api_secret:
        raise HTTPException(status_code=500, detail="LiveKit API credentials not configured")
    
    try:
        async with LiveKitAPI() as client:
            rooms = await client.room.list_rooms(ListRoomsRequest())
            return {
                "rooms": [
                    {
                        "name": room.name,
                        "participants": room.num_participants,
                        "created_at": room.creation_time
                    }
                    for room in rooms.rooms
                ],
                "total": len(rooms.rooms)
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list rooms: {str(e)}"
        )

if __name__ == "__main__":
    # For development
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )