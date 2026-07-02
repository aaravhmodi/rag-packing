"""
Retrieval stage: given a question, fetch top-N candidate chunks
from the HotpotQA supporting facts.
"""
import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_supporting_facts(example, max_tokens=60):
    """Split each supporting sentence into a chunk dict."""
    chunks = []
    for title, sentences in example["context"]["sentences"]:
        for i, sent in enumerate(sentences):
            chunks.append({"title": title, "sent_idx": i, "text": sent.strip()})
    return chunks


def retrieve(question: str, chunks: list[dict], top_n: int = 20) -> list[dict]:
    """Return top-N chunks by embedding similarity."""
    texts = [c["text"] for c in chunks]
    q_emb = model.encode(question, convert_to_tensor=True)
    c_embs = model.encode(texts, convert_to_tensor=True)
    scores = util.cos_sim(q_emb, c_embs)[0].cpu().tolist()
    for c, s in zip(chunks, scores):
        c["score"] = s
    return sorted(chunks, key=lambda x: x["score"], reverse=True)[:top_n]
