from __future__ import annotations

import modal

from humizz.adapters import DEFAULT_MODEL_ID, clean_generated_text

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "transformers")
    .add_local_python_source("humizz")
)
app = modal.App("humizz")

_pipeline = None
_loaded_model_id = None


def _load_pipeline(model_id: str):
    global _pipeline, _loaded_model_id
    if _pipeline is None or _loaded_model_id != model_id:
        from transformers import pipeline

        _pipeline = pipeline("text-generation", model=model_id)
        _loaded_model_id = model_id
    return _pipeline


@app.function(image=image, gpu="T4", timeout=600)
def generate_text(
    prompt: str,
    model_id: str = DEFAULT_MODEL_ID,
    max_new_tokens: int = 96,
    temperature: float = 0.2,
) -> dict[str, object]:
    pipe = _load_pipeline(model_id)
    output = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        return_full_text=False,
    )
    text = clean_generated_text(output[0]["generated_text"])
    return {"text": text, "model_id": model_id}
