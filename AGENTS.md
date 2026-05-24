# Repository Agent Instructions

- When changing `src/humizz/modal_app.py`, deploy the Modal app before considering the task complete:

  ```powershell
  modal deploy src/humizz/modal_app.py
  ```

- After deployment, run the test suite:

  ```powershell
  python -m unittest discover -s tests
  ```

- Also run a text smoke test to confirm the humanizer works on real input:

  ```powershell
  humizz "It is important to note that this solution provides significant utility." --backend modal
  ```

- If Modal deploy cannot run because auth, network, or dependencies are missing, report the exact blocker and still run tests.
