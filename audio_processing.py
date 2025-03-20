from pydub import AudioSegment
import numpy as np

def normalize_volume(audio_path, target_dBFS=-20.0):
    """
    Normalize the volume of an audio file to a target dBFS level.
    
    Args:
        audio_path (str): Path to the input audio file
        target_dBFS (float): Target volume level in dBFS (default: -20.0)
    
    Returns:
        str: Path to the normalized audio file
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_wav(audio_path)
        
        # Calculate the current dBFS
        current_dBFS = audio.dBFS
        
        # Calculate the change in dB needed
        change_in_dBFS = target_dBFS - current_dBFS
        
        # Apply the change
        normalized_audio = audio + change_in_dBFS
        
        # Generate output path
        output_path = audio_path.replace('.wav', '_normalized.wav')
        
        # Export the normalized audio
        normalized_audio.export(output_path, format="wav")
        
        return output_path
        
    except Exception as e:
        print(f"Error in volume normalization: {str(e)}")
        raise 