# CounselOS Architecture

## Overview

CounselOS is a modular monolith desktop application with clear layer boundaries:

```
┌─────────────────────────────────────┐
│         Tauri Desktop Shell          │
│      (React + TypeScript UI)         │
├─────────────────────────────────────┤
│         FastAPI Service Layer        │
│    (127.0.0.1:8741, auth required)   │
├──────────┬──────────┬───────────────┤
│ Ingestion│ Retrieval│  Inference    │
│  Layer   │  Layer   │   Layer       │
├──────────┴──────────┴───────────────┤
│       Workflow Orchestration         │
│  (Extraction, Chronology, Compare)   │
├─────────────────────────────────────┤
│         Persistence Layer            │
│   (SQLite + FTS5 + FAISS + Files)    │
└─────────────────────────────────────┘
```

## Key Design Decisions

### Offline-First (SEC-001, SEC-002)
- All processing runs locally
- No external API calls
- Network denial policy recommended
- Local LLM inference via llama.cpp

### Matter Isolation (SEC-008)
- Every data query is scoped to a matter_id
- Foreign key constraints enforced
- Cross-matter access tests are release blockers

### Evidence Provenance
- Every claim, event, and finding links to source chunks
- Chunks link to documents with page numbers
- Citations are validated against stored content

### Human Review
- AI outputs start as "pending" status
- Review decisions are recorded with history
- Accepted/rejected states persist across restarts

## Component Map

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Desktop shell | Tauri 2.x | Package web UI as native app |
| Frontend | React + TypeScript | Case workspace UI |
| API service | Python + FastAPI | Local REST API |
| Database | SQLite + FTS5 | Structured data + keyword search |
| Vector search | FAISS | Semantic retrieval |
| LLM inference | llama.cpp | Local model execution |
| Embeddings | sentence-transformers | Document embeddings |
| OCR | Tesseract | Scanned document processing |
| PDF parsing | PyMuPDF | Digital PDF extraction |
| DOCX parsing | python-docx | Word document extraction |
| Encryption | cryptography (Fernet/PBKDF2) | Backup encryption |
| Export | python-docx | DOCX report generation |

## Security Boundaries

1. **Tauri shell** → communicates with backend via localhost HTTP only
2. **FastAPI** → bound to 127.0.0.1, requires session token
3. **Document parser** → treats all input as untrusted
4. **LLM inference** → receives only scoped evidence context
5. **File system** → originals stored separately from derived data
