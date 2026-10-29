import tempfile
from pathlib import Path

from backend.security.encryption import (
    compute_file_hash,
    decrypt_file,
    encrypt_file,
    verify_file_integrity,
)


def test_encrypt_decrypt_roundtrip(tmp_path):
    original = tmp_path / "original.txt"
    encrypted = tmp_path / "encrypted.enc"
    decrypted = tmp_path / "decrypted.txt"

    original.write_text("Confidential case material: Rs. 50,000 payment on 1 Jan 2024")

    encrypt_file(original, encrypted, "test-password-123")
    assert encrypted.exists()
    assert encrypted.read_bytes() != original.read_bytes()

    decrypt_file(encrypted, decrypted, "test-password-123")
    assert decrypted.read_text() == "Confidential case material: Rs. 50,000 payment on 1 Jan 2024"


def test_wrong_password_fails(tmp_path):
    original = tmp_path / "original.txt"
    encrypted = tmp_path / "encrypted.enc"
    decrypted = tmp_path / "decrypted.txt"

    original.write_text("Secret data")
    encrypt_file(original, encrypted, "correct-password")

    import pytest
    with pytest.raises(Exception):
        decrypt_file(encrypted, decrypted, "wrong-password")


def test_file_hash():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"test content for hashing")
        path = Path(f.name)

    try:
        h = compute_file_hash(path)
        assert len(h) == 64
        assert h == compute_file_hash(path)
    finally:
        path.unlink()


def test_verify_integrity(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("integrity check")

    h = compute_file_hash(f)
    assert verify_file_integrity(f, h) is True
    assert verify_file_integrity(f, "wrong_hash") is False
    assert verify_file_integrity(tmp_path / "nonexistent.txt", h) is False
