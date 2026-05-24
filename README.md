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

## Feedback logging

Log rewrites for future dataset building and fine-tuning:

```powershell
humizz "This solution provides significant utility." --log-feedback --accepted no --detector-score 0.98 --preferred-rewrite "This helps."
```

By default, feedback is appended to `data/feedback.jsonl`. Each JSONL row includes the input, output, quality warnings, model metadata, optional detector score, accepted/rejected flag, and preferred rewrite.

Build fine-tuning-ready JSONL splits from logged feedback:

```powershell
python scripts/build_dataset.py --input data/feedback.jsonl --output-dir data/datasets/latest
```

Rejected rows are skipped unless they include `preferred_rewrite`. Output files use instruction-tuning rows with `instruction`, `input`, and `output` fields.

Extract supported public datasets into the same pair format:

```powershell
python -m pip install -e .[mlops]
python scripts/extract_public_datasets.py --preset human-ai-generated --limit 500 --output data/public/human-ai-generated.jsonl
python scripts/extract_public_datasets.py --preset hap-e --limit 500 --output data/public/hap-e.jsonl
```

Supported presets are `human-ai-generated` (`dmitva/human_ai_generated_text`) and `hap-e` (`browndw/human-ai-parallel-corpus`). Review each dataset license and attribution requirements before redistribution or commercial use.

## Evaluate

Run all modes with Modal remote functions:

```powershell
humizz-eval samples/ai_like_essay.txt --backend modal --model Qwen/Qwen2.5-1.5B-Instruct --output outputs/eval-modal.json
```

Evaluate a dataset split:

```powershell
python scripts/evaluate_model.py --dataset data/datasets/latest/test.jsonl --backend modal --output outputs/model-eval.json
```

## Modal backend notes

Humizz now defaults to a Modal remote function backend. The CLI and eval commands call `ModalAdapter`, which invokes `modal.Function.from_name("humizz", "generate_text").remote(...)`. The Modal function in `src/humizz/modal_app.py` runs the Transformers text-generation pipeline on a GPU-backed Modal worker.

Current generation defaults are tuned for concise rewrites:

- Model: `Qwen/Qwen2.5-1.5B-Instruct`
- `max_new_tokens`: `96`
- `temperature`: `0.2`

The engine prompt and output cleanup are intentionally strict to preserve meaning and avoid extra assistant chatter. The default prompt also discourages formal AI-sounding transitions and asks for shorter, everyday sentences.

## Fine-tuning prep

After enough reviewed pairs exist, launch LoRA training on Modal using the generated dataset location mounted in the training volume:

```powershell
python scripts/train_lora_modal.py --dataset-dir /runs/datasets/latest --model Qwen/Qwen2.5-1.5B-Instruct --output-name qwen2.5-1.5b-humizz-lora --max-steps 200
```

Treat this as an experiment until evaluation shows lower warning scores, acceptable detector scores, and manually reviewed meaning preservation.

## Non-goals

- Training a foundation model from scratch
- Guaranteeing AI-detector bypass
- Building a detector
- Hosted SaaS, accounts, billing, or cloud deployment
