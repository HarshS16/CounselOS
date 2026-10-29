import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_HASH_CHUNK_SIZE = 1 << 20  # 1 MiB


@dataclass
class ModelManifest:
    model_name: str
    model_path: str
    quantization: str
    context_length: int
    file_hash: str
    license_info: str = ""
    runtime: str = "llama.cpp"


def load_manifest(path: Path) -> ModelManifest:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return ModelManifest(**{k: v for k, v in data.items() if k in ModelManifest.__dataclass_fields__})


def save_manifest(manifest: ModelManifest, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")
    logger.info("Manifest saved to %s", path)


def compute_model_hash(model_path: Path) -> str:
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    sha = hashlib.sha256()
    with open(model_path, "rb") as f:
        while True:
            chunk = f.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def verify_model_integrity(manifest: ModelManifest) -> bool:
    model_path = Path(manifest.model_path)
    if not model_path.exists():
        logger.warning("Model file not found: %s", manifest.model_path)
        return False
    try:
        actual_hash = compute_model_hash(model_path)
        if actual_hash != manifest.file_hash:
            logger.warning(
                "Model hash mismatch: expected %s, got %s",
                manifest.file_hash,
                actual_hash,
            )
            return False
        return True
    except Exception as exc:
        logger.error("Integrity check failed: %s", exc)
        return False
