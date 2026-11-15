# Airline Complaint AI — Architecture

```mermaid
flowchart TD
    CSV[Airline review CSV]
    Train[train_pipeline.py]
    Load[Data loader]
    Clean[Structured cleaner]
    Labels[Rule-based label generator<br/>severity and risk]
    Split[Train / validation / test split]
    Text[Text preprocessing]
    MLText[ML cleaner<br/>BoW / TF-IDF]
    DLText[DL cleaner<br/>tokenizer / embeddings]
    TransformerText[Transformer cleaner<br/>model tokenizer]
    Features[Feature engineering<br/>text + structured ratings]
    ML[Traditional ML trainers]
    DL[Deep-learning trainers<br/>CNN / LSTM]
    Transformer[Transformer fine-tuning]
    Artifacts[(Saved models<br/>vectorizers / scalers / tokenizers)]
    Eval[Evaluation and comparison<br/>F1 / recall / AUC / confusion matrices]
    Explain[Explainability<br/>keywords / LIME / SHAP / linear features]
    App[Streamlit application<br/>app.py and pages]
    Input[Single review or batch CSV]
    Predict[Prediction and explanation]
    Output[Severity and service-risk results]
    Deploy[AWS or Hugging Face deployment]

    CSV --> Train --> Load --> Clean --> Labels --> Split
    Split --> Text
    Text --> MLText --> Features --> ML
    Text --> DLText --> Features
    Text --> TransformerText --> Transformer
    Features --> DL
    ML --> Artifacts
    DL --> Artifacts
    Transformer --> Artifacts
    ML --> Eval
    DL --> Eval
    Transformer --> Eval
    Artifacts --> App
    Input --> App --> Predict
    Predict --> Explain
    Predict --> Output
    Explain --> Output
    Eval --> App
    Artifacts --> Deploy
```

## Architecture notes

- The training pipeline reads and cleans airline reviews, then creates severity and risk labels from ratings, recommendation fields, aspect ratings, and keyword rules.
- The three text paths are intended for different model families: traditional ML, custom deep learning, and transformer tokenizers.
- Feature vectorizers and scalers should be fit on training data only, then reused for test and inference inputs.
- Evaluation and explanations are separate concerns: evaluation measures model performance; explainability helps describe individual predictions.
- The labels are rule-generated targets, not independently human-annotated ground truth.
- Streamlit pages expose introduction/data information, EDA, and prediction functionality. Saved artifacts must be available at the configured paths for inference.
