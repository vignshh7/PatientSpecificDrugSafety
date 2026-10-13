"""Dense/semantic retrieval over the evidence corpus.

Two backends are supported behind the same interface:

- "st_faiss": sentence-transformers embeddings + a FAISS index (the stack
  named in the project's architecture slides: BGE-family embeddings + FAISS).
  Used automatically when `sentence-transformers` and `faiss` are importable
  and the configured model can be loaded.
- "tfidf": a scikit-learn TF-IDF vectorizer + cosine similarity. Always
  available (scikit-learn is a hard dependency), so the system keeps working
  end-to-end even with no internet access / no downloaded embedding model at
  demo time.

The embedding model name is configurable via EMBEDDING_MODEL (default:
a small, fast sentence-transformers model). BAAI/bge-m3 can be substituted
if the hardware/bandwidth is available before a demo.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@dataclass
class ScoredChunk:
    chunk: dict
    score: float


class Retriever:
    """Backs retrieval with FAISS+embeddings when available, else TF-IDF."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self._texts = [self._chunk_text(c) for c in chunks]
        self.backend = "tfidf"
        self._st_model = None
        self._faiss_index = None
        self._tfidf = None
        self._tfidf_matrix = None

        self._try_init_embeddings()
        if self.backend == "tfidf":
            self._init_tfidf()

    @staticmethod
    def _chunk_text(chunk: dict) -> str:
        # Prepend drug + section so lexical/semantic signal captures context,
        # not just the raw clinical sentence.
        return f"{chunk['drug_name']} | {chunk['section']} | {chunk['text']}"

    def _try_init_embeddings(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
        except ImportError:
            return

        try:
            model = SentenceTransformer(EMBEDDING_MODEL)
            vectors = model.encode(
                self._texts, normalize_embeddings=True, show_progress_bar=False
            )
            vectors = np.asarray(vectors, dtype="float32")
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
        except Exception:
            # Model not downloaded / no network / incompatible env -> fall back.
            return

        self._st_model = model
        self._faiss_index = index
        self.backend = "st_faiss"

    def _init_tfidf(self) -> None:
        self._tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._tfidf_matrix = self._tfidf.fit_transform(self._texts)

    def search(self, query: str, top_k: int = 5, drug_id: str | None = None) -> list[ScoredChunk]:
        candidate_idx = list(range(len(self.chunks)))
        if drug_id is not None:
            candidate_idx = [i for i in candidate_idx if self.chunks[i]["drug_id"] == drug_id]
        if not candidate_idx:
            return []

        if self.backend == "st_faiss":
            scores = self._search_st(query)
        else:
            scores = self._search_tfidf(query)

        ranked = sorted(
            ((i, scores[i]) for i in candidate_idx), key=lambda x: x[1], reverse=True
        )
        return [ScoredChunk(chunk=self.chunks[i], score=float(s)) for i, s in ranked[:top_k]]

    def _search_st(self, query: str) -> np.ndarray:
        q_vec = self._st_model.encode([query], normalize_embeddings=True, show_progress_bar=False)
        q_vec = np.asarray(q_vec, dtype="float32")
        sims, idxs = self._faiss_index.search(q_vec, len(self.chunks))
        scores = np.zeros(len(self.chunks), dtype="float32")
        for rank_pos, idx in enumerate(idxs[0]):
            scores[idx] = sims[0][rank_pos]
        return scores

    def _search_tfidf(self, query: str) -> np.ndarray:
        q_vec = self._tfidf.transform([query])
        sims = cosine_similarity(q_vec, self._tfidf_matrix)[0]
        return sims
