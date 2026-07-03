"""
Unified dataset adapter.

Produces a common example shape regardless of source dataset:

  {
    "question": str,
    "answer": str,
    "qtype": str | None,   # e.g. "bridge" / "comparison" for multi-hop sets
    "chunks": [{"title": str, "sent_idx": int, "text": str}, ...],
  }

Supported --dataset values: hotpotqa, squad, triviaqa, 2wikimultihopqa
For any of these, pass --data_file pointing at a local export in either:
  (a) the dataset's native HF schema (same as prepare_hotpotqa.py produces), or
  (b) this unified schema directly (question/answer/qtype/chunks) -- useful for
      fully offline / custom data.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from datasets import Dataset, load_dataset

_SENT_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [s.strip() for s in _SENT_RE.split(text) if s.strip()]


def _hf_token() -> str | None:
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
    if token:
        return token
    env_path = Path(".env")
    if not env_path.exists():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in {"HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"}:
            return value.strip().strip("'\"")
    return None


def _is_unified_record(ex: dict) -> bool:
    return "chunks" in ex and "answer" in ex and "question" in ex


# ── Per-dataset example -> unified example ─────────────────────────────────

def _from_hotpotqa(ex: dict) -> dict | None:
    context = ex["context"]
    chunks = []
    for title, sentences in zip(context["title"], context["sentences"]):
        for i, sent in enumerate(sentences):
            chunks.append({"title": title, "sent_idx": i, "text": sent.strip()})
    answer = ex.get("answer", "")
    if not answer or not chunks:
        return None
    return {
        "question": ex["question"],
        "answer": answer,
        "qtype": ex.get("type"),
        "chunks": chunks,
    }


def _from_squad(ex: dict) -> dict | None:
    answers = ex.get("answers", {}) or {}
    texts = answers.get("text", [])
    if not texts:
        return None  # skip unanswerable questions -- AIC/EM/F1 aren't meaningful without a gold span
    context = ex.get("context", "")
    title = ex.get("title", "")
    chunks = [{"title": title, "sent_idx": i, "text": s}
              for i, s in enumerate(_split_sentences(context))]
    if not chunks:
        return None
    return {
        "question": ex["question"],
        "answer": texts[0],
        "qtype": None,
        "chunks": chunks,
    }


def _from_triviaqa(ex: dict) -> dict | None:
    answer = (ex.get("answer") or {}).get("value", "")
    if not answer:
        return None
    chunks = []
    entity_pages = ex.get("entity_pages") or {}
    titles = entity_pages.get("title", [])
    contexts = entity_pages.get("wiki_context", [])
    for title, context in zip(titles, contexts):
        for i, s in enumerate(_split_sentences(context)):
            chunks.append({"title": title, "sent_idx": i, "text": s})
    if not chunks:
        return None
    return {
        "question": ex["question"],
        "answer": answer,
        "qtype": None,
        "chunks": chunks,
    }


def _from_2wikimultihopqa(ex: dict) -> dict | None:
    context = ex.get("context")
    chunks = []
    if isinstance(context, dict) and "title" in context and "sentences" in context:
        for title, sentences in zip(context["title"], context["sentences"]):
            for i, sent in enumerate(sentences):
                chunks.append({"title": title, "sent_idx": i, "text": sent.strip()})
    elif isinstance(context, list):
        for title, sentences in context:
            for i, sent in enumerate(sentences):
                chunks.append({"title": title, "sent_idx": i, "text": sent.strip()})
    answer = ex.get("answer", "")
    if not answer or not chunks:
        return None
    return {
        "question": ex["question"],
        "answer": answer,
        "qtype": ex.get("type"),
        "chunks": chunks,
    }


_DATASETS = {
    "hotpotqa": {
        "hf_id": "hotpotqa/hotpot_qa",
        "hf_config": "distractor",
        "convert": _from_hotpotqa,
    },
    "squad": {
        "hf_id": "rajpurkar/squad_v2",
        "hf_config": None,
        "convert": _from_squad,
    },
    "triviaqa": {
        "hf_id": "mandarjoshi/trivia_qa",
        "hf_config": "rc.wikipedia",
        "convert": _from_triviaqa,
    },
    "2wikimultihopqa": {
        "hf_id": "voidful/2WikiMultihopQA",
        "hf_config": None,
        "convert": _from_2wikimultihopqa,
    },
}


def _load_hf_split(dataset: str, split: str):
    cfg = _DATASETS[dataset]
    kwargs = {"token": _hf_token()}
    if cfg["hf_config"]:
        return load_dataset(cfg["hf_id"], cfg["hf_config"], split=split, **kwargs)
    return load_dataset(cfg["hf_id"], split=split, **kwargs)


def _load_local(path: Path):
    suffix = path.suffix.lower()
    if path.is_dir():
        from datasets import load_from_disk
        return load_from_disk(str(path))
    if suffix in {".json", ".jsonl"}:
        return Dataset.from_json(str(path))
    if suffix == ".csv":
        return Dataset.from_csv(str(path))
    if suffix == ".parquet":
        return Dataset.from_parquet(str(path))
    raise ValueError(f"Unsupported local dataset format: {path}")


def load_examples(dataset: str, split: str, data_file: str | None = None) -> list[dict]:
    """Return a list of unified example dicts for the given dataset."""
    if dataset not in _DATASETS:
        raise ValueError(f"Unknown dataset '{dataset}'. Choose from: {sorted(_DATASETS)}")

    convert = _DATASETS[dataset]["convert"]

    if data_file:
        path = Path(data_file)
        if not path.exists():
            raise FileNotFoundError(f"Local dataset file not found: {path}")
        raw = _load_local(path)
    else:
        try:
            raw = _load_hf_split(dataset, split)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load '{dataset}' from Hugging Face. Export it locally first "
                f"(see prepare_dataset.py) and pass --data_file, or check network access."
            ) from exc

    examples = []
    for ex in raw:
        if _is_unified_record(ex):
            examples.append(ex)
            continue
        converted = convert(ex)
        if converted is not None:
            examples.append(converted)
    return examples
