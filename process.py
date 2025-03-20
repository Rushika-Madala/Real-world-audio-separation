import librosa
import numpy as np
import soundfile as sf
import os

SAMPLE_RATE = 44100
UPLOAD_FOLDER = "static/uploads"

def split_audio(audio_path, segment_length=10):
    audio, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
    num_samples = sr * segment_length
    step_size = int(num_samples)

    chunks = [audio[i:i+num_samples] for i in range(0, len(audio), step_size)]
    temp_files = []

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    try:
        for i, chunk in enumerate(chunks):
            temp_path = os.path.join(UPLOAD_FOLDER, f"temp_chunk_{i}.wav")
            sf.write(temp_path, chunk, sr)
            temp_files.append(temp_path)
    except Exception as e:
        print(f"Error saving chunks: {e}")
    return temp_files, sr

def merge_audio(chunk_files, sr, output_filename):
    merged_audio = []
    try:
        for file in chunk_files:
            audio, _ = librosa.load(file, sr=sr)
            merged_audio.append(audio)
            os.remove(file)

        output_audio = np.concatenate(merged_audio) if merged_audio else np.array([])
        output_file = os.path.join(UPLOAD_FOLDER, output_filename)
        sf.write(output_file, output_audio, sr)
        return output_file
    except Exception as e:
        print(f"Error merging audio: {e}")
        return None
