"""
CounselOS Desktop Launcher
Starts the FastAPI backend, serves the built frontend, and opens the browser.
"""

import logging
import os
import signal
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("counselos.launcher")


def get_base_dir() -> Path:
    """Get the base directory — handles both dev and PyInstaller frozen mode."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def find_frontend_dist() -> Path | None:
    """Locate the built frontend dist folder."""
    base = get_base_dir()
    candidates = [
        base / "frontend_dist",
        base / "apps" / "desktop" / "dist",
        Path(__file__).parent / "apps" / "desktop" / "dist",
    ]
    for p in candidates:
        if p.is_dir() and (p / "index.html").exists():
            return p
    return None


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_server(port: int, timeout: float = 30.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.3)
    return False


def main():
    port = int(os.environ.get("COUNSELOS_API_PORT", "8741"))

    if is_port_in_use(port):
        logger.info("CounselOS already running on port %d — opening browser", port)
        webbrowser.open(f"http://127.0.0.1:{port}")
        return

    dist_dir = find_frontend_dist()
    if dist_dir:
        os.environ["COUNSELOS_FRONTEND_DIST"] = str(dist_dir)
        logger.info("Frontend dist: %s", dist_dir)
    else:
        logger.warning("No frontend dist found — API-only mode")

    logger.info("Starting CounselOS on 127.0.0.1:%d ...", port)

    import uvicorn
    from backend.main import create_app

    app = create_app()

    if dist_dir:
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse

        index_html = dist_dir / "index.html"

        @app.get("/")
        async def serve_index():
            return FileResponse(index_html)

        app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="static-assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            file_path = dist_dir / full_path
            if file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(index_html)

    def open_browser():
        if wait_for_server(port):
            logger.info("Server ready — opening browser")
            webbrowser.open(f"http://127.0.0.1:{port}")
        else:
            logger.error("Server did not start within 30 seconds")

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    def handle_signal(sig, frame):
        logger.info("Shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("CounselOS stopped")


if __name__ == "__main__":
    main()
