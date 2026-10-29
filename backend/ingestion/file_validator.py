import hashlib
import zipfile
from io import BytesIO

from backend.config import settings


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_file(filename: str, content: bytes) -> tuple[str, str, str]:
    """Validate an uploaded file by signature and size.

    Returns (mime_type, sha256_hash, error). error is empty string on success.
    """
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        return "", "", f"File exceeds maximum size of {settings.max_file_size_mb} MB"

    if len(content) < 4:
        return "", "", "File is too small to be a valid document"

    sha256 = compute_sha256(content)

    # PDF: starts with %PDF
    if content[:4] == b"%PDF":
        return "application/pdf", sha256, ""

    # DOCX: ZIP archive containing word/ directory
    if content[:2] == b"PK":
        try:
            with zipfile.ZipFile(BytesIO(content), "r") as zf:
                names = zf.namelist()
                has_word = any(n.startswith("word/") for n in names)
                if has_word:
                    return (
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        sha256,
                        "",
                    )
                return "", sha256, "ZIP archive does not appear to be a valid DOCX file"
        except zipfile.BadZipFile:
            return "", sha256, "File has a ZIP signature but is not a valid ZIP archive"

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return "", "", (
        f"Unsupported file type (detected from file signature). "
        f"Extension: .{ext}. CounselOS currently supports PDF and DOCX files."
    )
