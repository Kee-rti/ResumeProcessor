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
  → Gemini prompt
  → answer
```

The API also returns the retrieved chunks and similarity scores so the retrieval step can be inspected while learning/debugging.

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

The response contains the grounded answer and the retrieved chunks used as evidence.

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

Copy `.env.example` to `.env` and set your Gemini key:

```
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash-lite
```

Never commit `.env`.

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
- Scanned/image-only PDFs require OCR, which is not implemented yet.
- Gemini requires a valid API key and subject to the provider's current quotas/model availability.

## Testing

Core RAG components include unit tests that use fake embedders/retrievers/LLMs where possible, so tests do not require Gemini API calls.

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
