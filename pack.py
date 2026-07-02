"""
Context packing strategies.

Each packer takes:
  question : str
  candidates : list[dict]  (from retrieve.py, sorted by score desc)
  budget : int             (max tokens in final context)

Returns:
  packed : list[dict]      (subset of candidates, in order)
"""
import re
import spacy
from sentence_transformers import SentenceTransformer, util

_nlp = spacy.load("en_core_web_sm")
_model = SentenceTransformer("all-MiniLM-L6-v2")


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
    texts = [c["text"] for c in candidates]
    q_emb = _model.encode(question, convert_to_tensor=True)
    embs = _model.encode(texts, convert_to_tensor=True)
    rel = util.cos_sim(q_emb, embs)[0].tolist()

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
                sim_to_sel = max(
                    util.cos_sim(embs[i], embs[j]).item()
                    for j in selected_idx
                )
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
    score = 0.45 * query_similarity
          + 0.25 * entity_overlap
          + 0.20 * cross_chunk_entity_bridge
          + 0.10 * brevity_score
    """
    q_ents = _entities(question)
    all_ents = [_entities(c["text"]) for c in candidates]

    scored = []
    for i, c in enumerate(candidates):
        qs = c["score"]

        eo = len(all_ents[i] & q_ents) / max(len(q_ents), 1)

        bridge = 0.0
        for j, other_ents in enumerate(all_ents):
            if j != i:
                shared = len(all_ents[i] & other_ents)
                if shared > 0:
                    bridge += shared
        bridge = min(bridge / 10.0, 1.0)

        words = _tok_len(c["text"])
        brevity = max(0.0, 1.0 - words / 100.0)

        score = 0.45 * qs + 0.25 * eo + 0.20 * bridge + 0.10 * brevity
        scored.append((score, c))

    scored.sort(reverse=True, key=lambda x: x[0])

    packed, used = [], 0
    for _, c in scored:
        n = _tok_len(c["text"])
        if used + n <= budget:
            packed.append(c)
            used += n
    return packed
