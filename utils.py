import os
import subprocess
from datetime import datetime
import mutagen
import math

def convert_to_mp3(input_path):
    """
    Converts an audio file to .mp3 using ffmpeg.
    Returns the path to the new .mp3 file.
    Raises subprocess.CalledProcessError if conversion fails.
    """
    base_name = os.path.splitext(input_path)[0]
    mp3_path = f"{base_name}.mp3"
    
    # Check if ffmpeg is installed/available is implicitly handled by subprocess.run failing
    subprocess.run(
        ["ffmpeg", "-i", input_path, "-y", mp3_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return mp3_path

def get_audio_duration(file_path):
    """
    Returns the duration of the audio file in seconds using mutagen.
    """
    try:
        f = mutagen.File(file_path)
        if f and f.info:
            return f.info.length
        return 0.0
    except Exception:
        return 0.0

def split_audio(file_path, segment_length=1200):
    """
    Splits audio into chunks of segment_length seconds using ffmpeg.
    Returns a list of file paths for the chunks.
    """
    duration = get_audio_duration(file_path)
    base_name = os.path.splitext(file_path)[0]
    chunks = []
    
    # If file is short enough, just return original path
    # (Checking against a slightly larger threshold to avoid unnecessary splitting close to edge)
    if duration <= segment_length:
        return [file_path]

    num_parts = math.ceil(duration / segment_length)

    for i in range(num_parts):
        start_time = i * segment_length
        chunk_path = f"{base_name}_part{i}.mp3"
        
        # ffmpeg split
        # -ss: start time
        # -t: duration
        subprocess.run([
            "ffmpeg", "-i", file_path, 
            "-ss", str(start_time), 
            "-t", str(segment_length), 
            "-y", chunk_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
