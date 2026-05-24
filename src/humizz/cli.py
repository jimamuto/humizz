from __future__ import annotations

import argparse
import json
import sys

from .adapters import DEFAULT_MODEL_ID, ModalAdapter, TransformersAdapter
from .engine import RewriteEngine, RewriteRequest
from .modes import MODES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="humizz", description="Local-first text humanizer")
    parser.add_argument("text", help="Text to rewrite")
    parser.add_argument("--mode", choices=sorted(MODES), default="natural")
    parser.add_argument("--backend", choices=["modal", "transformers"], default="modal")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--modal-app", default="humizz")
    parser.add_argument("--modal-function", default="generate_text")
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--json", action="store_true", help="Print rewrite result with metadata as JSON")
    return parser


def make_adapter(backend: str, model: str, modal_app: str = "humizz", modal_function: str = "generate_text"):
    if backend == "modal":
        return ModalAdapter(model_id=model, app_name=modal_app, function_name=modal_function)
    return TransformersAdapter(model_id=model)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    engine = RewriteEngine(make_adapter(args.backend, args.model, args.modal_app, args.modal_function))
    try:
        result = engine.rewrite(
            RewriteRequest(
                text=args.text,
                mode=args.mode,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                max_attempts=args.max_attempts,
            )
        )
    except Exception as exc:
        print(f"humizz: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
