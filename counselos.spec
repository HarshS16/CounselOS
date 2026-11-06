# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for CounselOS.

Produces a folder-based distribution (not a single file) because:
- The AI models are multi-GB and must be user-supplied
- sentence-transformers downloads on first run
- Single-file exe would be 500MB+ and slow to start

Usage:
    pip install pyinstaller
    pyinstaller counselos.spec

Output: dist/CounselOS/CounselOS.exe
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Paths
ROOT = os.path.abspath(".")
BACKEND = os.path.join(ROOT, "backend")
FRONTEND_DIST = os.path.join(ROOT, "apps", "desktop", "dist")

# Collect backend package data
backend_datas = [
    (BACKEND, "backend"),
]

# Include the built frontend if it exists
datas = []
if os.path.isdir(FRONTEND_DIST):
    datas.append((FRONTEND_DIST, "frontend_dist"))
else:
    print("WARNING: Frontend dist not found at", FRONTEND_DIST)
    print("Run 'cd apps/desktop && npm run build' first")

# Include models manifest if present
models_manifest = os.path.join(ROOT, "models", "manifest.json")
if os.path.isfile(models_manifest):
    datas.append((os.path.join(ROOT, "models"), "models"))

# Include migrations if present
migrations_dir = os.path.join(ROOT, "migrations")
if os.path.isdir(migrations_dir):
    datas.append((migrations_dir, "migrations"))

# Include .env if present (user config)
env_file = os.path.join(ROOT, ".env")
if os.path.isfile(env_file):
    datas.append((env_file, "."))

# Hidden imports that PyInstaller misses
hidden_imports = [
    # FastAPI / Uvicorn
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "fastapi",
    "fastapi.staticfiles",
    "fastapi.responses",
    "starlette.responses",
    "starlette.routing",
    "starlette.middleware",
    "starlette.middleware.cors",
    "multipart",
    "multipart.multipart",
    # SQLAlchemy
    "sqlalchemy",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.ext.declarative",
    # Pydantic
    "pydantic",
    "pydantic_settings",
    "pydantic.deprecated.decorator",
    # Backend modules
    "backend",
    "backend.main",
    "backend.config",
    "backend.db",
    "backend.db.session",
    "backend.db.models",
    "backend.auth",
    "backend.auth.session_auth",
    "backend.api",
    "backend.api.matters",
    "backend.api.documents",
    "backend.api.search",
    "backend.api.analysis",
    "backend.api.findings",
    "backend.api.exports",
    "backend.api.system",
    "backend.ingestion",
    "backend.ingestion.file_handler",
    "backend.ingestion.pdf_parser",
    "backend.ingestion.docx_parser",
    "backend.ingestion.chunker",
    "backend.retrieval",
    "backend.retrieval.embeddings",
    "backend.retrieval.vector_store",
    "backend.retrieval.keyword_search",
    "backend.retrieval.hybrid",
    "backend.inference",
    "backend.inference.llm_service",
    "backend.inference.qa_service",
    "backend.inference.prompts",
    "backend.workflows",
    "backend.workflows.claim_extractor",
    "backend.workflows.chronology_builder",
    "backend.workflows.document_comparator",
    "backend.exports",
    "backend.exports.report_generator",
    "backend.security",
    "backend.security.audit",
    "backend.security.encryption",
    # Document processing
    "fitz",
    "pymupdf",
    "docx",
    "PIL",
    "PIL.Image",
    "pytesseract",
    "numpy",
    "aiofiles",
    "aiofiles.os",
    # Crypto
    "cryptography",
    "cryptography.fernet",
    "cryptography.hazmat.primitives.kdf.pbkdf2",
    "jose",
    "passlib",
    "passlib.hash",
    # AI (optional — imported at runtime with try/except)
    "sentence_transformers",
    "torch",
    "transformers",
    "tokenizers",
    "huggingface_hub",
    "llama_cpp",
    "faiss",
    # httpx
    "httpx",
    "httpcore",
    "h11",
    "anyio",
    "sniffio",
    "certifi",
]

# Exclude large packages that are imported at runtime and may not be installed
excludes = []

a = Analysis(
    ["launcher.py"],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CounselOS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CounselOS",
)
