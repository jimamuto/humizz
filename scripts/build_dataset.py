from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Any, Iterable

DEFAULT_INSTRUCTION = "Rewrite this text so it sounds natural, clear, and human while preserving meaning."


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object on {path}:{line_number}")
            yield payload


def feedback_to_examples(rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for row in rows:
        source = normalize_text(str(row.get("input") or ""))
        target = normalize_text(str(row.get("preferred_rewrite") or row.get("output") or ""))
        accepted = row.get("accepted")

        if not source or not target:
            continue
        if accepted is False and not row.get("preferred_rewrite"):
            continue
        if source == target:
            continue

        key = (source.lower(), target.lower())
        if key in seen:
            continue
        seen.add(key)
        examples.append({"instruction": DEFAULT_INSTRUCTION, "input": source, "output": target})

    return examples


def split_examples(
    examples: list[dict[str, str]],
    *,
    seed: int = 13,
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
) -> dict[str, list[dict[str, str]]]:
    shuffled = examples[:]
    random.Random(seed).shuffle(shuffled)
    train_end = int(len(shuffled) * train_ratio)
    validation_end = train_end + int(len(shuffled) * validation_ratio)
    return {
        "train": shuffled[:train_end],
        "validation": shuffled[train_end:validation_end],
        "test": shuffled[validation_end:],
    }


def write_jsonl(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_dataset(input_path: Path, output_dir: Path, *, seed: int = 13) -> dict[str, int]:
    examples = feedback_to_examples(iter_jsonl(input_path))
    splits = split_examples(examples, seed=seed)
    for name, rows in splits.items():
        write_jsonl(output_dir / f"{name}.jsonl", rows)
    return {name: len(rows) for name, rows in splits.items()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Humizz fine-tuning JSONL splits from feedback logs")
    parser.add_argument("--input", type=Path, default=Path("data/feedback.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/datasets/latest"))
    parser.add_argument("--seed", type=int, default=13)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    counts = build_dataset(args.input, args.output_dir, seed=args.seed)
    print(json.dumps({"output_dir": str(args.output_dir), "counts": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
