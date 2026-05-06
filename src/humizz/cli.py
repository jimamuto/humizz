from __future__ import annotations

import argparse
import json
import sys

from .adapters import FakeAdapter, TransformersAdapter
from .engine import RewriteEngine, RewriteRequest
from .modes import MODES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="humizz", description="Local-first text humanizer")
    parser.add_argument("text", help="Text to rewrite")
    parser.add_argument("--mode", choices=sorted(MODES), default="natural")
    parser.add_argument("--backend", choices=["fake", "transformers"], default="fake")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--json", action="store_true", help="Print rewrite result with metadata as JSON")
    return parser


def make_adapter(backend: str, model: str):
    if backend == "fake":
        return FakeAdapter()
    return TransformersAdapter(model_id=model)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    engine = RewriteEngine(make_adapter(args.backend, args.model))
    try:
        result = engine.rewrite(
            RewriteRequest(
                text=args.text,
                mode=args.mode,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
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
