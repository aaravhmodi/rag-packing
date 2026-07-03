"""
Retrieval stage: given a question, fetch top-N candidate chunks
from the dataset's chunked context (see datasets_adapter.py).
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve(question: str, chunks: list[dict], top_n: int = 20) -> list[dict]:
    """Return top-N chunks by TF-IDF cosine similarity."""
    if not chunks:
        return []
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([question, *texts])
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel().tolist()
    for c, s in zip(chunks, scores):
        c["score"] = s
    return sorted(chunks, key=lambda x: x["score"], reverse=True)[:top_n]
