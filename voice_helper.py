import os
import base64

from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()


LANGUAGE_CODES = {
    "English": "en-IN",
    "Kannada": "kn-IN",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
}


def get_client():
    api_key = os.getenv("SARVAM_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "SARVAM_API_KEY is missing. Check your .env file."
        )

    return SarvamAI(api_subscription_key=api_key)


def speech_to_text(audio_file, language="Kannada"):
    """Convert recorded speech into text."""

    client = get_client()
    language_code = LANGUAGE_CODES.get(language, "unknown")

    response = client.speech_to_text.transcribe(
        file=audio_file,
        model="saaras:v3",
        language_code=language_code,
    )

    return response.transcript


def text_to_speech(text, language="Kannada"):
    client = get_client()

    language_code = LANGUAGE_CODES.get(language)
    if not language_code:
        raise ValueError(f"Unsupported language: {language}")

    response = client.text_to_speech.convert(
        text=text[:2500],
        language_code=language_code,
        model="bulbul:v3",
        output_audio_codec="wav",
    )

    if not response.audios:
        raise ValueError("Sarvam AI returned no audio.")

    return base64.b64decode(response.audios[0])