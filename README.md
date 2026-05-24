# Humizz

Open-source lightweight text humanizer.

Humizz is a local-first rewrite tool for turning stiff or robotic drafts into clearer, more natural text while preserving meaning. It is not positioned as a guaranteed AI-detector bypass tool.

## MVP

- CLI first
- Modal remote function execution for GPU-backed rewrites
- Optional local model execution
- Later local web UI
- Rewrite modes: `natural`, `concise`, `formal`, `casual`
- Default model target: `Qwen/Qwen2.5-1.5B-Instruct`
- Optional lightweight local target: `Qwen/Qwen2.5-0.5B-Instruct`

## Install

```powershell
python -m pip install -e .
```

Optional Modal dependency:

```powershell
python -m pip install -e .[modal]
```

Optional local model dependencies:

```powershell
python -m pip install -e .[models]
```

## Run

JSON output with quality metadata:

```powershell
humizz "This solution provides significant utility." --mode concise --json
```

Modal remote function backend:

```powershell
modal deploy src/humizz/modal_app.py
humizz "This solution provides significant utility." --backend modal --model Qwen/Qwen2.5-1.5B-Instruct
```

Local Transformers backend:

```powershell
humizz "This solution provides significant utility." --backend transformers --model Qwen/Qwen2.5-0.5B-Instruct
```

## Test

```powershell
python -m unittest discover -s tests
```

Tests use stub adapters and do not download models.

For Modal-backed changes, also deploy and run a real text smoke test:

```powershell
modal deploy src/humizz/modal_app.py
humizz "It is important to note that this solution provides significant utility." --backend modal
```

Expected behavior: one concise rewritten sentence with no explanations, labels, markdown, translations, or emoji.

## Evaluate

Run all modes with Modal remote functions:

```powershell
humizz-eval samples/ai_like_essay.txt --backend modal --model Qwen/Qwen2.5-1.5B-Instruct --output outputs/eval-modal.json
```

## Modal backend notes

Humizz now defaults to a Modal remote function backend. The CLI and eval commands call `ModalAdapter`, which invokes `modal.Function.from_name("humizz", "generate_text").remote(...)`. The Modal function in `src/humizz/modal_app.py` runs the Transformers text-generation pipeline on a GPU-backed Modal worker.

Current generation defaults are tuned for concise rewrites:

- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- `max_new_tokens`: `96`
- `temperature`: `0.2`

The engine prompt and output cleanup are intentionally strict to preserve meaning and avoid extra assistant chatter. The default prompt also discourages formal AI-sounding transitions and asks for shorter, everyday sentences.

## Non-goals

- Training a foundation model from scratch
- Guaranteeing AI-detector bypass
- Building a detector
- Hosted SaaS, accounts, billing, or cloud deployment
