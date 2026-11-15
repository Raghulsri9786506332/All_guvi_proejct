# Setup: Airline Complaint AI fixed copy

## Project location

Run commands from the nested project folder:

```powershell
cd "C:\Users\raghu\OneDrive\New folder\Guvi Auto code\airline-complaint-ai-fixed\airline-complaint-ai"
```

## Install

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project's default packages:

```powershell
python -m pip install -r requirements.txt
```

Use `requirements_full.txt` only when you need its extra deep-learning or transformer packages.

## Data, configuration, and models

Check the nested project's `README.md`, `.env.example`, and `src/utils/config.py` for required data, configuration, and artifact paths. Put real credentials in local environment settings; do not commit them. The `data/`, `models/`, and `artifacts/` directories are project inputs or generated artifacts and may need to be populated before every feature can run.

## Run the application

```powershell
python -m streamlit run app.py
```

The project also has `app_streamlit_cloud.py` for a cloud-oriented interface. Follow the deployment instructions under `deployment/` before publishing.

## Train models and run tests

Training is coordinated by `train_pipeline.py`. Check its options before starting a potentially long training run:

```powershell
python train_pipeline.py --help
```

Run tests from the nested project folder:

```powershell
python -m pytest
```

The test files use pytest and may need optional project dependencies installed.
