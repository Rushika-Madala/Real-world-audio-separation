import torch
import librosa
import numpy as np
import soundfile as sf
import os
from models.model_architecture import DemucsModel

SAMPLE_RATE = 44100
MODEL_PATH = "models/audio_separation_model_2.pth"
UPLOAD_FOLDER = r"C:\Users\Mora siri\Major_demucs\static\uploads"


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    model = DemucsModel().to(device)
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.eval()
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
    return model

model = load_model()

def separate_audio(chunk_path):
    try:
        audio, sr = librosa.load(chunk_path, sr=SAMPLE_RATE, mono=True)
        input_tensor = torch.tensor(audio, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)

        with torch.no_grad():
            output_tensors = model(input_tensor)
        print(f"Model output shape: {output_tensors.shape}")

        output_tensors = output_tensors.squeeze(0).cpu().numpy()
        labels = ["bass", "vocal", "drum", "music"]
        output_files = {}
        
        for i, label in enumerate(labels):
            output_file = chunk_path.replace("temp_chunk", f"separated_{label}").replace(".wav", f"_{label}.wav")
            sf.write(output_file, output_tensors[i], sr)
            output_files[label] = output_file

        if not all(key in output_files for key in labels):
            print(f"Error: Missing keys in output_files: {output_files.keys()}")
            return None
        
        return output_files
    except Exception as e:
        print(f"Error processing {chunk_path}: {e}")
        return None
