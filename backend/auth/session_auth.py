import secrets
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_ALLOWED_ORIGINS = {
    "http://localhost",
    "http://127.0.0.1",
    "https://localhost",
    "https://127.0.0.1",
    "tauri://localhost",
    "http://tauri.localhost",
    "https://tauri.localhost",
}

_session_token: str = ""
_bearer_scheme = HTTPBearer(auto_error=False)


def initialize_session() -> str:
    global _session_token
    _session_token = secrets.token_urlsafe(48)
    return _session_token


def get_session_token() -> str:
    if not _session_token:
        initialize_session()
    return _session_token


def _is_allowed_origin(origin: str | None) -> bool:
    if origin is None:
        return True
    normalized = origin.rstrip("/")
    if normalized in _ALLOWED_ORIGINS:
        return True
    for allowed in _ALLOWED_ORIGINS:
        if normalized.startswith(allowed + ":"):
            return True
    return False


async def verify_session(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    origin = request.headers.get("origin")
    if not _is_allowed_origin(origin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin not allowed",
        )

    if not _session_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session not initialized",
        )

    if credentials is None or credentials.credentials != _session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing session token",
            headers={"WWW-Authenticate": "Bearer"},
        )
