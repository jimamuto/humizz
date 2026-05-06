from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class GenerationRequest:
    prompt: str
    max_new_tokens: int = 256
    temperature: float = 0.7


@dataclass(frozen=True)
class GenerationResult:
    text: str
    metadata: dict[str, object] = field(default_factory=dict)


class ModelAdapter(Protocol):
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate text from a prompt."""


class FakeAdapter:
    def generate(self, request: GenerationRequest) -> GenerationResult:
        source = request.prompt.split("Text:", 1)[-1].split("Rewrite:", 1)[0].strip()
        return GenerationResult(
            text=f"Humanized: {source}",
            metadata={"adapter": "fake"},
        )


class TransformersAdapter:
    def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct") -> None:
        self.model_id = model_id
        self._pipeline = None

    def _load_pipeline(self):
        if self._pipeline is None:
            try:
                from transformers import pipeline
            except ImportError as exc:
                raise RuntimeError(
                    "Transformers backend requires optional dependencies. "
                    "Install with: pip install -e .[models]"
                ) from exc
            self._pipeline = pipeline("text-generation", model=self.model_id)
        return self._pipeline

    def generate(self, request: GenerationRequest) -> GenerationResult:
        pipe = self._load_pipeline()
        output = pipe(
            request.prompt,
            max_new_tokens=request.max_new_tokens,
            do_sample=True,
            temperature=request.temperature,
            return_full_text=False,
        )
        text = output[0]["generated_text"].strip()
        return GenerationResult(text=text, metadata={"adapter": "transformers", "model_id": self.model_id})
