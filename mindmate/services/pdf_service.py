import re
from io import BytesIO
from pypdf import PdfReader

def extract_and_chunk(pdf_bytes: bytes, words_per_chunk: int = 180):
    reader = PdfReader(BytesIO(pdf_bytes))
    chunks = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        words = text.split()
        for start in range(0, len(words), words_per_chunk):
            chunk = " ".join(words[start:start + words_per_chunk]).strip()
            if chunk:
                chunks.append({"page": page_number, "text": chunk})
    return chunks

def retrieve_chunks(question: str, chunks: list[dict], top_k: int = 3):
    """Simple transparent keyword-overlap retrieval; suitable as a baseline, not semantic search."""
    stop_words = {"the", "and", "for", "that", "with", "what", "when", "where",
                  "which", "does", "this", "from", "about", "into", "are", "how"}
    terms = {
        t for t in re.findall(r"[a-zA-Z0-9]+", question.lower())
        if len(t) > 2 and t not in stop_words
    }
    ranked = []
    for chunk in chunks:
        words = set(re.findall(r"[a-zA-Z0-9]+", chunk["text"].lower()))
        score = len(terms & words)
        if score:
            ranked.append((score, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:top_k]]
