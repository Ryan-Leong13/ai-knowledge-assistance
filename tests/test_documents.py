"""
Tests for the Document Management API (GET/POST/DELETE /api/documents).
"""

# A fresh database should return an empty list, not an error.
def test_list_documents_empty(client):
    
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_document_success(client):
    resp = client.post(
        "/api/documents",
        json={"title": "Test Policy", "content": "Some policy content."},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Test Policy"
    assert body["content"] == "Some policy content."
    assert "id" in body
    assert "created_at" in body


def test_list_documents_after_create(client):
    client.post("/api/documents", json={"title": "Doc A", "content": "Content A"})
    client.post("/api/documents", json={"title": "Doc B", "content": "Content B"})

    resp = client.get("/api/documents")
    assert resp.status_code == 200
    titles = [doc["title"] for doc in resp.json()]
    assert "Doc A" in titles
    assert "Doc B" in titles
    assert len(resp.json()) == 2


def test_create_document_missing_title_returns_422(client):
    resp = client.post("/api/documents", json={"content": "No title here."})
    assert resp.status_code == 422


def test_create_document_empty_content_returns_422(client):
    resp = client.post("/api/documents", json={"title": "Empty", "content": ""})
    assert resp.status_code == 422


def test_delete_document_success(client):
    create_resp = client.post(
        "/api/documents", json={"title": "To Delete", "content": "Delete me."}
    )
    doc_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/documents/{doc_id}")
    assert delete_resp.status_code == 204

    list_resp = client.get("/api/documents")
    assert list_resp.json() == []


def test_delete_nonexistent_document_returns_404(client):
    resp = client.delete("/api/documents/9999")
    assert resp.status_code == 404
