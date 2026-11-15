# Functions and classes: Airline Complaint AI fixed copy

This guide covers the main functions and classes in the nested fixed project. Test helper methods are described in [TESTS.md](./TESTS.md); they prepare inputs or check expected behavior rather than implement the application.

## Training workflow

In `train_pipeline.py`:

- `parse_args()` reads command-line options for training.
- `run_data_phases(sample=None)` loads and prepares the review data and labels.
- `run_ml_phases(df)` creates features, trains traditional machine-learning models, and records evaluation results.
- `run_dl_phase(...)` trains and evaluates a custom deep-learning model.
- `_encode(texts)` turns text into the representation needed by the deep-learning phase.
- `run_transformer_phase(...)` fine-tunes and evaluates a transformer model.
- `main()` connects the command-line options and training steps.

## Data preparation (`src/data/`)

In `data_loader.py`:

- `load_raw_dataset(path)` reads the source review dataset.
- `_inspect(df)` prints basic information useful for checking the loaded data.
- `get_inspection_report(df)` returns a structured summary of the dataset.

In `cleaner.py`:

- `clean_dataset(df)` runs the data-cleaning steps and returns the cleaned data.
- `_convert_overall_rating(df)` converts the overall rating to a numeric value.
- `_convert_aspect_ratings(df)` prepares aspect-rating columns and missing-value information.
- `_normalize_categoricals(df)` standardizes categorical text such as recommendation and traveller fields.
- `_drop_exact_duplicates(df)` removes repeated review records.
- `_fill_text_nulls(df)` handles missing title or review text.

In `label_generator.py`:

- `generate_labels(df)` adds severity and risk labels using the project rules.
- `_has_critical_keyword(text)` checks text for high-severity complaint terms.
- `_has_risk_keyword(text)` checks text for service-risk terms.
- `_count_poor_aspects(row)` counts low aspect ratings.
- `_assign_severity(row)` chooses Low, Medium, High, or Critical.
- `_assign_risk(row)` assigns the binary risk label.

These are rule-derived labels. They are not the same as labels manually reviewed by airline experts.

## Text and feature preparation

In `preprocessing/text_preprocessor.py`:

- `_base_clean(text)` performs common cleanup such as handling HTML, URLs, and whitespace.
- `ml_clean(text, lemmatize=True)` prepares text for traditional machine-learning models.
- `dl_clean(text)` prepares text for embedding-based deep-learning models.
- `transformer_clean(text)` keeps text less heavily processed for transformer tokenizers.
- `build_full_text(title, review, pipeline)` combines the title and review and applies a selected cleaner.
- `preprocess_dataframe(df, pipeline, title_col, review_col)` applies text preparation to each row.

In `features/feature_engineer.py`:

- `add_structured_features(df, raw_text_col)` adds review length and keyword-count features.
- `count_keywords(text)` counts distinct configured complaint and risk keywords.
- `build_inference_struct(title, review, ratings, scaler)` builds a scaled feature row for a prediction.
- `get_structured_matrix(df, scaler, fit)` builds numeric feature data and optionally fits its scaler.
- `BagOfWordsFeatures` wraps a count vectorizer. Its `fit_transform()` learns vocabulary and returns training features; `transform()` applies that vocabulary to new text; `save()` and `load()` persist and restore the vectorizer.
- `TFIDFFeatures` provides the same fit/transform/save/load operations for TF-IDF features.
- `build_combined_features(tfidf_matrix, struct_matrix)` joins text features and numeric features into one sparse matrix.

Fit vectorizers and scalers on training data only, then use `transform()` for test and prediction data to reduce data leakage.

## Model training (`src/models/`)

In `ml_trainer.py`:

- `_severity_models()` and `_risk_models()` prepare model choices for the two prediction tasks.
- `train_severity_models(...)` trains and evaluates severity classifiers.
- `train_risk_models(...)` trains and evaluates binary risk classifiers.
- `_save_model(clf, path)` saves a trained model artifact.

In `dl_trainer.py`:

- `ReviewDataset` adapts review text and labels to the PyTorch dataset interface. `__len__()` reports the number of examples; `__getitem__(idx)` returns an example.
- `_collate_fn(batch)` combines examples into a batch for model training.
- `SimpleTokenizer` builds a word vocabulary and converts text to token IDs. `build_vocab()`, `encode()`, `save()`, and `load()` handle those steps.
- `TextCNN` is a convolution-based text classifier; `forward()` calculates its output for a batch.
- `TextLSTM` is a recurrent text classifier; `forward()` calculates its output for a batch.
- `train_epoch(...)` performs one training pass through data.
- `eval_epoch(...)` evaluates a model without training updates.
- `train_dl_model(...)` coordinates deep-learning training and evaluation.

In `transformer_trainer.py`:

- `tokenize_data(...)` tokenizes the dataset.
- `_tokenise(batch)` tokenizes a batch for the transformer library.
- `_severity_metrics(eval_pred)` and `_risk_metrics(eval_pred)` calculate task-specific evaluation metrics.
- `fine_tune_transformer(...)` trains a transformer model.
- `WeightedTrainer.compute_loss(...)` calculates a training loss that can account for class weights.
- `load_transformer_for_inference(...)` loads a saved transformer for use.
- `predict_transformer(...)` runs predictions using a loaded transformer.

## Evaluation, explanation, and support

In `evaluation/evaluator.py`:

- `evaluate_severity(...)` reports multi-class severity metrics.
- `evaluate_risk(...)` reports binary-risk metrics, including recall and false negatives.
- `build_comparison_table(results)` turns results from different models into a table.
- `_plot_confusion_matrix(...)` saves a plot comparing true and predicted labels.

In `explainability/explainer.py`:

- `highlight_complaint_phrases(text)` finds relevant phrases in review text.
- `get_linear_top_features(...)` extracts important features from a supported linear model.
- `get_lime_explanation(...)` requests a local explanation with LIME.
- `get_shap_values(...)` requests SHAP explanations where supported.
- `explain_prediction(...)` creates an explanation for a prediction.

In `utils/logger.py`, `get_logger(name, log_dir)` obtains a configured project logger.

## Streamlit pages

- `pages/1_Introduction.py`: `load_dataset()` loads data used by the introduction page.
- `pages/2_EDA_Dashboard.py`: `load_data()` loads data for the EDA page.
- `pages/3_Prediction.py`: `load_models()` loads prediction artifacts; `predict_single(...)` runs a prediction for one review.
- `scripts/upload_models_to_hf.py`: `main()` reads deployment configuration and runs the artifact upload.

The main `app.py` files build their interfaces at module level and do not declare application functions.
