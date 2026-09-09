# Resume Information Extractor

## Overview

Resume Information Extractor is a sophisticated solution designed to extract critical information from resumes, including names, email addresses, and phone numbers. This tool leverages advanced NLP techniques to process and analyze resume content, providing a reliable and accurate extraction service. It is built with a Django backend for processing and a React frontend for a seamless user experience.

## Features

- **Text Extraction**: Handles various resume formats, including PDF and DOCX.
- **Information Extraction**: Identifies and extracts key details such as name, email, and phone number.
- **User-Friendly Interface**: A React-based frontend that allows users to upload resumes and view extracted information effortlessly.

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Frontend**: React
- **NLP**: PyPDF2, pdfplumber, docx2txt, pyresparser, spacy
- **Database**: PostgreSQL
- **Logging**: Python logging

## Installation

### Prerequisites

- Python 3.12 or higher
- Node.js and npm
- PostgreSQL

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Kee-rti/ResumeProcessor.git
   cd ResumeProcessor
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the Django server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the resume-frontend directory:
   ```bash
   cd resume-frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

## Usage

1. Access the application via http://localhost:3000 in your web browser.
2. Upload a resume file using the provided interface.
3. View the extracted information displayed on the screen.

## API Endpoints

### `/api/extract_resume/`
- **Method**: POST
- **Description**: Extracts information from the uploaded resume file.
- **Request Body**: Form-data with the resume file attached.
- **Response**: JSON object containing the extracted information.


Important Note on spaCy Compatibility
⚠️ Warning: This project uses spaCy for natural language processing. spaCy models are version-specific and may not be compatible across different versions of spaCy. Please ensure you're using the correct version of spaCy and its corresponding model as specified in the requirements.txt file.
If you encounter any issues related to spaCy models, try the following steps:

Verify your spaCy version:
bashCopypython -m spacy info

If needed, download the correct model for your spaCy version:
bashCopypython -m spacy download en_core_web_sm

If problems persist, consider creating a new virtual environment and reinstalling all dependencies.

For more information on spaCy compatibility, refer to the official spaCy documentation.

## Testing Strategy

To ensure reliability, we distinguish between **Smoke Tests** and **Meaningful Correctness Tests** for every core RAG component:

### 1. Ingestion (`test_ingestion.py`)
- **Smoke Test**: Checks if `ResumeExtractor` can open a file without crashing and returns a string.
  - *Proves*: The file exists, the PDF/DOCX library is installed, and basic reading works.
  - *Does NOT Prove*: The extracted text is accurate, cleanly formatted, or complete.
- **Correctness Test** (To be implemented): Ingest a dummy resume with a known expected string (e.g., "John Doe") and assert that the exact string is present in the output.
  - *Proves*: Text is extracted cleanly without mangling characters or dropping essential content.

### 2. Chunking (`test_chunking.py`)
- **Smoke Test**: Runs the chunking algorithm on a sample sentence and ensures it returns a list of strings without crashing (e.g., catching `MemoryError`).
  - *Proves*: The loop terminates, and it returns a list.
  - *Does NOT Prove*: The chunks overlap correctly or respect boundaries.
- **Correctness Test** (To be implemented): Pass a specific 100-character string with `chunk_size=50` and `overlap=10`. Assert that exactly 3 chunks are produced, and that the overlap between Chunk 1 and Chunk 2 is exactly the last 10 characters of Chunk 1.
  - *Proves*: The sliding window logic mathematically preserves context as designed.

### 3. Embeddings (`test_embeddings.py`)
- **Smoke Test**: Loads the `sentence-transformers` model and passes a dummy chunk.
  - *Proves*: The model is downloaded, torch is installed, and the tensor shape matches expected dimensions (e.g., `(3, 384)`).
  - *Does NOT Prove*: The embeddings are semantically meaningful.
- **Correctness Test** (To be implemented): Pass three chunks: A ("I love Python"), B ("I write Python code"), and C ("The sky is blue"). Compute similarity and assert that similarity(A, B) > similarity(A, C).
  - *Proves*: The model actually groups semantically related concepts closer in vector space.

### 4. Vector Retrieval
- **Smoke Test**: Insert 5 vectors and query for Top-2. Assert that exactly 2 vectors are returned.
  - *Proves*: The similarity search loop doesn't crash and returns the requested `k`.
  - *Does NOT Prove*: It retrieved the *most* similar vectors.
- **Correctness Test** (To be implemented): Insert known vectors (e.g., `[1,0]`, `[0,1]`) and query with `[0.9, 0.1]`. Assert that `[1,0]` is retrieved first based on cosine similarity logic.
  - *Proves*: The math for cosine similarity and sorting is correct.