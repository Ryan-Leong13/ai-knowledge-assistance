"""
Retrieval service - given a user query, finds the most relevant documents in the KB 
using TF-IDF + cosine similarity

TF-IDF is fit dynamically over the full document corpus and query on every retrieval 
call, rather than persisting pre-computed dense embeddings

Advantages:
Offline-capable - Avoid the needing of installing heavy neural embedding models, allowing 
                  the application to run completely self-contained out-of-the-box
Cache Coherence - Automatically eliminates vector drift and synchronization issues when 
                  managing documents

Trade-offs:
Computational Overhead - Refitting the vocabulary on every query introduces high computational 
                         cost since it would not scale to large document corpora     
"""

import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from backend.app.models import Document

logger = logging.getLogger("ai_knowledge_assistant")

# Return the top_k most relevant document for a query, ranked by TFIDF and cosine similarity
# Return a list of (Document, similarity score) tuples. An empty list means the knowledge base
# currently has no documents
def retrieve_relevant_doc(
        db: Session, query: str, top_k: int = 3
) -> list[tuple[Document, float]]:
    documents = db.query(Document).all()

    if not documents:
        logger.warning("No documents available for retrieval")
        return []

    corpus = [doc.content for doc in documents]

    # Fit Tfidf over corpus + query together so they share the same vocabulary/vector space
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus + [query])

    doc_vectors = tfidf_matrix[:-1]
    query_vector = tfidf_matrix[-1]

    similarities = cosine_similarity(query_vector, doc_vectors)[0]

    scored = list(zip(documents, similarities))
    scored.sort(key = lambda pair: pair[1], reverse = True)
    top_results = [(doc, float(score)) for doc, score in scored[:top_k]]

    logger.info(
        "Retrieval for query = %r returned top scores: %s",
        query,
        [(doc.title, round(score, 3)) for doc, score in top_results]
    )

    return top_results