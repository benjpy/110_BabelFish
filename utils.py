import os
import subprocess
from datetime import datetime

from pydub import AudioSegment

def convert_to_mp3(input_path):
    """
    Converts an audio file to .mp3 using pydub.
    Returns the path to the new .mp3 file.
    """
    base_name = os.path.splitext(input_path)[0]
    mp3_path = f"{base_name}.mp3"
    
    audio = AudioSegment.from_file(input_path)
    audio.export(mp3_path, format="mp3")
    return mp3_path

def get_audio_duration(file_path):
    """
    Returns the duration of the audio file in seconds using pydub.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0
    except Exception:
        return 0.0

def split_audio(file_path, segment_length=1200):
    """
    Splits audio into chunks of segment_length seconds.
    Returns a list of file paths for the chunks.
    """
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        print(f"Error loading audio for splitting: {e}")
        return [file_path] # Return original if load fails

    duration_sec = len(audio) / 1000.0
    
    # If file is short enough, just return original path
    if duration_sec <= segment_length:
        return [file_path]

    base_name = os.path.splitext(file_path)[0]
    chunks = []
    
    segment_ms = segment_length * 1000
    
    for i, start_ms in enumerate(range(0, len(audio), segment_ms)):
        chunk_path = f"{base_name}_part{i}.mp3"
        chunk = audio[start_ms : start_ms + segment_ms]
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
        
    return chunks

def cleanup_files(file_paths):
    """
    Safely removes a list of files if they exist.
    """
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except OSError as e:
                print(f"Error deleting {path}: {e}")

def get_timestamp():
    """
    Returns the current timestamp in YYYYMMDD_HHMMSS format.
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")
