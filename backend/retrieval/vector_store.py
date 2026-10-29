import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, dimension: int) -> None:
        import faiss

        self._dimension = dimension
        self._index = faiss.IndexFlatIP(dimension)
        self._id_to_pos: dict[str, int] = {}
        self._pos_to_id: dict[int, str] = {}
        self._next_pos = 0

    @property
    def count(self) -> int:
        return len(self._id_to_pos)

    def add(self, embeddings: np.ndarray, ids: list[str]) -> None:
        if len(embeddings) == 0:
            return
        if len(embeddings) != len(ids):
            raise ValueError("embeddings and ids must have the same length")

        vecs = embeddings.astype(np.float32)
        if vecs.ndim == 1:
            vecs = vecs.reshape(1, -1)

        for i, chunk_id in enumerate(ids):
            if chunk_id in self._id_to_pos:
                continue
            single = vecs[i : i + 1]
            self._index.add(single)
            pos = self._next_pos
            self._id_to_pos[chunk_id] = pos
            self._pos_to_id[pos] = chunk_id
            self._next_pos += 1

    def search(self, query_embedding: np.ndarray, k: int = 10) -> list[tuple[str, float]]:
        if self.count == 0:
            return []

        q = query_embedding.astype(np.float32)
        if q.ndim == 1:
            q = q.reshape(1, -1)

        actual_k = min(k, self.count)
        scores, indices = self._index.search(q, actual_k)

        results = []
        for score, pos in zip(scores[0], indices[0]):
            if pos < 0:
                continue
            chunk_id = self._pos_to_id.get(int(pos))
            if chunk_id is not None:
                results.append((chunk_id, float(score)))
        return results

    def remove(self, ids: list[str]) -> None:
        # FAISS IndexFlatIP doesn't support efficient removal.
        # Rebuild the index without the removed IDs.
        import faiss

        remove_set = set(ids)
        remaining = [
            (cid, pos)
            for cid, pos in self._id_to_pos.items()
            if cid not in remove_set
        ]
        if len(remaining) == len(self._id_to_pos):
            return

        old_index = self._index
        self._index = faiss.IndexFlatIP(self._dimension)
        self._id_to_pos.clear()
        self._pos_to_id.clear()
        self._next_pos = 0

        if remaining:
            remaining.sort(key=lambda x: x[1])
            positions = np.array([pos for _, pos in remaining], dtype=np.int64)
            vecs = np.empty((len(positions), self._dimension), dtype=np.float32)
            for i, pos in enumerate(positions):
                old_index.reconstruct(int(pos), vecs[i])

            self._index.add(vecs)
            for i, (cid, _) in enumerate(remaining):
                self._id_to_pos[cid] = i
                self._pos_to_id[i] = cid
            self._next_pos = len(remaining)

    def save(self, path: Path) -> None:
        import faiss

        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(path / "index.faiss"))
        mapping = {
            "id_to_pos": self._id_to_pos,
            "pos_to_id": {str(k): v for k, v in self._pos_to_id.items()},
            "next_pos": self._next_pos,
        }
        with open(path / "mapping.json", "w") as f:
            json.dump(mapping, f)
        logger.info("Saved vector store with %d vectors to %s", self.count, path)

    def load(self, path: Path) -> None:
        import faiss

        index_path = path / "index.faiss"
        mapping_path = path / "mapping.json"
        if not index_path.exists() or not mapping_path.exists():
            logger.warning("No saved vector store found at %s", path)
            return

        self._index = faiss.read_index(str(index_path))
        with open(mapping_path) as f:
            mapping = json.load(f)
        self._id_to_pos = mapping["id_to_pos"]
        self._pos_to_id = {int(k): v for k, v in mapping["pos_to_id"].items()}
        self._next_pos = mapping["next_pos"]
        logger.info("Loaded vector store with %d vectors from %s", self.count, path)
