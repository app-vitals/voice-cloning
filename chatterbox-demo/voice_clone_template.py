#!/usr/bin/env python3
"""
Generic voice cloning script using ChatterboxTTS.

This template demonstrates how to:
1. Load a ChatterboxTTS model
2. Use your own audio file for voice cloning
3. Generate speech with the cloned voice
4. Save the output

Usage:
    python voice_clone_template.py --audio path/to/your_voice.wav --text "Text to synthesize" --output output.wav

Requirements:
    - ChatterboxTTS installed
    - Audio file with clear speech (2+ minutes recommended)
    - Text to synthesize
"""

import argparse
import os
import sys
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS


def load_model(device="cpu"):
    """Load the ChatterboxTTS model."""
    print("Loading ChatterboxTTS model...")
    try:
        model = ChatterboxTTS.from_pretrained(device=device)
        print(f"Model loaded successfully on {device}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)


def validate_audio_file(audio_path):
    """Validate that the audio file exists and is accessible."""
    if not os.path.exists(audio_path):
        print(f"Error: Audio file {audio_path} not found!")
        sys.exit(1)
    
    try:
        # Try to load the audio file to verify it's valid
        ta.load(audio_path)
        print(f"Audio file validated: {audio_path}")
    except Exception as e:
        print(f"Error: Invalid audio file {audio_path}: {e}")
        sys.exit(1)


def generate_voice_clone(model, text, audio_prompt_path, exaggeration=0.5):
    """Generate cloned voice audio."""
    print("Generating cloned voice audio...")
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    
    try:
        wav = model.generate(
            text, 
            audio_prompt_path=audio_prompt_path, 
            exaggeration=exaggeration
        )
        return wav
    except Exception as e:
        print(f"Error generating audio: {e}")
        sys.exit(1)


def save_audio(wav, output_path, sample_rate):
    """Save the generated audio to file."""
    try:
        ta.save(output_path, wav, sample_rate)
        print(f"Cloned voice saved to: {output_path}")
    except Exception as e:
        print(f"Error saving audio: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate voice clones using ChatterboxTTS")
    parser.add_argument("--audio", "-a", required=True, 
                       help="Path to audio file for voice cloning (WAV format recommended)")
    parser.add_argument("--text", "-t", required=True,
                       help="Text to synthesize with the cloned voice")
    parser.add_argument("--output", "-o", default="cloned_voice.wav",
                       help="Output file path (default: cloned_voice.wav)")
    parser.add_argument("--exaggeration", "-e", type=float, default=0.5,
                       help="Exaggeration factor (0.0-1.0, default: 0.5)")
    parser.add_argument("--device", "-d", default="cpu", choices=["cpu", "cuda"],
                       help="Device to use for inference (default: cpu)")
    
    args = parser.parse_args()
    
    # Validate inputs
    validate_audio_file(args.audio)
    
    if not args.text.strip():
        print("Error: Text cannot be empty!")
        sys.exit(1)
    
    # Load model and generate
    model = load_model(args.device)
    wav = generate_voice_clone(model, args.text, args.audio, args.exaggeration)
    save_audio(wav, args.output, model.sr)
    
    print("Voice cloning completed successfully!")


if __name__ == "__main__":
    main()