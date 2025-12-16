from openai import OpenAI, APIConnectionError
import os
import time

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
        """
        transcription_kwargs = {
            "model": "gpt-4o-transcribe",
            "response_format": "text"
        }
        
        if language_code:
            transcription_kwargs["language"] = language_code
            
        with open(file_path, "rb") as audio_file:
            transcription_kwargs["file"] = audio_file
            # Use retry wrapper
            response = self._retry_api_call(
                self.client.audio.transcriptions.create, 
                **transcription_kwargs
            )
            
        # With response_format="text", response is the string directly
        return response

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
