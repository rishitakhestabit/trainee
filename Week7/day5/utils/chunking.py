from typing import List, Dict, Any
import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text: str, size: int = 700, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks


def make_chunks(docs: List[Dict[str, Any]], tags=None):
    tags = tags or []
    results = []

    for doc in docs:
        text = clean_text(doc["text"])
        for i, chunk in enumerate(chunk_text(text)):
            results.append({
                "text": chunk,
                "meta": {**doc["meta"], "chunk_id": i, "tags": tags}
            })

    return results