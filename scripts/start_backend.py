"""Start the CounselOS backend service."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from backend.config import settings


def main():
    settings.ensure_directories()

    print(f"CounselOS Backend v{settings.app_version}")
    print(f"Data directory: {settings.data_dir}")
    print(f"API: http://{settings.api_host}:{settings.api_port}")
    print(f"LLM model: {settings.llm_model_path or 'Not configured'}")
    print()

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
