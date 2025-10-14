# src/models.py
# Unified interface to call multiple chat models via OpenAI-compatible endpoints.
# Supports: OpenAI (gpt-4o-mini) and Groq (Llama 3 family).
# You can extend MODEL_ROUTING to add more providers or models.

import os
from typing import List, Dict
from openai import OpenAI

# Providers and how to connect to them
PROVIDERS = {
    "openai": {
        "env": "OPENAI_API_KEY",
        "base_url": None,  # default OpenAI endpoint
    },
    "groq": {
        "env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",  # OpenAI-compatible
    },
}

# Logical model name -> (provider_key, provider_specific_model_id)
# Logical model name -> (provider_key, provider_specific_model_id)
# Logical model name -> (provider_key, provider_specific_model_id)
MODEL_ROUTING = {
    # OpenAI
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),

    # Groq (Llama 3.x family)
    "llama3-8b": ("groq", "llama-3.1-8b-instant"),
    "llama3-70b": ("groq", "llama-3.3-70b-versatile"),  # new larger Groq model
}





def _client_for(provider_key: str) -> OpenAI:
    """Return an OpenAI-compatible client for the given provider."""
    cfg = PROVIDERS[provider_key]
    api_key = os.getenv(cfg["env"])
    if not api_key:
        raise RuntimeError(f"Missing API key for provider '{provider_key}'. Set {cfg['env']} in your environment.")
    if cfg["base_url"]:
        return OpenAI(api_key=api_key, base_url=cfg["base_url"])
    return OpenAI(api_key=api_key)

def generate(model_name: str, messages: List[Dict], temperature: float = 0.2) -> str:
    """
    model_name: key in MODEL_ROUTING, e.g., 'gpt-4o-mini' or 'llama-3.1-8b-instruct'
    messages: standard OpenAI chat-style messages list: [{"role": "user", "content": "..."}]
    """
    if model_name not in MODEL_ROUTING:
        raise ValueError(f"Unknown model_name '{model_name}'. Known: {list(MODEL_ROUTING.keys())}")
    provider_key, remote_id = MODEL_ROUTING[model_name]
    client = _client_for(provider_key)
    resp = client.chat.completions.create(model=remote_id, messages=messages, temperature=temperature)
    return resp.choices[0].message.content
