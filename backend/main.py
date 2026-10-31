import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth.session_auth import initialize_session
from backend.config import settings
from backend.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("CounselOS %s starting up", settings.app_version)

    settings.ensure_directories()
    init_db()

    token = initialize_session()
    logger.info("Session token generated (use for API auth)")
    logger.info("Session token: %s", token)

    token_path = settings.data_dir / "session.token"
    token_path.write_text(token)
    logger.info("Session token written to %s", token_path)

    app.state.llm_service = None
    app.state.embedding_service = None
    app.state.vector_store = None
    app.state.retriever = None
    app.state.qa_service = None

    try:
        from backend.retrieval.embeddings import EmbeddingService
        app.state.embedding_service = EmbeddingService()
        logger.info("Embedding service initialized")
    except Exception as e:
        logger.warning("Failed to initialize embedding service: %s", e)

    try:
        from backend.retrieval.vector_store import VectorStore
        app.state.vector_store = VectorStore(dimension=settings.embedding_dimension)

        index_path = settings.data_dir / "faiss_index"
        if index_path.exists():
            app.state.vector_store.load(index_path)
            logger.info("Loaded FAISS index with %d vectors", app.state.vector_store.count)
    except Exception as e:
        logger.warning("Failed to initialize vector store: %s", e)

    if app.state.embedding_service and app.state.vector_store:
        app.state.retriever = True
        logger.info("Retrieval services available (HybridRetriever created per-request)")

    if settings.llm_model_path and Path(settings.llm_model_path).exists():
        try:
            from backend.inference.llm_service import LLMService
            app.state.llm_service = LLMService()
            logger.info("LLM service initialized")

            if app.state.embedding_service and app.state.vector_store:
                from backend.inference.qa_service import QAService
                app.state.qa_service = QAService(
                    app.state.llm_service,
                    app.state.embedding_service,
                    app.state.vector_store,
                )
                logger.info("QA service initialized")
        except Exception as e:
            logger.warning("Failed to initialize LLM: %s", e)
    else:
        logger.info("No LLM model path configured — AI features will be unavailable")

    logger.info("CounselOS startup complete")
    yield

    if app.state.vector_store:
        try:
            index_path = settings.data_dir / "faiss_index"
            app.state.vector_store.save(index_path)
            logger.info("FAISS index saved")
        except Exception as e:
            logger.warning("Failed to save FAISS index: %s", e)

    logger.info("CounselOS shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="CounselOS API",
        description="Offline-first legal evidence-analysis backend",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://127.0.0.1",
            "https://localhost",
            "https://127.0.0.1",
            "tauri://localhost",
            "http://tauri.localhost",
            "https://tauri.localhost",
            f"http://localhost:{settings.api_port}",
            f"http://127.0.0.1:{settings.api_port}",
            "http://localhost:1420",
            "http://127.0.0.1:1420",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from backend.api.analysis import router as analysis_router
    from backend.api.documents import router as documents_router
    from backend.api.exports import router as exports_router
    from backend.api.findings import router as findings_router
    from backend.api.matters import router as matters_router
    from backend.api.search import router as search_router
    from backend.api.system import router as system_router

    app.include_router(matters_router)
    app.include_router(documents_router)
    app.include_router(search_router)
    app.include_router(analysis_router)
    app.include_router(findings_router)
    app.include_router(exports_router)
    app.include_router(system_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
