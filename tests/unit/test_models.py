from backend.db.models import Matter, Document, Chunk, Claim, Finding, gen_id, utcnow


def test_gen_id_unique():
    ids = {gen_id() for _ in range(100)}
    assert len(ids) == 100


def test_gen_id_format():
    id_ = gen_id()
    assert len(id_) == 32
    assert id_.isalnum()


def test_utcnow_has_timezone():
    now = utcnow()
    assert now.tzinfo is not None


def test_create_matter(db_session):
    matter = Matter(
        id=gen_id(),
        title="Test Case v. Defendant",
        jurisdiction="Delhi High Court",
        matter_type="civil",
    )
    db_session.add(matter)
    db_session.commit()

    loaded = db_session.query(Matter).filter(Matter.id == matter.id).first()
    assert loaded is not None
    assert loaded.title == "Test Case v. Defendant"
    assert loaded.status == "active"
    assert loaded.created_at is not None


def test_matter_document_relationship(db_session):
    matter = Matter(id=gen_id(), title="Test Matter")
    db_session.add(matter)
    db_session.flush()

    doc = Document(
        id=gen_id(),
        matter_id=matter.id,
        original_name="evidence.pdf",
        storage_key="test/evidence.pdf",
        sha256="a" * 64,
        mime_type="application/pdf",
        size_bytes=1024,
        processing_status="imported",
    )
    db_session.add(doc)
    db_session.commit()

    loaded = db_session.query(Matter).filter(Matter.id == matter.id).first()
    assert len(loaded.documents) == 1
    assert loaded.documents[0].original_name == "evidence.pdf"


def test_chunk_belongs_to_document(db_session):
    matter = Matter(id=gen_id(), title="Chunk Test")
    db_session.add(matter)
    db_session.flush()

    doc = Document(
        id=gen_id(),
        matter_id=matter.id,
        original_name="doc.pdf",
        storage_key="test/doc.pdf",
        sha256="b" * 64,
        mime_type="application/pdf",
        size_bytes=2048,
    )
    db_session.add(doc)
    db_session.flush()

    chunk = Chunk(
        id=gen_id(),
        document_id=doc.id,
        page_start=1,
        page_end=1,
        text="The agreement was signed on 15 March 2024.",
        content_hash="c" * 64,
        chunk_index=0,
    )
    db_session.add(chunk)
    db_session.commit()

    loaded = db_session.query(Chunk).filter(Chunk.id == chunk.id).first()
    assert loaded.document_id == doc.id
    assert loaded.page_start == 1


def test_matter_isolation(db_session):
    matter_a = Matter(id=gen_id(), title="Matter A")
    matter_b = Matter(id=gen_id(), title="Matter B")
    db_session.add_all([matter_a, matter_b])
    db_session.flush()

    doc_a = Document(
        id=gen_id(),
        matter_id=matter_a.id,
        original_name="a.pdf",
        storage_key="a/a.pdf",
        sha256="d" * 64,
        mime_type="application/pdf",
        size_bytes=100,
    )
    doc_b = Document(
        id=gen_id(),
        matter_id=matter_b.id,
        original_name="b.pdf",
        storage_key="b/b.pdf",
        sha256="e" * 64,
        mime_type="application/pdf",
        size_bytes=100,
    )
    db_session.add_all([doc_a, doc_b])
    db_session.commit()

    docs_a = db_session.query(Document).filter(Document.matter_id == matter_a.id).all()
    docs_b = db_session.query(Document).filter(Document.matter_id == matter_b.id).all()

    assert len(docs_a) == 1
    assert len(docs_b) == 1
    assert docs_a[0].id != docs_b[0].id


def test_claim_with_sources(db_session):
    matter = Matter(id=gen_id(), title="Claims Test")
    db_session.add(matter)
    db_session.flush()

    doc = Document(
        id=gen_id(),
        matter_id=matter.id,
        original_name="stmt.pdf",
        storage_key="test/stmt.pdf",
        sha256="f" * 64,
        mime_type="application/pdf",
        size_bytes=500,
    )
    db_session.add(doc)
    db_session.flush()

    chunk = Chunk(
        id=gen_id(),
        document_id=doc.id,
        page_start=1,
        page_end=1,
        text="Payment of Rs. 50,000 was made on 1 Jan 2024.",
        content_hash="g" * 64,
        chunk_index=0,
    )
    db_session.add(chunk)
    db_session.flush()

    claim = Claim(
        id=gen_id(),
        matter_id=matter.id,
        claim_text="Payment of Rs. 50,000 was made on 1 January 2024",
        claim_type="financial_claim",
        date_value="2024-01-01",
        date_precision="exact",
    )
    db_session.add(claim)
    db_session.commit()

    from backend.db.models import ClaimSource
    source = ClaimSource(
        id=gen_id(),
        claim_id=claim.id,
        chunk_id=chunk.id,
        quote_text="Payment of Rs. 50,000 was made on 1 Jan 2024.",
        evidence_role="supports",
    )
    db_session.add(source)
    db_session.commit()

    loaded = db_session.query(Claim).filter(Claim.id == claim.id).first()
    assert len(loaded.sources) == 1
    assert loaded.sources[0].chunk_id == chunk.id


def test_finding_review_status(db_session):
    matter = Matter(id=gen_id(), title="Findings Test")
    db_session.add(matter)
    db_session.flush()

    finding = Finding(
        id=gen_id(),
        matter_id=matter.id,
        finding_type="contradiction",
        summary="Date discrepancy between statements",
    )
    db_session.add(finding)
    db_session.commit()

    assert finding.review_status == "pending"

    finding.review_status = "accepted"
    finding.reviewer_note = "Confirmed by reviewing original documents"
    db_session.commit()

    loaded = db_session.query(Finding).filter(Finding.id == finding.id).first()
    assert loaded.review_status == "accepted"
    assert loaded.reviewer_note is not None
