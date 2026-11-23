from mindmate.services.pdf_service import retrieve_chunks

def test_retrieve_chunks_prefers_keyword_overlap():
    chunks = [
        {"page": 1, "text": "Machine learning uses data to identify patterns."},
        {"page": 2, "text": "A user interface supports interaction and feedback."},
    ]
    result = retrieve_chunks("How does machine learning use data?", chunks)
    assert result
    assert result[0]["page"] == 1
