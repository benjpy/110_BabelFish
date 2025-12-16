import os
import subprocess
from datetime import datetime

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
    Returns the duration of the audio file in seconds using ffprobe.
    """
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0

def split_audio(file_path, segment_length=1200):
    """
    Splits audio into chunks of segment_length seconds.
    Returns a list of file paths for the chunks.
    """
    duration = get_audio_duration(file_path)
    base_name = os.path.splitext(file_path)[0]
    chunks = []
    
    # If file is short enough, just return original (or converted) path
    if duration <= segment_length:
        return [file_path]

    for i in range(0, int(duration), segment_length):
        chunk_path = f"{base_name}_part{i//segment_length}.mp3"
        # ffmpeg split
        subprocess.run([
            "ffmpeg", "-i", file_path, 
            "-ss", str(i), 
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
