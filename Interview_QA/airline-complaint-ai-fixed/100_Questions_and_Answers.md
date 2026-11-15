# Airline Complaint AI — 100 Interview Questions and Answers

Code basis: the available project copy `airline-complaint-ai-fixed\airline-complaint-ai`. The separately specified source path under `Interview_QA\airline-complaint-ai-fixed` was not present when inspected. Answers below follow the available code, and call out relevant implementation caveats rather than treating documentation claims as verified runtime behavior.

1. **Q: What problem does Airline Complaint AI address?**  
   **A:** It analyzes airline review text and predicts one of four severity labels—Low, Medium, High, or Critical—and a separate binary service-risk flag. The app also supports review exploration and batch CSV prediction.

2. **Q: What is the main input dataset?**  
   **A:** The configured raw input is `data/raw/Airline_review.csv`, loaded by `load_raw_dataset(path)` in `src/data/data_loader.py`. Its columns include review title and text, overall and aspect ratings, recommendation, traveller and seat categories, and airline/date metadata.

3. **Q: How do the two prediction tasks differ?**  
   **A:** Severity is a four-class label represented internally by IDs 0–3. Risk is a separate binary `risk_flag` where 1 means Risk and 0 means No Risk. They have different label rules and evaluation metrics.

4. **Q: Which script coordinates training?**  
   **A:** `train_pipeline.py` is the entry point. Its `main()` calls data preparation, traditional ML training, optional deep-learning and transformer phases, then builds and saves a model comparison table.

5. **Q: What does `parse_args()` allow an operator to control?**  
   **A:** The script accepts `--sample N`, `--skip-dl`, and `--skip-transformers`. For example, `python train_pipeline.py --sample 2000 --skip-dl --skip-transformers` requests a smaller run without the two optional model families.

6. **Q: What happens in `run_data_phases()`?**  
   **A:** It loads and optionally samples the raw table, calls `clean_dataset()`, produces `text_ml`, `text_dl`, and `text_transformer`, generates labels, adds structured features, then writes `data/processed/airline_processed.parquet`.

7. **Q: How does the CSV loader handle malformed lines?**  
   **A:** `load_raw_dataset()` calls `pd.read_csv(..., encoding="utf-8", on_bad_lines="skip")`. This allows reading to continue but discards malformed rows, so the resulting dataset may omit source records.

8. **Q: What does `get_inspection_report()` report?**  
   **A:** It returns a dictionary with shape, columns, data types, missing-value counts, duplicate count, distinct overall ratings, and recommendation counts when that column exists. `_inspect()` logs similar diagnostics during loading.

9. **Q: What is the purpose of `clean_dataset()`?**  
   **A:** It returns a cleaned copy and applies overall-rating conversion, aspect-rating conversion and imputation, categorical normalization, exact-duplicate removal, and title null filling, in that order.

10. **Q: How are invalid overall ratings handled?**  
    **A:** `_convert_overall_rating()` uses `pd.to_numeric(..., errors="coerce")`; invalid strings become missing values instead of causing a conversion exception. The overall rating is not imputed in this function.

11. **Q: How are missing aspect ratings handled?**  
    **A:** `_convert_aspect_ratings()` converts each configured aspect to numeric, creates a corresponding `*_missing` indicator, and fills missing values with that column’s median. If an entire aspect column is missing, its median may itself be missing, so this code does not guarantee a finite fallback.

12. **Q: Which categorical fields does the cleaner normalize?**  
    **A:** `_normalize_categoricals()` strips whitespace and lowercases `Type Of Traveller`, `Seat Type`, `Recommended`, and `Verified` when their dtype is `object`. A boolean `Verified` column is mapped to the strings `yes` and `no`.

13. **Q: Which rows are considered duplicates?**  
    **A:** `_drop_exact_duplicates()` checks the available columns among `Airline Name`, `Review_Title`, `Review Date`, and `Review`, keeps the first matching row, then resets the index. It does not compare every column.

