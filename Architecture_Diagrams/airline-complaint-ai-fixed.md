# Airline Complaint AI - Fixed copy — Architecture

This diagram describes the separate project copy at `airline-complaint-ai-fixed/airline-complaint-ai/`. Confirm that copy's own configuration and artifacts before running it.

```mermaid
flowchart TD
    CSV[Airline review data]
    Train[train_pipeline.py<br/>training orchestration]
    Loader[src/data/data_loader.py]
    Cleaner[src/data/cleaner.py]
    Labels[src/data/label_generator.py<br/>rule-derived targets]
    Split[Data split]
    Text[src/preprocessing/text_preprocessor.py]
    MLFeatures[BoW / TF-IDF<br/>structured features]
    DLFeatures[Simple tokenizer<br/>CNN / LSTM inputs]
    HF[Transformer tokenizer]
    ML[src/models/ml_trainer.py]
    DL[src/models/dl_trainer.py]
    Transformer[src/models/transformer_trainer.py]
    Evaluation[src/evaluation/evaluator.py]
    Artifacts[(models and artifacts<br/>configured output paths)]
    Explain[src/explainability/explainer.py]
    LocalApp[app.py<br/>Streamlit]
    CloudApp[app_streamlit_cloud.py<br/>hosted variant]
    Pages[Streamlit pages<br/>Introduction / EDA / Prediction]
    User[Review text or batch input]
    Inference[Load model and prepare features]
    Result[Severity / risk predictions<br/>and explanations]
    Deploy[Deployment guides<br/>AWS / Hugging Face]

    CSV --> Train --> Loader --> Cleaner --> Labels --> Split
    Split --> Text
    Text --> MLFeatures --> ML
    Text --> DLFeatures --> DL
    Text --> HF --> Transformer
    ML --> Evaluation
    DL --> Evaluation
    Transformer --> Evaluation
    ML --> Artifacts
    DL --> Artifacts
    Transformer --> Artifacts
    Evaluation --> Pages
    User --> LocalApp
    User --> CloudApp
    User --> Pages
    Pages --> Inference
    LocalApp --> Inference
    CloudApp --> Inference
    Artifacts --> Inference
    Inference --> Explain --> Result
    Inference --> Result
    Artifacts --> Deploy
```

## Architecture notes

- This copy has its own nested application folder, `src` modules, pages, training code, tests, and deployment guides. It is separate from the sibling `airline-complaint-ai` directory.
- Training and inference share preprocessing and feature definitions; the saved vectorizer, tokenizer, scaler, and model artifacts need to match.
- Severity and risk labels come from configured rules and are not human-verified ground truth.
- The repository includes both an ordinary Streamlit app and a cloud-oriented variant. Deployment requires appropriate dependencies, input data, model artifacts, and secret configuration.
- Do not infer model quality from the diagram; use the actual evaluation output for measured results.
