# Humizz Fine-Tuning and MLOps Plan

## Summary

Humizz currently uses a Modal-hosted rewrite function with prompt rules, cleanup, quality checks, and retry logic. That improves outputs, but detector results still show the base model can sound too polished. The next step is a small MLOps pipeline that turns failed outputs and public human/AI corpora into fine-tuning data, trains LoRA adapters, evaluates them, and deploys versioned models through Modal.

## Dataset sources

Initial candidate datasets:

- Human-AI-Generated Text Corpus: human, AI-generated, and AI-rephrased education/news text.
- Ghostbuster Essay Dataset: human-authored and LLM-authored essays.
- CMU Human-AI Parallel Corpus: human and LLM writing on similar prompts.
- FAIDSet: human, AI, and human-LLM collaborative academic text.
- LLMTrace Detection: human, AI, and mixed-authorship text with span labels.
- OpAI-Bench: human text transformed with increasing AI involvement.
- PASTED: partially AI-paraphrased/polished text.

Most sources are classification or parallel-style datasets, not direct rewrite pairs. Humizz needs curated `AI-like input -> human rewrite` pairs, so a dataset builder must normalize, pair, filter, and review examples before training.

## Pipeline

```text
User text
  -> Humizz rewrite model
  -> Quality checks
     - meaning preservation signals
     - sentence length and burstiness
     - formal AI wording
     - assistant chatter
     - optional detector score
  -> Retry if needed
  -> Return best output
  -> Log feedback and failures
     - input
     - output
     - quality warnings
     - detector score when available
     - accepted/rejected flag
     - preferred rewrite when available
  -> Dataset builder
     - clean text
     - remove duplicates
     - split long docs into paragraphs
     - create train/validation/test JSONL
  -> LoRA fine-tune on Modal GPU
  -> Evaluation gate
     - unit tests
     - text smoke tests
     - detector score comparison
     - semantic/meaning checks
     - before/after examples
  -> Versioned Modal deployment
  -> Monitor outputs and collect more feedback
```

## Training approach

Start with LoRA instead of full model training.

- Base model: keep `Qwen/Qwen2.5-1.5B-Instruct` for first experiment, then compare a 7B model if cost allows.
- Training format: instruction examples where the model rewrites AI-like text into plain, natural text.
- Target data volume:
  - 200-500 curated pairs: first proof of concept.
  - 2k-10k pairs: useful style improvement.
  - More only after eval proves quality gains.

Example JSONL row:

```json
{"instruction":"Rewrite this text so it sounds natural, clear, and human while preserving meaning.","input":"Artificial intelligence has become an increasingly important tool in modern education...","output":"AI is becoming a useful tool in education. It helps students organize ideas..."}
```

## Self-improvement loop

The model will not improve live by itself. Humizz improves through a feedback flywheel:

1. Save weak outputs and detector failures.
2. Add a better preferred rewrite.
3. Periodically rebuild the dataset.
4. Fine-tune a new LoRA/model version.
5. Run evaluation gates.
6. Deploy only if the new version beats the current one.
7. Keep prior model versions available for rollback.

## Files and areas likely added later

- `data/feedback.jsonl` for local feedback capture.
- `scripts/build_dataset.py` to normalize and pair examples.
- `scripts/train_lora_modal.py` or Modal training app for LoRA jobs.
- `scripts/evaluate_model.py` for before/after model comparisons.
- `src/humizz/modal_app.py` to load a fine-tuned adapter or model version.
- `src/humizz/quality.py` to add stronger scoring and optional detector hooks.
- README docs for dataset, training, eval, and deployment workflows.

## Risks and edge cases

- Bad or weak pairs will make the model worse.
- Detector-specific optimization can reduce writing quality.
- Fine-tuning may overfit to essays and perform poorly on emails, docs, or casual text.
- Meaning drift is the main safety risk; entity, number, and claim preservation checks are needed.
- Retry loops and detector checks increase latency and Modal cost.
- Public dataset licenses must be checked before redistribution or commercial use.

## Verification gates

Before deploying any fine-tuned model:

```powershell
python -m unittest discover -s tests
modal deploy src/humizz/modal_app.py
humizz "It is important to note that this solution provides significant utility." --backend modal
humizz "Artificial intelligence has become an increasingly important tool in modern education because it can help students organize ideas, understand difficult concepts, and receive feedback more quickly. However, it should be used responsibly so learners still develop their own critical thinking skills and avoid depending on automated systems for every assignment." --backend modal
```

Also compare:

- detector scores before vs after
- quality warnings before vs after
- manually reviewed meaning preservation
- sample outputs across essays, email, technical, marketing, and casual text

## Recommended next step

Build feedback logging and dataset preparation first. Fine-tune only after enough high-quality pairs exist and evaluation gates are ready.
