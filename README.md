# AnswerSurvivalRAG

Budget-constrained multi-hop RAG packing experiments with offline evaluation support.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run

```bash
# Evaluate all 4 methods on 200 HotpotQA validation questions, 160-token budget
python evaluate.py --dataset hotpotqa --budget 160 --n_questions 200

# Other datasets: squad, triviaqa, 2wikimultihopqa
python evaluate.py --dataset squad --budget 160 --n_questions 200

# Offline: evaluate from a local export instead of downloading from Hugging Face
python evaluate.py --dataset hotpotqa --budget 160 --n_questions 200 --data_file data/hotpot_qa_validation.jsonl

# Generate the single-run figures (per method: AIC/F1/EM/tokens with CI, failure modes,
# AIC-vs-F1 scatter, F1 violin, AIC gain over Top-K, per-question-type breakdown)
python plot.py --dataset hotpotqa --budget 160

# Full sweep: all 4 datasets x budgets [80,160,256,384,512], plus multi-budget and
# cross-dataset comparison figures
python sweep.py --n_questions 200

# Statistical significance of AnswerSurvival vs each baseline (paired bootstrap CI)
python significance.py --dataset hotpotqa --budget 160

# Qualitative examples (markdown table for paper appendix)
python qualitative.py --dataset hotpotqa --budget 160 --n_examples 5 --mode wins
```

### Datasets

| `--dataset` | Source | Notes |
|---|---|---|
| `hotpotqa` | `hotpotqa/hotpot_qa` (distractor) | Multi-hop, has `qtype` (bridge/comparison) |
| `squad` | `rajpurkar/squad_v2` | Single-hop, single-passage; unanswerable questions are filtered out |
| `triviaqa` | `mandarjoshi/trivia_qa` (rc.wikipedia) | Open-domain, longer/noisier contexts |
| `2wikimultihopqa` | `voidful/2WikiMultihopQA` | Multi-hop, has `qtype` |

All loaders go through `datasets_adapter.py`, which normalizes every dataset into a common
`{question, answer, qtype, chunks}` shape before retrieval/packing. `--data_file` accepts either
the dataset's native HF schema or this unified schema directly, for fully offline use.

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
| `answer_survival` | Entity bridge + brevity-aware scoring |

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
