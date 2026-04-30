import os

from google import genai


def generate_summary(commits: str) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt_base = os.getenv("PROMPT_BASE", "")

    prompt = f"""
{prompt_base}

Commits do dia:

{commits}
""".strip()

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
    )

    return response.text or ""