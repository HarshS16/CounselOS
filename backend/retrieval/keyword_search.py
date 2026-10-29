import logging
import re

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _escape_fts5_query(query: str) -> str:
    cleaned = re.sub(r'[^\w\s]', ' ', query, flags=re.UNICODE)
    tokens = cleaned.split()
    if not tokens:
        return '""'
    escaped = " ".join(f'"{t}"' for t in tokens if t.strip())
    return escaped if escaped else '""'


def keyword_search(
    db: Session,
    matter_id: str,
    query: str,
    limit: int = 20,
) -> list[tuple[str, str]]:
    fts_query = _escape_fts5_query(query)
    sql = text("""
        SELECT c.id, snippet(chunks_fts, 0, '>>>', '<<<', '...', 40) AS snip
        FROM chunks_fts
        JOIN chunks c ON c.rowid = chunks_fts.rowid
        JOIN documents d ON d.id = c.document_id
        WHERE chunks_fts MATCH :query
          AND d.matter_id = :matter_id
        ORDER BY rank
        LIMIT :limit
    """)
    try:
        rows = db.execute(sql, {"query": fts_query, "matter_id": matter_id, "limit": limit}).all()
        return [(row[0], row[1] or "") for row in rows]
    except Exception as e:
        logger.warning("FTS5 search failed: %s", e)
        return []


def index_chunk_fts(db: Session, chunk_rowid: int, text_content: str) -> None:
    sql = text("""
        INSERT INTO chunks_fts(rowid, text) VALUES (:rowid, :text)
    """)
    db.execute(sql, {"rowid": chunk_rowid, "text": text_content})


def remove_document_fts(db: Session, document_id: str) -> None:
    sql = text("""
        DELETE FROM chunks_fts
        WHERE rowid IN (
            SELECT rowid FROM chunks WHERE document_id = :document_id
        )
    """)
    db.execute(sql, {"document_id": document_id})
    db.commit()