14. **Q: Does the cleaner discard records with optional information missing?**  
    **A:** It does not explicitly drop records for missing aircraft or route. It does fill missing titles with an empty string, while missing review text is handled later by label and text-building functions.

15. **Q: How are training labels created?**  
    **A:** `generate_labels(df)` makes a copy, converts `Overall_Rating` to numeric, joins title and review for keyword matching, then calls `_assign_severity()` and `_assign_risk()` row by row to add `severity_label`, `severity_id`, and `risk_flag`.

16. **Q: What is the mapping from severity names to IDs?**  
    **A:** The label generator maps Low→0, Medium→1, High→2, and Critical→3. `SEVERITY_LABELS` in `src/utils/config.py` lists the same order used by prediction code to turn class IDs back into names.

17. **Q: What are the base rules in `_assign_severity()`?**  
    **A:** A rating at most 2 gives Critical. Ratings 3–4 give High, except at least three poor aspects or a negative recommendation plus a critical phrase raises it to Critical. Ratings 5–6 give Medium, and ratings above 6 start at Low.

18. **Q: What happens when the overall rating is missing?**  
    **A:** `_assign_severity()` assigns High if a critical keyword appears and Medium otherwise. This fallback is a proxy rule, not a judgment from a human labeler.

19. **Q: How can a keyword upgrade severity?**  
    **A:** After the base rule, a critical keyword upgrades Low or Medium to High. A High label upgrades to Critical only when `Recommended` is `no`. For example, a high-rated review containing “cancelled” may be raised from Low to High.

20. **Q: How does `_assign_risk()` decide whether a review is risky?**  
    **A:** It returns 1 only when recommendation is `no`, overall rating is present and at most 4, and either at least two aspect ratings are at most 2 or a configured risk keyword occurs. All other cases return 0.

21. **Q: What counts as a “poor aspect” for the label rules?**  
    **A:** `_count_poor_aspects()` counts configured columns in `RATING_COLS` whose values are not missing and are at most 2. Those columns cover seven aspects, including seat comfort, cabin staff, food, ground service, entertainment, Wi-Fi, and value.

22. **Q: Why should these labels not be called verified ground truth?**  
    **A:** They are generated from ratings, recommendation, and keywords, not manually annotated. A model evaluated against them is learning to approximate those rules and their biases; this is not the same as proving real-world complaint severity.

23. **Q: Why is risk-label leakage a concern?**  
    **A:** `risk_flag` itself depends on `Recommended`, low overall rating, poor aspects, or risk keywords. Risk training uses structured aspects plus keyword count, so some model inputs overlap with the recipe for the target. Scores can therefore reflect rule recovery rather than independent risk detection.

24. **Q: What is `_base_clean()` responsible for?**  
    **A:** It fixes basic text encoding, HTML-unescapes text, expands contractions, removes HTML tags and URLs, drops some symbol characters, normalizes punctuation, and collapses whitespace. It is the shared initial step for all three text paths.

25. **Q: Why does the project have separate text cleaning paths?**  
    **A:** Traditional sparse models benefit from token and stop-word processing; embedding models retain more context; transformer tokenizers expect relatively intact language. `build_full_text()` routes text to `ml_clean`, `dl_clean`, or `transformer_clean` accordingly.

26. **Q: How does `ml_clean()` prepare a review?**  
    **A:** It applies `_base_clean()`, lowercases, tokenizes with NLTK, retains alphabetic tokens, removes English stop words except `no`, `not`, and `never`, and lemmatizes by default. This is the text representation used by BoW and TF-IDF.

27. **Q: Why are negations kept during ML cleaning?**  
    **A:** Words such as “not” can reverse sentiment: “not good” is different from “good.” The code explicitly keeps `no`, `not`, and `never`, and `_base_clean()` expands contractions such as “didn’t” to “did not.”

28. **Q: What does `dl_clean()` preserve or remove?**  
    **A:** It applies shared cleaning, lowercases, and removes characters outside letters, digits, whitespace, and apostrophes. Unlike `ml_clean()`, it does not remove stop words or lemmatize tokens.

