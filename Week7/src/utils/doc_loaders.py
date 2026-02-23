from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
import pandas as pd
import docx


def load_pdf(path: Path) -> List[Dict[str, Any]]:
    reader = PdfReader(str(path))
    docs = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        docs.append({
            "text": text,
            "meta": {"source": str(path), "page": i+1, "type": "pdf"}
        })
    return docs


def load_txt(path: Path):
    text = path.read_text(errors="ignore")
    return [{"text": text, "meta": {"source": str(path), "page": None, "type": "txt"}}]


def load_docx(path: Path):
    d = docx.Document(str(path))
    text = "\n".join([p.text for p in d.paragraphs])
    return [{"text": text, "meta": {"source": str(path), "page": None, "type": "docx"}}]


def load_csv(path: Path):
    df = pd.read_csv(path)
    rows = df.astype(str).apply(lambda r: ", ".join(r), axis=1)
    text = "\n".join(rows.tolist())
    return [{"text": text, "meta": {"source": str(path), "page": None, "type": "csv"}}]


def load_any(path: Path):
    ext = path.suffix.lower()
    if ext == ".pdf": return load_pdf(path)
    if ext == ".txt" or ext == ".md": return load_txt(path)
    if ext == ".docx": return load_docx(path)
    if ext == ".csv": return load_csv(path)
    return []