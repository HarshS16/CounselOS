import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.db.models import (
    AnalysisRun,
    Chunk,
    Claim,
    ClaimSource,
    Finding,
    FindingSource,
    gen_id,
)

logger = logging.getLogger(__name__)

COMPARISON_PROMPT = """You are a legal document comparison analyst. Compare the following two sets of claims from different documents and identify discrepancies, contradictions, agreements, and omissions.

For each finding, provide:
- finding_type: one of "contradiction", "date_discrepancy", "amount_discrepancy", "attribution_difference", "omission", "ambiguity", "corroboration", "other"
- summary: a brief description of the finding
- explanation: detailed explanation showing both sides
- claim_a_index: index of the relevant claim from Set A (or null)
- claim_b_index: index of the relevant claim from Set B (or null)
- severity: "high", "medium", or "low"

IMPORTANT RULES:
- A potential contradiction is NOT a proven falsehood — say "potential" or "apparent"
- Two statements may refer to different events, stages, or contexts — consider this
- Do NOT overclaim — if the discrepancy might have an innocent explanation, note it
- Identify agreements/corroborations too, not just contradictions
- Show BOTH sides of every comparison
- If a claim in one set has no counterpart in the other, flag it as a potential omission

Claims Set A (from {doc_a_name}):
{claims_a}

Claims Set B (from {doc_b_name}):
{claims_b}

Return a JSON array:
```json
[{{"finding_type": "...", "summary": "...", "explanation": "...", "claim_a_index": 0, "claim_b_index": 1, "severity": "..."}}]
```"""


@dataclass
class DiscrepancyItem:
    finding_type: str
    summary: str
    explanation: str
    claim_a_id: str | None = None
    claim_a_text: str | None = None
    claim_b_id: str | None = None
    claim_b_text: str | None = None
    severity: str = "medium"
    finding_id: str | None = None


@dataclass
class ComparisonResult:
    findings: list[DiscrepancyItem] = field(default_factory=list)
    analysis_run_id: str | None = None
    error: str | None = None


def compare_document_claims(
    db: Session,
    llm_service,
    matter_id: str,
    document_a_id: str,
    document_b_id: str,
    doc_a_name: str = "Document A",
    doc_b_name: str = "Document B",
) -> ComparisonResult:
    run = AnalysisRun(
        id=gen_id(),
        matter_id=matter_id,
        workflow_type="claim_comparison",
        workflow_version="1.0.0",
        status="running",
        document_ids=json.dumps([document_a_id, document_b_id]),
    )
    db.add(run)
    db.commit()

    result = ComparisonResult(analysis_run_id=run.id)

    try:
        claims_a = (
            db.query(Claim)
            .join(ClaimSource)
            .filter(Claim.matter_id == matter_id)
            .filter(
                ClaimSource.chunk_id.in_(
                    db.query(Chunk.id).filter(Chunk.document_id == document_a_id)
                )
            )
            .distinct()
            .all()
        )

        claims_b = (
            db.query(Claim)
            .join(ClaimSource)
            .filter(Claim.matter_id == matter_id)
            .filter(
                ClaimSource.chunk_id.in_(
                    db.query(Chunk.id).filter(Chunk.document_id == document_b_id)
                )
            )
            .distinct()
            .all()
        )

        if not claims_a and not claims_b:
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            return result

        claims_a_text = "\n".join(
            f"[A-{i}] (Type: {c.claim_type}, Date: {c.date_value or 'N/A'}):\n{c.claim_text}"
            for i, c in enumerate(claims_a)
        )
        claims_b_text = "\n".join(
            f"[B-{i}] (Type: {c.claim_type}, Date: {c.date_value or 'N/A'}):\n{c.claim_text}"
            for i, c in enumerate(claims_b)
        )

        prompt = COMPARISON_PROMPT.format(
            doc_a_name=doc_a_name,
            doc_b_name=doc_b_name,
            claims_a=claims_a_text,
            claims_b=claims_b_text,
        )

        response = llm_service.generate(prompt, max_tokens=2048, temperature=0.1)

        raw = response.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        parsed = json.loads(raw.strip())
        if not isinstance(parsed, list):
            parsed = []

        for pf in parsed:
            ftype = pf.get("finding_type", "other")
            valid_types = {
                "contradiction", "date_discrepancy", "amount_discrepancy",
                "attribution_difference", "omission", "ambiguity",
                "corroboration", "other",
            }
            if ftype not in valid_types:
                ftype = "other"

            claim_a_idx = pf.get("claim_a_index")
            claim_b_idx = pf.get("claim_b_index")

            claim_a = claims_a[claim_a_idx] if isinstance(claim_a_idx, int) and 0 <= claim_a_idx < len(claims_a) else None
            claim_b = claims_b[claim_b_idx] if isinstance(claim_b_idx, int) and 0 <= claim_b_idx < len(claims_b) else None

            finding = Finding(
                id=gen_id(),
                matter_id=matter_id,
                analysis_run_id=run.id,
                finding_type=ftype,
                summary=pf.get("summary", ""),
                explanation=pf.get("explanation", ""),
                claim_a_id=claim_a.id if claim_a else None,
                claim_b_id=claim_b.id if claim_b else None,
                review_status="pending",
            )
            db.add(finding)
            db.flush()

            for claim_obj in [claim_a, claim_b]:
                if claim_obj:
                    rel = "claim_a_source" if claim_obj == claim_a else "claim_b_source"
                    for cs in db.query(ClaimSource).filter(ClaimSource.claim_id == claim_obj.id).all():
                        fs = FindingSource(
                            id=gen_id(),
                            finding_id=finding.id,
                            chunk_id=cs.chunk_id,
                            relationship_type=rel,
                        )
                        db.add(fs)

            result.findings.append(
                DiscrepancyItem(
                    finding_type=ftype,
                    summary=pf.get("summary", ""),
                    explanation=pf.get("explanation", ""),
                    claim_a_id=claim_a.id if claim_a else None,
                    claim_a_text=claim_a.claim_text if claim_a else None,
                    claim_b_id=claim_b.id if claim_b else None,
                    claim_b_text=claim_b.claim_text if claim_b else None,
                    severity=pf.get("severity", "medium"),
                    finding_id=finding.id,
                )
            )

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        logger.exception("Comparison failed")
        run.status = "failed"
        run.error_message = str(e)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        result.error = str(e)

    return result


