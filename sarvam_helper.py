import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()


def _get_field(obj, field, default=None):
    """Read a field from an SDK object or dictionary."""
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


def _extract_text(response):
    """Extract generated text from the Sarvam API response."""
    choices = _get_field(response, "choices", None)

    if not choices:
        return ""

    message = _get_field(choices[0], "message", None)

    if message is None:
        return ""

    content = _get_field(message, "content", None)

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for part in content:
            if isinstance(part, str):
                parts.append(part)
            else:
                value = _get_field(part, "text", None)

                if isinstance(value, str):
                    parts.append(value)

        return "\n".join(
            part.strip() for part in parts if part.strip()
        ).strip()

    return ""


def explain_quote(text: str, target_language: str) -> str:
    """Generate an explanation of quotation comparisons."""

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

    quote_text = str(text).strip()

    if not quote_text:
        return "No quotation comparison data was provided."

    system_prompt = (
        f"You are QuoteWise. Explain the quotation comparison "
        f"in simple {language}. "
        "Identify which quotation is cheaper and state the price "
        "difference if the data provides it. "
        "Mention missing items only when supported by the data. "
        "Never invent prices or facts. "
        "Use complete sentences and return only the explanation."
    )

    client = SarvamAI(api_subscription_key=api_key)

    prompts = [
        (system_prompt, quote_text[:2500]),
        (
            f"Explain this quotation comparison in simple {language}. "
            "Use only the supplied data. Write 2-4 complete sentences.",
            quote_text[:1000],
        ),
    ]

    last_error = "The API returned no explanation text."

    for system_content, user_content in prompts:
        try:
            response = client.chat.completions(
                model="sarvam-105b",
                messages=[
                    {
                        "role": "system",
                        "content": system_content,
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ],
                max_tokens=512,
                reasoning_effort=None,
            )

            explanation = _extract_text(response)

            if explanation:
                return explanation

            choices = _get_field(response, "choices", None)

            finish_reason = (
                _get_field(choices[0], "finish_reason", None)
                if choices
                else None
            )

            last_error = (
                "Sarvam returned empty text. "
                f"Finish reason: {finish_reason!r}."
            )

        except Exception as error:
            last_error = f"{type(error).__name__}: {error}"

    return (
        f"AI explanation unavailable: {last_error} "
        "Quotation calculations remain available."
    )