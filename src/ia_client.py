import os

from google import genai


def generate_summary(
    commits: str,
    ai_settings: dict,
) -> str:
    if not isinstance(ai_settings, dict):
        raise ValueError(
            "As configurações da IA devem ser um objeto."
        )

    model = ai_settings.get(
        "model",
        "gemini-2.5-flash",
    ).strip()

    prompt_base = ai_settings.get(
        "prompt",
        "",
    ).strip()

    if not model:
        raise ValueError(
            "O modelo da IA não foi configurado."
        )

    if not prompt_base:
        raise ValueError(
            "O prompt da IA não foi configurado."
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "A variável GEMINI_API_KEY não está configurada."
        )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
{prompt_base}

Commits do dia:

{commits}
""".strip()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text or ""