def compare_claim_sets(
    db: Session,
    llm_service,
    matter_id: str,
    claim_ids_a: list[str],
    claim_ids_b: list[str],
) -> ComparisonResult:
    run = AnalysisRun(
        id=gen_id(),
        matter_id=matter_id,
        workflow_type="claim_set_comparison",
        workflow_version="1.0.0",
        status="running",
    )
    db.add(run)
    db.commit()

    result = ComparisonResult(analysis_run_id=run.id)

    try:
        claims_a = db.query(Claim).filter(Claim.id.in_(claim_ids_a), Claim.matter_id == matter_id).all()
        claims_b = db.query(Claim).filter(Claim.id.in_(claim_ids_b), Claim.matter_id == matter_id).all()

        claims_a_text = "\n".join(
            f"[A-{i}] (Type: {c.claim_type}):\n{c.claim_text}"
            for i, c in enumerate(claims_a)
        )
        claims_b_text = "\n".join(
            f"[B-{i}] (Type: {c.claim_type}):\n{c.claim_text}"
            for i, c in enumerate(claims_b)
        )

        prompt = COMPARISON_PROMPT.format(
            doc_a_name="Set A",
            doc_b_name="Set B",
            claims_a=claims_a_text,
            claims_b=claims_b_text,
        )

        response = llm_service.generate(prompt, max_tokens=2048, temperature=0.1)

        raw = response.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        parsed = json.loads(raw.strip())
        if not isinstance(parsed, list):
            parsed = []

        for pf in parsed:
            ftype = pf.get("finding_type", "other")
            valid_types = {
                "contradiction", "date_discrepancy", "amount_discrepancy",
                "attribution_difference", "omission", "ambiguity",
                "corroboration", "other",
            }
            if ftype not in valid_types:
                ftype = "other"

            claim_a_idx = pf.get("claim_a_index")
            claim_b_idx = pf.get("claim_b_index")
            claim_a = claims_a[claim_a_idx] if isinstance(claim_a_idx, int) and 0 <= claim_a_idx < len(claims_a) else None
            claim_b = claims_b[claim_b_idx] if isinstance(claim_b_idx, int) and 0 <= claim_b_idx < len(claims_b) else None

            finding = Finding(
                id=gen_id(),
                matter_id=matter_id,
                analysis_run_id=run.id,
                finding_type=ftype,
                summary=pf.get("summary", ""),
                explanation=pf.get("explanation", ""),
                claim_a_id=claim_a.id if claim_a else None,
                claim_b_id=claim_b.id if claim_b else None,
                review_status="pending",
            )
            db.add(finding)
            db.flush()

            result.findings.append(
                DiscrepancyItem(
                    finding_type=ftype,
                    summary=pf.get("summary", ""),
                    explanation=pf.get("explanation", ""),
                    claim_a_id=claim_a.id if claim_a else None,
                    claim_a_text=claim_a.claim_text if claim_a else None,
                    claim_b_id=claim_b.id if claim_b else None,
                    claim_b_text=claim_b.claim_text if claim_b else None,
                    severity=pf.get("severity", "medium"),
                    finding_id=finding.id,
                )
            )

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        logger.exception("Claim set comparison failed")
        run.status = "failed"
        run.error_message = str(e)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        result.error = str(e)

    return result
