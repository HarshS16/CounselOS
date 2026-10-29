import base64
import hashlib
import logging
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from backend.config import settings

logger = logging.getLogger(__name__)


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_file(input_path: Path, output_path: Path, password: str) -> None:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    fernet = Fernet(key)

    with open(input_path, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    with open(output_path, "wb") as f:
        f.write(salt)
        f.write(encrypted)


def decrypt_file(input_path: Path, output_path: Path, password: str) -> None:
    with open(input_path, "rb") as f:
        salt = f.read(16)
        encrypted = f.read()

    key = derive_key(password, salt)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted)

    with open(output_path, "wb") as f:
        f.write(decrypted)


def create_backup(password: str, matter_id: str | None = None) -> Path:
    settings.ensure_directories()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if matter_id:
        backup_name = f"counselos_backup_{matter_id[:8]}_{timestamp}"
    else:
        backup_name = f"counselos_backup_full_{timestamp}"

    zip_path = settings.backups_dir / f"{backup_name}.zip"
    encrypted_path = settings.backups_dir / f"{backup_name}.enc"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        db_path = settings.db_path
        if db_path.exists():
            zf.write(db_path, "counselos.db")

        originals_dir = settings.originals_dir
        if originals_dir.exists():
            if matter_id:
                matter_dir = originals_dir / matter_id
                if matter_dir.exists():
                    for file in matter_dir.rglob("*"):
                        if file.is_file():
                            arcname = f"originals/{file.relative_to(originals_dir)}"
                            zf.write(file, arcname)
            else:
                for file in originals_dir.rglob("*"):
                    if file.is_file():
                        arcname = f"originals/{file.relative_to(originals_dir)}"
                        zf.write(file, arcname)

    encrypt_file(zip_path, encrypted_path, password)
    zip_path.unlink()

    logger.info("Backup created: %s", encrypted_path.name)
    return encrypted_path


def restore_backup(backup_path: Path, password: str, target_dir: Path | None = None) -> Path:
    if target_dir is None:
        target_dir = settings.data_dir

    temp_zip = backup_path.with_suffix(".tmp.zip")

    try:
        decrypt_file(backup_path, temp_zip, password)

        restore_dir = target_dir / "restored"
        restore_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(temp_zip, "r") as zf:
            zf.extractall(restore_dir)

        logger.info("Backup restored to: %s", restore_dir)
        return restore_dir

    finally:
        if temp_zip.exists():
            temp_zip.unlink()


def compute_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_file_integrity(file_path: Path, expected_hash: str) -> bool:
    if not file_path.exists():
        return False
    return compute_file_hash(file_path) == expected_hash
