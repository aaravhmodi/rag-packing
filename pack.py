"""
Context packing strategies.

Each packer takes:
  question : str
  candidates : list[dict]  (from retrieve.py, sorted by score desc)
  budget : int             (max tokens in final context)

Returns:
  packed : list[dict]      (subset of candidates, in order)
"""
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_nlp = spacy.load("en_core_web_sm")


def _tok_len(text: str) -> int:
    return len(text.split())


def _entities(text: str) -> set[str]:
    doc = _nlp(text)
    return {ent.text.lower() for ent in doc.ents}


# ── Baseline 1: Naive Top-K ────────────────────────────────────────────────

def pack_topk(question, candidates, budget):
    packed, used = [], 0
    for c in candidates:
        n = _tok_len(c["text"])
        if used + n <= budget:
            packed.append(c)
            used += n
    return packed


# ── Baseline 2: MMR ────────────────────────────────────────────────────────

def pack_mmr(question, candidates, budget, lam=0.5):
    if not candidates:
        return []
    texts = [c["text"] for c in candidates]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([question, *texts])
    rel = cosine_similarity(matrix[0:1], matrix[1:]).ravel().tolist()

    selected_idx, packed, used = [], [], 0
    remaining = list(range(len(candidates)))

    while remaining:
        best_i, best_score = None, -1e9
        for i in remaining:
            n = _tok_len(candidates[i]["text"])
            if used + n > budget:
                continue
            if not selected_idx:
                mmr = rel[i]
            else:
                sim_to_sel = max(cosine_similarity(matrix[i + 1], matrix[j + 1]).item() for j in selected_idx)
                mmr = lam * rel[i] - (1 - lam) * sim_to_sel
            if mmr > best_score:
                best_i, best_score = i, mmr
        if best_i is None:
            break
        selected_idx.append(best_i)
        packed.append(candidates[best_i])
        used += _tok_len(candidates[best_i]["text"])
        remaining.remove(best_i)

    return packed


# ── Baseline 3: Focused Heuristic ─────────────────────────────────────────

def pack_focused(question, candidates, budget):
    q_ents = _entities(question)
    scored = []
    for c in candidates:
        ov = len(_entities(c["text"]) & q_ents) / max(len(q_ents), 1)
        score = 0.6 * c["score"] + 0.4 * ov
        scored.append((score, c))
    scored.sort(reverse=True, key=lambda x: x[0])

    packed, used = [], 0
    for _, c in scored:
        n = _tok_len(c["text"])
        if used + n <= budget:
            packed.append(c)
            used += n
    return packed


# ── Proposed: AnswerSurvival Packer ───────────────────────────────────────

def pack_answer_survival(question, candidates, budget):
    """
    score = 0.55 * query_similarity
          + 0.25 * entity_overlap
          + 0.10 * anchored_entity_bridge
          + 0.10 * brevity_score

    The single most query-relevant chunk is always seeded first (candidates arrive
    sorted by retrieval score), so the answer-bearing sentence can never be crowded
    out by tangential chunks that merely share entities with many other chunks.

    "Bridge" is restricted to entities that anchor back to the question itself (or
    the seed chunk) -- unrestricted cross-chunk entity overlap rewards citation/
    bibliography-style chunks that repeat names across many entries without being
    relevant to answering the question.
    """
    if not candidates:
        return []

    q_ents = _entities(question)
    all_ents = [_entities(c["text"]) for c in candidates]
    anchor_ents = set(q_ents) | all_ents[0]  # question entities + seed chunk's entities

    scored = []
    for i, c in enumerate(candidates):
        qs = c["score"]

        eo = len(all_ents[i] & q_ents) / max(len(q_ents), 1)

        bridge = len(all_ents[i] & anchor_ents) / max(len(anchor_ents), 1)

        words = _tok_len(c["text"])
        brevity = max(0.0, 1.0 - words / 100.0)

        score = 0.55 * qs + 0.25 * eo + 0.10 * bridge + 0.10 * brevity
        scored.append((score, i, c))

    seed = candidates[0]
    packed, used = [seed], _tok_len(seed["text"])
    if used > budget:
        return []

    scored.sort(reverse=True, key=lambda x: x[0])
    for _, i, c in scored:
        if i == 0:
            continue  # seed already packed
        n = _tok_len(c["text"])
        if used + n <= budget:
            packed.append(c)
            used += n
    return packed
