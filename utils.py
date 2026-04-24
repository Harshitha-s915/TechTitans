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