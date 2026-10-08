from tests.conftest import make_pdf


PDF_BYTES = make_pdf(["The proposed hybrid architecture combines a CNN and a Transformer."])


def _upload(client, name="paper.pdf"):
    return client.post("/api/upload", files=[("files", (name, PDF_BYTES, "application/pdf"))])


def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_upload_list_search_chat_delete(client):
    res = _upload(client)
    assert res.status_code == 200
    doc = res.json()["documents"][0]
    assert doc["filename"] == "paper.pdf" and doc["pages"] == 1

    assert _upload(client).json()["documents"][0]["document_id"] == doc["document_id"]  # dedupe
    assert len(client.get("/api/documents").json()) == 1

    s = client.post("/api/search", json={"query": "hybrid CNN Transformer", "top_k": 3}).json()
    assert s["results"][0]["document"] == "paper.pdf"

    c = client.post("/api/chat", json={"question": "What is proposed?"}).json()
    assert "paper.pdf" in c["answer"] and c["sources"][0]["page_start"] == 1

    assert client.delete(f"/api/documents/{doc['document_id']}").status_code == 200
    assert client.delete(f"/api/documents/{doc['document_id']}").status_code == 404
    assert client.post("/api/chat", json={"question": "anything"}).json()["sources"] == []


def test_rejects_non_pdf_and_fake_pdf(client):
    r = client.post("/api/upload", files=[("files", ("a.txt", b"hello", "text/plain"))])
    assert r.status_code == 400
    r = client.post("/api/upload", files=[("files", ("a.pdf", b"not really a pdf", "application/pdf"))])
    assert r.status_code == 400
