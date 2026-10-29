# CounselOS

Offline-first legal evidence-analysis desktop app for Indian litigation lawyers.

## Architecture

- **Backend**: Python 3.11+ / FastAPI, bound to `127.0.0.1:8741`
- **Frontend**: React 18 + TypeScript + Tailwind v4, Vite dev server on port 1420
- **Desktop**: Tauri 2.x shell wrapping the frontend
- **Database**: SQLite + FTS5 (keyword search), FAISS (vector search)
- **AI**: llama-cpp-python (local LLM), sentence-transformers (embeddings), Tesseract OCR

## Key Constraints

- **No external API calls** — all processing runs locally (SEC-001, SEC-002)
- **Matter-scoped isolation** — every query must be scoped by `matter_id` (SEC-008)
- **Evidence provenance** — every AI-generated claim/finding links to source chunks with page numbers
- **Human review** — AI outputs start as "pending", require accept/reject before use

## Development

```bash
# Backend
pip install -e ".[dev]"
python -m backend.main

# Frontend
cd apps/desktop
npm install
npm run dev

# Tests
pytest tests/
```

## Project Structure

- `backend/` — FastAPI app (config, db, api, ingestion, retrieval, inference, workflows, exports, security)
- `apps/desktop/` — Tauri + React frontend
- `tests/` — Unit, integration, and security tests
- `models/` — Model manifest
- `migrations/` — Alembic database migrations

## API Routes

All routes prefixed with `/api/`. Backend routers:
- `/api/matters/` — Matter CRUD
- `/api/matters/{id}/documents/` — Document upload/management
- `/api/matters/{id}/search`, `/ask` — Hybrid search & QA
- `/api/matters/{id}/extract`, `/claims`, `/entities` — Claim extraction
- `/api/matters/{id}/chronology` — Timeline construction
- `/api/matters/{id}/compare` — Cross-document comparison
- `/api/matters/{id}/findings/` — Finding review
- `/api/matters/{id}/exports/` — Report generation
- `/api/system/` — Health, model status, audit log

## Testing

Run `pytest tests/` from root. Tests use in-memory SQLite with fixtures in `tests/conftest.py`.
