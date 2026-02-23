
# MULTIMODAL-RAG.md 

## Goal
Extend the RAG system from text‑only to **multimodal** by allowing images and scanned PDFs to be indexed and retrieved using semantic similarity.

The system now understands:
- Images (PNG/JPG)
- Scanned PDFs (each page treated as an image)
- Diagrams / Flowcharts / Forms

---

## Architecture Overview

### Ingestion Pipeline
For every file inside:
```
src/data/images/
```

The pipeline performs:

1. **PDF Handling (PyMuPDF)**
   - Each PDF page → converted to image

2. **OCR Extraction (Tesseract)**
   - Extract readable text from image

3. **Caption Generation (BLIP)**
   - Generate human description of image

4. **Vision Embedding (CLIP)**
   - Convert image → 512‑dim vector

5. **Storage**
   - FAISS index → vectors
   - JSON metadata → captions + OCR + source info

Output:
```
src/data/vectorstore/image_index.faiss
src/data/vectorstore/image_index_meta.json
```

---

## Retrieval Modes

Run:
```
python -m src.retriever.image_search
```

### 1) Text → Image
User enters text query.
System embeds text using CLIP text encoder.
Returns most similar images/PDF pages.

### 2) Image → Image
User provides image path.
System retrieves visually similar images.

### 3) Image → Text Evidence
User provides image path.
System returns explanation context:
- caption
- OCR text
- source & page

---

## Multimodal Vector Design

Each record stored as:

Vector:
- CLIP image embedding (512‑d normalized)

Metadata:
- source file path
- file type (image/pdf)
- page number (for PDF)
- caption (BLIP)
- OCR text (Tesseract)
- tags

Similarity:
Cosine similarity via FAISS IndexFlatIP

---

## Demonstration (Flowchart PDF)

Added file:
```
src/data/images/flowchart.pdf
```

During ingestion:
- Each page converted to image
- OCR extracted flowchart text
- Caption generated
- Indexed into FAISS

Example query:
```
flowchart
```

Result:
System retrieved correct PDF pages with explanation context.

---

![Example Query](ss/day3ss/examplequery.png)


