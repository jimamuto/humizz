from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from humizz.adapters import DEFAULT_MODEL_ID, ModalAdapter, TransformersAdapter
from humizz.engine import RewriteEngine, RewriteRequest
from humizz.quality import warning_score


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def make_adapter(backend: str, model: str, modal_app: str, modal_function: str):
    if backend == "modal":
        return ModalAdapter(model_id=model, app_name=modal_app, function_name=modal_function)
    return TransformersAdapter(model_id=model)


def evaluate_dataset(
    dataset_path: Path,
    *,
    backend: str = "modal",
    model: str = DEFAULT_MODEL_ID,
    modal_app: str = "humizz",
    modal_function: str = "generate_text",
    limit: int | None = None,
) -> dict[str, Any]:
    engine = RewriteEngine(make_adapter(backend, model, modal_app, modal_function))
    rows = list(iter_jsonl(dataset_path))
    if limit is not None:
        rows = rows[:limit]

    examples = []
    total_warning_score = 0
    exact_matches = 0
    for row in rows:
        source = row.get("input") or row.get("text") or ""
        expected = row.get("output") or ""
        result = engine.rewrite(RewriteRequest(text=source))
        score = warning_score(result.quality)
        total_warning_score += score
        if expected and result.text.strip().lower() == expected.strip().lower():
            exact_matches += 1
        examples.append(
            {
                "input": source,
                "expected": expected,
                "actual": result.text,
                "quality": result.to_dict()["quality"],
                "warning_score": score,
                "metadata": result.metadata,
            }
        )

    count = len(examples)
    return {
        "dataset": str(dataset_path),
        "backend": backend,
        "model": model,
        "count": count,
        "average_warning_score": round(total_warning_score / count, 3) if count else 0.0,
        "exact_match_rate": round(exact_matches / count, 3) if count else 0.0,
        "examples": examples,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Humizz against an instruction JSONL dataset")
    parser.add_argument("--dataset", type=Path, default=Path("data/datasets/latest/test.jsonl"))
    parser.add_argument("--backend", choices=["modal", "transformers"], default="modal")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--modal-app", default="humizz")
    parser.add_argument("--modal-function", default="generate_text")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, default=Path("outputs/model-eval.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = evaluate_dataset(
        args.dataset,
        backend=args.backend,
        model=args.model,
        modal_app=args.modal_app,
        modal_function=args.modal_function,
        limit=args.limit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("dataset", "backend", "model", "count", "average_warning_score", "exact_match_rate")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
