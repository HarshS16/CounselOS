import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.db.models import (
    AnalysisRun,
    Claim,
    ClaimSource,
    Event,
    EventSource,
    gen_id,
)

logger = logging.getLogger(__name__)

CHRONOLOGY_PROMPT = """You are a legal chronology builder. Given the following claims extracted from case documents, build a chronological timeline of events.

For each event:
- event_date: the date (ISO format if possible, otherwise as written in the source)
- date_precision: "exact" if a specific date, "approximate" if roughly dated, "range" if a date range, "inferred" if you deduced it, "unknown" if no date
- description: clear description of what happened
- source_claim_indices: which claim numbers (0-indexed) support this event
- sort_key: a sortable date string (YYYY-MM-DD format, use YYYY-01-01 for year-only, YYYY-MM-01 for month-only, "9999-99-99" for unknown dates)

IMPORTANT:
- Do NOT invent events not supported by the claims
- Preserve date ambiguity — do NOT convert approximate dates to exact ones
- If two claims refer to the same event, merge them and cite both
- Mark conflicting dates explicitly
- Events with unknown dates should be listed separately at the end

Claims:
{claims}

Return a JSON array:
```json
[{{"event_date": "...", "date_precision": "...", "description": "...", "source_claim_indices": [0, 1], "sort_key": "..."}}]
```"""


@dataclass
class ChronologyEvent:
    event_date: str | None
    date_precision: str
    description: str
    source_claim_ids: list[str] = field(default_factory=list)
    sort_key: str = "9999-99-99"
    event_id: str | None = None


@dataclass
class ChronologyResult:
    events: list[ChronologyEvent] = field(default_factory=list)
    analysis_run_id: str | None = None
    error: str | None = None


def build_chronology(
    db: Session,
    llm_service,
    matter_id: str,
    claim_ids: list[str] | None = None,
) -> ChronologyResult:
    run = AnalysisRun(
        id=gen_id(),
        matter_id=matter_id,
        workflow_type="chronology_construction",
        workflow_version="1.0.0",
        status="running",
    )
    db.add(run)
    db.commit()

    result = ChronologyResult(analysis_run_id=run.id)

    try:
        query = db.query(Claim).filter(Claim.matter_id == matter_id)
        if claim_ids:
            query = query.filter(Claim.id.in_(claim_ids))
        claims = query.all()

        if not claims:
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            return result

        claims_data = []
        for i, claim in enumerate(claims):
            claims_data.append({
                "index": i,
                "claim_text": claim.claim_text,
                "claim_type": claim.claim_type,
                "date_value": claim.date_value,
                "date_precision": claim.date_precision,
                "speaker": None,
            })

        claims_text = "\n".join(
            f"[Claim {c['index']}] (Type: {c['claim_type']}, Date: {c['date_value'] or 'N/A'}, "
            f"Precision: {c['date_precision'] or 'N/A'}):\n{c['claim_text']}"
            for c in claims_data
        )

        prompt = CHRONOLOGY_PROMPT.format(claims=claims_text)
        response = llm_service.generate(prompt, max_tokens=2048, temperature=0.1)

        raw = response.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        parsed_events = json.loads(raw.strip())

        if not isinstance(parsed_events, list):
            parsed_events = []

        for pe in parsed_events:
            date_prec = pe.get("date_precision", "unknown")
            valid_precs = {"exact", "approximate", "range", "inferred", "unknown"}
            if date_prec not in valid_precs:
                date_prec = "unknown"

            event = Event(
                id=gen_id(),
                matter_id=matter_id,
                event_date=pe.get("event_date"),
                date_precision=date_prec,
                description=pe.get("description", ""),
                review_status="pending",
                analysis_run_id=run.id,
                sort_key=pe.get("sort_key", "9999-99-99"),
            )
            db.add(event)
            db.flush()

            source_indices = pe.get("source_claim_indices", [])
            source_claim_ids = []
            for idx in source_indices:
                if isinstance(idx, int) and 0 <= idx < len(claims):
                    source_claim = claims[idx]
                    source_claim_ids.append(source_claim.id)

                    for cs in db.query(ClaimSource).filter(
                        ClaimSource.claim_id == source_claim.id
                    ).all():
                        es = EventSource(
                            id=gen_id(),
                            event_id=event.id,
                            chunk_id=cs.chunk_id,
                            support_type="direct",
                        )
                        db.add(es)

            result.events.append(
                ChronologyEvent(
                    event_date=event.event_date,
                    date_precision=event.date_precision,
                    description=event.description,
                    source_claim_ids=source_claim_ids,
                    sort_key=event.sort_key or "9999-99-99",
                    event_id=event.id,
                )
            )

        result.events.sort(key=lambda e: e.sort_key)

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        logger.exception("Chronology construction failed")
        run.status = "failed"
        run.error_message = str(e)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        result.error = str(e)

    return result
