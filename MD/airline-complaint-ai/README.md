# Airline Complaint AI

## What this project does

This Python and Streamlit project analyzes airline reviews. It cleans review text, creates severity and service-risk labels, trains machine-learning and deep-learning models, evaluates predictions, and provides dashboards and prediction screens.

Severity classes are Low, Medium, High, and Critical. Risk is a separate yes/no prediction. The labels are created from ratings and complaint keywords, so they are rule-generated labels rather than manually verified answers.

## Start and setup

Read the project's original [README](../../airline-complaint-ai/README.md) for the full data expectations, model choices, and deployment instructions. Install packages from the included requirements file, provide the expected review CSV and model artifacts, then start the app with Streamlit. The project includes both a local app (`app.py`) and a cloud-oriented app (`app_streamlit_cloud.py`).

Run tests from the project directory with:

```powershell
python -m pytest
```

## Source file guide

### Application and training

- `app.py` — main Streamlit application for loading trained artifacts and presenting prediction/analysis features. Most of its UI logic is at module level rather than inside custom functions.
- `app_streamlit_cloud.py` — Streamlit application variant intended for hosted deployment; check its configuration and required artifacts before deploying.
- `train_pipeline.py` — coordinates data preparation and model training:
  - `parse_args()` reads command-line options.
  - `run_data_phases(sample)` loads, cleans, labels, and prepares data.
  - `run_ml_phases(df)` trains and evaluates the traditional ML alternatives.
  - `run_dl_phase(...)` trains/evaluates a deep-learning model.
  - `_encode(texts)` creates text inputs for a model phase.
  - `run_transformer_phase(...)` trains/evaluates a transformer model.
  - `main()` connects the command-line arguments and training phases.
- `pages/1_Introduction.py` — introduction page; `load_dataset()` loads the dataset used by that page.
- `pages/2_EDA_Dashboard.py` — exploratory analysis page; `load_data()` loads dashboard data.
- `pages/3_Prediction.py` — prediction page; `load_models()` loads saved models and `predict_single(...)` runs one review through prediction.
- `scripts/upload_models_to_hf.py` — `main()` uploads configured model files to Hugging Face. Check account, repository, and secret configuration before using it.

### Data and model support (`src/`)

- `src/data/data_loader.py` — `load_raw_dataset(path)` reads the source dataset; `_inspect(df)` prints/checks its shape and fields; `get_inspection_report(df)` returns a structured data summary.
- `src/data/cleaner.py` — `clean_dataset(df)` runs cleaning steps; helpers convert overall and aspect ratings, normalize categories, remove exact duplicates, and fill missing text values.
- `src/data/label_generator.py` — `generate_labels(df)` adds severity and risk labels. Helpers detect critical/risk keywords, count low aspect ratings, and assign each label.
- `src/preprocessing/text_preprocessor.py` — `_base_clean(text)` handles shared cleanup; `ml_clean(text, lemmatize)` prepares traditional-model text; `dl_clean(text)` prepares embedding-model text; `transformer_clean(text)` preserves text for transformer tokenizers; `build_full_text(...)` combines title and review; `preprocess_dataframe(...)` applies a selected pipeline to rows.
- `src/features/feature_engineer.py` — builds structured complaint features and text vectors. `add_structured_features(...)`, `count_keywords(...)`, `build_inference_struct(...)`, and `get_structured_matrix(...)` prepare numeric inputs. `BagOfWordsFeatures` and `TFIDFFeatures` wrap vectorizers with fit, transform, save, and load operations. `build_combined_features(...)` combines sparse text and structured features.
- `src/evaluation/evaluator.py` — `evaluate_severity(...)` measures multi-class performance; `evaluate_risk(...)` measures binary risk performance; `build_comparison_table(...)` compares models; `_plot_confusion_matrix(...)` saves a plot.
- `src/explainability/explainer.py` — explains model output using highlighted complaint phrases and supported linear/LIME/SHAP explanations. Main functions include `highlight_complaint_phrases(...)`, `get_linear_top_features(...)`, `get_lime_explanation(...)`, `get_shap_values(...)`, and `explain_prediction(...)`.
- `src/utils/config.py` — shared paths, labels, column names, keyword lists, and model settings.
- `src/utils/logger.py` — `get_logger(name, log_dir)` creates or returns a configured logger.
- `__init__.py` files — mark Python package folders and may expose package-level imports; they contain no separate user workflow.

## Tests

- `tests/test_data.py` and `tests/test_fixes.py` cover data preparation, text processing, labels, explainability, and previously fixed behavior.
- `test cases/TC_001_smoke_tests.py` through `TC_009_boundary_edge_cases.py` organize smoke, unit, integration, regression, and edge-case checks.
- `test cases/conftest.py` contains shared test setup and fixtures.

## Other project files

- `requirements.txt` and `requirements_full.txt` list Python dependencies for different install options.
- `CHANGES.md` records project changes.
- `.streamlit/config.toml` configures Streamlit.
- `deployment/aws/README_aws.md` and `deployment/huggingface/README_hf.md` describe deployment paths.
- `artifacts/`, `models/`, `data/`, and `logs/` contain runtime inputs, generated outputs, model files, or logs. These are data/artifact folders, not Python modules.

## Technical points to explain in an interview

- The text-cleaning pipeline differs for traditional ML, deep learning, and transformer tokenizers.
- The project compares multiple model families using metrics such as F1, recall, ROC-AUC, and confusion matrices.
- The labels are derived from ratings and keyword rules; they should not be presented as human-annotated ground truth.
- Vectorizers and scalers should be fitted on training data only to avoid data leakage.
