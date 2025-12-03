from openai import OpenAI
import os

class AudioTranslator:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key is required.")
        self.client = OpenAI(api_key=api_key)

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
            response = self.client.audio.transcriptions.create(**transcription_kwargs)
            
        # With response_format="text", response is the string directly
        return response

    def translate(self, text, target_language):
        """
        Translates the text to the target language using GPT-4o.
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text into {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
