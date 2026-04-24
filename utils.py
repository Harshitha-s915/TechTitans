from __future__ import annotations

import os
import re
import json
import random
from typing import Tuple, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
REQUEST_TIMEOUT = 30

def has_groq_key() -> bool:
    key = os.getenv("GROQ_API_KEY", "").strip()
    return bool(key) and key.lower() != "your_groq_api_key_here"


def active_provider() -> str:
    return "groq" if has_groq_key() else "offline"

def llm_complete(
    system_prompt: str,
    user_prompt: str,
    *,
    fallback: str,
    temperature: float = 0.4,
    max_tokens: int = 900,
) -> Tuple[str, str]:
    """
    Returns (text, provider_used).
    `fallback` is the offline string to return if Groq is unavailable.
    """
    if not has_groq_key():
        return fallback, "offline"

    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY').strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return fallback, "offline"
        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        if not text:
            return fallback, "offline"
        return text, "groq"
    except Exception:
        return fallback, "offline"