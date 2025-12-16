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
