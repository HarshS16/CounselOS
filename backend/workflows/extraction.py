import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.db.models import (
    AnalysisRun,
    Claim,
    ClaimSource,
    Entity,
    EntityAlias,
    gen_id,
)

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a legal document analyst. Extract all factual claims from the following text passages.

For each claim, provide:
- claim_text: the factual assertion
- claim_type: one of "factual_assertion", "temporal_claim", "financial_claim", "attribution", "legal_assertion", "other"
- speaker: who made or is attributed this claim (if known)
- date_value: any date mentioned (ISO format if possible, otherwise as written)
- date_precision: "exact", "approximate", "range", "inferred", or "unknown"
- uncertainty: any caveats or ambiguity about this claim
- source_chunk_index: which passage number (0-indexed) this claim comes from
- quote: the exact text from the passage supporting this claim

IMPORTANT:
- Only extract claims actually stated or clearly implied in the text
- Do NOT fabricate claims not present in the passages
- Mark uncertain or ambiguous claims explicitly
- Preserve original language for quotes

Passages:
{passages}

Return a JSON array of claims:
```json
[{{"claim_text": "...", "claim_type": "...", "speaker": "...", "date_value": "...", "date_precision": "...", "uncertainty": "...", "source_chunk_index": 0, "quote": "..."}}]
```"""

ENTITY_PROMPT = """Extract all named entities from the following text passages.

For each entity, provide:
- text: the entity name as it appears
- entity_type: one of "person", "organization", "location", "amount", "date", "other"
- source_chunk_index: which passage number (0-indexed)

Passages:
{passages}

