from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import DEFAULT_MODEL_ID, ModalAdapter, TransformersAdapter
from .engine import RewriteEngine, RewriteRequest
from .modes import MODES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="humizz-eval", description="Run Humizz rewrite samples")
    parser.add_argument("input", type=Path, help="Text file to rewrite")
    parser.add_argument("--backend", choices=["modal", "transformers"], default="modal")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--modal-app", default="humizz")
    parser.add_argument("--modal-function", default="generate_text")
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--output", type=Path)
    return parser


def make_adapter(backend: str, model: str, modal_app: str = "humizz", modal_function: str = "generate_text"):
    if backend == "modal":
        return ModalAdapter(model_id=model, app_name=modal_app, function_name=modal_function)
    return TransformersAdapter(model_id=model)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.input.read_text(encoding="utf-8")
    engine = RewriteEngine(make_adapter(args.backend, args.model, args.modal_app, args.modal_function))
    results = []

    for mode in sorted(MODES):
        result = engine.rewrite(RewriteRequest(text=source, mode=mode, max_attempts=args.max_attempts))
        results.append(result.to_dict())

    payload = {"input": str(args.input), "backend": args.backend, "model": args.model, "results": results}
    text = json.dumps(payload, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
