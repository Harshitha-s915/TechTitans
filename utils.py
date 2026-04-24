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
    
    _VERDICT_RE = re.compile(r"VERDICT\s*:\s*(CORRECT|PARTIAL|INCORRECT)", re.I)
_FEEDBACK_RE = re.compile(r"FEEDBACK\s*:\s*(.+?)(?:\nHINT\s*:|\Z)", re.I | re.S)
_HINT_RE = re.compile(r"HINT\s*:\s*(.+?)\Z", re.I | re.S)


def parse_evaluation(text: str) -> dict:
    verdict_m = _VERDICT_RE.search(text or "")
    verdict = verdict_m.group(1).upper() if verdict_m else "PARTIAL"

    feedback_m = _FEEDBACK_RE.search(text or "")
    feedback = feedback_m.group(1).strip() if feedback_m else (text or "").strip()

    hint_m = _HINT_RE.search(text or "")
    hint = hint_m.group(1).strip() if hint_m else ""
    if hint.upper().startswith("N/A"):
        hint = ""

    return {"verdict": verdict, "feedback": feedback, "hint": hint}


# --------------------------------------------------------------------------
# Offline fallback engine
# --------------------------------------------------------------------------
# Tiny built-in lessons so TEACH still works without an API key.
_OFFLINE_LESSONS = {
    "loops": (
        "A **loop** repeatedly executes a block of code while a condition "
        "holds, letting you process collections or repeat work without "
        "duplicating code."
    ),
    "arrays": (
        "An **array** (or list) stores an ordered, indexed collection of "
        "values. You access elements by their integer position (index)."
    ),
    "functions": (
        "A **function** is a named, reusable block of code that takes "
        "inputs (parameters), performs work, and may return a result."
    ),
    "recursion": (
        "**Recursion** is when a function calls itself to solve a smaller "
        "instance of the same problem. It needs a base case to stop."
    ),
    "conditionals": (
        "**Conditionals** let a program choose between paths of execution "
        "based on whether a boolean expression is true."
    ),
    "strings": (
        "A **string** is an ordered sequence of characters. Most languages "
        "treat strings as immutable and provide rich operations on them."
    ),
    "dictionaries": (
        "A **dictionary** (a.k.a. map / hash table) stores key→value pairs "
        "with average O(1) lookup, insertion, and deletion."
    ),
    "classes": (
        "A **class** is a blueprint for creating objects that bundle data "
        "(attributes) with behavior (methods)."
    ),
}

_OFFLINE_SYNTAX = {
    "Python": {
        "loops": "for i in range(5):\n    print(i)",
        "arrays": "nums = [1, 2, 3]\nprint(nums[0])",
        "functions": "def add(a, b):\n    return a + b",
        "recursion": "def fact(n):\n    return 1 if n <= 1 else n * fact(n - 1)",
        "conditionals": "if x > 0:\n    print('positive')\nelse:\n    print('non-positive')",
        "strings": "s = 'hello'\nprint(s.upper())",
        "dictionaries": "d = {'a': 1, 'b': 2}\nprint(d['a'])",
        "classes": "class Dog:\n    def __init__(self, name):\n        self.name = name",
    },
    "Java": {
        "loops": "for (int i = 0; i < 5; i++) {\n    System.out.println(i);\n}",
        "arrays": "int[] nums = {1, 2, 3};\nSystem.out.println(nums[0]);",
        "functions": "static int add(int a, int b) { return a + b; }",
        "recursion": "static int fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }",
        "conditionals": "if (x > 0) System.out.println(\"positive\");\nelse System.out.println(\"non-positive\");",
        "strings": "String s = \"hello\";\nSystem.out.println(s.toUpperCase());",
        "dictionaries": "Map<String,Integer> d = new HashMap<>();\nd.put(\"a\", 1);",
        "classes": "class Dog {\n    String name;\n    Dog(String n) { name = n; }\n}",
    },
    "C": {
        "loops": "for (int i = 0; i < 5; i++) {\n    printf(\"%d\\n\", i);\n}",
        "arrays": "int nums[3] = {1, 2, 3};\nprintf(\"%d\\n\", nums[0]);",
        "functions": "int add(int a, int b) { return a + b; }",
        "recursion": "int fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }",
        "conditionals": "if (x > 0) printf(\"positive\\n\"); else printf(\"non-positive\\n\");",
        "strings": "char s[] = \"hello\";\nprintf(\"%s\\n\", s);",
        "dictionaries": "// C has no built-in dict — use a struct array or hash table lib.",
        "classes": "// C has no classes — use struct + functions taking the struct as 1st arg.",
    },
    "JavaScript": {
        "loops": "for (let i = 0; i < 5; i++) {\n  console.log(i);\n}",
        "arrays": "const nums = [1, 2, 3];\nconsole.log(nums[0]);",
        "functions": "function add(a, b) { return a + b; }",
        "recursion": "function fact(n) { return n <= 1 ? 1 : n * fact(n - 1); }",
        "conditionals": "if (x > 0) console.log('positive');\nelse console.log('non-positive');",
        "strings": "const s = 'hello';\nconsole.log(s.toUpperCase());",
        "dictionaries": "const d = { a: 1, b: 2 };\nconsole.log(d.a);",
        "classes": "class Dog {\n  constructor(name) { this.name = name; }\n}",
    },
}

