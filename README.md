# Voice Cloning Project

A template project for creating voice clones using ChatterboxTTS. Bring your own audio training data to create custom voice models.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create your voice clone:**
   ```bash
   python chatterbox-demo/voice_clone_template.py --audio your_training_audio.wav --text "Hello world"
   ```

## Creating Voice Clones

### Step 1: Prepare Training Audio

You need 2+ minutes of clean, varied speech from a single speaker. Here's how to get it:

#### 1a. Source Audio
```bash
# Download from YouTube with transcripts
yt-dlp -x --audio-format wav "{YOUR_YOUTUBE_URL}"
yt-dlp --write-auto-sub --sub-lang en --skip-download --output "%(title)s.%(ext)s" "{YOUR_YOUTUBE_URL}"

# Or convert existing audio files
ffmpeg -i input.m4a output.wav
```

#### 1b. Generate/Get Transcripts
```bash
# If you have YouTube transcripts, use those
# Or generate transcripts with Whisper (split long files first)
pip install openai-whisper

# For long files, split into chunks for Whisper
ffmpeg -i long_audio.wav -f segment -segment_time 600 -c copy chunk_%03d.wav

# Generate transcripts
whisper chunk_001.wav --model small --output_format vtt
whisper chunk_002.wav --model small --output_format vtt
```

#### 1c. Analyze Transcripts & Plan Segments
```bash
# Use an LLM to analyze transcripts and identify high-quality segments
# Look for: clear speech, emotional variety, minimal background noise, single speaker
# Get timestamp ranges for the best segments from your analysis
```

#### 1d. Extract Target Segments
```bash
# Extract specific segments based on transcript analysis
ffmpeg -i input.wav -ss 02:15 -t 00:45 segment1.wav
ffmpeg -i input.wav -ss 08:30 -t 01:20 segment2.wav
ffmpeg -i input.wav -ss 15:45 -t 00:55 segment3.wav
```

#### 1e. Review & Edit Segments
```bash
# Use Audacity to:
# - Remove background noise
# - Trim silence/filler words  
# - Normalize volume levels
# - Ensure clean speech only
```

#### 1f. Combine Best Segments
```bash
# Create file list of your cleaned segments
echo "file 'segment1_clean.wav'" > filelist.txt
echo "file 'segment2_clean.wav'" >> filelist.txt
echo "file 'segment3_clean.wav'" >> filelist.txt

# Combine into final training audio
ffmpeg -f concat -safe 0 -i filelist.txt -c copy training_audio.wav
```

### Step 2: Clone Voice
```bash
python chatterbox-demo/voice_clone_template.py \
  --audio training_audio.wav \
  --text "Your custom text here" \
  --output cloned_voice.wav
```

### Step 3: Create Custom Scripts
Copy and modify the template for your specific voice:
```bash
cp chatterbox-demo/voice_clone_template.py chatterbox-demo/voice_clone_your_name.py
# Edit to use your training audio file
```

## Alternative: Hosted Voice Cloning Services

You can also use your prepared training audio with hosted voice cloning services:

### ElevenLabs
1. Upload your `training_audio.wav` to [ElevenLabs Voice Lab](https://elevenlabs.io/voice-lab)
2. Create a custom voice using their web interface
3. Use their API or web interface to generate speech

### Resemble.AI
1. Upload your training audio to [Resemble.AI](https://www.resemble.ai/)
2. Train a custom voice model through their platform
3. Generate speech via their API or dashboard

### Benefits of Hosted Services
- No local setup required
- Professional-grade voice models
- API access for integration
- Often better quality than local models

### Benefits of Local ChatterboxTTS
- Complete privacy and control
- No usage limits or costs
- Works offline
- Customizable and open source

## Dependencies

### Core Requirements
- **chatterbox-tts** - Main TTS engine for voice cloning
- **torchaudio** - Audio file loading and saving

### Optional Tools
- **ffmpeg** - Audio format conversion and extraction
- **yt-dlp** - YouTube downloading
- **openai-whisper** - Audio transcription
- **Audacity** - Manual audio editing and cleaning

## Testing Your Setup

```bash
# Test core packages
python -c "import chatterbox.tts, torchaudio; print('✅ Core packages OK')"

# Test voice cloning template
python chatterbox-demo/voice_clone_template.py --help
```

## Project Structure

- `chatterbox-demo/` - Voice cloning scripts and template
- `training_data/` - Your processed training audio files (add your own)
- `processing_steps/` - Audio processing examples and workflows
- `raw_audio/` - Original source audio files (add your own)

## Tips for Best Results

- **Audio quality:** Use 2+ minutes of clean, varied speech
- **Single speaker:** Ensure training audio contains only the target voice
- **Voice variety:** Include different emotions and speaking styles in training data
- **File formats:** WAV format recommended for best quality

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'chatterbox'` | Activate virtual environment and reinstall requirements |
| `Error loading audio file` | Check file format and permissions |
| Poor voice quality | Use more/better training audio, ensure single speaker |
| Unsupported audio format | Install ffmpeg or convert to WAV/MP3 |

## LiveKit Voice Cloning Demo

This project also includes a real-time voice cloning demo using LiveKit and Resemble AI.

### Quick Start - LiveKit Demo

1. **Setup backend:**
   ```bash
   cd backend
   uv sync
   cp .env.example .env
   # Configure your API keys in .env
   ```

2. **Setup frontend:**
   ```bash
   cd frontend
   npm install
   ```

3. **Run the demo:**
   ```bash
   # Terminal 1 - Start API server
   cd backend && python main.py api

   # Terminal 2 - Start voice agent
   cd backend && python main.py agent dev

   # Terminal 3 - Start frontend
   cd frontend && npm run dev
   ```

4. **Try it:** Open http://localhost:5173 and have a voice conversation!

### Custom Characters

Create custom character files for different personalities:

1. **Create character files:**
   ```bash
   backend/prompts/your_character_instructions.md
   backend/prompts/your_character_intro.md
   ```

2. **Use them by setting environment variables:**
   ```bash
   # Option 1: Export environment variables
   export VOICE_INSTRUCTIONS_FILE=prompts/your_character_instructions.md
   export VOICE_INTRO_FILE=prompts/your_character_intro.md
   python main.py agent dev

   # Option 2: Add to your .env file
   echo "VOICE_INSTRUCTIONS_FILE=prompts/your_character_instructions.md" >> .env
   echo "VOICE_INTRO_FILE=prompts/your_character_intro.md" >> .env
   python main.py agent dev
   ```

### Required API Keys

Configure these in `backend/.env`:
- **LiveKit** - For real-time audio communication
- **Resemble AI** - For voice cloning (needs voice UUID)
- **OpenAI** - For AI conversation
- **Deepgram** - For speech-to-text
- **Langfuse** - For observability (optional)

## Contributing

This is a template project. Add your own:
- Training audio files to `raw_audio/`
- Processed training data to `training_data/`
- Custom voice clone scripts to `chatterbox-demo/`
- Custom character prompts to `backend/prompts/` (ignored by git)