"""
llm_service.py
--------------
Provider-agnostic LLM wrapper.  Currently wired to Groq (llama-3.3-70b-versatile).

To switch providers later, just change LLM_PROVIDER in your .env:
  LLM_PROVIDER=groq   → uses Groq (default)
  LLM_PROVIDER=gemini → uses Google Gemini Flash
  LLM_PROVIDER=ollama → uses a local Ollama server
"""

import os
from config import get_llm_config


def call_llm(system_prompt: str, history: list[dict], user_message: str) -> str:
    """
    Send a conversation to the configured LLM and return the text response.

    Args:
        system_prompt:  The system/context message (financial data injected here).
        history:        A list of {"role": "user"|"assistant", "content": "..."} dicts
                        representing prior turns (oldest first, max 10 turns).
        user_message:   The latest user question.

    Returns:
        The assistant's reply as a plain string.
    """
    cfg = get_llm_config()
    provider = cfg["provider"].lower()

    if provider == "groq":
        return _call_groq(cfg, system_prompt, history, user_message)
    elif provider == "gemini":
        return _call_gemini(cfg, system_prompt, history, user_message)
    elif provider == "ollama":
        return _call_ollama(cfg, system_prompt, history, user_message)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'. Use groq, gemini, or ollama.")


# ── Groq ─────────────────────────────────────────────────────────────────────

def _call_groq(cfg: dict, system_prompt: str, history: list, user_message: str) -> str:
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Install the groq package: pip install groq")

    api_key = cfg.get("api_key", "").strip()
    if not api_key:
        raise ValueError("Missing Groq API Key. Please add LLM_API_KEY to your database/.env file.")

    client = Groq(api_key=api_key)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=cfg["model"] or "llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


# ── Google Gemini ─────────────────────────────────────────────────────────────

def _call_gemini(cfg: dict, system_prompt: str, history: list, user_message: str) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Install the Gemini package: pip install google-generativeai")

    genai.configure(api_key=cfg["api_key"])
    model = genai.GenerativeModel(
        model_name=cfg["model"] or "gemini-1.5-flash",
        system_instruction=system_prompt,
    )

    # Convert history to Gemini format
    gemini_history = []
    for turn in history:
        role = "user" if turn["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [turn["content"]]})

    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(user_message)
    return response.text.strip()


# ── Ollama (local) ────────────────────────────────────────────────────────────

def _call_ollama(cfg: dict, system_prompt: str, history: list, user_message: str) -> str:
    import urllib.request
    import json

    base_url = cfg.get("ollama_url", "http://localhost:11434")
    model    = cfg["model"] or "llama3"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model":    model,
        "messages": messages,
        "stream":   False,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data["message"]["content"].strip()
