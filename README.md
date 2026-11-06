# CounselOS

**Offline-First Legal Evidence Analysis Desktop Application for Indian Litigation Lawyers**

CounselOS is a privacy-first, fully offline desktop application purpose-built for Indian litigation advocates, legal researchers, and law chambers. It provides AI-powered evidence analysis, document comparison, chronology construction, and claim extraction — all running entirely on the user's local machine with zero data leaving the device.

Built with FastAPI, React 18, Tauri 2, and local LLMs via llama.cpp, CounselOS treats attorney-client privilege as an architectural constraint, not a policy checkbox.

---

## Table of Contents

- [Why CounselOS](#why-counselos)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Architecture Overview](#architecture-overview)
- [Technical Deep Dive](#technical-deep-dive)
  - [Backend (Python / FastAPI)](#backend-python--fastapi)
  - [Frontend (React / TypeScript / Tailwind)](#frontend-react--typescript--tailwind)
  - [Desktop Shell (Tauri 2)](#desktop-shell-tauri-2)
  - [AI & ML Stack](#ai--ml-stack)
  - [Database Layer](#database-layer)
  - [Search & Retrieval](#search--retrieval)
  - [Document Ingestion Pipeline](#document-ingestion-pipeline)
  - [Workflow Engine](#workflow-engine)
  - [Export System](#export-system)
  - [Security Architecture](#security-architecture)
- [Design System](#design-system)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Quick Start (Standalone Executable)](#quick-start-standalone-executable)
- [Installation & Setup (Development)](#installation--setup-development)
- [Usage Guide](#usage-guide)
- [Trade-offs & Design Decisions](#trade-offs--design-decisions)
- [Configuration Reference](#configuration-reference)
- [Building the Executable from Source](#building-the-executable-from-source)
- [Testing](#testing)
- [License](#license)

---

## Why CounselOS

Indian litigation involves managing enormous volumes of evidence — FIRs, charge sheets, affidavits, witness statements, court orders, and documentary exhibits often spanning thousands of pages across multiple volumes. Lawyers spend significant time manually cross-referencing dates, identifying contradictions between witness statements, and building chronologies for arguments.

Existing legal-tech solutions either require uploading sensitive case data to cloud servers (unacceptable for privileged legal communications) or offer surface-level document management without analytical depth.

CounselOS addresses this by:

1. **Running entirely offline** — no internet connection required after initial setup. All AI inference, search, and analysis happens on the lawyer's own machine.
2. **Understanding Indian legal context** — supports Hindi+English OCR, Indian statutory citation formats (e.g., Section 65B(4) IEA / Section 63 BSA), and Indian court hierarchy references.
3. **Maintaining evidentiary provenance** — every AI-generated claim, finding, or timeline event links back to the exact source document, page number, and text excerpt.
4. **Requiring human review** — AI outputs start as "pending" and must be explicitly accepted or rejected by the lawyer before inclusion in any export or report.

---

## Key Features

| Feature | Description |
|---|---|
| **Matter Management** | Organize cases as isolated matters with metadata (title, reference, jurisdiction, case type) |
| **Document Ingestion** | Upload PDFs and DOCX files with automatic text extraction, OCR for scanned documents, and intelligent chunking |
| **Hybrid Search** | Combined keyword (SQLite FTS5 / BM25) and semantic (FAISS / sentence-transformers) search with Reciprocal Rank Fusion |
| **AI Question Answering** | Ask natural language questions about case evidence with cited, provenance-linked answers |
| **Claim Extraction** | Automatically identify factual assertions, temporal claims, financial claims, and legal assertions from evidence |
| **Entity Recognition** | Extract persons, organizations, locations, dates, and monetary amounts from documents |
| **Chronology Construction** | Build timelines from extracted claims with date precision tracking (exact, approximate, range, inferred) |
| **Document Comparison** | Cross-reference claims between documents to identify contradictions, discrepancies, corroborations, and omissions |
| **Findings Review** | Human-in-the-loop review workflow for all AI-generated findings (accept/reject/needs evidence/ambiguous) |
| **Report Export** | Generate DOCX reports with findings, chronology, claims, and source citations |
| **Encrypted Backups** | PBKDF2 + Fernet encrypted ZIP backups per matter or full database |
| **Audit Trail** | Complete audit log of all user actions with sensitive field filtering |

---

## System Requirements

### Minimum Specifications

| Component | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10 (64-bit), macOS 12+, Ubuntu 20.04+ | Windows 11, macOS 14+, Ubuntu 22.04+ |
| **CPU** | 4 cores, x86_64 or ARM64 | 8+ cores with AVX2 support |
| **RAM** | 8 GB | 16 GB (32 GB for large case files) |
| **Storage** | 10 GB free (application + models) | SSD with 50+ GB free |
| **GPU** | Not required (CPU inference) | NVIDIA GPU with 6+ GB VRAM (optional, for faster inference) |
| **Python** | 3.11+ | 3.12 |
| **Node.js** | 18+ | 20 LTS |
| **Rust** | 1.70+ (for Tauri compilation) | Latest stable |

### Additional Requirements

- **Tesseract OCR** — required for scanned PDF processing. Install separately:
  - Windows: download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr tesseract-ocr-hin`
- **Hindi language pack** for Tesseract (`hin`) — required for bilingual Hindi+English document OCR
- **GGUF model file** — a quantized LLM in GGUF format (see [AI & ML Stack](#ai--ml-stack) for recommendations)

### Storage Estimates

| Content | Approximate Size |
|---|---|
| Application code + dependencies | ~2 GB |
| Embedding model (all-MiniLM-L6-v2) | ~90 MB |
| Primary LLM (8B Q4_K_M) | ~4.5 GB |
| Fallback LLM (4B Q4_K_M) | ~2.5 GB |
| FAISS index (per 10,000 chunks) | ~15 MB |
| SQLite database (per 1,000 documents) | ~50-200 MB |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Tauri 2 Desktop Shell                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    React 18 Frontend                      │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │  │
│  │  │  Matter   │ │ Document │ │  Search  │ │ Chronology │  │  │
│  │  │  Manager  │ │  Viewer  │ │  & Ask   │ │  Builder   │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │  │
│  │  │ Compare  │ │ Findings │ │  Export  │ │  Settings  │  │  │
│  │  │  Docs    │ │  Review  │ │  Report  │ │  & Status  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │  │
│  │              React Query · React Router                   │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          │ HTTP (localhost:8741)                 │
│  ┌───────────────────────┴───────────────────────────────────┐  │
│  │                  FastAPI Backend (Python)                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │  │
│  │  │   API    │ │ Ingest   │ │ Retrieval│ │  Inference  │  │  │
│  │  │ Routers  │ │ Pipeline │ │  Engine  │ │  (LLM/QA)  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │  │
│  │  │Workflows │ │ Exports  │ │ Security │ │   Auth     │  │  │
│  │  │(Extract/ │ │  (DOCX)  │ │ (Audit/  │ │ (Session)  │  │  │
│  │  │ Compare) │ │          │ │  Crypto) │ │            │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │  │
│  │              SQLAlchemy · Pydantic · aiofiles              │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          │                                      │
│  ┌───────────────────────┴───────────────────────────────────┐  │
│  │                     Data Layer                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │   SQLite +   │  │    FAISS     │  │   Local File   │  │  │
│  │  │    FTS5      │  │ Vector Index │  │    Storage     │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     AI Models (Local)                      │  │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐  │  │
│  │  │  GGUF LLM Model  │  │  sentence-transformers       │  │  │
│  │  │  (llama.cpp)      │  │  (all-MiniLM-L6-v2)         │  │  │
│  │  └──────────────────┘  └──────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         All components run on 127.0.0.1 — nothing leaves the device
```

The architecture follows a **three-tier local stack** pattern:

1. **Tauri 2 Shell** — a Rust-based desktop wrapper that hosts the React frontend in a native webview. It enforces CSP restrictions and filesystem sandboxing, ensuring the frontend can only communicate with the local backend.

2. **FastAPI Backend** — a Python HTTP server bound exclusively to `127.0.0.1:8741` (loopback interface). It handles all business logic: document ingestion, AI inference, search, workflow orchestration, and data persistence. It never binds to `0.0.0.0` and never makes outbound network requests.

3. **Data Layer** — SQLite for structured data (with FTS5 for keyword search), FAISS for vector similarity search, and the local filesystem for original document storage and model files.

---

## Technical Deep Dive

### Backend (Python / FastAPI)

The backend is a FastAPI application structured as a modular Python package under `backend/`.

**Server configuration:**
- Binds to `127.0.0.1:8741` (loopback only — unreachable from the network)
- CORS restricted to `localhost`, `127.0.0.1`, and `tauri://localhost` origins
- Async lifespan manager handles startup/shutdown sequences
- Uvicorn ASGI server in single-worker mode

**Startup sequence:**
1. Ensure data directories exist (`~/.counselos/data/` with subdirs for originals, extracted text, exports, backups)
2. Initialize SQLite database and create FTS5 virtual tables
3. Generate a per-session authentication token (48-byte `secrets.token_urlsafe`)
4. Load the embedding model (sentence-transformers singleton)
5. Load or create the FAISS vector index
6. Optionally load the LLM (llama-cpp-python) if a GGUF file is configured
7. Initialize the QA service with retriever and LLM references

**Key dependencies and versions:**
| Package | Version | Purpose |
|---|---|---|
| fastapi | ≥0.115 | HTTP framework with automatic OpenAPI docs |
| uvicorn | ≥0.32 | ASGI server |
| sqlalchemy | ≥2.0.36 | ORM with 2.0-style declarative mappings |
| alembic | ≥1.14 | Database migrations |
| pydantic | ≥2.10 | Request/response validation |
| pymupdf (fitz) | ≥1.25 | PDF text extraction |
| python-docx | ≥1.1.2 | DOCX reading and report generation |
| pytesseract | ≥0.3.13 | OCR bridge to Tesseract |
| Pillow | ≥11 | Image processing for OCR |
| numpy | ≥1.26 | Numerical operations |
| cryptography | ≥44 | Fernet encryption for backups |
| python-jose | ≥3.3 | Token handling |
| aiofiles | ≥24.1 | Async file I/O |
| llama-cpp-python | ≥0.3.2 | Local LLM inference (optional) |
| sentence-transformers | ≥3.3 | Text embeddings (optional but recommended) |
| faiss-cpu | ≥1.9 | Vector similarity search (optional but recommended) |

### Frontend (React / TypeScript / Tailwind)

The frontend is a single-page React application under `apps/desktop/`.

**Stack:**
| Technology | Version | Purpose |
|---|---|---|
| React | 18.3.1 | UI component library |
| TypeScript | 5.6.3 | Static type checking |
| Vite | 6.0.0 | Build tool and dev server (port 1420) |
| Tailwind CSS | 4.0.0 | Utility-first CSS with `@theme` configuration |
| React Router | 6.28.0 | Client-side routing with nested layouts |
| TanStack React Query | 5.62.0 | Server state management, caching, and mutations |
| date-fns | 4.1.0 | Date formatting and manipulation |
| clsx | 2.1.1 | Conditional CSS class merging |

**Component architecture:**

The app uses a fixed shell layout with a 260px sidebar and 56px header. Navigation is context-dependent — the sidebar shows global navigation (all matters, settings) when no matter is active, and switches to matter-scoped navigation (documents, search, chronology, compare, findings, export) when a matter is selected.

**Routing structure:**
```
/                           → MatterList (dashboard)
/settings                   → SettingsView
/matters/:matterId          → MatterOverview
/matters/:matterId/documents → DocumentList
/matters/:matterId/search   → SearchView
/matters/:matterId/chronology → ChronologyView
/matters/:matterId/compare  → ComparisonView
/matters/:matterId/findings → FindingsReview
/matters/:matterId/export   → ExportView
```

**API communication layer:**

The `lib/api.ts` module provides 37 typed API functions that communicate with the backend over HTTP. All requests include a session token via `Authorization: Bearer <token>` header. The token is obtained during startup via a handshake: the frontend polls `GET /api/system/session-token` (up to 30 retries, 1 second apart) until the backend is ready.

TanStack React Query wraps these API functions in 22 custom hooks (`useApi.ts`), providing:
- Automatic caching with 30-second stale time
- Single retry on failure
- Cache invalidation on mutations (e.g., uploading a document invalidates the documents query)
- No refetch on window focus (appropriate for a desktop app)

**TypeScript types:**

26 interfaces in `types/index.ts` mirror the backend's Pydantic schemas: `Matter`, `Document`, `DocumentPage`, `Chunk`, `Claim`, `Entity`, `TimelineEvent`, `Finding`, `SearchResult`, `Citation`, `DiscrepancyResult`, and their associated request/response types.

### Desktop Shell (Tauri 2)

Tauri 2 provides the native desktop wrapper. Unlike Electron, Tauri uses the OS's native webview (WebView2 on Windows, WebKit on macOS/Linux) instead of bundling Chromium, resulting in significantly smaller binary sizes.

**Configuration (`tauri.conf.json`):**
- Product name: "CounselOS"
- Bundle identifier: `com.counselos.app`
- Default window: 1400×900, minimum 1024×700, resizable
- Title: "CounselOS - Private Legal Evidence Analysis"

**Content Security Policy:**
```
default-src 'self';
connect-src 'self' http://127.0.0.1:8741;
style-src 'self' 'unsafe-inline';
img-src 'self' data: blob:;
```
This CSP ensures the frontend can only make HTTP requests to the local backend — no external network calls are possible from the webview.

**Filesystem sandboxing:**
- Scoped to `$APPDATA/**` and `$HOME/.counselos/**` only
- No access to arbitrary filesystem paths

**Tauri plugins:**
- `tauri-plugin-shell` — open URLs in the system browser
- `tauri-plugin-dialog` — native file picker dialogs
- `tauri-plugin-fs` — scoped filesystem access

**Rust side (`lib.rs`):**
The Rust code is minimal — it registers the three plugins and launches the Tauri application. All business logic lives in the Python backend; Tauri serves purely as a secure container.

### AI & ML Stack

CounselOS uses two AI models, both running locally:

#### Embedding Model — all-MiniLM-L6-v2

| Property | Value |
|---|---|
| Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Dimensions | 384 |
| Max tokens | 512 |
| Size | ~90 MB |
| Runtime | sentence-transformers (PyTorch) |
| License | Apache 2.0 |

The embedding model converts text chunks into 384-dimensional vectors for semantic search. It runs as a singleton service, loading once at startup. Embeddings are L2-normalized before storage, enabling cosine similarity via inner product.

#### LLM — GGUF Quantized Model

| Property | Primary | Fallback |
|---|---|---|
| Class | 8B parameters | 4B parameters |
| Quantization | Q4_K_M | Q4_K_M |
| Context length | 4096 tokens | 2048 tokens |
| Size | ~4.5 GB | ~2.5 GB |
| Runtime | llama-cpp-python | llama-cpp-python |

The LLM handles question answering, claim extraction, chronology construction, and document comparison. It runs via llama-cpp-python, which provides Python bindings to llama.cpp for efficient CPU inference (with optional GPU offloading via CUDA).

**Configuration (`backend/config.py`):**
- `llm_model_path` — path to the GGUF file
- `llm_context_length` — 4096 tokens (default)
- `llm_max_tokens` — 2048 tokens max generation
- `llm_temperature` — 0.1 (low for factual accuracy)
- `llm_threads` — 4 (CPU threads for inference)
- `llm_gpu_layers` — 0 (set higher if GPU available)

**Model manifest (`models/manifest.json`):**
Each model entry includes a SHA-256 hash for integrity verification. On startup, the backend can verify the model file hasn't been tampered with by comparing its hash against the manifest.

**Recommended models (compatible GGUF files):**
- Llama 3.1 8B Instruct Q4_K_M — best balance of quality and speed
- Mistral 7B Instruct v0.3 Q4_K_M — strong alternative
- Phi-3 Mini 4B Q4_K_M — for systems with limited RAM (8 GB)

### Database Layer

**Engine:** SQLite with WAL (Write-Ahead Logging) journal mode for concurrent read/write performance.

**Pragmas:**
- `journal_mode = WAL` — allows readers and a writer to operate concurrently
- `foreign_keys = ON` — enforces referential integrity
- `busy_timeout = 5000` — waits up to 5 seconds for locked database

**ORM:** SQLAlchemy 2.0+ with declarative base and mapped columns.

**Schema (13 tables):**

```
matters
  ├── documents
  │     ├── document_pages
  │     └── chunks (+ chunks_fts FTS5 virtual table)
  ├── entities
  │     └── entity_aliases
  ├── claims
  │     └── claim_sources → chunks
  ├── events (timeline)
  │     └── event_sources → chunks
  ├── findings
  │     └── finding_sources → chunks
  └── analysis_runs
       └── review_events

audit_events (global)
```

**Key design decisions:**
- **UUID primary keys** — 32-character hex strings (UUID4) for all entities, preventing ID prediction
- **Matter-scoped isolation** — every query joins through the `matters` table, enforcing SEC-008 (no cross-matter data leakage)
- **Cascading deletes** — deleting a matter removes all its documents, chunks, claims, events, findings, and analysis runs
- **Content hashing** — SHA-256 hashes on documents (for deduplication) and chunks (for integrity verification)
- **FTS5 virtual table** — `chunks_fts` mirrors the `chunks` table content for full-text search with BM25 ranking

**Migrations:** Alembic with a single migration head. The initial migration creates all 13 tables and indexes.

### Search & Retrieval

CounselOS implements a hybrid search architecture combining keyword and semantic search, fused via Reciprocal Rank Fusion (RRF).

#### Keyword Search (SQLite FTS5)

- Uses SQLite's built-in FTS5 extension with BM25 ranking
- Queries are tokenized and quoted individually for safety (special characters stripped)
- Returns ranked results with text snippets showing match context
- Retrieves up to 2,000 candidates per search

**When it excels:** Exact term matching, case numbers, statutory section references, proper nouns, exhibit numbers.

#### Semantic Search (FAISS)

- Uses `IndexFlatIP` (flat inner product index) on L2-normalized vectors
- Equivalent to cosine similarity search
- Embeddings generated by all-MiniLM-L6-v2 (384 dimensions)
- Index persisted to disk as `index.faiss` + `mapping.json`
- Retrieves up to 2,000 candidates per search

**When it excels:** Conceptual similarity, paraphrased content, questions about themes or topics, finding relevant passages when exact terminology is unknown.

**Limitation:** `IndexFlatIP` performs brute-force search (O(n) per query). This is acceptable for the expected scale (tens of thousands of chunks per matter) but would need to be replaced with `IndexIVFFlat` or `IndexHNSW` for millions of chunks.

#### Hybrid Fusion (Reciprocal Rank Fusion)

When search mode is set to "hybrid" (the default), both keyword and semantic search run in parallel. Results are fused using RRF with k=60:

```
RRF_score(doc) = Σ 1 / (k + rank_in_system)
```

Each result is tagged with its source: `"keyword"`, `"semantic"`, or `"both"` (appeared in both result sets). This gives users transparency into why a result was surfaced.

### Document Ingestion Pipeline

The ingestion pipeline processes uploaded files through a multi-stage process:

```
Upload → Validate → Store Original → Extract Pages → Chunk → Embed → Index
```

#### Stage 1: Validation
- Magic-byte detection (PDF: `%PDF`, DOCX: `PK` with `word/` directory)
- SHA-256 hash computation for deduplication
- File size check (max 500 MB, configurable)
- Duplicate detection against existing documents in the same matter

#### Stage 2: Text Extraction

**PDF files (PyMuPDF + Tesseract):**
- Each page is classified as digital, scanned, or mixed based on text density (threshold: 50 characters)
- Digital pages: text extracted directly via PyMuPDF (`fitz`)
- Scanned pages: rendered at 300 DPI, processed through Tesseract OCR
- Mixed pages: digital text extracted first, OCR applied if text density is low
- OCR confidence scores recorded per page for quality tracking
- Supports `eng+hin` (English + Hindi) language packs

**DOCX files (python-docx):**
- Paragraphs extracted sequentially
- Grouped into logical "pages" of ~3,000 characters each (since DOCX has no inherent page boundaries)

#### Stage 3: Chunking
- Sentence-boundary-aware splitting using regex on `.!?।` (includes the Hindi Devanagari danda `।`)
- Default chunk size: 512 characters with 64-character overlap
- Each chunk receives a SHA-256 content hash for integrity verification
- Chunks maintain references to their source document and page range

#### Stage 4: Embedding & Indexing
- Each chunk is embedded via all-MiniLM-L6-v2
- Vectors added to the FAISS index with a mapping to chunk IDs
- FTS5 virtual table updated for keyword search

**Document statuses:** `uploading` → `processing` → `indexed` (success) or `failed` (error)

### Workflow Engine

CounselOS provides three analytical workflows, all powered by the local LLM:

#### Claim Extraction

Processes document chunks in batches of 5, extracting structured claims and entities.

**Claim types:**
- `factual_assertion` — statements of fact ("The accused was present at the scene")
- `temporal_claim` — date/time assertions ("The incident occurred on 15 March 2024")
- `financial_claim` — monetary assertions ("The total damages amount to ₹15,00,000")
- `attribution` — statements attributed to a person ("The witness stated that...")
- `legal_assertion` — legal conclusions ("This constitutes a violation of Section 420 IPC")

**Entity types:** person, organization, location, amount, date, other. Entities are de-duplicated by type and normalized label.

#### Chronology Construction

Takes extracted claims and builds a timeline via the LLM.

**Date precision levels:**
| Level | Example | Sort behavior |
|---|---|---|
| `exact` | 2024-03-15 | Sorted by date |
| `approximate` | March 2024 | Sorted by approximate date |
| `range` | 2024-01 to 2024-03 | Sorted by range start |
| `inferred` | "before the arrest" | Sorted by inferred date |
| `unknown` | No date determinable | Sorted to end (9999-99-99) |

Each timeline event links back to its source claims and chunks, maintaining full provenance.

#### Document Comparison

Compares claims between two documents to identify discrepancies.

**Finding types:**
| Type | Description | Severity |
|---|---|---|
| `contradiction` | Direct factual conflict between documents | High |
| `date_discrepancy` | Different dates for the same event | High |
| `amount_discrepancy` | Different figures for the same amount | High |
| `attribution_difference` | Same statement attributed to different people | Medium |
| `omission` | Significant fact present in one document but absent in the other | Medium |
| `ambiguity` | Vague or unclear claims that could be interpreted differently | Low |
| `corroboration` | Claims that support each other across documents | Low |

All findings link to source chunks from both documents. Findings with severity "high" automatically receive `pending` review status.

### Export System

The export module generates DOCX reports using python-docx.

**Report sections (configurable):**
1. **Metadata table** — matter title, reference, jurisdiction, generation date
2. **AI disclaimer** — red italic caveat: "This report contains AI-generated analysis. All findings are provisional and must be verified by qualified legal counsel."
3. **Documents analyzed** — list of source documents with page counts and processing status
4. **Findings** — each finding with type badge, severity, status (color-coded), summary, and source references
5. **Chronology** — tabular timeline with date, precision, event description, and sources
6. **Extracted claims** — claims grouped by type with source citations

**Export options:**
- Include/exclude individual sections (findings, chronology, claims, sources, review status)
- Filter by finding statuses (e.g., only accepted findings)
- Filter by specific document IDs
- Chronology-only DOCX export

### Security Architecture

Security is implemented across multiple layers:

#### Network Isolation (SEC-001, SEC-002)
- Backend binds exclusively to `127.0.0.1:8741` — unreachable from the network
- CORS allowlist: only `localhost`, `127.0.0.1`, and `tauri://localhost`
- Tauri CSP: `connect-src 'self' http://127.0.0.1:8741` — frontend cannot make any external requests
- No outbound HTTP calls from the backend — all AI inference runs locally

#### Session Authentication
- Per-session token generated on startup (48-byte `secrets.token_urlsafe`)
- Token written to `~/.counselos/data/session.token` (filesystem-based handshake)
- All API endpoints (except `/api/system/health`) require `Authorization: Bearer <token>`
- Session token endpoint (`/api/system/session-token`) restricted to loopback IP addresses
- Origin header validated against the allowlist

#### Matter Isolation (SEC-008)
- Every API query is scoped by `matter_id` via URL path parameters
- Database queries always join through the `matters` table
- Foreign key constraints prevent cross-matter data references
- Cascading deletes ensure complete matter removal

#### Audit Logging
- 15 event types tracked: matter CRUD, document lifecycle, search, analysis, export, backup
- Sensitive key filtering: automatically strips `password`, `secret`, `token`, `key`, `credential`, `ssn`, `aadhaar`, `pan_number` from logged data
- Audit log accessible via `/api/system/audit-log`

#### Encrypted Backups
- PBKDF2-HMAC-SHA256 with 600,000 iterations for key derivation
- Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256)
- Workflow: ZIP archive → encrypt with user-provided password → delete plaintext ZIP
- Per-matter or full database backup support
- File integrity verification via SHA-256 hash comparison

#### Document Integrity
- SHA-256 hash computed on upload for every document
- Content hash computed for every text chunk
- Duplicate detection prevents re-ingesting the same file
- Model manifest includes SHA-256 hashes for integrity verification of AI model files

---

## Design System

CounselOS uses a custom design system inspired by Material Design 3, tailored for the legal domain.

### Philosophy

The visual language projects **judicial gravitas with modern information utility**:
- Warm stone neutrals (not sterile blue-grey) referencing physical legal bond paper
- Authoritative indigo accents for interactive elements
- Monospace typography for legal citations and case identifiers
- Compact density optimized for information-heavy legal workflows
- Low-elevation, flat design with tactile micro-shadows

### Color Palette (MD3 Tonal)

| Token | Hex | Usage |
|---|---|---|
| `surface` | `#FFF8F5` | Page background (warm stone) |
| `surface-container-lowest` | `#FFFFFF` | Cards, panels, reading surfaces |
| `surface-container-low` | `#FAF2EE` | Sidebar, inspector panels |
| `surface-container` | `#F4ECE8` | Active matter selector, badges |
| `primary` | `#3525CD` | Primary actions, links |
| `primary-container` | `#4F46E5` | Active navigation, selected states |
| `tertiary` | `#005424` | Success, verified, admitted evidence |
| `error` | `#BA1A1A` | Contradictions, rejected, destructive |
| `secondary` | `#1D4ED8` | Case law cross-references |

### Typography (Tri-Font Hierarchy)

| Font | Usage | Sizes |
|---|---|---|
| **Source Serif 4** | Case titles, headings, judicial text | 32px (display), 26px (headline-lg), 22px (headline-md), 18px (headline-sm) |
| **Inter** | UI chrome, body text, labels, inputs | 16px (title), 15px (body-lg), 14px (body-md), 13px (body-sm), 12px (label-md), 11px (label-sm) |
| **JetBrains Mono** | Case numbers, citations, hashes, exhibit IDs | 13px (code-md), 11px (code-sm) |

### Spacing

4px baseline grid: `space-xs` (4px), `space-sm` (8px), `space-md` (12px), `space-lg` (16px), `space-xl` (24px).

### Border Radius

Compact and professional: `sm` (2px), default (4px), `md` (6px), `lg` (8px), `xl` (12px). No large rounded corners — the design conveys administrative firmness.

### Icons

Material Symbols Outlined (variable font, weight 400, optical size 24). Replaces lucide-react for consistency with the MD3 tonal design language.

---

## API Reference

All routes are prefixed with `/api/`. The backend serves OpenAPI documentation at `http://127.0.0.1:8741/docs` when running.

### Matters
| Method | Path | Description |
|---|---|---|
| GET | `/api/matters/` | List all matters |
| POST | `/api/matters/` | Create a matter |
| GET | `/api/matters/{id}` | Get matter details |
| PUT | `/api/matters/{id}` | Update matter |
| POST | `/api/matters/{id}/archive` | Archive matter |
| DELETE | `/api/matters/{id}` | Delete matter and all data |

### Documents
| Method | Path | Description |
|---|---|---|
| GET | `/api/matters/{id}/documents/` | List documents |
| POST | `/api/matters/{id}/documents/` | Upload document (multipart) |
| GET | `/api/matters/{id}/documents/{doc_id}` | Get document details |
| DELETE | `/api/matters/{id}/documents/{doc_id}` | Delete document |
| GET | `/api/matters/{id}/documents/{doc_id}/pages` | Get extracted pages |
| GET | `/api/matters/{id}/documents/{doc_id}/chunks` | Get text chunks |

### Search & QA
| Method | Path | Description |
|---|---|---|
| GET | `/api/matters/{id}/search` | Hybrid search (query, mode, limit) |
| POST | `/api/matters/{id}/ask` | Ask a question (RAG) |

### Analysis
| Method | Path | Description |
|---|---|---|
| POST | `/api/matters/{id}/extract` | Extract claims from documents |
| GET | `/api/matters/{id}/claims` | List extracted claims |
| PUT | `/api/matters/{id}/claims/{claim_id}` | Update claim review status |
| GET | `/api/matters/{id}/entities` | List extracted entities |
| POST | `/api/matters/{id}/chronology` | Build timeline from claims |
| GET | `/api/matters/{id}/chronology` | Get timeline events |
| POST | `/api/matters/{id}/compare` | Compare two documents |

### Findings
| Method | Path | Description |
|---|---|---|
| GET | `/api/matters/{id}/findings/` | List findings (filterable by status) |
| GET | `/api/matters/{id}/findings/{finding_id}` | Get finding details |
| POST | `/api/matters/{id}/findings/{finding_id}/review` | Review finding (accept/reject/needs_evidence/ambiguous) |

### Exports
| Method | Path | Description |
|---|---|---|
| POST | `/api/matters/{id}/exports/` | Generate DOCX report |
| GET | `/api/matters/{id}/exports/` | List generated exports |

### System
| Method | Path | Description |
|---|---|---|
| GET | `/api/system/health` | Health check (no auth required) |
| GET | `/api/system/session-token` | Get session token (loopback only) |
| GET | `/api/system/model-status` | LLM and embedding model status |
| GET | `/api/system/audit-log` | Query audit events |

---

## Project Structure

```
CounselOS/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, server startup
│   ├── config.py            # pydantic-settings configuration
│   ├── auth/
│   │   └── session.py       # Session token generation & validation
│   ├── db/
│   │   ├── engine.py        # SQLAlchemy engine, session factory, pragmas
│   │   ├── models.py        # ORM models (13 tables)
│   │   └── init_db.py       # Table creation, FTS5 setup
│   ├── api/
│   │   ├── matters.py       # Matter CRUD router
│   │   ├── documents.py     # Document upload/management router
│   │   ├── search.py        # Search & QA router
│   │   ├── analysis.py      # Claims, chronology, comparison router
│   │   ├── findings.py      # Findings review router
│   │   ├── exports.py       # Report generation router
│   │   └── system.py        # Health, model status, audit router
│   ├── ingestion/
│   │   ├── file_handler.py  # File validation, magic bytes, hashing
│   │   ├── pdf_parser.py    # PyMuPDF + Tesseract OCR extraction
│   │   ├── docx_parser.py   # python-docx extraction
│   │   └── chunker.py       # Sentence-boundary-aware text chunking
│   ├── retrieval/
│   │   ├── embeddings.py    # Sentence-transformers singleton service
│   │   ├── vector_store.py  # FAISS index (IndexFlatIP)
│   │   ├── keyword_search.py # SQLite FTS5 search
│   │   └── hybrid.py        # Reciprocal Rank Fusion
│   ├── inference/
│   │   ├── llm_service.py   # llama-cpp-python wrapper
│   │   ├── qa_service.py    # RAG question answering
│   │   └── prompts.py       # Prompt templates for all tasks
│   ├── workflows/
│   │   ├── claim_extractor.py   # Batch claim + entity extraction
│   │   ├── chronology_builder.py # Timeline construction
│   │   └── document_comparator.py # Cross-document comparison
│   ├── exports/
│   │   └── report_generator.py  # DOCX report builder
│   └── security/
│       ├── audit.py         # Audit event logging
│       └── encryption.py    # PBKDF2 + Fernet backup encryption
├── apps/
│   └── desktop/
│       ├── package.json     # Frontend dependencies
│       ├── vite.config.ts   # Vite build config
│       ├── tsconfig.json    # TypeScript config
│       ├── index.html       # HTML entry with font loading
│       ├── src/
│       │   ├── main.tsx     # React entry point, session handshake
│       │   ├── App.tsx      # Layout shell, routing, sidebar, header
│       │   ├── app.css      # Tailwind v4 @theme design tokens
│       │   ├── lib/
│       │   │   └── api.ts   # 37 typed API functions
│       │   ├── hooks/
│       │   │   └── useApi.ts # 22 React Query hooks
│       │   ├── types/
│       │   │   └── index.ts # 26 TypeScript interfaces
│       │   └── features/
│       │       ├── matters/
│       │       │   ├── MatterList.tsx
│       │       │   └── MatterOverview.tsx
│       │       ├── documents/
│       │       │   └── DocumentList.tsx
│       │       ├── search/
│       │       │   └── SearchView.tsx
│       │       ├── chronology/
│       │       │   └── ChronologyView.tsx
│       │       ├── comparison/
│       │       │   └── ComparisonView.tsx
│       │       ├── review/
│       │       │   └── FindingsReview.tsx
│       │       ├── export/
│       │       │   └── ExportView.tsx
│       │       └── settings/
│       │           └── SettingsView.tsx
│       └── src-tauri/
│           ├── tauri.conf.json  # Tauri window, CSP, plugins
│           ├── Cargo.toml       # Rust dependencies
│           └── src/
│               └── lib.rs       # Tauri plugin registration
├── models/
│   └── manifest.json        # Model specifications & hashes
├── migrations/
│   ├── alembic.ini
│   └── versions/            # Database migration scripts
├── tests/
│   ├── conftest.py          # Shared fixtures (in-memory SQLite)
│   ├── test_matters.py
│   ├── test_documents.py
│   ├── test_search.py
│   ├── test_security.py
│   └── ...
├── pyproject.toml           # Python package config & dependencies
├── CLAUDE.md                # AI assistant project instructions
└── README.md                # This file
```

---

## Quick Start (Standalone Executable)

The fastest way to use CounselOS. No Python, Node.js, or Rust installation required. Just download, configure, and run.

### What You Get

```
CounselOS/
├── CounselOS.exe              ← main application (double-click to run)
├── Start CounselOS.bat        ← launcher with console output (recommended)
├── .env.example               ← configuration template
└── _internal/                 ← bundled runtime (do not modify)
```

### Step 1: Download & Extract

Download the `CounselOS.zip` file and extract it to any location on your computer (e.g., `C:\CounselOS` or your Desktop). Do **not** extract it into a path that contains special characters or very deep nesting.

### Step 2: Install Tesseract OCR (Required for Scanned PDFs)

If you plan to upload scanned PDF documents (not digitally-created PDFs), install Tesseract OCR:

1. Download the Windows installer from [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. During installation, check the box for **Hindi** language pack under "Additional language data"
3. Install to the default path: `C:\Program Files\Tesseract-OCR\`
4. Note the installation path — you may need it in Step 3

If you only work with digitally-created PDFs (not scans/photos), you can skip this step.

### Step 3: Download an AI Model (Required for AI Features)

CounselOS uses a local AI model in GGUF format for question answering, claim extraction, chronology building, and document comparison. You need to download one:

**Recommended models (pick one):**

| Model | Size | RAM Required | Best For |
|---|---|---|---|
| Llama 3.1 8B Instruct Q4_K_M | ~4.5 GB | 16 GB RAM | Best quality — recommended for most users |
| Mistral 7B Instruct v0.3 Q4_K_M | ~4.1 GB | 16 GB RAM | Strong alternative, slightly faster |
| Phi-3 Mini 4B Q4_K_M | ~2.5 GB | 8 GB RAM | For systems with limited RAM |

**Where to download:**
- Visit [HuggingFace](https://huggingface.co) and search for the model name with "GGUF"
- Download the file ending in `Q4_K_M.gguf`
- Save it to a permanent location, e.g., `C:\CounselOS\models\` or `C:\Users\YourName\.counselos\models\`

**If you skip this step:** CounselOS will still work for document upload, text extraction, OCR, keyword search, and semantic search. Only the AI-powered features (Ask AI, Claim Extraction, Chronology, Document Comparison) will be unavailable.

### Step 4: Configure CounselOS

1. In the `CounselOS` folder, find `.env.example`
2. **Copy** it and rename the copy to `.env` (just `.env`, no other extension)
3. Open `.env` in Notepad and configure:

```ini
# REQUIRED — path to your downloaded GGUF model file
COUNSELOS_LLM_MODEL_PATH=C:\CounselOS\models\llama-3.1-8b-instruct-q4_k_m.gguf

# OPTIONAL — GPU acceleration (NVIDIA GPU only)
# Set to the number of model layers to offload to GPU
# 0 = CPU only (default), 35 = full offload for 8B models
COUNSELOS_LLM_GPU_LAYERS=0

# OPTIONAL — CPU threads for AI inference (default: 4)
# Set to the number of performance cores on your CPU
COUNSELOS_LLM_THREADS=4

# OPTIONAL — Tesseract OCR path (only if not in default location)
# Uncomment and edit if Tesseract is not at the default path
# COUNSELOS_TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

> **Important:** Use the full absolute path to the model file. Use backslashes (`\`) on Windows. Do not wrap the path in quotes.

### Step 5: Launch CounselOS

**Option A (Recommended):** Double-click `Start CounselOS.bat`
- A console window opens showing server startup progress
- Your default browser opens automatically to `http://127.0.0.1:8741`
- Keep the console window open while using CounselOS
- Press `Ctrl+C` in the console to stop the server when done

**Option B:** Double-click `CounselOS.exe` directly
- Same behavior, but the console window may close if an error occurs

### Step 6: Start Using CounselOS

Once the browser opens:

1. **Create a Matter** — click **+ New Matter** in the top-right. Enter the case title, reference number (e.g., `CS(OS) 1234/2024`), jurisdiction, and matter type.

2. **Upload Documents** — navigate to **Documents** in the sidebar. Drag and drop PDF or DOCX files, or click the upload button. Wait for processing to complete (status changes from "processing" to "indexed").

3. **Search Your Evidence** — go to **Search & Ask**:
   - **Keyword Search** — finds exact matches. Great for case numbers, names, dates, statutory sections.
   - **Ask AI** — pose natural language questions like "What date did the defendant sign the agreement?" and get cited answers with page references.

4. **Extract Claims** — from the **Compare** view, extract structured claims (factual, temporal, financial, legal) from your documents.

5. **Build Chronology** — go to **Chronology** and click **Build Chronology** to create an AI-generated timeline with source citations.

6. **Compare Documents** — select two documents in **Compare** to identify contradictions, date discrepancies, and corroborations.

7. **Review Findings** — all AI outputs start as "pending" in **Findings**. Accept, reject, or flag each finding.

8. **Export Report** — go to **Export** to generate a DOCX report with your reviewed findings, chronology, and source citations.

### Troubleshooting

| Problem | Solution |
|---|---|
| **Browser doesn't open** | Manually navigate to `http://127.0.0.1:8741` in any browser |
| **"Port 8741 is already in use"** | Another instance is already running. Check your taskbar/system tray, or restart your computer |
| **AI features show "unavailable"** | Check that `COUNSELOS_LLM_MODEL_PATH` in `.env` points to a valid `.gguf` file |
| **OCR not working on scanned PDFs** | Install Tesseract OCR (Step 2). If installed to a non-default path, set `COUNSELOS_TESSERACT_CMD` in `.env` |
| **Application crashes on startup** | Ensure you have enough free RAM (8 GB minimum, 16 GB recommended). Check the console window for error messages |
| **"Session token" error in browser** | The backend may still be starting up. Wait 10-15 seconds and refresh the page |
| **Slow AI responses** | Normal on CPU — an 8B model generates ~10-15 tokens/second. Set `COUNSELOS_LLM_GPU_LAYERS=35` if you have an NVIDIA GPU with 6+ GB VRAM |
| **Hindi OCR not working** | Ensure the Hindi language pack was installed with Tesseract. Set `COUNSELOS_OCR_LANGUAGE=eng+hin` in `.env` |

### Where Is My Data Stored?

All data is stored locally at `C:\Users\<YourName>\.counselos\data\`:

```
~/.counselos/data/
├── counselos.db          ← SQLite database (all matters, findings, etc.)
├── session.token         ← temporary auth token (regenerated each launch)
├── faiss_index/          ← vector search index
├── originals/            ← uploaded document files
├── extracted/            ← extracted text from documents
├── exports/              ← generated DOCX reports
└── backups/              ← encrypted backup archives
```

You can back up or move this entire folder. To start fresh, delete this folder and CounselOS will create a new one on next launch.

### Uninstalling

1. Close CounselOS (Ctrl+C in the console or close the window)
2. Delete the `CounselOS` folder
3. Optionally delete `C:\Users\<YourName>\.counselos\` to remove all stored data
4. Optionally uninstall Tesseract OCR from Windows Settings → Apps

---

## Installation & Setup (Development)

These instructions are for developers who want to modify, debug, or contribute to CounselOS.

### Prerequisites

1. **Python 3.11+** — [python.org](https://www.python.org/downloads/)
2. **Node.js 18+** — [nodejs.org](https://nodejs.org/)
3. **Rust toolchain** — [rustup.rs](https://rustup.rs/) (for Tauri compilation)
4. **Tesseract OCR** — required for scanned document processing
   - Windows: [UB Mannheim installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract tesseract-lang`
   - Linux: `sudo apt install tesseract-ocr tesseract-ocr-hin`

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd CounselOS

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install the backend with all dependencies
pip install -e ".[dev]"

# Install AI dependencies (optional but recommended)
pip install -e ".[ai]"

# (Optional) Download a GGUF model for AI features
# Place the .gguf file anywhere and set COUNSELOS_LLM_MODEL_PATH
# Example: ~/.counselos/models/llama-3.1-8b-instruct-q4_k_m.gguf

# Set environment variables (or create a .env file)
# COUNSELOS_LLM_MODEL_PATH=/path/to/your/model.gguf
# COUNSELOS_LLM_GPU_LAYERS=0  (set higher for GPU acceleration)

# Start the backend server
python -m backend.main
# Server starts on http://127.0.0.1:8741
```

### Frontend Setup

```bash
# Navigate to the desktop app
cd apps/desktop

# Install Node.js dependencies
npm install

# Start the Vite dev server
npm run dev
# Dev server starts on http://localhost:1420
```

### Running as a Desktop App (Tauri)

```bash
# From apps/desktop/
npm run tauri dev
# Compiles Rust shell and launches native window
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `COUNSELOS_DATA_DIR` | `~/.counselos/data` | Base directory for all data storage |
| `COUNSELOS_LLM_MODEL_PATH` | (none) | Path to GGUF model file |
| `COUNSELOS_LLM_CONTEXT_LENGTH` | `4096` | LLM context window size |
| `COUNSELOS_LLM_MAX_TOKENS` | `2048` | Max generation tokens |
| `COUNSELOS_LLM_TEMPERATURE` | `0.1` | Generation temperature (low = factual) |
| `COUNSELOS_LLM_THREADS` | `4` | CPU threads for LLM inference |
| `COUNSELOS_LLM_GPU_LAYERS` | `0` | Layers offloaded to GPU (0 = CPU only) |
| `COUNSELOS_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model name |
| `COUNSELOS_CHUNK_SIZE` | `512` | Text chunk size in characters |
| `COUNSELOS_CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `COUNSELOS_MAX_FILE_SIZE` | `524288000` | Max upload size in bytes (500 MB) |
| `COUNSELOS_MAX_CONTEXT_CHUNKS` | `15` | Max chunks in RAG context |
| `COUNSELOS_OCR_LANGUAGES` | `eng+hin` | Tesseract language packs |
| `COUNSELOS_OCR_QUALITY_THRESHOLD` | `60` | Minimum OCR confidence (%) |

---

## Usage Guide

### 1. Create a Matter

A "matter" is the top-level container for a legal case. Click **+ New Matter** in the header or sidebar. Fill in:
- **Title** — case name (e.g., "Singh v. Sharma")
- **Reference** — docket/case number (e.g., "CS(OS) 1234/2024")
- **Jurisdiction** — court (e.g., "Delhi High Court")
- **Matter Type** — civil, criminal, constitutional, etc.

### 2. Upload Documents

Navigate to **Documents** in the sidebar. Upload PDFs or DOCX files via drag-and-drop or the upload button. The pipeline will:
- Extract text from digital PDFs
- Run OCR on scanned pages (English + Hindi)
- Split text into searchable chunks
- Build the vector search index

Monitor the status column: `processing` → `indexed` (ready) or `failed` (check file format).

### 3. Search & Ask

Navigate to **Search & Ask**.

**Keyword Search:** finds exact matches using SQLite FTS5 with BM25 ranking. Best for case numbers, statutory sections, names.

**Ask AI:** poses a natural language question to the local LLM with RAG (Retrieval-Augmented Generation). The system retrieves the most relevant chunks, builds a prompt, and generates an answer with citations. Each citation links to a specific document and page range.

### 4. Extract Claims

Use the **Compare** view or trigger extraction from the overview. The system processes document chunks in batches, extracting structured claims (factual, temporal, financial, legal) and entities (persons, organizations, dates, amounts).

### 5. Build Chronology

Navigate to **Chronology** and click **Build Chronology**. The system takes extracted claims and constructs a timeline. Each event shows:
- Date with precision level (exact, approximate, inferred)
- Description
- Source document and page references
- Review status (pending, accepted, rejected)

Review each event and accept, reject, or flag for further evidence.

### 6. Compare Documents

Navigate to **Compare**, select two documents, extract claims from both, then click **Compare**. The system identifies contradictions, date discrepancies, amount discrepancies, omissions, and corroborations between the documents.

### 7. Review Findings

Navigate to **Findings**. All AI-generated findings start as "pending". Review each finding and take action:
- **Accept** — confirmed by human review
- **Reject** — incorrect or irrelevant
- **Needs Evidence** — requires additional source material
- **Ambiguous** — cannot determine accuracy

Only accepted findings appear in exported reports by default.

### 8. Export Reports

Navigate to **Export**. Select which sections to include (findings, chronology, claims) and generate a DOCX report. The report includes an AI disclaimer and links all findings to their source evidence.

---

## Trade-offs & Design Decisions

### Offline-Only vs. Cloud Hybrid

**Decision:** Fully offline. No cloud fallback, no optional API calls, no telemetry.

**Why:** Attorney-client privilege and legal professional privilege under the Indian Evidence Act (and its successor, the Bharatiya Sakshya Adhiniyam) require that case strategies and client communications remain confidential. Sending case data to external APIs — even encrypted — creates risk vectors that are unacceptable for practicing advocates. The security model is simpler when the answer to "does data leave the device?" is always "no."

**Trade-off:** The LLM runs on CPU (unless the user has a compatible GPU), which means inference is slower than cloud APIs. An 8B model on 4 CPU threads generates roughly 10-15 tokens/second vs. 50+ tokens/second from cloud endpoints. This is acceptable because legal analysis is not latency-sensitive — a lawyer can wait 30 seconds for a thorough, cited answer.

### SQLite vs. PostgreSQL

**Decision:** SQLite with WAL mode.

**Why:** Zero configuration, zero external dependencies, single-file database, built-in FTS5 for full-text search. Perfect for a single-user desktop application. WAL mode provides concurrent read/write without blocking.

**Trade-off:** No concurrent write scaling (single writer at a time), no built-in replication, and FTS5's ranking is less sophisticated than PostgreSQL's `ts_rank_cd`. These limitations don't matter for a single-user desktop app.

### FAISS IndexFlatIP vs. Approximate NN

**Decision:** Flat (brute-force) index with inner product on normalized vectors.

**Why:** Exact results, no training step, trivial to add/rebuild. For the expected scale (tens of thousands of chunks per matter), brute-force search completes in milliseconds.

**Trade-off:** O(n) search time per query. If a single matter grew to millions of chunks, this would become slow. The fix would be switching to `IndexIVFFlat` or `IndexHNSWFlat`, which requires a training step but provides sub-linear search.

**Note:** The current implementation rebuilds the entire index when chunks are removed (since `IndexFlatIP` doesn't support efficient removal). This is acceptable for the expected deletion frequency but would need a tombstone-based approach at larger scale.

### Sentence-Boundary Chunking vs. Semantic Chunking

**Decision:** Fixed-size chunks with sentence-boundary awareness and overlap.

**Why:** Predictable chunk sizes work well with the embedding model's 512-token context window. Sentence boundaries prevent splitting mid-thought. Overlap (64 characters) ensures context isn't lost at boundaries.

**Trade-off:** Some chunks may split a logical argument across two chunks. Semantic chunking (using paragraph structure or topic shifts) would produce more coherent chunks but requires either heuristics that are fragile across document types or an additional ML model.

### Local LLM (llama.cpp) vs. No AI

**Decision:** Optional local LLM via llama-cpp-python with GGUF quantized models.

**Why:** Q4_K_M quantization provides good quality at ~4.5 GB for an 8B model, runnable on consumer hardware. llama-cpp-python provides a mature Python API with support for structured (JSON) output, which is essential for claim extraction and chronology construction.

**Trade-off:** 8B models are less capable than larger cloud models (GPT-4, Claude) at nuanced legal reasoning. Mitigated by: (1) using low temperature (0.1) for factual tasks, (2) structured output with JSON validation and retry logic, (3) human review of all AI outputs, and (4) extensive prompt engineering with 6 system rules (cite sources, no fabrication, show both sides, express uncertainty, use exact quotes, include page references).

### Tauri 2 vs. Electron

**Decision:** Tauri 2 with native webview.

**Why:** Tauri produces binaries that are ~10-20x smaller than Electron (no bundled Chromium). It uses the OS's native webview (WebView2 on Windows, WebKit on macOS/Linux), which reduces memory footprint. The Rust backend provides strong CSP enforcement and filesystem sandboxing.

**Trade-off:** Less cross-platform rendering consistency (different webview engines on different OSes), smaller ecosystem of Tauri plugins vs. Electron, and requires a Rust toolchain for compilation. The rendering differences are minimal in practice since the app uses standard CSS and no platform-specific APIs.

### Session Token vs. Full Auth

**Decision:** Per-session random token with filesystem handshake.

**Why:** CounselOS is a single-user desktop application. There's no user registration, no multi-tenant access, and no remote access. The session token exists solely to prevent other local processes from accessing the backend API. It's generated fresh on every startup, stored on the filesystem, and read by the frontend via a loopback-restricted endpoint.

**Trade-off:** No persistent authentication, no user accounts, no role-based access control. These aren't needed for a single-user desktop tool. If CounselOS ever supported multiple users on a shared server, this would need to be replaced with proper JWT-based authentication.

### Human-in-the-Loop vs. Automated

**Decision:** All AI outputs require human review before they're considered authoritative.

**Why:** AI-generated legal analysis can be wrong — hallucinated citations, misinterpreted dates, false contradictions. In litigation, acting on incorrect analysis can have serious consequences. The review workflow (pending → accepted/rejected) ensures a lawyer has examined every finding before it influences case strategy or appears in a report.

**Trade-off:** More clicks for the lawyer. Every finding, timeline event, and comparison result needs explicit review. This is intentional — the friction is the feature.

---

## Configuration Reference

CounselOS uses pydantic-settings for configuration. All settings can be provided via:
1. Environment variables (prefixed with `COUNSELOS_`)
2. A `.env` file in the project root
3. Defaults in `backend/config.py`

See the [Environment Variables](#environment-variables) table in the Installation section for the complete list.

### Data Directory Structure

```
~/.counselos/
└── data/
    ├── counselos.db          # SQLite database
    ├── session.token         # Current session auth token
    ├── index.faiss           # FAISS vector index
    ├── mapping.json          # FAISS ID → chunk_id mapping
    ├── originals/            # Uploaded document files
    ├── extracted/            # Extracted text and page data
    ├── exports/              # Generated DOCX reports
    └── backups/              # Encrypted backup archives
```

---

## Building the Executable from Source

If you want to build the standalone `CounselOS.exe` yourself from the source code:

### Prerequisites

1. All development prerequisites installed (Python 3.11+, Node.js 18+)
2. Backend dependencies: `pip install -e ".[ai]"`
3. PyInstaller: `pip install pyinstaller`
4. Frontend built: `cd apps/desktop && npm install && npm run build`

### Build Process

```bash
# From the project root
cd CounselOS

# Step 1: Build the React frontend (produces apps/desktop/dist/)
cd apps/desktop
npm run build
cd ../..

# Step 2: Run the build script
python build_exe.py
```

This takes 5-15 minutes depending on your system. PyInstaller analyzes all Python imports, copies binary dependencies, bundles the frontend, and creates the executable.

### Build Output

```
dist/CounselOS/
├── CounselOS.exe              (124 MB — main executable)
├── Start CounselOS.bat        (launcher with console output)
├── .env.example               (configuration template for end users)
└── _internal/                 (~877 MB — Python runtime + all libraries)
    ├── frontend_dist/         (built React UI served by FastAPI)
    ├── torch/                 (PyTorch for sentence-transformers)
    ├── sentence_transformers/ (embedding model runtime)
    └── ...                    (FastAPI, SQLAlchemy, PyMuPDF, FAISS, etc.)
```

**Total distribution size:** ~1 GB (primarily PyTorch + sentence-transformers)

### Build Internals

The build uses three files:

| File | Purpose |
|---|---|
| `launcher.py` | Entry point — starts FastAPI, serves the built frontend as static files, opens the browser |
| `counselos.spec` | PyInstaller spec — defines hidden imports, data files to bundle, and output structure |
| `build_exe.py` | Build orchestrator — checks prerequisites, runs PyInstaller, creates `.env.example` and `.bat` launcher |

**How it works:**
1. `launcher.py` detects whether it's running from source or frozen (PyInstaller bundles set `sys.frozen = True`)
2. In frozen mode, it finds the frontend at `sys._MEIPASS/frontend_dist/`
3. It mounts the frontend as static files on the FastAPI app and adds a catch-all route for React Router
4. It starts Uvicorn on `127.0.0.1:8741` and opens the default browser
5. The `.env` file (if present alongside the exe) is read by pydantic-settings automatically

### Customizing the Build

To reduce the distribution size:
- Remove `sentence_transformers` and `torch` from `counselos.spec` hidden imports if you don't need semantic search (~700 MB saved)
- Remove `llama_cpp` if you don't need AI features (~50 MB saved)
- Use UPX compression (already enabled in the spec, but install UPX separately: `choco install upx` or download from [upx.github.io](https://upx.github.io/))

To add an application icon:
- Place a `.ico` file in the project root
- Update the `icon=None` line in `counselos.spec` to `icon='your-icon.ico'`

---

## Testing

```bash
# Run the full test suite
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_matters.py

# Run tests matching a pattern
pytest tests/ -k "search"
```

Tests use an in-memory SQLite database (`:memory:`) with fixtures defined in `tests/conftest.py`. No external services or model files are required for testing.

---

## License

Copyright (c) 2024 CounselOS. All rights reserved.