29. **Q: What does `transformer_clean()` do differently?**  
    **A:** It returns the shared-cleaned text without lowercasing or stop-word removal, preserving case and most language context for the tokenizer. The configured base model `distilbert-base-uncased` may itself use an uncased tokenizer.

30. **Q: How does `build_full_text()` treat missing titles and reviews?**  
    **A:** It converts `None` and pandas missing values to empty strings, joins title and review with a space, then dispatches to the requested cleaner. An unsupported pipeline name raises `ValueError`.

31. **Q: What does `preprocess_dataframe()` return?**  
    **A:** It applies `build_full_text()` row by row using the requested title and review columns and returns a pandas Series of processed text. In training, it is called once for each of the three named pipelines.

32. **Q: Which text fields are used to make labels versus model text?**  
    **A:** Label generation joins the raw title and review into a lowercase helper string for keyword checks. The model paths separately create cleaned text, while `full_review_text` is also assembled for structured review-length and keyword features.

33. **Q: What does `BagOfWordsFeatures` wrap?**  
    **A:** It wraps scikit-learn’s `CountVectorizer` with unigrams and a default maximum vocabulary of 20,000 features. It exposes `fit_transform()`, `transform()`, `save()`, and `load()`.

34. **Q: What does `TFIDFFeatures` wrap?**  
    **A:** It wraps `TfidfVectorizer`, defaulting to up to 30,000 features, unigrams and bigrams, and sublinear term frequency. It has the same fit, transform, persistence, and load interface as the BoW wrapper.

35. **Q: Why must vectorizers be fitted only on training data?**  
    **A:** Fitting on all text would let the held-out test vocabulary influence feature construction. `run_ml_phases()` fits each vectorizer on `X_ml_train` and uses only `transform()` on `X_ml_test`, reducing this source of leakage.

36. **Q: Which structured columns are concatenated with text?**  
    **A:** `STRUCTURED_COLS` is `RATING_COLS` plus `review_length` and `keyword_count`, so the combined representation has the available aspect ratings and two review-derived measures.

37. **Q: How are `review_length` and `keyword_count` calculated?**  
    **A:** `add_structured_features()` measures the character length of the raw full review text and counts distinct strings in the union of critical and risk keyword lists. `count_keywords()` uses the same distinct-keyword idea for one text.

38. **Q: What does `get_structured_matrix()` do?**  
    **A:** It selects available structured columns, fills remaining nulls with zero, converts to `float32`, and either fits a `StandardScaler` or applies a supplied fitted scaler. It raises a `ValueError` if asked to transform without a scaler.

39. **Q: How does `build_combined_features()` join text and numeric data?**  
    **A:** It converts the structured NumPy array into a CSR sparse matrix and horizontally stacks it with the TF-IDF matrix using `scipy.sparse.hstack()`. The resulting columns must match between training and inference.

40. **Q: How does `build_inference_struct()` handle missing values?**  
    **A:** It builds one row in `STRUCTURED_COLS` order, derives length and keyword count from title plus review, substitutes the fitted scaler’s mean for absent or zero ratings, and transforms the row with that scaler. The function exists and has tests, but the prediction page does not call it.

41. **Q: What is the train/test split strategy in `run_ml_phases()`?**  
    **A:** It splits text, severity IDs, risk labels, and row indexes together using `train_test_split`, `TEST_SIZE=0.20`, and seed 42, stratifying on severity. It does not stratify directly on risk.

42. **Q: How does the code avoid fitting the structured scaler on test data?**  
    **A:** `get_structured_matrix(df_train, fit=True)` fits the scaler, then `get_structured_matrix(df_test, scaler=scaler, fit=False)` only transforms test rows. The scaler is saved as `artifacts/vectorizers/struct_scaler.pkl`.

43. **Q: Which severity models are created by `_severity_models()`?**  
    **A:** The factory returns Logistic Regression, a calibrated Linear SVM, and Multinomial Naive Bayes. The trainer is run on BoW and TF-IDF, and Logistic Regression and SVM are also trained on TF-IDF plus structured features.

