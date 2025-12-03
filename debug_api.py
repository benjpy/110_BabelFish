import os
from openai import OpenAI
import sys
import subprocess

def test_api(api_key, file_path):
    print(f"Testing API with key: {api_key[:5]}... and file: {file_path}")
    
    client = OpenAI(api_key=api_key)
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Convert to mp3 if opus
    final_file_path = file_path
    converted = False
    
    if file_path.endswith(".opus"):
        print("Converting .opus to .mp3...")
        mp3_path = file_path.replace(".opus", ".mp3")
        try:
            subprocess.run(
                ["ffmpeg", "-i", file_path, "-y", mp3_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            final_file_path = mp3_path
            converted = True
            print(f"Converted to {final_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Conversion failed: {e.stderr.decode()}")
            return

    try:
        print(f"1. Testing Transcription (whisper-1) with {final_file_path}...")
        with open(final_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
        print("Success! Transcript snippet:", response.text[:50])
        print("Detected Language:", getattr(response, 'language', 'Unknown'))
        
    except Exception as e:
        print(f"Transcription (whisper-1) failed: {e}")

    try:
        print(f"\n2. Testing Transcription (gpt-4o-transcribe) with {final_file_path}...")
        with open(final_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                response_format="text"
            )
        print("Success! Transcript snippet:", response[:50])
        
    except Exception as e:
        print(f"Transcription (gpt-4o-transcribe) failed: {e}")
        
    # Cleanup
    if converted and os.path.exists(final_file_path):
        os.unlink(final_file_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python debug_api.py <api_key> <path_to_opus_file>")
    else:
        test_api(sys.argv[1], sys.argv[2])
