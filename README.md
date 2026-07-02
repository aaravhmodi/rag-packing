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

# Offline: evaluate from a local export instead of downloading from Hugging Face
python evaluate.py --budget 160 --n_questions 200 --data_file data/hotpot_qa_validation.jsonl

# Generate all 5 plots
python plot.py --budget 160
```

## Offline Data

If this environment cannot reach Hugging Face, export the dataset elsewhere and copy it into the repo as one of:

- `data/hotpot_qa_validation.jsonl`
- `data/hotpot_qa_validation.json`
- `data/hotpot_qa_validation.csv`
- a directory saved with `datasets.save_to_disk()`

Each record should contain:

- `question`
- `answer`
- `context`, with HotpotQA-style supporting sentences at `context["sentences"]`

To generate that file when you do have network access:

```bash
python prepare_hotpotqa.py --split validation --output data/hotpot_qa_validation.jsonl
```

Or save the full dataset directory for offline reuse:

```bash
python prepare_hotpotqa.py --split validation --output data/hotpot_qa_validation --format disk
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
