from __future__ import annotations

import argparse
from pathlib import Path


def build_modal_app():
    try:
        import modal
    except ImportError as exc:
        raise RuntimeError("Install Modal first: python -m pip install -e .[modal]") from exc

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install("torch", "transformers", "datasets", "peft", "trl", "accelerate", "bitsandbytes")
    )
    volume = modal.Volume.from_name("humizz-lora-runs", create_if_missing=True)
    app = modal.App("humizz-lora-train")

    @app.function(image=image, gpu="T4", timeout=60 * 60 * 4, volumes={"/runs": volume})
    def train_lora(dataset_dir: str, model_id: str, output_name: str, max_steps: int = 200) -> dict[str, str | int]:
        from datasets import load_dataset
        from peft import LoraConfig
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer

        output_dir = f"/runs/{output_name}"
        dataset = load_dataset("json", data_files={"train": f"{dataset_dir}/train.jsonl", "validation": f"{dataset_dir}/validation.jsonl"})
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

        def format_row(row):
            return f"Instruction: {row['instruction']}\nInput: {row['input']}\nRewrite: {row['output']}"

        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset["train"],
            eval_dataset=dataset.get("validation"),
            formatting_func=format_row,
            peft_config=LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM"),
            args=TrainingArguments(
                output_dir=output_dir,
                per_device_train_batch_size=1,
                gradient_accumulation_steps=8,
                learning_rate=2e-4,
                max_steps=max_steps,
                logging_steps=10,
                eval_strategy="steps" if len(dataset.get("validation", [])) else "no",
                eval_steps=50,
                save_steps=50,
                report_to=[],
            ),
        )
        trainer.train()
        trainer.save_model(output_dir)
        volume.commit()
        return {"output_dir": output_dir, "model_id": model_id, "max_steps": max_steps}

    return app, train_lora


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch Humizz LoRA training on Modal")
    parser.add_argument("--dataset-dir", default="/runs/datasets/latest", help="Dataset directory visible inside Modal")
    parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--output-name", default="qwen2.5-1.5b-humizz-lora")
    parser.add_argument("--max-steps", type=int, default=200)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _app, train_lora = build_modal_app()
    result = train_lora.remote(args.dataset_dir, args.model, args.output_name, args.max_steps)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
