from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RewriteMode:
    name: str
    instruction: str


MODES: dict[str, RewriteMode] = {
    "natural": RewriteMode(
        "natural",
        "Rewrite the text so it sounds natural, clear, and human while preserving meaning.",
    ),
    "concise": RewriteMode(
        "concise",
        "Rewrite the text to be shorter, direct, and natural while preserving key meaning.",
    ),
    "formal": RewriteMode(
        "formal",
        "Rewrite the text in a polished formal tone while preserving meaning.",
    ),
    "casual": RewriteMode(
        "casual",
        "Rewrite the text in a relaxed conversational tone while preserving meaning.",
    ),
}


def get_mode(name: str) -> RewriteMode:
    try:
        return MODES[name]
    except KeyError as exc:
        valid = ", ".join(sorted(MODES))
        raise ValueError(f"Unknown mode '{name}'. Valid modes: {valid}") from exc
