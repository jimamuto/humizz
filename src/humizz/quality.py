from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import pstdev

FORMAL_AI_TERMS = {
    "additionally",
    "aid",
    "aids",
    "considerable",
    "crucial",
    "delve",
    "elevate",
    "ensure",
    "essential",
    "facilitate",
    "furthermore",
    "hence",
    "moreover",
    "nevertheless",
    "nonetheless",
    "significant",
    "substantial",
    "ought",
    "prudently",
    "therefore",
    "utilize",
    "wholly",
}
CHATTER_MARKERS = (
    "as an ai",
    "here's",
    "here is",
    "i hope",
    "let me know",
    "please note",
    "translation:",
    "explanation:",
)


@dataclass(frozen=True)
class QualityReport:
    input_chars: int
    output_chars: int
    length_delta: int
    length_ratio: float
    warnings: tuple[str, ...]
    sentence_count: int
    average_sentence_words: float
    sentence_word_stddev: float
    formal_term_count: int


def assess_quality(input_text: str, output_text: str) -> QualityReport:
    input_len = len(input_text.strip())
    output_len = len(output_text.strip())
    warnings: list[str] = []

    if output_len == 0:
        warnings.append("empty-output")

    ratio = output_len / input_len if input_len else 0.0
    if input_len and ratio < 0.45:
        warnings.append("large-shrink")
    if input_len and ratio > 1.8:
        warnings.append("large-expansion")

    sentence_lengths = sentence_word_counts(output_text)
    sentence_count = len(sentence_lengths)
    average_sentence_words = sum(sentence_lengths) / sentence_count if sentence_count else 0.0
    sentence_word_stddev = pstdev(sentence_lengths) if sentence_count > 1 else 0.0
    formal_term_count = count_formal_terms(output_text)

    if average_sentence_words > 24:
        warnings.append("long-sentences")
    if sentence_count >= 3 and sentence_word_stddev < 3.0:
        warnings.append("low-burstiness")
    if formal_term_count:
        warnings.append("too-formal")
    if has_assistant_chatter(output_text):
        warnings.append("assistant-chatter")

    return QualityReport(
        input_chars=input_len,
        output_chars=output_len,
        length_delta=output_len - input_len,
        length_ratio=round(ratio, 3),
        warnings=tuple(warnings),
        sentence_count=sentence_count,
        average_sentence_words=round(average_sentence_words, 2),
        sentence_word_stddev=round(sentence_word_stddev, 2),
        formal_term_count=formal_term_count,
    )


def sentence_word_counts(text: str) -> list[int]:
    sentences = [part.strip() for part in re.split(r"[.!?]+", text) if part.strip()]
    return [len(re.findall(r"\b[\w']+\b", sentence)) for sentence in sentences]


def count_formal_terms(text: str) -> int:
    words = re.findall(r"\b[\w']+\b", text.lower())
    return sum(1 for word in words if word in FORMAL_AI_TERMS)


def has_assistant_chatter(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in CHATTER_MARKERS)


def warning_score(report: QualityReport) -> int:
    weights = {
        "empty-output": 10,
        "assistant-chatter": 8,
        "large-shrink": 5,
        "large-expansion": 5,
        "long-sentences": 3,
        "low-burstiness": 2,
        "too-formal": 2,
    }
    return sum(weights.get(warning, 1) for warning in report.warnings)
