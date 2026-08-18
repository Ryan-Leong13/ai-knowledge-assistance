# AI Usage

## 1. Tools Used

- **Claude** (Anthropic) — used throughout for architecture planning, writing backend/frontend code, debugging, and documentation.

## 2. AI Contributions

**Example 1 — RAG pipeline design and implementation.**
Claude designed and implemented the full retrieval-augmented generation flow: the TF-IDF retrieval service, the prompt construction logic in `rag_func.py`, and the two-layer hallucination-handling approach (a similarity-threshold early exit plus explicit grounding instructions in the prompt). This included proactively testing retrieval scores across realistic and adversarial queries (e.g. discovering that a "maternity leave" query still partially matches the "Leave Application" document by vocabulary overlap) and designing the defense specifically around that discovered edge case, rather than a generic assumption.

**Example 2 — Isolated, mocked test suite.**
Claude built the `pytest` suite (`tests/conftest.py`, `test_documents.py`, `test_chat.py`) using an isolated temporary-file SQLite database per test and a fully mocked LLM call, so the 13-test suite runs in under a second with no dependency on a running Ollama instance or the real seeded database. 

## 3. AI Mistake

**What happened:** Claude's initial retrieval implementation used `sentence-transformers` (neural embedding model `all-MiniLM-L6-v2`) for semantic search. When this was actually run, the model download from Hugging Face failed due to a network restriction in the development environment used at the time.

**How it was identified:** The failure surfaced immediately when the seed/retrieval code was executed — a clear connection error, not a silent bug.

**How it was corrected:** Rather than treating this as a one-off environment problem to route around, Claude re-evaluated the retrieval approach against the project's actual constraints (must run offline after `pip install`, no external downloads at runtime) and switched to TF-IDF + cosine similarity via `scikit-learn`. This was tested against the same set of realistic queries used to validate the original approach, confirmed to correctly retrieve the right document for every knowledge base topic, and its known trade-off (vocabulary-based rather than semantic matching) was explicitly documented in `README.md` under Known Limitations (Section 11), along with the reasoning for why the prompt-level grounding layer exists specifically to compensate for it.

*A second, smaller example worth noting:* during manual local testing, a one-character typo (`{document.id}` instead of `{document_id}`) was introduced into the delete route during a manual rename of service functions. This typo was syntactically valid, so neither Python nor FastAPI raised any error at startup — the route silently registered but could never match a real request. It was caught specifically by the automated `test_delete_document_success` test, not by manual testing via Swagger UI, which is a useful demonstration of why the automated test suite (Step 11) matters beyond satisfying the assessment checklist.

## 4. Verification

AI-generated code was verified at each step before moving on, rather than accepted as final on generation:

- **Every service/route was executed and its actual output inspected** — not just read for plausibility. Examples: retrieval was tested against 8+ realistic queries and their similarity scores were manually reviewed; the RAG endpoint was tested end-to-end (with the LLM mocked) via FastAPI's `TestClient` before being tested again with a real local LLM.
- **The full automated test suite (13 tests) was run and required to pass** before any step was considered complete, covering document CRUD, input validation, a retrieval scenario, and hallucination-avoidance behavior.
- **Cross-platform issues were caught through actual testing on both environments**, not assumed away — e.g. the in-memory SQLite test database worked reliably in the development sandbox (Linux) but failed consistently on Windows; this was diagnosed and fixed (switched to a temp-file-backed database) rather than dismissed as a one-off.
- **Security-relevant code was specifically audited**: grep-based scans for hardcoded secrets, manual review of `.gitignore` coverage, and confirmation that no API key is required anywhere in the final architecture (Ollama runs locally with no key).
- **Manual, human-driven testing of the actual running application** (via Swagger UI and the chat UI in a browser) was performed at multiple points, independent of the automated tests, and is what surfaced the delete-route typo described above.
