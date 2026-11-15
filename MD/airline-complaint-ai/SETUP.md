# Airline Complaint AI setup

1. Open PowerShell in `airline-complaint-ai`.
2. Create and activate a virtual environment if desired:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

   Use `requirements_full.txt` only if you need the additional packages listed there.
4. Put the expected airline review data and required model artifacts in the locations described by the project's [README](../../airline-complaint-ai/README.md). Do not assume missing input data or model files are present.
5. Launch the local interface:

   ```powershell
   python -m streamlit run app.py
   ```

6. To run the tests:

   ```powershell
   python -m pytest
   ```

Review the deployment guides before publishing. Keep tokens and credentials out of source code.
