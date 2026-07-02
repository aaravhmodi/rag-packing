"""
Evaluation metrics.
"""
import re
import string
from collections import Counter


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def token_f1(pred: str, gold: str) -> float:
    pred_toks = normalize(pred).split()
    gold_toks = normalize(gold).split()
    common = Counter(pred_toks) & Counter(gold_toks)
    n_common = sum(common.values())
    if n_common == 0:
        return 0.0
    p = n_common / len(pred_toks)
    r = n_common / len(gold_toks)
    return 2 * p * r / (p + r)


def exact_match(pred: str, gold: str) -> float:
    return float(normalize(pred) == normalize(gold))


def answer_in_context(answer: str, context_chunks: list[dict]) -> bool:
    """True if the gold answer string appears (normalized) in any packed chunk."""
    norm_ans = normalize(answer)
    for c in context_chunks:
        if norm_ans in normalize(c["text"]):
            return True
    return False


def avg_token_cost(packed_list: list[list[dict]]) -> float:
    costs = [sum(len(c["text"].split()) for c in p) for p in packed_list]
    return sum(costs) / max(len(costs), 1)
