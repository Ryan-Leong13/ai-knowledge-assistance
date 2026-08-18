"""
Standalone LLM connection test - run this to confirm Ollama is installed, running,
and the configured model is pulled, before the LLM is wired into the full RAG pipeline

Prerequisites:
    1. Install Ollama: https://ollama.com/download
    2. Pull the model: ollama pull llama3.2:3b
    3. Ollama should be running in the background (starts automatically after install
    on most system; otherwise run `ollama serve`)

Run using:
    python -m backend.app.test_llm_connection
"""

from dotenv import load_dotenv

load_dotenv()

from backend.app.services.llm_func import generate_response

if __name__ == "__main__":
    print("Sending a test prompt to the LLM...\n")
    try:
        answer = generate_response("Say hello in one short sentence.")
        print("SUCCESS. Model responded:\n")
        print(answer)
    except Exception as e:
        print("FAILED. Error details:\n")
        print(f"{type(e).__name__}: {e}")
        print(
            "\nCommon causes: Ollama isn't running, the model hasn't been "
            "pulled yet (run: ollama pull llama3.2:3b), or OLLAMA_BASE_URL "
            "in .env doesn't match where Ollama is actually listening."
        )