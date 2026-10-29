import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CounselOS"
    app_version: str = "1.0.0"
    debug: bool = False

    data_dir: Path = Path(os.path.expanduser("~")) / ".counselos" / "data"
    db_name: str = "counselos.db"
    originals_dir_name: str = "originals"
    extracted_dir_name: str = "extracted"
    exports_dir_name: str = "exports"
    backups_dir_name: str = "backups"

    api_host: str = "127.0.0.1"
    api_port: int = 8741
    api_secret_key: str = ""

    max_file_size_mb: int = 500
    max_context_chunks: int = 15
    chunk_size: int = 512
    chunk_overlap: int = 64

    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    llm_model_path: str = ""
    llm_context_length: int = 4096
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.1
    llm_n_gpu_layers: int = 0
    llm_n_threads: int = 4

    tesseract_cmd: str = ""
    ocr_language: str = "eng+hin"
    ocr_quality_threshold: float = 60.0

    encryption_enabled: bool = True

    model_config = {"env_prefix": "COUNSELOS_", "env_file": ".env"}

    @property
    def db_path(self) -> Path:
        return self.data_dir / self.db_name

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"

    @property
    def originals_dir(self) -> Path:
        return self.data_dir / self.originals_dir_name

    @property
    def extracted_dir(self) -> Path:
        return self.data_dir / self.extracted_dir_name

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / self.exports_dir_name

    @property
    def backups_dir(self) -> Path:
        return self.data_dir / self.backups_dir_name

    def ensure_directories(self) -> None:
        for d in [self.data_dir, self.originals_dir, self.extracted_dir,
                   self.exports_dir, self.backups_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
