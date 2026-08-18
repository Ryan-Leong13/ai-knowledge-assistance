"""
RAG service - the core pipeline mentioned in the description of assessment

    User Question
        -> Retrieve Relevant Document
        -> Select Top-K Context
        -> Construct Prompt
        -> LLM
        -> Answer + Source

Combines retreival_func and llm_func. 

Hallucination handling uses two-layers, sicne TF-IDF retrieval alone cannot reliably 
distinguish "wrong topic taht shares vocabulary" (eg. "maternity leave" vs. a retrieved 
"Leave Application" doc) from a genuine match:

1. Similarity threshold: if the top retrieval score is at or near zero, the query shares 
   essentially no vocabulary with any document — a strong signal the topic isn't in the 
   KB at all (e.g. "what's the weather today"). The LLM call here is entirely skipped
   in this case and return a fixed not-found message. This is a cheap early exit, not a 
   strict scope filter — it only catches near-zero matches, so it never blocks a 
   legitimately relevant question.

2. Prompt-level grounding (_build_prompt): for everything that passes the threshold, the 
   LLM itself is instructed to answer only from the retrieved context and to say so plainly 
   if the specific fact isn't present — even if a retrieved document is topically related but
   doesn't contain the requested detail (e.g. "Leave Application" is retrieved for a maternity 
   leave question, but only describes annual/sick/compassionate leave; the LLM correctly reports 
   the fact is missing rather than inventing a policy). Verified manually against real queries; 
   see tests/test_chat.py for the automated version.
"""

import logging
import os

from sqlalchemy.orm import Session

from backend.app.services.retrieval_func import retrieve_relevant_doc
from backend.app.services.llm_func import generate_response

logger = logging.getLogger("ai_knowledge_assistant")

NOT_FOUND_MESSAGE = (
    "I couldn't find information about that in the knowledge base."
    " Please check with the relevant team or try rephrasing your question"
)

# Constrcut a ground prompt from the retrieved document
def _build_prompt(query: str, context_docs: list[tuple]) -> str:
    context_blocks = "\n\n".join(
        f"### {doc.title}\n{doc.content}" for doc, _score in context_docs
    )
    return f"""You are a company knowledge assistant. Answer the user's question using ONLY the information in the context below.

Rules:
- If the answer is fully or partially contained in the context, answer clearly and concisely using that information.
- If the context does not contain the answer, say plainly that the information could not be found in the knowledge base. Do NOT guess, assume, or invent any policy, number, or procedure that is not explicitly stated in the context.
- Do not mention these rules in your answer.

Context:
{context_blocks}

Question: {query}

Answer:"""

# Run the full RAG pipeline for a user query
# Returns a dict: {"answer": str, "sources": [{"title": str, "content": str}, ...]}
def answer_question(db: Session, query: str) -> dict:

    top_k = int(os.getenv("TOP_K" , "3"))
    threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.05"))

    results = retrieve_relevant_doc(db, query, top_k = top_k)

    if not results:
        logger.info("No documents in knowledge base to answer query=%r" , query)
        return {"answer": NOT_FOUND_MESSAGE, "sources": []}

    top_score = results[0][1]
    if top_score < threshold:
        logger.info(
            "Top retrieval score %.3f below threshold %.3f for query=%r — "
            "skipping LLM call, returning not-found message.",
            top_score,
            threshold,
            query,
        )
        return {"answer": NOT_FOUND_MESSAGE, "sources": []}

    prompt = _build_prompt(query, results)

    try:
        answer = generate_response(prompt)
    except Exception:
        logger.exception("LLM call failed for query = %r", query)
        raise

    sources = [{"title": doc.title, "content": doc.content} for doc, _score in results]
    return {"answer": answer.strip(), "sources": sources}