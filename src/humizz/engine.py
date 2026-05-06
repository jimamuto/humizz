from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .adapters import GenerationRequest, ModelAdapter
from .modes import get_mode
from .quality import QualityReport, assess_quality


@dataclass(frozen=True)
class RewriteRequest:
    text: str
    mode: str = "natural"
    max_new_tokens: int = 256
    temperature: float = 0.7


@dataclass(frozen=True)
class RewriteResult:
    text: str
    mode: str
    quality: QualityReport
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "mode": self.mode,
            "quality": asdict(self.quality),
            "metadata": self.metadata,
        }


class RewriteEngine:
    def __init__(self, adapter: ModelAdapter) -> None:
        self.adapter = adapter

    def rewrite(self, request: RewriteRequest) -> RewriteResult:
        if not request.text.strip():
            raise ValueError("Input text cannot be empty.")

        mode = get_mode(request.mode)
        prompt = build_prompt(mode.instruction, request.text)
        generation = self.adapter.generate(
            GenerationRequest(
                prompt=prompt,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
            )
        )
        quality = assess_quality(request.text, generation.text)
        return RewriteResult(
            text=generation.text,
            mode=mode.name,
            quality=quality,
            metadata=generation.metadata,
        )


def build_prompt(instruction: str, text: str) -> str:
    return (
        "You are Humizz, a rewrite tool.\n"
        f"Task: {instruction}\n"
        "Rules:\n"
        "- Return only the rewritten text.\n"
        "- Do not explain your changes.\n"
        "- Do not add facts.\n"
        "- Keep the original meaning.\n\n"
        f"Original text:\n{text.strip()}\n\n"
        "Rewritten text:"
    )
