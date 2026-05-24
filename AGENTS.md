# Repository Agent Instructions

- When changing `src/humizz/modal_app.py`, deploy the Modal app before considering the task complete:

  ```powershell
  modal deploy src/humizz/modal_app.py
  ```

- After deployment, run the test suite:

  ```powershell
  python -m unittest discover -s tests
  ```

- Also run text smoke tests to confirm the humanizer works on real input:

  ```powershell
  humizz "It is important to note that this solution provides significant utility." --backend modal
  humizz "Artificial intelligence has become an increasingly important tool in modern education because it can help students organize ideas, understand difficult concepts, and receive feedback more quickly. However, it should be used responsibly so learners still develop their own critical thinking skills and avoid depending on automated systems for every assignment." --backend modal
  ```

- If Modal deploy cannot run because auth, network, or dependencies are missing, report the exact blocker and still run tests.