44. **Q: What should an interviewer know about the Logistic Regression configuration in this copy?**  
    **A:** The checked-in `src/models/ml_trainer.py` uses `solver="saga"` and calls `warnings.filterwarnings("ignore")`; the combined-feature Logistic Regression in `train_pipeline.py` also uses `saga`. This differs from some statements in `CHANGES.md`, so inspect the executable code before claiming a solver or convergence fix.

45. **Q: Why is the Linear SVM wrapped in `CalibratedClassifierCV`?**  
    **A:** `LinearSVC` provides decision scores rather than class probabilities. Calibration with three-fold CV lets app code call `predict_proba()`, which it uses to display severity confidence.

46. **Q: Why is Multinomial Naive Bayes skipped for combined features?**  
    **A:** Standard-scaled numeric features can be negative, while `MultinomialNB` expects non-negative inputs. The combined-feature path therefore trains only Logistic Regression and calibrated SVM.

47. **Q: Which models can train for the risk task?**  
    **A:** `_risk_models()` defines Logistic Regression and Random Forest. It adds XGBoost if importable, otherwise attempts LightGBM. The pipeline trains them on TF-IDF plus structured data.

48. **Q: What does `train_severity_models()` record?**  
    **A:** For each successful classifier, it records accuracy, macro precision/recall/F1, per-class recall, confusion matrix, training and inference time, and the fitted classifier object. It saves the estimator under `models/ml/`.

49. **Q: What does `train_risk_models()` record?**  
    **A:** It computes predicted labels and probabilities, then records ROC-AUC, average precision (PR-AUC), precision, recall, F1, false negatives, confusion matrix, and timings. This function’s result dictionary does not include accuracy.

50. **Q: Where do vectorizers and ML estimators get saved?**  
    **A:** The pipeline writes BoW and TF-IDF vectorizers and the structured scaler under `artifacts/vectorizers/`. `train_severity_models()` and `train_risk_models()` use `joblib.dump()` to save fitted ML estimators under `models/ml/`.

51. **Q: How does the DL tokenizer build its vocabulary?**  
    **A:** `SimpleTokenizer.build_vocab()` counts whitespace-separated words from training text and retains up to 50,000 entries, with `<PAD>` at 0 and `<UNK>` at 1. `encode()` maps unknown words to 1 and pads or truncates to `MAX_LEN_DL=256`.

52. **Q: What is the DL `ReviewDataset` interface?**  
    **A:** It stores token ID sequences, labels, and optional structured features. `__getitem__()` returns tensors named `input_ids` and `label`, and includes `struct` when numeric features are provided.

53. **Q: What does `_collate_fn()` do for a batch?**  
    **A:** It pads sequences to the longest sequence in that batch, stacks labels, and optionally stacks structured features. In this pipeline, however, `SimpleTokenizer.encode()` already pads each sequence to 256, so batches usually remain that long.

54. **Q: How does `TextCNN` classify a review?**  
    **A:** It embeds token IDs, applies parallel one-dimensional convolutions with kernel sizes 3, 4, and 5, max-pools each output, concatenates the pooled vectors, applies dropout, and sends the result to a linear classifier.

55. **Q: What is the difference between `TextLSTM` and its bidirectional form?**  
    **A:** `TextLSTM` uses an embedding followed by a two-layer LSTM by default. With `bidirectional=True`, it concatenates the final forward and backward hidden states before classification; the pipeline uses that mode for BiLSTM.

56. **Q: How are DL model parameters updated and early stopping applied?**  
    **A:** `train_dl_model()` uses weighted cross-entropy when class weights are supplied, Adam with learning rate `2e-3`, gradient clipping at 1.0, and a `ReduceLROnPlateau` scheduler. It tracks validation accuracy and stops after `patience` non-improving epochs.

