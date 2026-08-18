"""
Tests for POST /api/chat — covers a valid request, invalid input, a
retrieval scenario, and AI behaviour on out-of-scope questions.

The LLM is mocked throughout the assessment brief's guidance: this keeps 
tests fast, deterministic, and free of any dependency on Ollama actually 
running.
"""
from unittest.mock import patch

# A relevant question should return a 200 with an answer and sources.
def test_chat_valid_request(seeded_client):

    with patch("backend.app.services.rag_func.generate_response") as mock_llm:
        mock_llm.return_value = "You can reset your password via the Identity Portal."

        resp = seeded_client.post(
            "/api/chat", json={"message": "How do I reset my password?"}
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "sources" in body
    assert body["answer"] == "You can reset your password via the Identity Portal."
    assert len(body["sources"]) > 0


def test_chat_empty_message_returns_422(seeded_client):
    resp = seeded_client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 422


def test_chat_missing_message_field_returns_422(seeded_client):
    resp = seeded_client.post("/api/chat", json={})
    assert resp.status_code == 422

# Retrieval scenario: a WiFi-specific question should surface the 'Office WiFi' document 
# among the top sources, not an unrelated one.
def test_chat_retrieval_scenario_returns_correct_source(seeded_client):
    
    with patch("backend.app.services.rag_func.generate_response") as mock_llm:
        mock_llm.return_value = "Connect using your company email and password."

        resp = seeded_client.post(
            "/api/chat", json={"message": "How do I connect to office WiFi?"}
        )

    assert resp.status_code == 200
    source_titles = [s["title"] for s in resp.json()["sources"]]
    assert "Office WiFi" in source_titles

# AI Behaviour test: a question with essentially no vocabulary overlap with any KB document
# (e.g. an unrelated everyday question) should NOT be sent to the LLM at all — it should be 
# caught by the similarity threshold and answered with a fixed not-found message, with no 
# sources. This is the cheapest and most deterministic way to test hallucination avoidance, 
# since it doesn't depend on how an LLM chooses to phrase its refusal.
def test_chat_out_of_domain_question_skips_llm_and_avoids_hallucination(seeded_client):
    
    with patch("backend.app.services.rag_func.generate_response") as mock_llm:
        resp = seeded_client.post(
            "/api/chat", json={"message": "What's the weather like today?"}
        )

        mock_llm.assert_not_called()

    assert resp.status_code == 200
    body = resp.json()
    assert body["sources"] == []
    assert "couldn't find" in body["answer"].lower()

# For an in-scope-vocabulary-but-out-of-scope-fact question (e.g. asking about a leave type not 
# covered in any document), the LLM IS called — but the prompt sent to it must explicitly instruct 
# it not to invent information. This verifies the grounding instruction is actually present in what 
# gets sent, which is the mechanism this project relies on for that class of hallucination.
def test_chat_prompt_instructs_llm_not_to_invent_information(seeded_client):
    
    with patch("backend.app.services.rag_func.generate_response") as mock_llm:
        mock_llm.return_value = (
            "The provided context does not mention maternity leave."
        )

        resp = seeded_client.post(
            "/api/chat",
            json={"message": "What is the maternity leave policy?"},
        )

        assert mock_llm.called
        sent_prompt = mock_llm.call_args[0][0]
        assert "do not" in sent_prompt.lower() or "not guess" in sent_prompt.lower()
        assert "could not be found" in sent_prompt.lower() or "not explicitly stated" in sent_prompt.lower()

    assert resp.status_code == 200
