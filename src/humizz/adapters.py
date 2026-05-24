from __future__ import annotations

import re
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


DEFAULT_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"


class ModalAdapter:
    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        app_name: str = "humizz",
        function_name: str = "generate_text",
    ) -> None:
        self.model_id = model_id
        self.app_name = app_name
        self.function_name = function_name
        self._function = None

    def _load_function(self):
        if self._function is None:
            try:
                import modal
            except ImportError as exc:
                raise RuntimeError(
                    "Modal backend requires optional dependencies. "
                    "Install with: pip install -e .[modal]"
                ) from exc
            self._function = modal.Function.from_name(self.app_name, self.function_name)
        return self._function

    def generate(self, request: GenerationRequest) -> GenerationResult:
        function = self._load_function()
        output = function.remote(
            prompt=request.prompt,
            model_id=self.model_id,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
        )
        text = clean_generated_text(str(output["text"]))
        return GenerationResult(
            text=text,
            metadata={
                "adapter": "modal",
                "app_name": self.app_name,
                "function_name": self.function_name,
                "model_id": output.get("model_id", self.model_id),
            },
        )


class TransformersAdapter:
    def __init__(self, model_id: str = DEFAULT_MODEL_ID) -> None:
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
        text = clean_generated_text(output[0]["generated_text"])
        return GenerationResult(text=text, metadata={"adapter": "transformers", "model_id": self.model_id})


def clean_generated_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^Rewrite:\s*", "", cleaned, flags=re.IGNORECASE).strip()
    for marker in (
        "\n\n",
        "\n#",
        "\n---",
        "\n**",
        "\nTranslation:",
        "\n#Translation:",
        "\nUpdated Translation:",
        "\nExplanation:",
        "\nNote:",
        "\nPlease note",
        "\nI apologize",
        "\nFeel free",
        "\nLet me know",
        "\nI hope",
        "\nCan you provide",
    ):
        if marker in cleaned:
            cleaned = cleaned.split(marker, 1)[0].strip()
    cleaned = cleaned.strip('"`*_ ')
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
