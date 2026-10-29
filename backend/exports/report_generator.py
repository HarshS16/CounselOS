import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from docx import Document as DocxDocument
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.models import (
    Matter,
    Document,
    Finding,
    FindingSource,
    Claim,
    ClaimSource,
    Chunk,
    Event,
    EventSource,
    AnalysisRun,
    gen_id,
)

logger = logging.getLogger(__name__)


@dataclass
class ExportOptions:
    include_chronology: bool = True
    include_findings: bool = True
    include_claims: bool = True
    include_sources: bool = True
    include_review_status: bool = True
    finding_statuses: list[str] | None = None
    document_ids: list[str] | None = None
    format: str = "docx"


def generate_evidence_report(
    db: Session,
    matter_id: str,
    options: ExportOptions | None = None,
) -> Path:
    if options is None:
        options = ExportOptions()

    matter = db.query(Matter).filter(Matter.id == matter_id).first()
    if not matter:
        raise ValueError(f"Matter {matter_id} not found")

    doc = DocxDocument()

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    title = doc.add_heading(f"Evidence Report: {matter.title}", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("")
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.style = "Light Grid Accent 1"
    cells = meta_table.rows[0].cells
    cells[0].text = "Matter Title"
    cells[1].text = matter.title
    cells = meta_table.rows[1].cells
    cells[0].text = "Reference"
    cells[1].text = matter.reference or "N/A"
    cells = meta_table.rows[2].cells
    cells[0].text = "Jurisdiction"
    cells[1].text = matter.jurisdiction or "N/A"
    cells = meta_table.rows[3].cells
    cells[0].text = "Export Date"
    cells[1].text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cells = meta_table.rows[4].cells
    cells[0].text = "Status"
    cells[1].text = matter.status

    doc.add_paragraph("")
    caveat = doc.add_paragraph()
    caveat_run = caveat.add_run(
        "IMPORTANT: This report contains AI-generated analysis. All findings are provisional "
        "and require professional legal review. Source citations indicate where text was found, "
        "not whether the underlying statements are true. Absence of a finding does not prove "
        "absence of evidence."
    )
    caveat_run.italic = True
    caveat_run.font.color.rgb = RGBColor(180, 0, 0)

    documents = db.query(Document).filter(Document.matter_id == matter_id).all()
    if options.document_ids:
        documents = [d for d in documents if d.id in options.document_ids]

    doc.add_heading("Documents Analyzed", level=1)
    if documents:
        doc_table = doc.add_table(rows=1, cols=4)
        doc_table.style = "Light Grid Accent 1"
        hdr = doc_table.rows[0].cells
        hdr[0].text = "Document"
        hdr[1].text = "Type"
        hdr[2].text = "Status"
        hdr[3].text = "Pages"
        for d in documents:
            row = doc_table.add_row().cells
            row[0].text = d.original_name
            row[1].text = d.mime_type
            row[2].text = d.processing_status
            row[3].text = str(d.page_count or "N/A")
    else:
        doc.add_paragraph("No documents in scope.")

    if options.include_findings:
        doc.add_heading("Findings", level=1)
        query = db.query(Finding).filter(Finding.matter_id == matter_id)
        if options.finding_statuses:
            query = query.filter(Finding.review_status.in_(options.finding_statuses))
        findings = query.order_by(Finding.created_at).all()

        if findings:
            for i, finding in enumerate(findings, 1):
                doc.add_heading(f"Finding {i}: {finding.summary[:80]}", level=2)

                p = doc.add_paragraph()
                p.add_run("Type: ").bold = True
                p.add_run(finding.finding_type)

                p = doc.add_paragraph()
                p.add_run("Review Status: ").bold = True
                status_text = finding.review_status
                if options.include_review_status:
                    run = p.add_run(status_text)
                    if status_text == "accepted":
                        run.font.color.rgb = RGBColor(0, 128, 0)
                    elif status_text == "rejected":
                        run.font.color.rgb = RGBColor(180, 0, 0)
                    else:
                        run.font.color.rgb = RGBColor(180, 120, 0)

                if finding.explanation:
                    p = doc.add_paragraph()
                    p.add_run("Explanation: ").bold = True
                    p.add_run(finding.explanation)

                if finding.reviewer_note:
                    p = doc.add_paragraph()
                    p.add_run("Reviewer Note: ").bold = True
                    p.add_run(finding.reviewer_note)

                if options.include_sources:
                    sources = (
                        db.query(FindingSource, Chunk, Document)
                        .join(Chunk, FindingSource.chunk_id == Chunk.id)
                        .join(Document, Chunk.document_id == Document.id)
                        .filter(FindingSource.finding_id == finding.id)
                        .all()
                    )
                    if sources:
                        p = doc.add_paragraph()
                        p.add_run("Sources:").bold = True
                        for fs, chunk, d in sources:
                            doc.add_paragraph(
                                f"  [{fs.relationship_type}] {d.original_name}, "
                                f"Pages {chunk.page_start}-{chunk.page_end}",
                                style="List Bullet",
                            )

                doc.add_paragraph("")
        else:
            doc.add_paragraph("No findings in scope.")

    if options.include_chronology:
        doc.add_heading("Chronology", level=1)
        events = (
            db.query(Event)
            .filter(Event.matter_id == matter_id)
            .order_by(Event.sort_key)
            .all()
        )

        if events:
            evt_table = doc.add_table(rows=1, cols=4)
            evt_table.style = "Light Grid Accent 1"
            hdr = evt_table.rows[0].cells
            hdr[0].text = "Date"
            hdr[1].text = "Precision"
            hdr[2].text = "Description"
            hdr[3].text = "Status"
            for event in events:
                row = evt_table.add_row().cells
                row[0].text = event.event_date or "Unknown"
                row[1].text = event.date_precision or "unknown"
                row[2].text = event.description
                row[3].text = event.review_status
        else:
            doc.add_paragraph("No chronology events generated.")

    if options.include_claims:
        doc.add_heading("Extracted Claims", level=1)
        claims = (
            db.query(Claim)
            .filter(Claim.matter_id == matter_id)
            .order_by(Claim.created_at)
            .all()
        )

        if claims:
            for i, claim in enumerate(claims, 1):
                p = doc.add_paragraph()
                p.add_run(f"Claim {i} [{claim.claim_type}]").bold = True
                if claim.review_status != "pending":
                    p.add_run(f" ({claim.review_status})")
                doc.add_paragraph(claim.claim_text)
                if claim.date_value:
                    doc.add_paragraph(
                        f"  Date: {claim.date_value} ({claim.date_precision or 'unknown'})",
                        style="List Bullet",
                    )
                if claim.uncertainty_note:
                    doc.add_paragraph(
                        f"  Uncertainty: {claim.uncertainty_note}", style="List Bullet"
                    )
        else:
            doc.add_paragraph("No claims extracted.")

    doc.add_heading("Report Metadata", level=1)
    p = doc.add_paragraph()
    p.add_run("Generated by: ").bold = True
    p.add_run("CounselOS v1.0.0 (AI-assisted analysis)")
    p = doc.add_paragraph()
    p.add_run("Note: ").bold = True
    p.add_run(
        "AI-generated content is marked as such. Items marked 'pending' have not been "
        "reviewed by a human. This report is not legal advice."
    )

    settings.ensure_directories()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"evidence_report_{matter.title[:30].replace(' ', '_')}_{timestamp}.docx"
    filepath = settings.exports_dir / filename
    doc.save(str(filepath))

    return filepath
