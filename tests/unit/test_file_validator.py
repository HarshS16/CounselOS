import pytest
from backend.ingestion.file_validator import validate_file


def test_validate_pdf(sample_pdf_bytes):
    mime_type, sha256, error = validate_file("test.pdf", sample_pdf_bytes)
    assert mime_type == "application/pdf"
    assert error == ""
    assert len(sha256) == 64


def test_validate_docx(sample_docx_bytes):
    mime_type, sha256, error = validate_file("test.docx", sample_docx_bytes)
    assert mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert error == ""


def test_reject_unsupported_type():
    _, _, error = validate_file("test.exe", b"MZ\x90\x00")
    assert error != ""


def test_reject_empty_file():
    _, _, error = validate_file("empty.pdf", b"")
    assert error != ""


def test_reject_wrong_extension():
    _, _, error = validate_file("fake.pdf", b"This is not a PDF")
    assert error != ""