57. **Q: What DL architectures does the pipeline request?**  
    **A:** `run_dl_phase()` loops over `"CNN"`, `"LSTM"`, and `"BiLSTM"`, with 128-dimensional embeddings and up to eight epochs. DL is skipped if `--skip-dl` is passed or PyTorch is unavailable.

58. **Q: What does the transformer path use?**  
    **A:** Configuration names `distilbert-base-uncased` as the primary model and `bert-base-uncased` for comparison. `tokenize_data()` uses a Hugging Face tokenizer with truncation at 256 tokens and dynamic padding via `DataCollatorWithPadding`.

59. **Q: How are transformer training datasets prepared?**  
    **A:** `tokenize_data(texts, labels, model_name)` creates a Hugging Face `Dataset` from text and labels, maps the selected tokenizer in batches, removes the raw text column, and returns both the dataset and tokenizer.

60. **Q: How does `fine_tune_transformer()` account for class imbalance?**  
    **A:** Its custom `WeightedTrainer.compute_loss()` applies `CrossEntropyLoss` with supplied class weights, when provided. The training code computes weights from labels in the training split before calling it.

61. **Q: What transformer metrics are computed for severity and risk?**  
    **A:** Severity metrics include accuracy, macro-F1, and macro-recall. Risk metrics use softmax probabilities for ROC-AUC and calculate F1, recall, and precision from predicted classes.

62. **Q: Is the transformer evaluation set independent from model selection here?**  
    **A:** No. Despite a configured `VAL_SIZE=0.10`, the pipeline creates one train/test split and passes `df_test` as the `val_ds` for transformer training. `load_best_model_at_end` can therefore select checkpoints using the set later treated as test.

63. **Q: Does the DL phase also evaluate on a separate validation split?**  
    **A:** No. `run_dl_phase()` wraps `df_test` in `test_ds` and passes its DataLoader as `val_dl` for early stopping, then reports results from that same loader. The current pipeline has no distinct validation partition.

64. **Q: What is the practical meaning of `VAL_SIZE` in this code?**  
    **A:** `VAL_SIZE` is imported from configuration but is not used to construct a separate split in the shown pipeline. Do not describe the current run as a train/validation/test protocol without changing and verifying the split code.

65. **Q: What does `evaluate_severity()` return?**  
    **A:** It returns accuracy, macro precision, macro recall, macro-F1, critical-class recall when the class name is supplied, a classification report, and a confusion matrix. It can also save a confusion-matrix plot.

66. **Q: What does `evaluate_risk()` return?**  
    **A:** It returns ROC-AUC, PR-AUC, precision, recall, F1, false-negative count and rate, and confusion matrix. It does not return accuracy, so accuracy should not be inferred from its ROC-AUC.

67. **Q: How does `build_comparison_table()` handle missing metrics?**  
    **A:** Accuracy is `NaN` if absent; macro-F1, recall, ROC-AUC, and timings use zero-valued defaults when their keys are missing. Review result keys before interpreting a comparison row, especially when comparing risk and severity tasks.

68. **Q: Where are the comparison results written?**  
    **A:** `main()` writes the DataFrame from `build_comparison_table()` to `data/processed/model_comparison_table.csv` and logs the table. The existence of a report does not by itself establish the validity or reproducibility of reported scores.

69. **Q: What performance claims are safe to make in an interview?**  
    **A:** Explain the evaluation code and point to a specific, reproducible run with its split and label definitions. Do not invent a score or present the rule-derived labels as human-verified truth; `CHANGES.md` contains reported figures, but this Q&A does not claim to have reproduced them.

70. **Q: What does `highlight_complaint_phrases()` explain?**  
    **A:** It searches review text for configured critical and risk phrases and returns the original text plus a list of matches. It is a transparent keyword display, not a model attribution method.

71. **Q: How does keyword highlighting treat overlapping phrases?**  
    **A:** It checks longer phrases first and skips a shorter phrase contained within one already found. For example, it aims to show “cancelled” without also listing the substring “cancel.”

