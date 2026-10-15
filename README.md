# Resume Processor + RAG Chatbot

A Django REST + React resume application that now includes an explicit, first-principles RAG pipeline.

## Architecture

```
React
  ↓ HTTP
Django REST API
  ↓
Resume extraction
  ↓
Chunking
  ↓
Hugging Face / sentence-transformers embeddings
  ↓
Per-session NumPy vector store
  ↓
Top-k retrieval
  ↓
RAG prompt + short chat history
  ↓
Gemini API
  ↓
Grounded answer + retrieved sources
```

FAISS is intentionally not used in V1. The NumPy vector store makes the retrieval math visible and easy to learn. FAISS can replace it later behind the same vector-store interface.

## RAG lifecycle

### Indexing

When a resume is uploaded:

```
PDF/DOCX
  → text extraction
  → chunks
  → embeddings
  → session-specific vector store
```

The uploaded file itself is written only to a temporary file during extraction and then deleted.

### Querying

For every question:

```
question
  → question embedding
  → cosine similarity against indexed chunks
  → top-k chunks
  → minimum similarity threshold
  → Gemini prompt (only if relevant matches remain)
  → answer
```

The API also returns the retrieved chunks and similarity scores so the retrieval step can be inspected while learning/debugging.

### Retrieval threshold

`RAG_MIN_SIMILARITY_SCORE` sets the minimum cosine-similarity score for a retrieved chunk to be included in the generation prompt. The initial default is `0.45`. If no retrieved chunk meets the cutoff, the pipeline returns an insufficient-evidence response without calling Gemini.

This score is **not** an LLM confidence percentage or a guarantee that the final answer is correct. The cutoff is an initial value, not a calibrated threshold. Tune it against labelled examples for your resume corpus and track both false accepts and false abstentions. Invalid, non-finite, or out-of-range values fail fast.

## Session model

V1 uses an in-memory, process-local session registry.

Each session owns:
- uploaded resume identity
- its own vector store
- chunk count
- short chat history

Sessions expire after one hour of inactivity and are capped to avoid unbounded memory growth. A user can explicitly delete their session.

**Important:** this is ephemeral storage, not a production multi-server persistence layer. If the application runs with multiple Django worker processes or multiple replicas, the in-memory session registry is not shared between them. A production version should use a shared store such as Redis and/or persistent document/vector storage.

## API

### Upload and index

`POST /api/rag/upload/`

Multipart form-data:

`resume=<PDF or DOCX>`

Response:

```json
{
  "session_id": "...",
  "filename": "candidate.pdf",
  "chunks_indexed": 12,
  "message": "Resume indexed successfully."
}
```

### Chat

`POST /api/rag/chat/`

```json
{
  "session_id": "...",
  "question": "What machine learning experience does the candidate have?"
}
```

The response contains the grounded answer and the retrieved chunks used as evidence. If all retrieved chunks score below the cutoff, the answer is an insufficient-evidence response with an empty source list.

### Delete session

`DELETE /api/rag/session/<session_id>/`

## Setup

Python 3.12 is recommended.

Create/activate the virtual environment and install dependencies:

```powershell
.\venv\Scripts\activate
python -m pip install -r requirements.txt
```

If your Windows certificate store is required for Python HTTPS connections, the application initializes `truststore` before Hugging Face/Gemini HTTP clients are created.

Copy `.env.example` from the repository root to `.env` in the repository root and set your Gemini key and retrieval cutoff:

```dotenv
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash-lite
RAG_MIN_SIMILARITY_SCORE=0.45
```

The Django settings also support an existing `.env` inside the `ResumeProcessor/` project directory; if both exist, the project-local file takes precedence. Never commit either `.env` file.

Run Django:

```powershell
python manage.py runserver
```

Run React separately:

```powershell
cd resume-frontend
npm install
npm start
```

Then open `http://localhost:3000`.

## What this project demonstrates

- document ingestion
- chunking and overlap
- dense embeddings
- cosine similarity retrieval
- explicit RAG prompt construction
- grounding and refusal when evidence is missing
- LLM API integration
- session-scoped ephemeral RAG state
- Django REST API design
- React client integration
- testable separation between retrieval, prompting, and generation

## Current limitations

- NumPy retrieval is intentionally simple and does not scale to large corpora.
- Embeddings run in the Django application process.
- Session state is process-local and ephemeral.
- A single resume is indexed per session.
- The retrieval cutoff is an initial default and has not yet been calibrated on a representative labelled dataset.
- Passing the similarity guard does not prove that the retrieved text supports every generated claim.
- Scanned/image-only PDFs require OCR, which is not implemented yet.
- Gemini requires a valid API key and subject to the provider's current quotas/model availability.

## Diagnosing retrieval misses

`evaluate_retrieval()` reports why a labelled gold evidence span was missed:

- `not_in_index`: no indexed chunk contains the gold span; inspect extraction and chunking.
- `indexed_but_missed_top_k`: the span exists in an indexed chunk, but that chunk was not retrieved; inspect the query, embeddings and top-k.
- `retrieved_in_top_k`: the gold span appears within a returned chunk.

The match is case- and whitespace-insensitive, and the full gold span must fit inside one indexed chunk. If chunking splits a gold span across chunks, the diagnostic reports `not_in_index`, directing you to inspect chunk boundaries. This diagnoses only the index-to-top-k stage; it does not detect reranker drops or LLM failures.

## Testing

Core RAG components include unit tests that use fake embedders/retrievers/LLMs where possible, so tests do not require Gemini API calls.

Run the focused unit tests from the repository root:

```powershell
python -m pytest test_config.py test_prompts.py test_rag_pipeline.py test_retrieval.py test_retrieval_evaluation.py
```

Before calling the project complete locally, test the real path:

1. Start Django.
2. Start React.
3. Upload a real PDF/DOCX resume.
4. Confirm a non-zero chunk count.
5. Ask a question whose answer is explicitly present.
6. Inspect the returned retrieved chunks.
7. Ask a question not supported by the resume and confirm the assistant says the information is unavailable.
8. Upload a second resume in a fresh session and verify its retrieval is isolated from the first session.
9. Delete the session and verify subsequent chat returns 404.

## Next optimization

Once the end-to-end behavior is understood and tested, FAISS can replace the NumPy vector store without changing the higher-level RAG flow.
