from flask import Flask, request, render_template, send_file, redirect, url_for, send_from_directory, jsonify
import os
import time
import atexit
import shutil
import zipfile
from separation_model import separate_audio
from process import split_audio, merge_audio
from enhancement import enhance_audio, enhance_all_components
from speaker_separation import separate_speakers
from audio_processing import normalize_volume
from pydub import AudioSegment

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum age of files in seconds (24 hours)
MAX_FILE_AGE = 24 * 60 * 60

def cleanup_on_exit():
    """Clean up all files when the application shuts down"""
    print("\n=== Cleaning up files before shutdown ===")
    try:
        # Clean up all files in the upload folder
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"Removed file: {filename}")
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
                    print(f"Removed directory: {filename}")
            except Exception as e:
                print(f"Error removing {filename}: {str(e)}")
        print("✓ Cleanup completed successfully")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

# Register the cleanup function to run on application exit
atexit.register(cleanup_on_exit)

def cleanup_old_files():
    """Remove files older than MAX_FILE_AGE seconds"""
    current_time = time.time()
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            # Skip if it's a directory
            if os.path.isdir(filepath):
                continue
                
            # Get file's last modification time
            file_time = os.path.getmtime(filepath)
            
            # Remove if file is older than MAX_FILE_AGE
            if current_time - file_time > MAX_FILE_AGE:
                try:
                    os.remove(filepath)
                    print(f"Cleaned up old file: {filename}")
                except Exception as e:
                    print(f"Error removing file {filename}: {str(e)}")
        except Exception as e:
            print(f"Error processing file {filename}: {str(e)}")

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Clean up old files before processing new upload
        cleanup_old_files()
        
        file = request.files["file"]
        if file:
            print("\n=== Starting Audio Processing Pipeline ===")
            print(f"1. Uploading file: {file.filename}")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            print("   ✓ File uploaded successfully")

            print("\n2. Splitting audio into chunks...")
            chunk_files, sr = split_audio(filepath)
            print(f"   ✓ Split into {len(chunk_files)} chunks")

            print("\n3. Processing each chunk for separation...")
            separated_files = {"bass": [], "vocal": [], "drum": [], "music": []}
            for i, chunk in enumerate(chunk_files, 1):
                print(f"   Processing chunk {i}/{len(chunk_files)}...")
                outputs = separate_audio(chunk)
                if outputs:
                    separated_files["bass"].append(outputs["bass"])
                    separated_files["vocal"].append(outputs["vocal"])
                    separated_files["drum"].append(outputs["drum"])
                    separated_files["music"].append(outputs["music"])
            print("   ✓ All chunks processed successfully")

            print("\n4. Merging separated components...")
            merged_files = {}
            for component in ["bass", "vocal", "drum", "music"]:
                print(f"   Merging {component}...")
                merged_files[component] = merge_audio(separated_files[component], sr, f"merged_{component}.wav")
            print("   ✓ All components merged successfully")

            print("\n5. Applying enhancement to denoise files...")
            enhanced_files = enhance_all_components(merged_files, UPLOAD_FOLDER)
            print("   ✓ Enhancement completed successfully")

            print("\n=== Audio Processing Completed Successfully ===")
            return render_template(
                "download.html", 
                bass_file="denoised_merged_bass.wav",
                vocal_file="denoised_merged_vocal.wav",
                drum_file="denoised_merged_drum.wav",
                music_file="denoised_merged_music.wav",
                show_speaker_separation=True
            )

    return render_template("index.html")