72. **Q: What does `explain_prediction()` provide to the app?**  
    **A:** It formats severity and risk outputs, confidence/probability percentages, detected phrases, and phrase subsets associated with severity or risk keyword lists. Its disclaimer correctly says phrase association does not establish causality.

73. **Q: How does `get_linear_top_features()` work?**  
    **A:** It attempts to read model coefficients, gets feature names from the vectorizer, and returns the largest absolute coefficients for a requested class. It catches exceptions and returns an `("error", ...)` tuple, so callers should not assume coefficients are available for every calibrated estimator.

74. **Q: When would `get_lime_explanation()` be usable?**  
    **A:** It can use LIME’s text explainer with a callback that accepts a list of strings and returns probabilities. It requests a local explanation with a default of 10 features and 500 samples, or returns `None` if LIME is unavailable.

75. **Q: What is the role and limitation of `get_shap_values()`?**  
    **A:** It tries to create a `TreeExplainer` and return SHAP values for a tree model. It is optional and returns `None` on errors; the function does not return feature names or prove that a feature caused a prediction.

76. **Q: What does the root `app.py` configure?**  
    **A:** It sets the Streamlit page title, icon, wide layout, and sidebar branding/navigation, then ensures the project root is importable. Streamlit discovers the multipage scripts in `pages/`.

77. **Q: What does the Introduction page communicate?**  
    **A:** `pages/1_Introduction.py` presents the problem, business uses, project goals, and high-level KPIs. Those KPI values are UI copy, not a live check of model artifacts or a measured test result.

78. **Q: How does the EDA page find its data?**  
    **A:** `load_data()` prefers `data/processed/airline_processed.parquet`, then local `data/raw/Airline_review.csv`, and finally attempts a CSV download from a fixed GitHub raw URL. If labels are missing, it cleans and generates them.

79. **Q: What does the EDA page show?**  
    **A:** It offers severity and airline filters and visualizes distributions and comparisons such as severity by airline and overall ratings. The page uses Streamlit and Plotly; its date/trend handling should be verified against actual date formats and data.

80. **Q: What validation does the prediction page apply to uploaded CSVs?**  
    **A:** It requires a `Review` column and creates an empty `Review_Title` if absent. Aspect-rating columns are described as optional, and the page previews the first five rows before prediction.

81. **Q: How does `load_models()` choose local or hosted artifacts?**  
    **A:** It checks for a TF-IDF vectorizer, severity model, risk model, and scaler locally; if not all exist, it downloads corresponding files with `hf_hub_download()` from a configured Hugging Face model repository.

82. **Q: What controls the prediction page’s Hugging Face repository?**  
    **A:** `HF_MODEL_REPO` comes from an environment variable and defaults to `Raghulsri9786506332/airline-models`. A deployment should configure that value intentionally and ensure the repository contents are trusted.

83. **Q: Why is `load_models()` decorated with `st.cache_resource`?**  
    **A:** Streamlit can cache the loaded estimators and vectorizer as shared resources rather than deserializing them on every rerun. The cache improves responsiveness but does not validate artifact provenance or compatibility.

84. **Q: What does `predict_single()` do with a review’s text?**  
    **A:** It calls `build_full_text(title, review, pipeline="ml")`, transforms the result using the loaded TF-IDF vectorizer, and uses the severity classifier’s probability vector to select a class and confidence.

85. **Q: How is the severity label chosen for a single prediction?**  
    **A:** The page applies `np.argmax()` to `predict_proba()` output, then maps the resulting index through `["Low", "Medium", "High", "Critical"]`. This assumes the classifier’s class ordering matches that list.

86. **Q: Is single-review risk feature construction aligned with training?**  
    **A:** Not in the current page code. It builds TF-IDF plus seven ratings, `len(review)`, and a hard-coded zero keyword count; missing ratings become zero. Although `build_inference_struct()` exists to align and scale features, `predict_single()` does not use it.

