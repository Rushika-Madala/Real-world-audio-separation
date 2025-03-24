# 🎵 Audio Source Separation Tool

A powerful web application for separating and enhancing audio components from music tracks, with additional features for speaker separation and audio enhancement.

## ✨ Features

- **🎸 Music Source Separation**
  - Separates audio into four components:
    - Vocals
    - Bass
    - Drums
    - Other Musical Elements
  - High-quality separation using deep learning models
  - Real-time processing feedback

- **👥 Speaker Separation**
  - Separates different speakers from vocal tracks
  - Automatic speaker diarization
  - Individual audio tracks for each detected speaker

- **🔊 Audio Enhancement**
  - Noise reduction and audio cleanup
  - Volume normalization
  - Quality improvement for all separated components

- **💻 User-Friendly Interface**
  - Web-based interface for easy access
  - Interactive audio players
  - Download options for all separated components
  - Batch processing capabilities

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- FFmpeg installed on your system

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/audio-separation-tool.git
cd audio-separation-tool
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.\.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with necessary configurations
configuration:
HUGGINGFACE_TOKEN=YOUR TOKEN HERE
touch .env
# Add required environment variables
```

### Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## 🛠️ Project Structure

```
Major_demucs/
├── Core Application Files
│   ├── app.py                 # Main Flask application
│   ├── speaker_separation.py  # Speaker diarization module
│   ├── separation_model.py    # Audio separation model
│   ├── enhancement.py         # Audio enhancement module
│   ├── enhancement.ipnyb         # Audio enhancement module
│   ├── process.py            # Audio processing utilities
│   ├── audio_processing.py   # Additional audio tools
│   └── requirements.txt      # Python dependencies
│
├── Testing
│   └── test_speaker_separation.py  # Speaker separation test
│
├── Templates
│   └── templates/            # HTML templates
│       ├── index.html       # Upload page
│       ├── index1.html       # Upload  page
│       └── download.html    # Results page
│       └── download1.html    # Final Results page
│
├── Static Files
│   └── static/
│       └── uploads/         # Processed files
│           ├── speakers/    # Speaker-separated audio
│           │   ├── speaker_speaker00.wav
│           │   ├── speaker_speaker00_normalized.wav
│           │   ├── speaker_speaker01.wav
│           │   └── speaker_speaker01_normalized.wav
│           ├── denoised_merged_*.wav  # Enhanced components
│           ├── merged_*.wav           # Merged components
│           ├── temp_chunk_*.wav       # Temporary chunks
│           ├── bp08.mp3               # Original input file
│           └── all_separated_files.zip # All processed files
│
├── Models and Data
│   ├── models/             # Pre-trained models
│   ├── dataset/           # Training dataset
│   ├── dataset_3/         # Additional dataset
│   ├── model_save.pth     # Saved model weights
│   └── train_model.ipynb  # Training notebook
│   └── evaluation.ipynb  # Evaluation notebook
│
├── Configuration
│   └── .env              # Environment variables
│
└── Documentation
    └── README.md         # Project documentation
```

## 🔧 Technical Details

### Audio Processing Pipeline

1. **Upload**: Audio file is uploaded and validated
2. **Preprocessing**: File is split into manageable chunks
3. **Source Separation**: Deep learning model separates audio components
4. **Enhancement**: Each component is enhanced and denoised
5. **Speaker Separation**: (Optional) Speakers are separated from vocals
6. **Post-processing**: Volume normalization and quality checks
7. **Delivery**: Processed files are prepared for download

### Models Used

- **Source Separation**: Custom-trained deep learning model
- **Speaker Diarization**: Pyannote.audio
- **Audio Enhancement**: Custom denoising model

## 📝 Usage Guidelines

1. **Upload Audio**:
   - Click "Choose File" to select your audio file
   - Supported formats: WAV, MP3, FLAC
   - Maximum file size: 100MB

2. **Process Audio**:
   - Click "Upload and Process" to start separation
   - Wait for processing to complete
   - Monitor progress indicators

3. **Speaker Separation**:
   - After initial separation, click "Separate Speakers"
   - Wait for speaker detection and separation
   - Listen to individual speaker tracks

4. **Download Results**:
   - Preview each component using the audio players
   - Download individual components or all files as ZIP
   - Use the enhancement options if needed

## ⚠️ Limitations

- Maximum audio file size: 100MB
- Supported audio formats: WAV, MP3, FLAC
- Processing time depends on file size and complexity
- Speaker separation works best with clear vocal tracks

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Demucs](https://github.com/facebookresearch/demucs) for inspiration
- [Pyannote.audio](https://github.com/pyannote/pyannote-audio) for speaker diarization
- All contributors

