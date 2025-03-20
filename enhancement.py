import torch
import numpy as np
import soundfile as sf
import os
import librosa
from demucs.apply import apply_model
from demucs.pretrained import get_model
from huggingface_hub import HfApi

# Load the pretrained model (only once)
model = get_model("htdemucs")  # Change to "hdemucs_mmi" if needed
model.cpu()  # Run on CPU
print(" Enhancement Model Loaded Successfully")

def enhance_audio(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return False
    
    try:
        # Load the audio file
        y, sr = librosa.load(input_path, sr=44100)  # Load as mono
        print(f"🔹 Processing: {input_path}")

        # Convert mono to stereo (Demucs expects stereo input)
        y_stereo = np.stack([y, y], axis=0)  # [2, samples]
        waveform = torch.tensor(y_stereo).unsqueeze(0)  # Shape: [1, 2, samples]

        # Apply the enhancement model
        with torch.no_grad():
            sources = apply_model(model, waveform, device="cpu")

        # Extract the enhanced signal
        denoised_signal = sources[0].numpy()
        denoised_signal = np.mean(denoised_signal, axis=0)  # Convert back to mono

        # Save the denoised audio
        sf.write(output_path, denoised_signal.T, sr, format='WAV', subtype='PCM_16')
        print(f"✓ Denoised file saved: {output_path}")
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def enhance_all_components(input_files, output_folder=None):
    """
    Enhance multiple audio files.
    
    Args:
        input_files (dict): Dictionary mapping component names to their file paths
        output_folder (str, optional): Folder to save enhanced files. If None, uses same folder as input
    """
    if not input_files:
        print("No input files provided")
        return {}
    
    # If output_folder is None, use the directory of the first input file
    if output_folder is None:
        output_folder = os.path.dirname(next(iter(input_files.values())))
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Dictionary to store enhanced file paths
    enhanced_files = {}
    
    # Enhance each file
    for component_name, input_path in input_files.items():
        if os.path.exists(input_path):
            print(f"\nEnhancing {component_name}...")
            output_filename = f"denoised_{os.path.basename(input_path)}"
            output_path = os.path.join(output_folder, output_filename)
            
            if enhance_audio(input_path, output_path):
                enhanced_files[component_name] = output_path
            else:
                print(f"Failed to enhance {component_name}")
        else:
            print(f"File {input_path} not found.")
    
    return enhanced_files

def main():
    """Main function to demonstrate usage."""
    # Example usage
    input_folder = "static/uploads"
    
    # Example input files (in practice, these would come from the separation process)
    input_files = {
        "vocal": os.path.join(input_folder, "merged_vocal.wav"),
        "bass": os.path.join(input_folder, "merged_bass.wav"),
        "drums": os.path.join(input_folder, "merged_drum.wav"),
        "music": os.path.join(input_folder, "merged_music.wav")
    }
    
    # Check if input files exist
    print("\nChecking input files...")
    for component, filepath in input_files.items():
        if os.path.exists(filepath):
            print(f"✓ {component}: {filepath} exists")
        else:
            print(f"✗ {component}: {filepath} not found")
    
    # Enhance all components
    print("\nStarting enhancement process...")
    enhanced_files = enhance_all_components(input_files, input_folder)
    print("\nEnhanced files:", enhanced_files)

    # Test token access
    api = HfApi(token="your_token")
    api.model_info("pyannote/speaker-diarization-3.1")

if __name__ == "__main__":
    main() 