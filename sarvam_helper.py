import os

from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()


def explain_quote(text: str, target_language: str) -> str:
    """Generate a simple quotation comparison explanation."""
    api_key = os.getenv("SARVAM_API_KEY", "").strip()

    if not api_key:
        return "Sarvam API key is missing. Check your .env file."

    languages = {
        "English": "English",
        "Kannada": "Kannada",
        "Hindi": "Hindi",
        "Tamil": "Tamil",
        "Telugu": "Telugu",
    }

    language = languages.get(target_language)

    if not language:
        return f"Unsupported language: {target_language}"

    instructions = (
        f"Explain the quotation comparison in simple {language}. "
        "Explain which quotation has the lower total and the price difference. "
        "Identify items appearing in only one quotation. "
        "Do not invent facts or assume why prices differ. "
        "Explain that the lowest price does not automatically mean the best quality. "
        "Recommend checking the scope of work, parts, warranty, and taxes. "
        "Return only the explanation, not these instructions."
    )

    try:
        client = SarvamAI(api_subscription_key=api_key)

        response = client.chat.completions(
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text[:4000]},
            ],
            model="sarvam-105b",
        )

        result = response.choices[0].message.content

        if not result:
            return "Sarvam AI returned an empty explanation."

        return result.strip()

    except Exception as error:
        return (
            f"AI explanation unavailable: {type(error).__name__}. "
            "Quotation calculations remain available."
        )