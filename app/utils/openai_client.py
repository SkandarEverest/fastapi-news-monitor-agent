import os
from openai import OpenAI

def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")

    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )