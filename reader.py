"""
Reader: given packed context + question, produce an answer string.

This project originally used a Hugging Face QA pipeline, but the installed
transformers build in this environment does not expose the
``question-answering`` task. To keep the evaluation runnable end-to-end, we use
an offline spaCy-based extractor that scores sentences and short phrases from
the packed context.
"""
from __future__ import annotations

import re

import spacy

_nlp = spacy.load("en_core_web_sm")


def build_context(packed: list[dict]) -> str:
    return " ".join(c["text"] for c in packed)


def _content_terms(doc) -> set[str]:
    terms = set()
    for token in doc:
        if token.is_stop or token.is_punct or not token.is_alpha:
            continue
        lemma = token.lemma_.strip().lower()
        if lemma:
            terms.add(lemma)
    return terms


def _question_hint(question: str) -> set[str]:
    q = question.lower()
    if re.search(r"\bwho\b", q):
        return {"PERSON"}
    if re.search(r"\bwhen\b", q):
        return {"DATE", "TIME"}
    if re.search(r"\bwhere\b", q):
        return {"GPE", "LOC", "FAC"}
    if re.search(r"\bhow many\b|\bnumber of\b", q):
        return {"CARDINAL", "QUANTITY", "MONEY"}
    return set()


def _candidate_phrases(sent_doc) -> list[str]:
    phrases: list[str] = []

    for ent in sent_doc.ents:
        text = ent.text.strip()
        if text and text not in phrases:
            phrases.append(text)

    for chunk in sent_doc.noun_chunks:
        text = chunk.text.strip()
        if text and text not in phrases:
            phrases.append(text)

    sentence = sent_doc.text.strip()
    if sentence and sentence not in phrases:
        phrases.append(sentence)

    return phrases


def _score_sentence(sent_doc, question_terms: set[str], expected_labels: set[str]) -> float:
    sent_terms = _content_terms(sent_doc)
    overlap = len(sent_terms & question_terms)
    entity_bonus = 0.0
    for ent in sent_doc.ents:
        if ent.label_ in expected_labels:
            entity_bonus += 1.5
    length_penalty = max(len(sent_doc), 1) / 80.0
    return overlap + entity_bonus - length_penalty


def _score_phrase(phrase: str, question_terms: set[str], expected_labels: set[str], sent_doc) -> float:
    doc = _nlp(phrase)
    terms = _content_terms(doc)
    overlap = len(terms & question_terms)
    entity_bonus = 0.0
    for ent in doc.ents:
        if ent.label_ in expected_labels:
            entity_bonus += 2.0
    if expected_labels:
        for ent in sent_doc.ents:
            if ent.text == phrase and ent.label_ in expected_labels:
                entity_bonus += 2.0
    length_penalty = max(len(doc), 1) / 12.0
    return overlap + entity_bonus - length_penalty


def _fallback_answer(context: str) -> str:
    words = context.split()
    return " ".join(words[:20]).strip()


def generate_answer(question: str, packed: list[dict]) -> str:
    context = build_context(packed)
    if not context.strip():
        return ""

    q_doc = _nlp(question)
    c_doc = _nlp(context)
    question_terms = _content_terms(q_doc)
    expected_labels = _question_hint(question)

    best_sent = None
    best_sent_score = float("-inf")
    for sent in c_doc.sents:
        score = _score_sentence(sent, question_terms, expected_labels)
        if score > best_sent_score:
            best_sent = sent
            best_sent_score = score

    if best_sent is None:
        return _fallback_answer(context)

    best_phrase = best_sent.text.strip()
    best_phrase_score = _score_phrase(best_phrase, question_terms, expected_labels, best_sent)

    for phrase in _candidate_phrases(best_sent):
        score = _score_phrase(phrase, question_terms, expected_labels, best_sent)
        if score > best_phrase_score:
            best_phrase = phrase
            best_phrase_score = score

    return best_phrase.strip()
