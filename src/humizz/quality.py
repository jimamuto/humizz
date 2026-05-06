from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityReport:
    input_chars: int
    output_chars: int
    length_delta: int
    length_ratio: float
    warnings: tuple[str, ...]


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

    return QualityReport(
        input_chars=input_len,
        output_chars=output_len,
        length_delta=output_len - input_len,
        length_ratio=round(ratio, 3),
        warnings=tuple(warnings),
    )
