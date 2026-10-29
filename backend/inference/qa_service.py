import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.db.models import AnalysisRun, Chunk, Document, gen_id
from backend.inference.llm_service import LLMService
from backend.inference.prompts import build_qa_prompt

logger = logging.getLogger(__name__)


@dataclass
class CitationResult:
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int | None
    quote: str
    valid: bool = True


@dataclass
class QAResult:
    answer: str
    citations: list[CitationResult] = field(default_factory=list)
    confidence: str = "medium"
    abstained: bool = False
    conflicts_noted: bool = False
    analysis_run_id: str = ""


class QAService:
    def __init__(self, llm_service: LLMService, embedding_service, vector_store) -> None:
        self._llm = llm_service
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    async def answer_question(
        self, db: Session, matter_id: str, question: str
    ) -> QAResult:
        from backend.retrieval.hybrid_search import HybridRetriever

        run = AnalysisRun(
            id=gen_id(),
            matter_id=matter_id,
            workflow_type="question_answering",
            workflow_version="1.0.0",
            model_manifest_id=self._llm.model_info.get("model_path", ""),
            prompt_version="qa_v1",
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.flush()

        try:
            retriever = HybridRetriever(self._embedding_service, self._vector_store, db)
            raw_results = retriever.search(matter_id, question)
            passages = [
                {
                    "chunk_id": r.chunk_id,
                    "document_id": r.document_id,
                    "text": r.text,
                    "page_number": r.page_start,
                }
                for r in raw_results
            ]

            if not passages:
                run.status = "completed"
                run.completed_at = datetime.now(timezone.utc)
                db.commit()
                return QAResult(
                    answer="Insufficient evidence in the provided documents to answer this question.",
                    abstained=True,
                    analysis_run_id=run.id,
                )

            context = _passages_to_context(db, passages)
            prompt = build_qa_prompt(question, context)
            raw_answer = self._llm.generate(prompt)

            raw_citations = _extract_citations_from_answer(raw_answer)
            validated = self.validate_citations(db, raw_citations, matter_id)

            conflicts = _detect_conflict_language(raw_answer)

            confidence = "high" if len(validated) >= 2 else "medium"
            if any(not c.valid for c in validated):
                confidence = "low"

            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()

            return QAResult(
                answer=raw_answer,
                citations=validated,
                confidence=confidence,
                abstained=False,
                conflicts_noted=conflicts,
                analysis_run_id=run.id,
            )

        except Exception as exc:
            logger.error("QA failed for matter %s: %s", matter_id, exc)
            run.status = "failed"
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise

    def validate_citations(
        self, db: Session, citations: list[CitationResult], matter_id: str
    ) -> list[CitationResult]:
        validated: list[CitationResult] = []
        for cit in citations:
            chunk = (
                db.query(Chunk)
                .join(Document)
                .filter(Chunk.id == cit.chunk_id, Document.matter_id == matter_id)
                .first()
            )
            if chunk is None:
                doc = (
                    db.query(Document)
                    .filter(
                        Document.id == cit.document_id,
                        Document.matter_id == matter_id,
                    )
                    .first()
                )
                if doc is None:
                    cit.valid = False
                    validated.append(cit)
                    continue

                matching_chunk = (
                    db.query(Chunk)
                    .filter(
                        Chunk.document_id == doc.id,
                        Chunk.page_start <= (cit.page_number or 0),
                        Chunk.page_end >= (cit.page_number or 0),
                    )
                    .first()
                )
                if matching_chunk:
                    cit.chunk_id = matching_chunk.id
                    cit.valid = True
                else:
                    cit.valid = False
                validated.append(cit)
                continue

            if cit.quote:
                normalized_quote = _normalize_text(cit.quote)
                normalized_chunk = _normalize_text(chunk.text)
                if normalized_quote not in normalized_chunk:
                    cit.valid = False

            cit.document_id = chunk.document_id
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            if doc:
                cit.document_name = doc.original_name
            validated.append(cit)

        return validated


def _passages_to_context(db: Session, passages: list[dict]) -> list[dict]:
    context: list[dict] = []
    for p in passages:
        chunk_id = p.get("chunk_id", "")
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first() if chunk_id else None
        doc = None
        if chunk:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()

        context.append({
            "chunk_id": chunk_id,
            "document_id": doc.id if doc else p.get("document_id", ""),
            "document_name": doc.original_name if doc else p.get("document_name", "unknown"),
            "page_number": chunk.page_start if chunk else p.get("page_number"),
            "text": p.get("text", chunk.text if chunk else ""),
            "quality_indicator": p.get("quality_indicator"),
        })
    return context


_CITATION_PATTERN = re.compile(
    r"\[DOC-([a-f0-9]+),\s*Page\s+(\d+)\]",
    re.IGNORECASE,
)


def _extract_citations_from_answer(answer: str) -> list[CitationResult]:
    seen: set[tuple[str, int]] = set()
    citations: list[CitationResult] = []

    for match in _CITATION_PATTERN.finditer(answer):
        doc_id = match.group(1)
        page = int(match.group(2))
        key = (doc_id, page)
        if key in seen:
            continue
        seen.add(key)

        citations.append(CitationResult(
            chunk_id="",
            document_id=doc_id,
            document_name="",
            page_number=page,
            quote="",
        ))

    return citations


def _detect_conflict_language(answer: str) -> bool:
    conflict_phrases = [
        "however,", "in contrast,", "contradicts", "differs from",
        "conflicting", "discrepancy", "on the other hand",
        "inconsistent", "disagree",
    ]
    lower = answer.lower()
    return any(phrase in lower for phrase in conflict_phrases)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())
