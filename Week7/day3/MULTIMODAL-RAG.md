# MULTIMODAL‑RAG --- Day 3 (Image Retrieval Augmented Generation)
![Output](ss/day3ss/examplequery.png)

## Overview

Day‑3 extends the existing text‑RAG pipeline into a **multimodal RAG
system** capable of understanding and retrieving information from images
and scanned PDFs.

The system ingests visual data, extracts semantic meaning, stores vector
representations, and allows three query modes: 1. Text -> Image 2. Image
-> Image 3. Image -> Text Answer (OCR + Caption context)

The goal is to simulate enterprise document intelligence where diagrams,
screenshots, and scanned documents become searchable knowledge.

------------------------------------------------------------------------

## Project Structure

    src/
     ├── data/
     │   └── images/                 # Raw images + PDFs (input)
     │
     ├── multimodal_vectorstore/
     │   ├── images.faiss            # CLIP vector index
     │   └── images_meta.jsonl       # Metadata (OCR + captions)
     │
     ├── embeddings/
     │   └── clip_embedder.py        # CLIP text + image embedding model
     │
     ├── pipelines/
     │   └── image_ingest.py         # Image ingestion pipeline
     │
     └── retriever/
         └── image_search.py         # Interactive multimodal search

------------------------------------------------------------------------

## Image Ingestion Pipeline (`image_ingest.py`)

### Step 1 --- File Discovery

The system scans:

    src/data/images/

Supported formats: - PNG, JPG, JPEG - PDF (each page converted to image)

Each file is converted to RGB format for model compatibility.

------------------------------------------------------------------------

### Step 2 --- Information Extraction

For every image/page:

**OCR Extraction (Tesseract)** - Extracts visible text from diagrams,
forms, or screenshots - Used later for explanation grounding

**Caption Generation (BLIP)** - Produces natural language description of
image content - Helps semantic understanding beyond raw OCR

------------------------------------------------------------------------

### Step 3 --- Embedding Generation

Uses CLIP model:

    Image → 512‑dim vector
    Text  → 512‑dim vector

Both lie in the same vector space → enables cross‑modal retrieval.

Vectors are normalized and stored in FAISS for cosine similarity search.

------------------------------------------------------------------------

### Step 4 --- Storage

The pipeline generates:

**Vector index**

    src/multimodal_vectorstore/images.faiss

**Metadata**

    src/multimodal_vectorstore/images_meta.jsonl

Stored metadata: - Source path - Page number (for PDFs) - OCR text -
Caption

------------------------------------------------------------------------

## Retrieval System (`image_search.py`)

Running the file launches an interactive menu:

    1) Text → Image
    2) Image → Image
    3) Image → Text Answer
    4) Exit

The menu repeats after each query.

------------------------------------------------------------------------

### Mode 1 --- Text → Image

User enters a natural language description.

Process: 1. Convert text -> CLIP embedding 2. Compare with stored image
vectors 3. Return most semantically similar images

Example:

    network architecture diagram

------------------------------------------------------------------------

### Mode 2 --- Image → Image

User provides an image path.

Process: 1. Convert query image → embedding 2. Retrieve visually similar
images

Equivalent to reverse image search.

------------------------------------------------------------------------

### Mode 3 --- Image → Text Answer

User provides an image.

Process: 1. Find similar images/pages 2. Combine OCR + caption 3.
Provide explainable textual context

This prepares grounded information for future LLM answering.

------------------------------------------------------------------------

## How to Run

### 1) Build multimodal index

    python -m src.pipelines.image_ingest

### 2) Start search interface

    python -m src.retriever.image_search

------------------------------------------------------------------------

## Key Concepts Implemented

-   CLIP cross‑modal embeddings
-   OCR document understanding
-   Vision caption generation
-   Multimodal vector database
-   Interactive semantic search

------------------------------------------------------------------------

## Outcome

The system transforms images into searchable knowledge. Users can now
search diagrams and screenshots using natural language and obtain
contextual explanations instead of raw files.

This completes the transition from **text‑only RAG -> multimodal
enterprise knowledge retrieval system**.
