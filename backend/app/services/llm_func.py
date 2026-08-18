"""
LLM Service - wrapper around local Ollama server

Kept deliberately simple and isolated logic here so it can be tested standalone 
and mocked easily in the future
"""

import logging
import os

import ollama 

logger = logging.getLogger("ai_knowledge_assistant")


# Send a prompt to the configured local Ollama model and return the plain text response
# Raises whatever exception the client raises on failure (eg. Ollama not running, model 
# model not pulled) - callers are responsible for catching and translating this into an 
# appropriate API error response
def generate_response(prompt: str) -> str:
    model_name = os.getenv("LLM Model", "llama3.2:3b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    logger.info("Calling LLM model=%s prompt_len=%d", model_name, len(prompt))

    client = ollama.Client(host = base_url)

    response = client.chat(
        model = model_name,
        messages = [{"role": "user", "content": prompt}],
    )

    answer = response["message"]["content"]
    logger.info("LLM response received, length=%d", len(answer))

    return answer