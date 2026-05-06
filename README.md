# Humizz

Open-source lightweight text humanizer.

Humizz is a local-first rewrite tool for turning stiff or robotic drafts into clearer, more natural text while preserving meaning. It is not positioned as a guaranteed AI-detector bypass tool.

## MVP

- CLI first
- Local model execution
- Later local web UI
- Rewrite modes: `natural`, `concise`, `formal`, `casual`
- Default lightweight model target: `Qwen/Qwen2.5-0.5B-Instruct`
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

Fake backend, no model download:

```powershell
humizz "It is important to note that this solution provides significant utility." --mode natural
```

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

Tests use the fake backend and do not download models.

## Non-goals

- Training a foundation model from scratch
- Guaranteeing AI-detector bypass
- Building a detector
- Hosted SaaS, accounts, billing, or cloud deployment