Return a JSON array:
```json
[{{"text": "...", "entity_type": "...", "source_chunk_index": 0}}]
```"""


@dataclass
class ExtractedClaim:
    claim_text: str
    claim_type: str
    speaker: str | None = None
    date_value: str | None = None
    date_precision: str | None = None
    uncertainty: str | None = None
    source_chunk_id: str | None = None
    quote: str | None = None


@dataclass
class ExtractedEntity:
    text: str
    entity_type: str
    source_chunk_id: str | None = None


@dataclass
class ExtractionResult:
    claims: list[ExtractedClaim] = field(default_factory=list)
    entities: list[ExtractedEntity] = field(default_factory=list)
    analysis_run_id: str | None = None
    error: str | None = None


def extract_claims_from_chunks(
    llm_service,
    chunks: list[dict],
    max_chunks_per_batch: int = 5,
) -> list[dict]:
    all_claims = []

    for i in range(0, len(chunks), max_chunks_per_batch):
        batch = chunks[i : i + max_chunks_per_batch]
        passages_text = "\n\n".join(
            f"[Passage {j}] (Document: {c['document_name']}, Pages {c['page_start']}-{c['page_end']}):\n{c['text']}"
            for j, c in enumerate(batch)
        )

        prompt = EXTRACTION_PROMPT.format(passages=passages_text)

        try:
            response = llm_service.generate(
                prompt,
                max_tokens=2048,
                temperature=0.1,
                stop=["```\n"],
            )
            raw = response.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            parsed_claims = json.loads(raw.strip())
            if isinstance(parsed_claims, list):
                for claim in parsed_claims:
                    idx = claim.get("source_chunk_index", 0)
                    if 0 <= idx < len(batch):
                        claim["source_chunk_id"] = batch[idx]["chunk_id"]
                        claim["source_document_id"] = batch[idx]["document_id"]
                    all_claims.append(claim)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse extraction response: %s", e)
            continue

    return all_claims


def extract_entities_from_chunks(
    llm_service,
    chunks: list[dict],
    max_chunks_per_batch: int = 5,
) -> list[dict]:
    all_entities = []

    for i in range(0, len(chunks), max_chunks_per_batch):
        batch = chunks[i : i + max_chunks_per_batch]
        passages_text = "\n\n".join(
            f"[Passage {j}]:\n{c['text']}" for j, c in enumerate(batch)
        )

        prompt = ENTITY_PROMPT.format(passages=passages_text)

        try:
            response = llm_service.generate(prompt, max_tokens=1024, temperature=0.1)
            raw = response.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            parsed = json.loads(raw.strip())
            if isinstance(parsed, list):
                for ent in parsed:
                    idx = ent.get("source_chunk_index", 0)
                    if 0 <= idx < len(batch):
                        ent["source_chunk_id"] = batch[idx]["chunk_id"]
                    all_entities.append(ent)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse entity extraction: %s", e)
            continue

    return all_entities


def run_extraction(
    db: Session,
    llm_service,
    matter_id: str,
    chunks: list[dict],
    document_ids: list[str] | None = None,
) -> ExtractionResult:
    run = AnalysisRun(
        id=gen_id(),
        matter_id=matter_id,
        workflow_type="claim_entity_extraction",
        workflow_version="1.0.0",
        status="running",
        document_ids=json.dumps(document_ids) if document_ids else None,
    )
    db.add(run)
    db.commit()

    result = ExtractionResult(analysis_run_id=run.id)

    try:
        raw_claims = extract_claims_from_chunks(llm_service, chunks)

        for rc in raw_claims:
            claim_type = rc.get("claim_type", "other")
            valid_types = {
                "factual_assertion", "temporal_claim", "financial_claim",
                "attribution", "legal_assertion", "other",
            }
            if claim_type not in valid_types:
                claim_type = "other"

            date_prec = rc.get("date_precision", "unknown")
            valid_precs = {"exact", "approximate", "range", "inferred", "unknown"}
            if date_prec not in valid_precs:
                date_prec = "unknown"

            claim = Claim(
                id=gen_id(),
                matter_id=matter_id,
                claim_text=rc.get("claim_text", ""),
                claim_type=claim_type,
                date_value=rc.get("date_value"),
                date_precision=date_prec,
                uncertainty_note=rc.get("uncertainty"),
                analysis_run_id=run.id,
                review_status="pending",
            )
            db.add(claim)
            db.flush()

            chunk_id = rc.get("source_chunk_id")
            if chunk_id:
                source = ClaimSource(
                    id=gen_id(),
                    claim_id=claim.id,
                    chunk_id=chunk_id,
                    quote_text=rc.get("quote"),
                    evidence_role="supports",
                )
                db.add(source)

            result.claims.append(
                ExtractedClaim(
                    claim_text=claim.claim_text,
                    claim_type=claim.claim_type,
                    speaker=rc.get("speaker"),
                    date_value=claim.date_value,
                    date_precision=claim.date_precision,
                    uncertainty=claim.uncertainty_note,
                    source_chunk_id=chunk_id,
                    quote=rc.get("quote"),
                )
            )

        raw_entities = extract_entities_from_chunks(llm_service, chunks)
        seen_entities: dict[str, str] = {}

        for re_ in raw_entities:
            text = re_.get("text", "").strip()
            if not text:
                continue

            etype = re_.get("entity_type", "other")
            valid_etypes = {"person", "organization", "location", "amount", "date", "other"}
            if etype not in valid_etypes:
                etype = "other"

            key = f"{etype}:{text.lower()}"
            if key in seen_entities:
                entity_id = seen_entities[key]
            else:
                entity = Entity(
                    id=gen_id(),
                    matter_id=matter_id,
                    entity_type=etype,
                    canonical_label=text,
                    status="proposed",
                )
                db.add(entity)
                db.flush()
                entity_id = entity.id
                seen_entities[key] = entity_id

            alias = EntityAlias(
                id=gen_id(),
                entity_id=entity_id,
                alias_text=text,
                source_chunk_id=re_.get("source_chunk_id"),
                review_status="proposed",
            )
            db.add(alias)

            result.entities.append(ExtractedEntity(text=text, entity_type=etype))

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        logger.exception("Extraction failed")
        run.status = "failed"
        run.error_message = str(e)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        result.error = str(e)

    return result
