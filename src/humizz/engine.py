from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .adapters import GenerationRequest, ModelAdapter
from .modes import get_mode
from .quality import QualityReport, assess_quality, warning_score


@dataclass(frozen=True)
class RewriteRequest:
    text: str
    mode: str = "natural"
    max_new_tokens: int = 96
    temperature: float = 0.2
    max_attempts: int = 2


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
        best_result: RewriteResult | None = None
        attempts = max(1, request.max_attempts)

        for attempt in range(attempts):
            prompt = build_prompt(
                mode.instruction,
                request.text,
                retry_warnings=best_result.quality.warnings if best_result else (),
            )
            generation = self.adapter.generate(
                GenerationRequest(
                    prompt=prompt,
                    max_new_tokens=request.max_new_tokens,
                    temperature=request.temperature,
                )
            )
            quality = assess_quality(request.text, generation.text)
            result = RewriteResult(
                text=generation.text,
                mode=mode.name,
                quality=quality,
                metadata={**generation.metadata, "attempt": attempt + 1},
            )
            if best_result is None or warning_score(quality) < warning_score(best_result.quality):
                best_result = result
            if not quality.warnings:
                break

        if best_result is None:
            raise RuntimeError("Rewrite failed.")
        return best_result


def build_prompt(instruction: str, text: str, retry_warnings: tuple[str, ...] = ()) -> str:
    return (
        "Rewrite the text between <original> tags.\n"
        f"Goal: {instruction}\n"
        "Write like a real person making a quick, clear revision. Do a light rewrite, not a fancy paraphrase.\n"
        "Examples:\n"
        "Original: It is important to note that this solution provides significant utility.\n"
        "Rewrite: This solution is useful.\n"
        "Original: Artificial intelligence has become an increasingly important tool in modern education because it can help students organize ideas, understand difficult concepts, and receive feedback more quickly. However, it should be used responsibly so learners still develop their own critical thinking skills and avoid depending on automated systems for every assignment.\n"
        "Rewrite: AI is becoming a useful tool in education. It can help students organize ideas, understand hard topics, and get feedback faster. Still, students need to use it carefully. They should keep building their own critical thinking instead of relying on automated tools for every assignment.\n\n"
        f"{build_retry_guidance(retry_warnings)}"
        "Hard rules:\n"
        "- Output one rewrite only.\n"
        "- Output no explanations, labels, notes, translations, markdown, bullets, or emoji.\n"
        "- Preserve meaning, facts, names, and numbers.\n"
        "- Do not add new claims.\n"
        "- Avoid polished AI-sounding transitions and words such as surely, nevertheless, nonetheless, furthermore, moreover, in conclusion, aid, aids, considerable, crucial, essential, substantial, significant, utilize, facilitate, ensure, enhance, judicious, prudently, ought, wholly, refrain, assist, complex, wisely, solely, cautiously, honing, entirely.\n"
        "- Prefer everyday words: helps, use, hard, faster, useful, good, clear.\n"
        "- Use shorter sentences. Split long sentences when it sounds natural.\n"
        "- Keep a human rhythm: mix short and medium sentences; do not make every sentence the same length.\n"
        "- Keep the tone natural, not corporate, academic, or promotional.\n\n"
        f"<original>\n{text.strip()}\n</original>\n\n"
        "Rewrite:"
    )


def build_retry_guidance(warnings: tuple[str, ...]) -> str:
    if not warnings:
        return ""

    guidance = ["Improve the next rewrite based on these issues:"]
    if "long-sentences" in warnings:
        guidance.append("- Split long sentences into shorter ones.")
    if "low-burstiness" in warnings:
        guidance.append("- Mix short and medium sentences instead of using the same rhythm.")
    if "too-formal" in warnings:
        guidance.append("- Use plainer, everyday words.")
    if "assistant-chatter" in warnings:
        guidance.append("- Remove any assistant-style comments or labels.")
    if "large-shrink" in warnings:
        guidance.append("- Keep a little more of the original detail.")
    if "large-expansion" in warnings:
        guidance.append("- Cut added wording and stay closer to the source.")
    return "\n".join(guidance) + "\n\n"
