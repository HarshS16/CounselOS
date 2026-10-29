# CounselOS Data Retention Policy

## What Is Stored

| Data Type | Location | Encryption |
|-----------|----------|-----------|
| Original documents | data/originals/{matter_id}/ | At rest (backup) |
| Extracted text | SQLite database | At rest (backup) |
| Embeddings | FAISS index files | At rest (backup) |
| Analysis results | SQLite database | At rest (backup) |
| Review decisions | SQLite database | At rest (backup) |
| Audit events | SQLite database | At rest (backup) |
| Export reports | data/exports/ | User-managed |
| Backups | data/backups/ | Encrypted (Fernet/PBKDF2) |

## Deletion Workflow

When a matter is deleted:
1. Original files in data/originals/{matter_id}/ are removed
2. All database records (documents, pages, chunks, claims, events, findings, reviews) are cascade-deleted
3. FAISS index entries for the matter's chunks are removed
4. FTS5 index entries are removed
5. Export reports remain (user manages separately)
6. Audit events are retained for the configured retention period
7. Backups that include the matter remain until manually deleted

**Important**: Deletion does not reach backups created before deletion. Users must manage backup lifecycle separately.

## Backup Lifecycle

- Backups are encrypted with a user-provided password
- Password is never stored by the application
- If the password is lost, the backup cannot be recovered
- Users should maintain their own backup rotation policy
