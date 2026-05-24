from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .engine import RewriteRequest, RewriteResult

DEFAULT_FEEDBACK_PATH = Path("data/feedback.jsonl")


@dataclass(frozen=True)
class FeedbackRecord:
    timestamp: str
    input: str
    output: str
    mode: str
    quality: dict[str, Any]
    metadata: dict[str, Any]
    accepted: bool | None = None
    detector_score: float | None = None
    preferred_rewrite: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_feedback_record(
    request: RewriteRequest,
    result: RewriteResult,
    *,
    accepted: bool | None = None,
    detector_score: float | None = None,
    preferred_rewrite: str | None = None,
) -> FeedbackRecord:
    return FeedbackRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        input=request.text,
        output=result.text,
        mode=result.mode,
        quality=asdict(result.quality),
        metadata={
            **result.metadata,
            "requested_mode": request.mode,
            "max_new_tokens": request.max_new_tokens,
            "temperature": request.temperature,
            "max_attempts": request.max_attempts,
        },
        accepted=accepted,
        detector_score=detector_score,
        preferred_rewrite=preferred_rewrite,
    )


def append_feedback(record: FeedbackRecord, path: Path = DEFAULT_FEEDBACK_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
