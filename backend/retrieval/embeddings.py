import logging
import threading

import numpy as np

from backend.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._model = None
                    cls._instance._load_error = None
        return cls._instance

    def _load_model(self) -> None:
        if self._model is not None or self._load_error is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                settings.embedding_model_name,
                device="cpu",
            )
            logger.info("Loaded embedding model: %s", settings.embedding_model_name)
        except Exception as e:
            self._load_error = str(e)
            logger.error("Failed to load embedding model: %s", e)

    @property
    def is_available(self) -> bool:
        self._load_model()
        return self._model is not None

    def encode(self, texts: list[str]) -> np.ndarray:
        self._load_model()
        if self._model is None:
            raise RuntimeError(f"Embedding model unavailable: {self._load_error}")
        if not texts:
            return np.empty((0, settings.embedding_dimension), dtype=np.float32)
        embeddings = self._model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        result = self.encode([query])
        return result[0]