87. **Q: Does the optional overall rating input affect the normal model path?**  
    **A:** The `rating` parameter is used only by the rule-based fallback. In the loaded-model path, the risk feature row includes the seven aspect ratings, review length, and keyword count but not overall rating.

88. **Q: How does bulk prediction construct the risk model input?**  
    **A:** In the model-loaded branch, it transforms batch text to TF-IDF and calls the risk classifier directly with that matrix. The training pipeline fits risk models on TF-IDF plus structured features, so the shipped input dimensions may not match and the call can fail.

89. **Q: What fallback is used if models cannot be loaded?**  
    **A:** The page falls back to private label helpers `_assign_severity()` and `_assign_risk()` for single prediction and uses `generate_labels()` for bulk prediction. These outputs are rule-based proxies, not trained-model predictions.

90. **Q: Are there caveats in the single-review rule fallback?**  
    **A:** Yes. The current code constructs `Recommended` as `no` regardless of its walrus-expression branch, and its `_text` expression has operator-precedence behavior that may omit the review when a title is present. That can skew fallback severity and risk.

91. **Q: What does bulk prediction return to the user?**  
    **A:** It concatenates the original input rows with severity prediction, confidence, risk flag, and risk probability columns, displays the result, and offers `airline_predictions.csv` as a download.

92. **Q: Which models are deliberately used by the lightweight Streamlit Cloud entry point?**  
    **A:** `app_streamlit_cloud.py` describes a lightweight ML-only deployment using Logistic Regression with TF-IDF for severity and a TF-IDF-plus-structured Logistic Regression for risk, excluding DL, transformers, and SHAP to reduce resource demand.

93. **Q: Does the application load DL or transformer checkpoints for prediction?**  
    **A:** The current `pages/3_Prediction.py` loader loads only TF-IDF, two ML estimators, and the structured scaler. DL and transformer trainers exist, but that page does not provide inference loading for their checkpoints.

94. **Q: What does `upload_models_to_hf.py` upload?**  
    **A:** It uploads the TF-IDF vectorizer, selected severity and risk Logistic Regression pickles, and the structured scaler to a Hugging Face model repository. It skips missing local files and reports the missing paths.

95. **Q: What security concern applies to the Hugging Face upload command?**  
    **A:** The script accepts `--token` directly on the command line. Tokens passed this way may be exposed through shell history or process inspection; use a secure secret mechanism and never commit a real token.

96. **Q: What should be checked before deploying the AWS materials?**  
    **A:** The available `deployment/aws/README_aws.md` is only a short docstring naming `deploy_ec2.sh`; no runnable EC2 script is present in that folder. A real deployment still needs validated IAM, network exposure, authentication, logging, and secret handling, so do not assume production readiness from that placeholder.

97. **Q: How do `requirements.txt` and `requirements_full.txt` differ in intent?**  
    **A:** `requirements.txt` is aimed at the lighter ML inference app and omits PyTorch and Transformers. `requirements_full.txt` includes those training dependencies, plus pytest and optional explainability packages such as SHAP.

98. **Q: What tests cover core behavior?**  
    **A:** `tests/test_data.py` checks cleaning, label rules, preprocessing, and basic model interfaces. `tests/test_fixes.py` checks negations and null text, string ratings, structured inference features, keyword overlap, comparison-table behavior, and optional DL shapes.

99. **Q: What regressions are particularly relevant to test after changes?**  
    **A:** Verify train/inference feature dimensions for risk, null and zero rating handling, keyword count and review-length consistency, text negation preservation, and that evaluation metrics are not mislabeled. The current tests exercise `build_inference_struct()`, but do not by themselves prove the Streamlit page uses it.

100. **Q: What broader limitations and safeguards should a reviewer mention?**  
     **A:** Targets are proxy labels, risk inputs overlap with its label rule, validation uses the held-out test set for DL/transformer selection, and prediction-page feature paths have alignment gaps. Review text and CSVs are untrusted input; avoid exposing sensitive review data, validate uploaded files, and load `joblib`/pickle artifacts only from trusted sources because deserialization can execute code.
