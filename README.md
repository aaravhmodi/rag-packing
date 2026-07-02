# AnswerSurvivalRAG

Reproduction and extension of budget-constrained multi-hop RAG packing research.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run

```bash
# Evaluate all 4 methods on 200 HotpotQA validation questions, 160-token budget
python evaluate.py --budget 160 --n_questions 200

# Generate all 5 plots
python plot.py --budget 160
```

## Methods

| Method | Description |
|---|---|
| `topk` | Naive: fill budget with highest-similarity chunks |
| `mmr` | Maximal Marginal Relevance balances relevance + diversity |
| `focused` | Heuristic: query similarity + entity overlap |
| `answer_survival` | **Proposed**: entity bridge + brevity-aware scoring |

## Scoring formula (AnswerSurvival)

```
score = 0.45 * query_similarity
      + 0.25 * entity_overlap
      + 0.20 * cross_chunk_entity_bridge
      + 0.10 * brevity_score
```

## Metrics

- **AIC** – Answer-in-Context rate (does gold answer appear in packed context?)
- **F1** – Token-level F1 between predicted and gold answer
- **EM** – Exact match
- **Tokens** – Average packed token count
