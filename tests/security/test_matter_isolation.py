"""SEC-008: Cross-matter isolation tests. These MUST pass before pilot release."""

from backend.db.models import (
    Matter, Document, Chunk, Claim, ClaimSource, Finding, gen_id,
)


def test_document_query_isolated_by_matter(db_session):
    m1 = Matter(id=gen_id(), title="Matter 1")
    m2 = Matter(id=gen_id(), title="Matter 2")
    db_session.add_all([m1, m2])
    db_session.flush()

    d1 = Document(
        id=gen_id(), matter_id=m1.id, original_name="m1.pdf",
        storage_key="m1/m1.pdf", sha256="a" * 64,
        mime_type="application/pdf", size_bytes=100,
    )
    d2 = Document(
        id=gen_id(), matter_id=m2.id, original_name="m2.pdf",
        storage_key="m2/m2.pdf", sha256="b" * 64,
        mime_type="application/pdf", size_bytes=100,
    )
    db_session.add_all([d1, d2])
    db_session.commit()

    results = db_session.query(Document).filter(Document.matter_id == m1.id).all()
    assert all(d.matter_id == m1.id for d in results)
    assert len(results) == 1


def test_chunk_query_isolated_by_matter(db_session):
    m1 = Matter(id=gen_id(), title="Matter A")
    m2 = Matter(id=gen_id(), title="Matter B")
    db_session.add_all([m1, m2])
    db_session.flush()

    d1 = Document(
        id=gen_id(), matter_id=m1.id, original_name="a.pdf",
        storage_key="a/a.pdf", sha256="c" * 64,
        mime_type="application/pdf", size_bytes=100,
    )
    d2 = Document(
        id=gen_id(), matter_id=m2.id, original_name="b.pdf",
        storage_key="b/b.pdf", sha256="d" * 64,
        mime_type="application/pdf", size_bytes=100,
    )
    db_session.add_all([d1, d2])
    db_session.flush()

    c1 = Chunk(
        id=gen_id(), document_id=d1.id, page_start=1, page_end=1,
        text="Matter A content", content_hash="e" * 64, chunk_index=0,
    )
    c2 = Chunk(
        id=gen_id(), document_id=d2.id, page_start=1, page_end=1,
        text="Matter B content", content_hash="f" * 64, chunk_index=0,
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    chunks_m1 = (
        db_session.query(Chunk)
        .join(Document)
        .filter(Document.matter_id == m1.id)
        .all()
    )
    assert len(chunks_m1) == 1
    assert chunks_m1[0].text == "Matter A content"


def test_claims_isolated_by_matter(db_session):
    m1 = Matter(id=gen_id(), title="Claims Matter 1")
    m2 = Matter(id=gen_id(), title="Claims Matter 2")
    db_session.add_all([m1, m2])
    db_session.flush()

    claim1 = Claim(
        id=gen_id(), matter_id=m1.id,
        claim_text="Claim from matter 1", claim_type="factual_assertion",
    )
    claim2 = Claim(
        id=gen_id(), matter_id=m2.id,
        claim_text="Claim from matter 2", claim_type="factual_assertion",
    )
    db_session.add_all([claim1, claim2])
    db_session.commit()

    m1_claims = db_session.query(Claim).filter(Claim.matter_id == m1.id).all()
    assert len(m1_claims) == 1
    assert m1_claims[0].claim_text == "Claim from matter 1"


def test_findings_isolated_by_matter(db_session):
    m1 = Matter(id=gen_id(), title="Findings Matter 1")
    m2 = Matter(id=gen_id(), title="Findings Matter 2")
    db_session.add_all([m1, m2])
    db_session.flush()

    f1 = Finding(
        id=gen_id(), matter_id=m1.id,
        finding_type="contradiction", summary="Finding in M1",
    )
    f2 = Finding(
        id=gen_id(), matter_id=m2.id,
        finding_type="corroboration", summary="Finding in M2",
    )
    db_session.add_all([f1, f2])
    db_session.commit()

    m1_findings = db_session.query(Finding).filter(Finding.matter_id == m1.id).all()
    assert len(m1_findings) == 1
    assert m1_findings[0].summary == "Finding in M1"


def test_cascade_delete_matter(db_session):
    m = Matter(id=gen_id(), title="Delete Test")
    db_session.add(m)
    db_session.flush()

    d = Document(
        id=gen_id(), matter_id=m.id, original_name="del.pdf",
        storage_key="del/del.pdf", sha256="g" * 64,
        mime_type="application/pdf", size_bytes=100,
    )
    db_session.add(d)
    db_session.flush()

    c = Chunk(
        id=gen_id(), document_id=d.id, page_start=1, page_end=1,
        text="Will be deleted", content_hash="h" * 64, chunk_index=0,
    )
    db_session.add(c)
    db_session.commit()

    db_session.delete(m)
    db_session.commit()

    assert db_session.query(Document).filter(Document.matter_id == m.id).count() == 0
    assert db_session.query(Chunk).filter(Chunk.document_id == d.id).count() == 0
