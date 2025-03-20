import os
from speaker_separation import separate_speakers
from dotenv import load_dotenv

def test_speaker_separation():
    print("\n=== Testing Speaker Separation Module ===")
    
    # Load environment variables
    load_dotenv()
    
    # Test parameters
    input_file = "static/uploads/denoised_merged_vocal.wav"
    output_dir = "static/uploads/speakers"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        print("Please ensure you have run the audio enhancement process first.")
        return
    
    try:
        print(f"🔹 Processing vocal file: {input_file}")
        print(f"📁 Output directory: {output_dir}")
        
        # Run speaker separation
        speaker_files = separate_speakers(input_file, output_dir)
        
        # Check results
        if speaker_files:
            print("\n✓ Speaker separation completed successfully!")
            print(f"Found {len(speaker_files)} speakers")
            print("\nOutput files:")
            for speaker, filepath in speaker_files.items():
                print(f"  • Speaker {speaker}: {filepath}")
        else:
            print("❌ No speakers were detected in the audio")
            
    except Exception as e:
        print(f"❌ Error during speaker separation: {str(e)}")
        print("Please check your HuggingFace token in the .env file")

if __name__ == "__main__":
    test_speaker_separation() 