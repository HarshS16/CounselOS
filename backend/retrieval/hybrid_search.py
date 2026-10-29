import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from backend.db.models import Chunk, Document
from backend.retrieval.embeddings import EmbeddingService
from backend.retrieval.keyword_search import (
    index_chunk_fts,
    keyword_search,
    remove_document_fts,
)
from backend.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)

RRF_K = 60


@dataclass
class RetrievalResult:
    chunk_id: str
    document_id: str
    text: str
    page_start: int
    page_end: int
    score: float
    source: str = field(default="keyword")


class HybridRetriever:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        db: Session,
    ) -> None:
        self._embeddings = embedding_service
        self._vector_store = vector_store
        self._db = db

    def search(
        self,
        matter_id: str,
        query: str,
        k: int = 15,
    ) -> list[RetrievalResult]:
        kw_results = keyword_search(self._db, matter_id, query, limit=k * 2)
        kw_ranked: dict[str, int] = {}
        for rank, (chunk_id, _snippet) in enumerate(kw_results):
            kw_ranked[chunk_id] = rank

        sem_ranked: dict[str, int] = {}
        if self._embeddings.is_available and self._vector_store.count > 0:
            query_vec = self._embeddings.encode_query(query)
            sem_results = self._vector_store.search(query_vec, k=k * 2)
            for rank, (chunk_id, _score) in enumerate(sem_results):
                sem_ranked[chunk_id] = rank

        all_ids = set(kw_ranked.keys()) | set(sem_ranked.keys())
        scored: dict[str, tuple[float, str]] = {}
        for chunk_id in all_ids:
            rrf_score = 0.0
            source = "keyword"
            if chunk_id in kw_ranked:
                rrf_score += 1.0 / (RRF_K + kw_ranked[chunk_id])
            if chunk_id in sem_ranked:
                rrf_score += 1.0 / (RRF_K + sem_ranked[chunk_id])
            if chunk_id in kw_ranked and chunk_id in sem_ranked:
                source = "both"
            elif chunk_id in sem_ranked:
                source = "semantic"
            scored[chunk_id] = (rrf_score, source)

        top_ids = sorted(scored, key=lambda x: scored[x][0], reverse=True)[:k]

        if not top_ids:
            return []

        chunks = (
            self._db.query(Chunk)
            .filter(Chunk.id.in_(top_ids))
            .join(Document, Document.id == Chunk.document_id)
            .filter(Document.matter_id == matter_id)
            .all()
        )
        chunk_map = {c.id: c for c in chunks}

        results = []
        for cid in top_ids:
            chunk = chunk_map.get(cid)
            if chunk is None:
                continue
            rrf_score, source = scored[cid]
            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    score=rrf_score,
                    source=source,
                )
            )
        return results

    def index_document(self, document_id: str) -> int:
        chunks = (
            self._db.query(Chunk)
            .filter(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
            .all()
        )
        if not chunks:
            return 0

        texts = [c.text for c in chunks]
        ids = [c.id for c in chunks]

        if self._embeddings.is_available:
            embeddings = self._embeddings.encode(texts)
            self._vector_store.add(embeddings, ids)

        for chunk in chunks:
            try:
                from sqlalchemy import inspect as sa_inspect
                mapper = sa_inspect(chunk)
                rowid = mapper.dict.get("rowid", None)
                if rowid is None:
                    row = self._db.execute(
                        __import__("sqlalchemy").text(
                            "SELECT rowid FROM chunks WHERE id = :id"
                        ),
                        {"id": chunk.id},
                    ).first()
                    rowid = row[0] if row else None
                if rowid is not None:
                    index_chunk_fts(self._db, rowid, chunk.text)
            except Exception as e:
                logger.warning("Failed to index chunk %s in FTS5: %s", chunk.id, e)

        self._db.commit()
        logger.info("Indexed %d chunks for document %s", len(chunks), document_id)
        return len(chunks)

    def remove_document(self, document_id: str) -> None:
        chunk_ids = [
            cid
            for (cid,) in self._db.query(Chunk.id)
            .filter(Chunk.document_id == document_id)
            .all()
        ]
        if chunk_ids:
            self._vector_store.remove(chunk_ids)

        remove_document_fts(self._db, document_id)
        logger.info("Removed document %s from indexes", document_id)