@app.route("/separate_speakers", methods=["POST"])
def separate_speakers_route():
    try:
        # Check if vocal file exists
        vocal_file = os.path.join(UPLOAD_FOLDER, "denoised_merged_vocal.wav")
        if not os.path.exists(vocal_file):
            return jsonify({"error": "Vocal file not found. Please process the audio first."}), 404
            
        # Validate file size
        if os.path.getsize(vocal_file) == 0:
            return jsonify({"error": "Vocal file is empty or corrupted."}), 400
            
        # Validate file format
        try:
            audio = AudioSegment.from_wav(vocal_file)
            if len(audio) == 0:
                return jsonify({"error": "Invalid audio file format."}), 400
        except Exception as e:
            return jsonify({"error": f"Invalid audio file format: {str(e)}"}), 400
        
        # Create speakers directory if it doesn't exist
        speakers_dir = os.path.join(UPLOAD_FOLDER, "speakers")
        os.makedirs(speakers_dir, exist_ok=True)
        
        # Clean up old speaker files
        for old_file in os.listdir(speakers_dir):
            if old_file.startswith("speaker_"):
                try:
                    os.remove(os.path.join(speakers_dir, old_file))
                except Exception as e:
                    print(f"Warning: Could not remove old speaker file {old_file}: {str(e)}")
        
        # Get speaker files
        speaker_files = separate_speakers(vocal_file, speakers_dir)
        
        if not speaker_files:
            return jsonify({"error": "No speakers detected in the audio."}), 400
        
        # Normalize all audio files (main components and speakers)
        normalized_files = {}
        
        # Normalize main components
        for component in ['bass', 'vocal', 'drum', 'music']:
            file_path = os.path.join(UPLOAD_FOLDER, f"denoised_merged_{component}.wav")
            if os.path.exists(file_path):
                try:
                    normalized_path = normalize_volume(file_path)
                    normalized_files[component] = os.path.basename(normalized_path)
                except Exception as e:
                    print(f"Warning: Could not normalize {component}: {str(e)}")
        
        # Normalize speaker files
        for speaker, file_path in speaker_files.items():
            if os.path.exists(file_path):
                try:
                    normalized_path = normalize_volume(file_path)
                    normalized_files[f"speaker_{speaker}"] = os.path.basename(normalized_path)
                except Exception as e:
                    print(f"Warning: Could not normalize speaker {speaker}: {str(e)}")

        if not normalized_files:
            return jsonify({"error": "Failed to process any audio files."}), 500

        return jsonify({
            "success": True,
            "speaker_files": normalized_files
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error in speaker separation: {str(e)}")
        return jsonify({"error": "An unexpected error occurred during speaker separation."}), 500

@app.route("/download/<filename>")
def download_file(filename):
    try:
        # Check if the file is in the speakers directory
        if filename.startswith("speaker_"):
            file_path = os.path.join(UPLOAD_FOLDER, "speakers", filename)
        else:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return "File not found", 404
            
        print(f"Downloading file: {filename}")
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error during download: {str(e)}")
        return f"Error downloading file: {str(e)}", 500

def create_zip_file():
    """Create a zip file containing all processed audio files"""
    zip_path = os.path.join(UPLOAD_FOLDER, "all_separated_files.zip")
    
    # Create a zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main components
        main_components = [
            "denoised_merged_bass.wav",
            "denoised_merged_vocal.wav",
            "denoised_merged_drum.wav",
            "denoised_merged_music.wav"
        ]
        
        for component in main_components:
            file_path = os.path.join(UPLOAD_FOLDER, component)
            if os.path.exists(file_path):
                zipf.write(file_path, component)
        
        # Add speaker files if they exist
        speakers_dir = os.path.join(UPLOAD_FOLDER, "speakers")
        if os.path.exists(speakers_dir):
            for speaker_file in os.listdir(speakers_dir):
                if speaker_file.endswith('.wav'):
                    file_path = os.path.join(speakers_dir, speaker_file)
                    zipf.write(file_path, os.path.join("speakers", speaker_file))
    
    return zip_path

@app.route("/download_all", methods=["POST"])
def download_all():
    try:
        print("\n=== Creating zip file with all separated files ===")
        zip_path = create_zip_file()
        print("✓ Zip file created successfully")
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name="all_separated_files.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        print(f"Error creating zip file: {str(e)}")
        return f"Error creating zip file: {str(e)}", 500

@app.route("/normalize/<filename>")
def normalize_file(filename):
    try:
        # Check if the file is in the speakers directory
        if filename.startswith("speaker_"):
            file_path = os.path.join(UPLOAD_FOLDER, "speakers", filename)
        else:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
        if not os.path.exists(file_path):
            return "File not found", 404
            
        print(f"Normalizing volume for: {filename}")
        normalized_path = normalize_volume(file_path)
        
        # Get the normalized filename
        normalized_filename = os.path.basename(normalized_path)
        
        return jsonify({
            "success": True,
            "normalized_file": normalized_filename
        })
    except Exception as e:
        print(f"Error during normalization: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/get_audio_info/<filename>")
def get_audio_info(filename):
    try:
        # Check if the file is in the speakers directory
        if filename.startswith("speaker_"):
            file_path = os.path.join(UPLOAD_FOLDER, "speakers", filename)
        else:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
        if not os.path.exists(file_path):
            return "File not found", 404
            
        audio = AudioSegment.from_wav(file_path)
        duration = len(audio) / 1000.0  # Convert to seconds
        
        return jsonify({
            "success": True,
            "duration": duration,
            "sample_rate": audio.frame_rate,
            "channels": audio.channels
        })
    except Exception as e:
        print(f"Error getting audio info: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("=== Starting Audio Processing Application ===")
    # Clean up old files on startup
    cleanup_old_files()
    app.run(debug=True)
