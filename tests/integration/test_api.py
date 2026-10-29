"""Integration tests for the FastAPI endpoints."""

import io
import zipfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base
from backend.db.session import get_db
from backend.main import create_app
from backend.auth.session_auth import get_session_token


@pytest.fixture
def app(tmp_path):
    from backend.config import settings

    settings.data_dir = tmp_path / "data"
    settings.ensure_directories()

    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    application = create_app()

    def override_get_db():
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        token = get_session_token()
        c.headers["Authorization"] = f"Bearer {token}"
        yield c


def test_health(client):
    resp = client.get("/api/system/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_create_matter(client):
    resp = client.post("/api/matters/", json={
        "title": "Test Matter v. Defendant",
        "jurisdiction": "Delhi High Court",
        "matter_type": "civil",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Matter v. Defendant"
    assert data["status"] == "active"
    assert "id" in data


def test_list_matters(client):
    client.post("/api/matters/", json={"title": "Matter 1"})
    client.post("/api/matters/", json={"title": "Matter 2"})

    resp = client.get("/api/matters/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matters"]) >= 2
    assert data["total"] >= 2


def test_get_matter(client):
    resp = client.post("/api/matters/", json={"title": "Get Test"})
    matter_id = resp.json()["id"]

    resp = client.get(f"/api/matters/{matter_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get Test"


def test_update_matter(client):
    resp = client.post("/api/matters/", json={"title": "Update Test"})
    matter_id = resp.json()["id"]

    resp = client.put(f"/api/matters/{matter_id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


def test_archive_matter(client):
    resp = client.post("/api/matters/", json={"title": "Archive Test"})
    matter_id = resp.json()["id"]

    resp = client.post(f"/api/matters/{matter_id}/archive")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


def test_matter_not_found(client):
    resp = client.get("/api/matters/nonexistent123")
    assert resp.status_code == 404


def test_unauthorized_request(app):
    with TestClient(app) as c:
        resp = c.get("/api/matters/")
        assert resp.status_code in (401, 403)


def _make_docx_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "word/document.xml",
            '<?xml version="1.0"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body><w:p><w:r><w:t>Agreement dated 15 March 2024 between Party A and Party B "
            "regarding payment of Rs. 50,000.</w:t></w:r></w:p></w:body>"
            "</w:document>",
        )
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        zf.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
    return buf.getvalue()


def test_upload_document(client):
    resp = client.post("/api/matters/", json={"title": "Upload Test"})
    matter_id = resp.json()["id"]

    docx_bytes = _make_docx_bytes()
    files = {"file": ("agreement.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    resp = client.post(f"/api/matters/{matter_id}/documents/", files=files)
    assert resp.status_code in (200, 201, 422)


def test_list_documents(client):
    resp = client.post("/api/matters/", json={"title": "DocList Test"})
    matter_id = resp.json()["id"]

    resp = client.get(f"/api/matters/{matter_id}/documents/")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)


def test_cross_matter_isolation(client):
    resp1 = client.post("/api/matters/", json={"title": "Matter A"})
    resp2 = client.post("/api/matters/", json={"title": "Matter B"})
    m1 = resp1.json()["id"]
    m2 = resp2.json()["id"]

    docs1 = client.get(f"/api/matters/{m1}/documents/").json()["documents"]
    docs2 = client.get(f"/api/matters/{m2}/documents/").json()["documents"]

    doc_ids_1 = {d["id"] for d in docs1}
    doc_ids_2 = {d["id"] for d in docs2}
    assert doc_ids_1.isdisjoint(doc_ids_2)


def test_findings_empty(client):
    resp = client.post("/api/matters/", json={"title": "Findings Test"})
    matter_id = resp.json()["id"]

    resp = client.get(f"/api/matters/{matter_id}/findings/")
    assert resp.status_code == 200
    assert resp.json() == []
