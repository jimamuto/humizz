# Humizz

Open-source lightweight text humanizer.

Humizz is a local-first rewrite tool for turning stiff or robotic drafts into clearer, more natural text while preserving meaning. It is not positioned as a guaranteed AI-detector bypass tool.

## MVP

- CLI first
- Local model execution
- Later local web UI
- Rewrite modes: `natural`, `concise`, `formal`, `casual`
- Default local model target: `Qwen/Qwen2.5-0.5B-Instruct`
- Optional higher-quality target: `Qwen/Qwen2.5-1.5B-Instruct`

## Install

```powershell
python -m pip install -e .
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

Transformers backend:

```powershell
humizz "This solution provides significant utility." --backend transformers --model Qwen/Qwen2.5-0.5B-Instruct
```

## Test

```powershell
python -m unittest discover -s tests
```

Tests use stub adapters and do not download models.

## Evaluate

Run all modes with a local Transformers model:

```powershell
humizz-eval samples/ai_like_essay.txt --backend transformers --model Qwen/Qwen2.5-0.5B-Instruct --output outputs/eval-qwen.json
```

## Non-goals

- Training a foundation model from scratch
- Guaranteeing AI-detector bypass
- Building a detector
- Hosted SaaS, accounts, billing, or cloud deployment
