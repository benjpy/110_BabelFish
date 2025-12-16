from openai import OpenAI, APIConnectionError
import os
import time

from utils import split_audio, cleanup_files

class AudioTranslator:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key is required.")
        self.client = OpenAI(api_key=api_key)

    def validate_key(self):
        """
        Validates the API key by making a lightweight API call.
        Returns True if valid, False otherwise.
        """
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    def _retry_api_call(self, func, *args, **kwargs):
        """Helper to retry API calls on connection error."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except APIConnectionError as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1 * (attempt + 1))  # Exponential backoff
            except Exception as e:
                raise e

    def transcribe(self, file_path, language_code=None):
        """
        Transcribes the audio file using gpt-4o-transcribe.
        Handles large files by splitting them into chunks.
        """
        transcription_kwargs = {
            "model": "gpt-4o-transcribe",
            "response_format": "text"
        }
        
        if language_code:
            transcription_kwargs["language"] = language_code
            
        # Split audio if necessary (returns list of [file_path] if small enough)
        # Using 1200s (20 min) chunks to be safe under the 1400s limit
        chunks = split_audio(file_path, segment_length=1200)
        
        full_transcript = []
        
        try:
            for chunk_path in chunks:
                with open(chunk_path, "rb") as audio_file:
                    transcription_kwargs["file"] = audio_file
                    # Use retry wrapper
                    response = self._retry_api_call(
                        self.client.audio.transcriptions.create, 
                        **transcription_kwargs
                    )
                    full_transcript.append(response)
        finally:
            # Clean up chunks if they are different from the original file
            # split_audio returns the original path if no split happened, 
            # so we check if the path is in the chunks list and strict check not original
            # Actually, split_audio generates NEW files if split, or returns original path
            # We should only delete if it's a generated chunk.
            # Simpler: split_audio returns new temp paths if split, or single list [original]
            if len(chunks) > 1: 
                cleanup_files(chunks)
            elif chunks[0] != file_path: # Case where it was re-encoded but single chunk? (split_audio logic)
                 # split_audio currently returns [original] if duration <= segment. 
                 # So if len > 1, we know they are temp files.
                 pass
            
        return "\n".join(full_transcript)

    def translate(self, text, target_language):
        """
        Translates the text to the target language using GPT-4o.
        """
        response = self._retry_api_call(
            self.client.chat.completions.create,
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text into {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
