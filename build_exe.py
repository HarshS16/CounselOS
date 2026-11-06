"""
Build CounselOS into a distributable folder with CounselOS.exe.

Prerequisites:
    pip install pyinstaller
    cd apps/desktop && npm run build   (already done if dist/ exists)

Usage:
    python build_exe.py

Output:
    dist/CounselOS/CounselOS.exe
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DIST_DIR = ROOT / "dist" / "CounselOS"
FRONTEND_DIST = ROOT / "apps" / "desktop" / "dist"


def check_prerequisites():
    errors = []

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        errors.append("PyInstaller not installed. Run: pip install pyinstaller")

    if not FRONTEND_DIST.is_dir() or not (FRONTEND_DIST / "index.html").exists():
        errors.append(
            f"Frontend not built. Run: cd apps/desktop && npm run build\n"
            f"  Expected: {FRONTEND_DIST / 'index.html'}"
        )

    if errors:
        print("=" * 60)
        print("PREREQUISITES NOT MET:")
        for e in errors:
            print(f"  - {e}")
        print("=" * 60)
        sys.exit(1)


def build():
    check_prerequisites()

    print("=" * 60)
    print("Building CounselOS Desktop Application")
    print("=" * 60)

    spec_file = ROOT / "counselos.spec"
    if not spec_file.exists():
        print(f"ERROR: {spec_file} not found")
        sys.exit(1)

    print("\n[1/3] Running PyInstaller...")
    result = subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            str(spec_file),
            "--noconfirm",
            "--distpath", str(ROOT / "dist"),
            "--workpath", str(ROOT / "build"),
        ],
        cwd=str(ROOT),
    )

    if result.returncode != 0:
        print("\nERROR: PyInstaller failed. Check output above for details.")
        sys.exit(1)

    print("\n[2/3] Creating default .env template...")
    env_template = DIST_DIR / ".env.example"
    env_template.write_text(
        "# CounselOS Configuration\n"
        "# Copy this file to .env and edit as needed.\n"
        "#\n"
        "# Path to your GGUF model file (required for AI features)\n"
        "COUNSELOS_LLM_MODEL_PATH=\n"
        "#\n"
        "# GPU layers to offload (0 = CPU only, set higher for NVIDIA GPU)\n"
        "COUNSELOS_LLM_GPU_LAYERS=0\n"
        "#\n"
        "# CPU threads for LLM inference\n"
        "COUNSELOS_LLM_THREADS=4\n"
        "#\n"
        "# LLM context window size\n"
        "COUNSELOS_LLM_CONTEXT_LENGTH=4096\n"
        "#\n"
        "# Tesseract OCR path (Windows — usually auto-detected)\n"
        "# COUNSELOS_TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe\n"
        "#\n"
        "# OCR languages (default: English + Hindi)\n"
        "COUNSELOS_OCR_LANGUAGE=eng+hin\n"
        "#\n"
        "# Data directory (default: ~/.counselos/data)\n"
        "# COUNSELOS_DATA_DIR=\n",
        encoding="utf-8",
    )

    print("\n[3/3] Creating startup batch file...")
    bat_file = DIST_DIR / "Start CounselOS.bat"
    bat_file.write_text(
        '@echo off\n'
        'title CounselOS - Legal Evidence Analysis\n'
        'echo.\n'
        'echo  ========================================\n'
        'echo   CounselOS - Starting...\n'
        'echo   Local-only legal evidence analysis\n'
        'echo  ========================================\n'
        'echo.\n'
        'echo  The application will open in your browser.\n'
        'echo  Keep this window open while using CounselOS.\n'
        'echo  Press Ctrl+C to stop the server.\n'
        'echo.\n'
        'if exist "%~dp0.env" (\n'
        '    echo  Configuration: .env found\n'
        ') else if exist "%~dp0.env.example" (\n'
        '    echo  NOTE: No .env file found.\n'
        '    echo  Copy .env.example to .env and configure your model path.\n'
        '    echo.\n'
        ')\n'
        'cd /d "%~dp0"\n'
        '"%~dp0CounselOS.exe"\n'
        'pause\n',
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"\nOutput folder: {DIST_DIR}")
    print(f"Executable:    {DIST_DIR / 'CounselOS.exe'}")
    print(f"Batch file:    {bat_file}")
    print(f"\nTo distribute:")
    print(f"  1. Copy the entire 'dist/CounselOS' folder")
    print(f"  2. User copies .env.example → .env and sets COUNSELOS_LLM_MODEL_PATH")
    print(f"  3. User double-clicks 'Start CounselOS.bat' or 'CounselOS.exe'")
    print(f"  4. Browser opens to http://127.0.0.1:8741")


if __name__ == "__main__":
    build()
