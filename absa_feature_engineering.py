"""
Feature engineering helpers for ABSA research workflows.

Provides:
- BPE tokenization using a Hugging Face tokenizer
- BIO tagging for aspect spans
- context-window extraction around aspect mentions
- TF-IDF feature matrices
- PMI-style association scores between aspects and terms
- optional dependency parsing via spaCy
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Sequence, Tuple
import math
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from transformers import AutoTokenizer
except Exception:
    AutoTokenizer = None

try:
    import spacy
except Exception:
    spacy = None


_WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_'-]*")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class AspectSpan:
    """Simple span representation for aspect annotations."""

    aspect: str
    start_token: int
    end_token: int


@lru_cache(maxsize=8)
def _get_bpe_tokenizer(model_name: str = "bert-base-uncased"):
    if AutoTokenizer is None:
        return None
    try:
        return AutoTokenizer.from_pretrained(model_name, use_fast=True)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _get_spacy_model():
    if spacy is None:
        return None
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        return None


def simple_word_tokens(text: str) -> List[str]:
    """Return lightweight word tokens for downstream BIO alignment."""
    return _WORD_PATTERN.findall(str(text))


def bpe_tokenize(text: str, model_name: str = "bert-base-uncased") -> List[str]:
    """Tokenize text with a BPE/WordPiece tokenizer when available."""
    tokenizer = _get_bpe_tokenizer(model_name)
    if tokenizer is None:
        return simple_word_tokens(text)
    return tokenizer.tokenize(str(text))


def sentence_split(text: str) -> List[str]:
    """Split text into sentences with a lightweight regex fallback."""
    text = str(text).strip()
    if not text:
        return []

    try:
        import nltk

        return [sentence.strip() for sentence in nltk.sent_tokenize(text) if sentence.strip()]
    except Exception:
        return [sentence.strip() for sentence in _SENTENCE_SPLIT_PATTERN.split(text) if sentence.strip()]


def _find_span_tokens(tokens: Sequence[str], aspect_tokens: Sequence[str]) -> List[int]:
    if not tokens or not aspect_tokens:
        return []

    lower_tokens = [token.lower() for token in tokens]
    lower_aspect = [token.lower() for token in aspect_tokens]
    span_length = len(lower_aspect)
    matches: List[int] = []

    for index in range(0, len(lower_tokens) - span_length + 1):
        if lower_tokens[index:index + span_length] == lower_aspect:
            matches.append(index)
    return matches


def annotate_bio_tags(text: str, aspect_terms: Sequence[str]) -> pd.DataFrame:
    """Annotate tokens with BIO tags for one or more aspect terms."""
    tokens = simple_word_tokens(text)
    tags = ["O"] * len(tokens)
    lowered = [token.lower() for token in tokens]

    spans: List[AspectSpan] = []
    for aspect in aspect_terms:
        aspect_tokens = simple_word_tokens(aspect)
        if not aspect_tokens:
            continue
        for start in _find_span_tokens(tokens, aspect_tokens):
            end = start + len(aspect_tokens)
            if any(tag != "O" for tag in tags[start:end]):
                continue
            tags[start] = f"B-{aspect}"
            for index in range(start + 1, end):
                tags[index] = f"I-{aspect}"
            spans.append(AspectSpan(aspect=aspect, start_token=start, end_token=end - 1))
            break

    return pd.DataFrame(
        {
            "token": tokens,
            "token_lower": lowered,
            "bio_tag": tags,
        }
    )


def build_context_pairs(text: str, aspect_terms: Sequence[str], window_size: int = 2) -> List[Dict[str, str]]:
    """Build aspect-context pairs from sentence windows around aspect mentions."""
    sentences = sentence_split(text)
    if not sentences:
        return []

    rows: List[Dict[str, str]] = []
    normalized_sentences = [sentence.lower() for sentence in sentences]
    aspects = [aspect.strip() for aspect in aspect_terms if aspect and str(aspect).strip()]

    for aspect in aspects:
        aspect_lower = aspect.lower()
        matching_indices = [index for index, sentence in enumerate(normalized_sentences) if aspect_lower in sentence]
        if not matching_indices:
            matching_indices = [0]

        for index in matching_indices:
            left = max(0, index - window_size)
            right = min(len(sentences), index + window_size + 1)
            context = " ".join(sentences[left:right])
            rows.append(
                {
                    "aspect": aspect,
                    "target_sentence": sentences[index],
                    "context_window": context,
                    "window_start": str(left),
                    "window_end": str(right - 1),
                }
            )

    return rows


def compute_tfidf_features(texts: Sequence[str], max_features: int = 5000) -> Tuple[TfidfVectorizer, np.ndarray, List[str]]:
    """Compute a TF-IDF matrix and return the vectorizer, matrix, and feature names."""
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([str(text) for text in texts])
    feature_names = vectorizer.get_feature_names_out().tolist()
    return vectorizer, matrix, feature_names


def compute_pmi_scores(texts: Sequence[str], aspect_terms: Sequence[str], top_k: int = 10) -> Dict[str, List[Tuple[str, float]]]:
    """Compute simple PMI scores between aspect terms and nearby words."""
    aspect_terms = [aspect.lower() for aspect in aspect_terms if aspect and str(aspect).strip()]
    texts = [str(text).lower() for text in texts if str(text).strip()]
    if not aspect_terms or not texts:
        return {}

    document_count = len(texts)
    aspect_doc_counts: Dict[str, int] = {aspect: 0 for aspect in aspect_terms}
    word_doc_counts: Dict[str, int] = {}
    pair_doc_counts: Dict[Tuple[str, str], int] = {}

    for text in texts:
        tokens = set(simple_word_tokens(text.lower()))
        for token in tokens:
            word_doc_counts[token] = word_doc_counts.get(token, 0) + 1

        for aspect in aspect_terms:
            if aspect in text:
                aspect_doc_counts[aspect] += 1
                aspect_tokens = set(simple_word_tokens(aspect))
                context_tokens = tokens - aspect_tokens
                for token in context_tokens:
                    pair_doc_counts[(aspect, token)] = pair_doc_counts.get((aspect, token), 0) + 1

    results: Dict[str, List[Tuple[str, float]]] = {}
    smoothing = 1e-9
    for aspect in aspect_terms:
        scored_terms: List[Tuple[str, float]] = []
        aspect_prob = (aspect_doc_counts.get(aspect, 0) + smoothing) / document_count
        for token, word_count in word_doc_counts.items():
            pair_count = pair_doc_counts.get((aspect, token), 0)
            if pair_count == 0:
                continue
            pair_prob = (pair_count + smoothing) / document_count
            word_prob = (word_count + smoothing) / document_count
            pmi = math.log2(pair_prob / (aspect_prob * word_prob))
            scored_terms.append((token, float(pmi)))

        scored_terms.sort(key=lambda item: item[1], reverse=True)
        results[aspect] = scored_terms[:top_k]

    return results


def dependency_parse(text: str) -> List[Dict[str, str]]:
    """Return dependency relations when spaCy is available."""
    nlp = _get_spacy_model()
    if nlp is None:
        return []

    doc = nlp(str(text))
    rows: List[Dict[str, str]] = []
    for token in doc:
        rows.append(
            {
                "token": token.text,
                "lemma": token.lemma_,
                "dep": token.dep_,
                "head": token.head.text,
                "pos": token.pos_,
            }
        )
    return rows


def build_feature_preview(text: str, aspect_terms: Sequence[str], window_size: int = 2) -> Dict[str, object]:
    """Build a compact feature preview bundle for app or notebook use."""
    tokens = simple_word_tokens(text)
    bio_df = annotate_bio_tags(text, aspect_terms)
    context_rows = build_context_pairs(text, aspect_terms, window_size=window_size)
    dependencies = dependency_parse(text)

    return {
        "tokens": tokens,
        "bpe_tokens": bpe_tokenize(text),
        "bio_table": bio_df,
        "context_pairs": pd.DataFrame(context_rows),
        "dependencies": pd.DataFrame(dependencies),
    }
