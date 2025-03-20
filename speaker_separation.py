from pyannote.audio import Pipeline
import torch
import os
from pydub import AudioSegment
import numpy as np
from dotenv import load_dotenv
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def validate_token(token):
    """Validate the HuggingFace token format."""
    if not token or len(token) < 10:
        return False
    return True

def separate_speakers(audio_path, output_dir):
    """
    Separate individual speakers from an audio file using pyannote.audio
    
    Args:
        audio_path (str): Path to the input audio file
        output_dir (str): Directory to save the separated speaker audio files
    
    Returns:
        dict: Dictionary containing paths to separated speaker audio files
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Get and validate the token
        token = os.getenv("HUGGINGFACE_TOKEN")
        if not token:
            raise ValueError("HUGGINGFACE_TOKEN not found in environment variables")
        
        if not validate_token(token):
            raise ValueError("Invalid HuggingFace token format")
        
        print("🔑 Token validated successfully")
        
        # Initialize the speaker diarization pipeline
        print("🔄 Initializing speaker diarization pipeline...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        print("✓ Pipeline initialized successfully")
        
        # Check if input file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Input audio file not found: {audio_path}")
        
        # Load the audio file
        print(f"🔊 Loading audio file: {audio_path}")
        audio = AudioSegment.from_wav(audio_path)
        print("✓ Audio file loaded successfully")
        
        # Perform speaker diarization
        print("🎯 Performing speaker diarization...")
        diarization = pipeline(audio_path)
        print("✓ Diarization completed")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory ready: {output_dir}")
        
        # Dictionary to store speaker audio segments
        speaker_segments = {}
        
        # Process each speaker segment
        print("\n🔍 Processing speaker segments...")
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # Convert time to milliseconds
            start_ms = int(turn.start * 1000)
            end_ms = int(turn.end * 1000)
            
            # Extract the segment for this speaker
            speaker_audio = audio[start_ms:end_ms]
            
            # Add to speaker segments dictionary
            if speaker not in speaker_segments:
                speaker_segments[speaker] = []
            speaker_segments[speaker].append(speaker_audio)
        
        if not speaker_segments:
            print("⚠️ No speaker segments were detected")
            return {}
        
        # Merge segments for each speaker and save to files
        speaker_files = {}
        print("\n💾 Saving speaker audio files...")
        for speaker, segments in speaker_segments.items():
            # Concatenate all segments for this speaker
            merged_audio = sum(segments)
            
            # Convert speaker label to lowercase and remove any special characters
            speaker_key = f"speaker_{speaker.lower().replace('_', '')}"
            
            # Save to file
            output_path = os.path.join(output_dir, f"{speaker_key}.wav")
            merged_audio.export(output_path, format="wav")
            speaker_files[speaker_key] = output_path
            print(f"✓ Saved speaker {speaker} to {output_path}")
        
        print("\n✨ Speaker separation completed successfully!")
        return speaker_files
        
    except Exception as e:
        print(f"\n❌ Error during speaker separation: {str(e)}")
        print("Please check:")
        print("1. Your HuggingFace token is valid and has access to pyannote/speaker-diarization-3.1")
        print("2. You have a stable internet connection")
        print("3. The input audio file exists and is a valid WAV file")
        return {} 