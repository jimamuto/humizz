from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

PAIR_INSTRUCTION = "Rewrite this text so it sounds natural, clear, and human while preserving meaning."

DATASET_PRESETS: dict[str, dict[str, str]] = {
    "human-ai-generated": {
        "dataset": "dmitva/human_ai_generated_text",
        "ai_field": "ai_text",
        "human_field": "human_text",
        "license_note": "Review Hugging Face dataset card before redistribution or commercial use.",
    },
    "hap-e": {
        "dataset": "browndw/human-ai-parallel-corpus",
        "group_field": "doc_id",
        "source_field": "source",
        "text_field": "text",
        "human_source_contains": "chunk",
        "license_note": "MIT per dataset card search result; keep attribution with exported data.",
    },
}


def load_hf_dataset(dataset_name: str, split: str):
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install dataset extraction dependency with: python -m pip install datasets") from exc
    return load_dataset(dataset_name, split=split)


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def pair_direct_rows(rows: Iterable[dict[str, Any]], ai_field: str, human_field: str) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        ai_text = normalize_text(row.get(ai_field))
        human_text = normalize_text(row.get(human_field))
        if not ai_text or not human_text or ai_text == human_text:
            continue
        key = (ai_text.lower(), human_text.lower())
        if key in seen:
            continue
        seen.add(key)
        pairs.append({"instruction": PAIR_INSTRUCTION, "input": ai_text, "output": human_text, "source": "public"})
    return pairs


def pair_parallel_rows(
    rows: Iterable[dict[str, Any]],
    *,
    group_field: str,
    source_field: str,
    text_field: str,
    human_source_contains: str,
) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, list[str]]] = {}
    for row in rows:
        group = normalize_text(row.get(group_field))
        source = normalize_text(row.get(source_field)).lower()
        text = normalize_text(row.get(text_field))
        if not group or not source or not text:
            continue
        bucket = grouped.setdefault(group, {"human": [], "ai": []})
        if human_source_contains.lower() in source:
            bucket["human"].append(text)
        else:
            bucket["ai"].append(text)

    pairs: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for bucket in grouped.values():
        if not bucket["human"] or not bucket["ai"]:
            continue
        human_text = bucket["human"][0]
        for ai_text in bucket["ai"]:
            if ai_text == human_text:
                continue
            key = (ai_text.lower(), human_text.lower())
            if key in seen:
                continue
            seen.add(key)
            pairs.append({"instruction": PAIR_INSTRUCTION, "input": ai_text, "output": human_text, "source": "public"})
    return pairs


def write_jsonl(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def extract_preset(name: str, output_path: Path, *, split: str = "train", limit: int | None = None) -> int:
    if name not in DATASET_PRESETS:
        valid = ", ".join(sorted(DATASET_PRESETS))
        raise ValueError(f"Unknown dataset preset '{name}'. Valid presets: {valid}")

    preset = DATASET_PRESETS[name]
    rows = load_hf_dataset(preset["dataset"], split)
    if limit is not None:
        rows = rows.select(range(min(limit, len(rows))))

    if "ai_field" in preset:
        pairs = pair_direct_rows(rows, preset["ai_field"], preset["human_field"])
    else:
        pairs = pair_parallel_rows(
            rows,
            group_field=preset["group_field"],
            source_field=preset["source_field"],
            text_field=preset["text_field"],
            human_source_contains=preset["human_source_contains"],
        )

    write_jsonl(output_path, pairs)
    return len(pairs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract public human/AI datasets into Humizz instruction JSONL pairs")
    parser.add_argument("--preset", choices=sorted(DATASET_PRESETS), required=True)
    parser.add_argument("--split", default="train")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    count = extract_preset(args.preset, args.output, split=args.split, limit=args.limit)
    preset = DATASET_PRESETS[args.preset]
    print(json.dumps({"preset": args.preset, "dataset": preset["dataset"], "output": str(args.output), "pairs": count, "license_note": preset["license_note"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
