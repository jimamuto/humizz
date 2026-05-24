import unittest
from unittest.mock import Mock, patch

from humizz.adapters import GenerationRequest, ModalAdapter, clean_generated_text


class ModalAdapterTests(unittest.TestCase):
    def test_modal_adapter_calls_remote_function(self):
        remote_function = Mock()
        remote_function.remote.return_value = {"text": "Rewritten text.", "model_id": "model-x"}
        modal_module = Mock()
        modal_module.Function.from_name.return_value = remote_function

        adapter = ModalAdapter(model_id="model-x", app_name="app-x", function_name="fn-x")

        with patch.dict("sys.modules", {"modal": modal_module}):
            result = adapter.generate(GenerationRequest(prompt="Prompt", max_new_tokens=64, temperature=0.3))

        modal_module.Function.from_name.assert_called_once_with("app-x", "fn-x")
        remote_function.remote.assert_called_once_with(
            prompt="Prompt",
            model_id="model-x",
            max_new_tokens=64,
            temperature=0.3,
        )
        self.assertEqual(result.text, "Rewritten text.")
        self.assertEqual(result.metadata["adapter"], "modal")
        self.assertEqual(result.metadata["model_id"], "model-x")

    def test_clean_generated_text_removes_explanations(self):
        self.assertEqual(clean_generated_text("Rewrite.\n\nExplanation: details"), "Rewrite.")
        self.assertEqual(clean_generated_text("Rewrite: This is useful.\n#Translation:\nOther"), "This is useful.")


if __name__ == "__main__":
    unittest.main()
