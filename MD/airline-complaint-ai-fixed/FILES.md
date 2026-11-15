# File guide: Airline Complaint AI fixed copy

The source project is located at `airline-complaint-ai-fixed/airline-complaint-ai/`.

## Main files

- `app.py` — Streamlit application entry point.
- `app_streamlit_cloud.py` — Streamlit entry point for hosted use.
- `train_pipeline.py` — command-line training workflow for data preparation and model families.
- `requirements.txt` and `requirements_full.txt` — Python package lists.
- `README.md` — project description, methodology, setup, and deployment notes.
- `CHANGES.md` — project change notes.
- `.env.example` — example names for environment configuration; it should not contain real secrets.
- `.gitignore` — patterns Git should ignore.
- `.streamlit/config.toml` — Streamlit configuration.

## Application pages and scripts

- `pages/1_Introduction.py` — introduction and dataset information.
- `pages/2_EDA_Dashboard.py` — exploratory data analysis dashboard.
- `pages/3_Prediction.py` — single and batch prediction interface.
- `scripts/upload_models_to_hf.py` — script for publishing configured model artifacts to Hugging Face.
- `deployment/aws/README_aws.md` and `deployment/huggingface/README_hf.md` — deployment guides.

## Python package (`src/`)

- `src/data/` — raw-data loading, data cleaning, and rule-based label creation.
- `src/preprocessing/` — separate text cleaning paths for traditional ML, deep learning, and transformer models.
- `src/features/` — text vectorizers and structured feature construction.
- `src/models/` — training helpers for traditional ML, custom deep learning, and transformers.
- `src/evaluation/` — model metrics and comparison tables.
- `src/explainability/` — methods for showing which text or features contributed to an explanation.
- `src/utils/` — shared configuration and logging.
- `__init__.py` files — make directories importable as Python packages.

## Tests and generated folders

- `tests/` — pytest data and regression tests.
- `test cases/` — smoke, unit, integration, regression, and edge-case test files.
- `notebooks/` — interactive analysis notebooks.
- `data/`, `models/`, `artifacts/`, and `logs/` — inputs, trained model files, generated outputs, and logs. They are not source-code modules.
- `.devcontainer/` — development-container settings.

See [FUNCTIONS.md](./FUNCTIONS.md) for what the major functions and classes do.