_OFFLINE_CHECK_QUESTION = {
    "loops": "Why might you prefer a `for` loop over a `while` loop here?",
    "arrays": "What is the time complexity of indexing into an array?",
    "functions": "What's the difference between a parameter and an argument?",
    "recursion": "What happens if you forget the base case?",
    "conditionals": "What does an `else if` chain give you over nested `if`s?",
    "strings": "Are strings mutable or immutable in your chosen language?",
    "dictionaries": "What is the average lookup complexity of a dictionary?",
    "classes": "What's the difference between a class and an instance?",
}


def offline_lesson(topic: str, language: str, difficulty: int) -> str:
    t = _norm(topic)
    syntax = _OFFLINE_SYNTAX.get(language, {}).get(
        t, f"// No built-in offline syntax for {topic} in {language}."
    )
    definition = _OFFLINE_LESSONS.get(
        t,
        f"**{topic.title()}** is a programming concept in {language}. "
        f"(Offline mode — connect a Groq key for richer explanations.)",
    )
    check = _OFFLINE_CHECK_QUESTION.get(
        t, f"In one sentence, when would you reach for {topic} in {language}?"
    )
    return (
        f"### Definition\n{definition}\n\n"
        f"### Syntax\n```{language.lower()}\n{syntax}\n```\n\n"
        f"### Example\n```{language.lower()}\n{syntax}\n```\n"
        f"_The snippet above is the minimal working example at level {difficulty}._\n\n"
        f"### Quick Check\n{check}"
    )
_OFFLINE_CHALLENGE_BANK = {
    "loops": [
        ("Print all even numbers from 1 to N.",
         "An integer N (1 ≤ N ≤ 100).",
         "Even numbers from 1 to N, one per line.",
         "Input: 6\nOutput: 2\n4\n6"),
        ("Compute the sum of integers 1..N.",
         "An integer N.",
         "The sum 1+2+…+N.",
         "Input: 5\nOutput: 15"),
    ],
    "arrays": [
        ("Return the maximum value in an array.",
         "A list of integers.",
         "The maximum integer.",
         "Input: [3, 1, 7, 4]\nOutput: 7"),
        ("Reverse an array in place.",
         "A list of integers.",
         "The reversed list.",
         "Input: [1, 2, 3]\nOutput: [3, 2, 1]"),
    ],
    "functions": [
        ("Write a function `is_even(n)` that returns True if n is even.",
         "An integer n.",
         "Boolean.",
         "Input: 4\nOutput: True"),
    ],
    "recursion": [
        ("Compute factorial(n) using recursion.",
         "A non-negative integer n.",
         "n!",
         "Input: 5\nOutput: 120"),
        ("Compute the nth Fibonacci number recursively.",
         "A non-negative integer n.",
         "F(n)",
         "Input: 6\nOutput: 8"),
    ],
    "conditionals": [
        ("Given an integer, print 'positive', 'negative', or 'zero'.",
         "An integer x.",
         "One of the three strings.",
         "Input: -3\nOutput: negative"),
    ],
    "strings": [
        ("Check whether a string is a palindrome.",
         "A string s.",
         "True or False.",
         "Input: 'racecar'\nOutput: True"),
    ],
    "dictionaries": [
        ("Count how many times each character appears in a string.",
         "A string s.",
         "A dict char -> count.",
         "Input: 'aab'\nOutput: {'a': 2, 'b': 1}"),
    ],
    "classes": [
        ("Define a class `Counter` with `inc()` and `value()`.",
         "A sequence of inc() calls.",
         "Final counter value.",
         "Input: inc, inc, inc\nOutput: 3"),
    ],
}


def offline_challenge(topic: str, language: str, difficulty: int) -> str:
    bank = _OFFLINE_CHALLENGE_BANK.get(_norm(topic))
    if not bank:
        problem = (
            f"Write a {language} program that demonstrates the concept of "
            f"**{topic}** at difficulty {difficulty}/4."
        )
        return _format_challenge(problem, "Free-form.", "Free-form.", "—")
    idx = min(difficulty - 1, len(bank) - 1)
    problem, inp, out, ex = bank[idx]
    return _format_challenge(problem, inp, out, ex)


def offline_interview(topic: str, language: str, difficulty: int, time_limit: int) -> str:
    base = offline_challenge(topic, language, difficulty)
    return (
        "**Interview Question**\n"
        f"{base}\n\n"
        f"**Time limit:** {time_limit} minutes\n\n"
        "**What I'm looking for:**\n"
        "- Correctness\n- Time/space complexity\n- Edge cases\n"
    )


def offline_evaluate(challenge: str, answer: str, topic: str, language: str) -> str:
    """Heuristic offline evaluation — never claims certainty."""
    a = (answer or "").strip()
    if not a:
        return ("VERDICT: INCORRECT\n"
                "FEEDBACK: You didn't submit any code. Try writing at least the "
                "function signature and the base case before submitting.\n"
                "HINT: Start by writing the function header and a return statement "
                "for the simplest input.")