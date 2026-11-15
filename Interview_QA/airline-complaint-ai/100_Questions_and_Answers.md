# Airline Complaint AI: 100 Technical Interview Questions and Answers

1. **What problem does this project solve?**  
   It helps an airline triage customer reviews by predicting one of four severity levels and a binary service-risk flag. The intention is to help staff prioritize reviews, not to make final customer-service decisions automatically.

2. **What does the end-to-end pipeline do?**  
   `train_pipeline.py` loads and inspects the CSV, cleans structured columns, creates three cleaned text views, generates rule-based labels, adds engineered features, splits the data, trains model families, evaluates them, and writes a model-comparison CSV. It can skip DL or transformers and can sample rows for a quick run.

3. **Which files are the main entry points?**  
   `train_pipeline.py` is the training entry point, while `app.py` starts the multi-page Streamlit interface. `src/data`, `src/preprocessing`, `src/features`, `src/models`, `src/evaluation`, and `src/explainability` hold the key implementation modules.

4. **What is the dataset, and what are its key fields?**  
   The README describes `Airline_review.csv` as 23,171 rows and 20 source columns. It includes review title and text, overall and aspect ratings, airline and travel context, dates, and a recommendation field. `Unnamed: 0` is an exported index and is not intended as a model feature.

5. **How is the raw dataset loaded?**  
   `src/data/data_loader.py` uses `pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")`. It logs shape, columns, data types, missing values, duplicates, rating values, and selected categorical distributions for inspection.

6. **Why inspect the dataset before training?**  
   Inspection reveals data quality problems such as invalid rating strings, missing values, duplicates, and unexpected categories. The loader's `_inspect` function makes these visible in logs before later pipeline steps depend on them.

7. **How are invalid overall ratings handled?**  
   `cleaner._convert_overall_rating` calls `pd.to_numeric(..., errors="coerce")`; values such as `"n"` become `NaN`. The label generator also defensively converts the rating, but the README does not claim that every missing overall rating is recovered.

8. **How are aspect ratings cleaned?**  
   `cleaner._convert_aspect_ratings` converts each configured rating to numeric and fills missing values with that column's median. Before filling, it adds a `*_missing` indicator, preserving a signal that the original value was unavailable.

9. **Why add missing-value indicators before imputation?**  
   A missing rating may mean “not rated,” rather than an average experience. The indicator lets downstream analysis distinguish an imputed rating from a value the reviewer supplied. In the current training feature list, however, `STRUCTURED_COLS` contains ratings, length, and keyword count—not these indicator columns.

10. **How are categories normalized?**  
    `cleaner._normalize_categoricals` strips whitespace and lowercases object values for `Type Of Traveller`, `Seat Type`, `Recommended`, and `Verified`. Boolean `Verified` values are mapped to `"yes"` or `"no"`.

11. **How does the pipeline handle duplicates?**  
    `cleaner._drop_exact_duplicates` removes repeated records using whichever of `Airline Name`, `Review_Title`, `Review Date`, and `Review` are present, retaining the first and resetting the index. This is a key-field duplicate rule, not a fuzzy match for paraphrased reviews.

12. **Are rows dropped when optional fields are missing?**  
    No. The README says records missing optional fields such as aircraft or route are retained. The cleaner fills missing titles with an empty string but does not generally drop rows to remove missingness.

13. **What happens to missing review titles and review text?**  
    The cleaner fills null `Review_Title` values with `""`; `build_full_text` also treats null or NaN title/review values as empty strings. This avoids turning a missing title into the literal text `"nan"`.

14. **What are the three text preprocessing paths?**  
    `text_preprocessor.py` exposes `ml_clean`, `dl_clean`, and `transformer_clean`. The ML path aggressively normalizes text for sparse n-gram models; the DL path retains stopwords for learned embeddings; and the transformer path does minimal cleanup for the pretrained tokenizer.

15. **What shared operations happen in `_base_clean`?**  
    It normalizes encoding, HTML-unescapes text, expands common negation contractions, removes HTML tags and URLs, removes Unicode “Symbol, Other” characters, normalizes punctuation, and collapses whitespace. It returns cleaned text that each specialized path further processes.

16. **Why preserve negations in preprocessing?**  
    Words such as “not” can reverse the meaning of a complaint. `ml_clean` explicitly keeps `no`, `not`, and `never` even though it removes most English stopwords. Regression tests check that forms such as “didn't” and “can't” become negations.

17. **How does `ml_clean` prepare text?**  
    It applies `_base_clean`, lowercases, tokenizes with NLTK, keeps alphabetic tokens while preserving selected negations, and lemmatizes by default with `WordNetLemmatizer`. The result is a space-separated token string for BoW or TF-IDF.

18. **How does the DL cleaning path differ?**  
    `dl_clean` lowercases and removes characters outside letters, digits, whitespace, and apostrophes, but does not remove stopwords or lemmatize. This leaves surrounding word context available to the embedding and sequence model.

19. **Why use a separate transformer cleaning path?**  
    A pretrained tokenizer expects relatively natural text. `transformer_clean` only applies shared cleanup and whitespace normalization; it does not lowercase, lemmatize, or remove stopwords itself. The configured DistilBERT/BERT tokenizers handle their own tokenization rules.

20. **How are title and review combined?**  
    `build_full_text(title, review, pipeline)` safely converts non-null fields to strings, joins them with a space, and dispatches to the requested cleaner. For example, `"Cancelled flight"` plus `"No refund"` becomes one text input.

21. **What if a caller requests an unknown preprocessing path?**  
    `build_full_text` raises a `ValueError` listing the supported names: `"ml"`, `"dl"`, and `"transformer"`. Failing clearly is safer than silently applying the wrong model-specific preprocessing.

22. **What are the labels, and how should they be interpreted?**  
    Severity is mapped as Low=0, Medium=1, High=2, Critical=3; risk is 0 or 1. Importantly, these are generated by `label_generator.py` from rules, ratings, recommendation, and keywords. They are proxy targets, not verified human annotations.

23. **How is severity initially assigned?**  
    `_assign_severity` makes ratings of 1–2 Critical; 3–4 High, with an additional Critical condition for at least three poor aspects or a negative recommendation plus a critical phrase; 5–6 Medium; and 7 or higher Low before keyword upgrades. Missing overall rating becomes High if a critical keyword appears, otherwise Medium.

24. **What do severity keyword upgrades do?**  
    A critical phrase upgrades Low or Medium to High. High is upgraded to Critical only when the recommendation is `"no"`. The keyword list in `config.py` includes terms and phrases such as `"cancelled"`, `"lost baggage"`, `"unsafe"`, `"rude staff"`, and `"nightmare"`.

25. **How is risk defined?**  
    `_assign_risk` returns 1 only when `Recommended` is `"no"`, the overall rating is present and at most 4, and either at least two aspect ratings are at most 2 or a risk keyword appears. It returns 0 otherwise, including when those conditions are not all met.

26. **Why be cautious about calling these labels ground truth?**  
    The README and module docstring explicitly state that labels are derived and not manually verified. A model scoring well against them shows how well it reproduces the rule system; it does not, by itself, prove that it correctly understands real-world complaint severity or future churn.

27. **What is a potential label leakage or shortcut concern here?**  
    The labels use ratings, recommendation, and complaint keywords, while model features can also include ratings and keyword count. Those overlapping signals can make prediction easier by encoding parts of the labeling recipe. This may be intentional proxy-label replication, but it is not independent validation against human judgments.

28. **How can the project improve the label design?**  
    Collect human-reviewed severity/risk annotations, document an annotation guide, measure annotator agreement, and reserve an independently labeled test set. Compare model predictions to that set separately from the rule-generated labels.

29. **What features does `add_structured_features` create?**  
    It adds `review_length`, based on character count of a full title-plus-review field, and `keyword_count`, based on the number of distinct keywords in the union of the critical and risk lists that occur in the text.

30. **What is the difference between keyword count and keyword occurrence count?**  
    `count_keywords` iterates through a set of configured terms and adds one for each term found as a substring. Repeating the same term does not increase the count. It is therefore a distinct matching-term count, not a raw word-frequency count.

31. **What is Bag-of-Words in this system?**  
    `BagOfWordsFeatures` wraps scikit-learn `CountVectorizer` with unigrams and a configured maximum of 20,000 features. It represents a review by token counts and does not model word order beyond token identity.

32. **How does TF-IDF differ from BoW here?**  
    `TFIDFFeatures` uses up to 30,000 features, unigrams and bigrams, and `sublinear_tf=True`. TF-IDF scales term importance using corpus statistics, while a bigram can represent a short phrase such as `"lost baggage"`.

33. **What is the combined feature representation?**  
    `build_combined_features` horizontally stacks sparse TF-IDF vectors and a scaled structured matrix. The structured columns are the available aspect ratings plus `review_length` and `keyword_count`.

34. **Why scale structured features?**  
    Ratings, character lengths, and keyword counts have different numeric ranges. `StandardScaler` puts them on comparable scales for models such as logistic regression, reducing the chance that raw units alone dominate the structured contribution.

35. **How does inference treat omitted rating values in the feature helper?**  
    `build_inference_struct` uses the fitted scaler's mean for an omitted or zero rating, so that value becomes neutral (zero) after standardization. It also recomputes review length and keyword count in the same column order as training.

36. **What split strategy does `run_ml_phases` use?**  
    It calls `train_test_split` with `test_size=TEST_SIZE`, a fixed random seed, and `stratify=y_sev`. The same indices split text, severity labels, risk labels, and the dataframe so paired rows stay aligned.

37. **What does stratifying on severity achieve, and what does it not achieve?**  
    It approximately preserves severity class proportions in train and test. It does not guarantee a balanced risk split, prevent related reviews from crossing the boundary, or test generalization to future dates or unseen airlines.

38. **How does the code prevent vectorizer vocabulary leakage?**  
    It fits BoW and TF-IDF only on `X_ml_train`, then calls `transform` on test text. Thus the test vocabulary and document frequencies do not influence feature selection or IDF weights.

39. **How does it prevent scaler leakage?**  
    `get_structured_matrix(df_train, fit=True)` fits the `StandardScaler` on training rows. The test matrix is transformed using that same fitted scaler, rather than computing test-set means and variances.

40. **Does the overall pipeline have any evaluation-design concern?**  
    Yes. In `run_dl_phase` and `run_transformer_phase`, the held-out test indices are passed as a validation dataset for training-time evaluation and early model selection. A stronger design would split training data again into train/validation and retain a final untouched test set for one-time reporting.

41. **Why might a random split be optimistic for reviews?**  
    Similar airline, route, time-period, or templated reviews could appear in both partitions. Random splitting measures interpolation within the sampled dataset, not necessarily future performance. A temporal, grouped, or airline-held-out evaluation would test different and often more realistic deployment conditions.

42. **Which traditional models are used for severity?**  
    `ml_trainer.py` creates Logistic Regression, calibrated Linear SVM, and Multinomial Naive Bayes. The main pipeline tries BoW and TF-IDF for all three and TF-IDF plus structured features for Logistic Regression and Linear SVM.

43. **Why calibrate the Linear SVM?**  
    A standard `LinearSVC` provides decision scores rather than native probabilities. `CalibratedClassifierCV` wraps it with cross-validated calibration so interfaces that need `predict_proba`, such as the Streamlit confidence display, can receive probability estimates.

44. **Why is Multinomial Naive Bayes skipped for the combined feature matrix?**  
    Multinomial NB expects non-negative inputs. Standard-scaled structured columns can be negative, so `train_pipeline.py` avoids fitting NB on `tfidf_struct` rather than feeding it an invalid representation.

45. **Which traditional models are used for risk?**  
    The risk factory includes Logistic Regression and Random Forest, plus XGBoost when installed or LightGBM as a fallback. The main pipeline trains risk models using the TF-IDF-plus-structured representation.

46. **How does class imbalance get handled?**  
    Logistic Regression and Linear SVM use `class_weight="balanced"`; Random Forest is also configured with balanced class weights. The DL and transformer phases compute weights from training labels. This changes training emphasis but does not guarantee good minority-class recall.

47. **What deep-learning architectures are implemented?**  
    `dl_trainer.py` provides `TextCNN` and `TextLSTM`, with the latter configured as unidirectional or bidirectional. The CNN applies parallel 1-D convolutions with kernel sizes 3, 4, and 5, max-pools each output, concatenates them, then classifies.

48. **How does the LSTM model form a review representation?**  
    It embeds token IDs and passes them through a two-layer LSTM with a hidden size of 256 by default. It uses the final hidden state, concatenating the final forward and backward states for the bidirectional variant.

49. **What role does the embedding layer play?**  
    The custom DL model maps each vocabulary ID to a trainable 128-dimensional vector in the pipeline configuration. Unlike a transformer, this embedding starts as model parameters learned during this task rather than contextual representations from pretraining.

50. **How is text tokenized for custom DL?**  
    `SimpleTokenizer` splits on whitespace and builds a vocabulary from training texts only, capped at 50,000 entries. ID 0 is padding and ID 1 is unknown. Encoding truncates to `MAX_LEN_DL` (256 by default) and pads to that length.

51. **Why fit the custom vocabulary on training text only?**  
    It prevents the test set from influencing which words enter the model's vocabulary. Unseen test words map to `<UNK>`, which is the intended behavior for a deployed model encountering new language.

52. **How are variable-length sequences batched?**  
    `ReviewDataset` stores token IDs and labels; `_collate_fn` pads each batch to its longest sequence. The current tokenizer also pads encoded sequences to its maximum length, so in the configured path this can mean fixed-length examples despite batch-level padding support.

53. **How does the DL training loop reduce overfitting or unstable updates?**  
    Training uses Adam, dropout, gradient clipping at norm 1.0, class-weighted loss, early stopping, and a `ReduceLROnPlateau` scheduler. The pipeline uses a limited epoch count for DL; the exact learning outcomes should be measured rather than assumed.

54. **What do the transformer models add?**  
    `transformer_trainer.py` fine-tunes `distilbert-base-uncased` and `bert-base-uncased` for four-class severity and binary risk. Their pretrained contextual representations can capture word meaning in context, at greater compute and memory cost than sparse ML.

55. **How are transformer inputs prepared?**  
    `tokenize_data` loads the model-specific `AutoTokenizer`, truncates at `MAX_LEN_TRANSFORMER` (256 by default), and leaves examples unpadded. `DataCollatorWithPadding` dynamically pads each batch.

56. **How does the transformer training code address class imbalance?**  
    It computes balanced class weights from training labels, then a custom `WeightedTrainer.compute_loss` applies weighted cross-entropy. The Trainer uses early stopping with patience two and selects best checkpoints by macro F1 for severity or F1 for risk.

57. **How does the project account for hardware differences?**  
    The DL and transformer modules choose CUDA when available and otherwise use CPU. Transformer training enables fp16 only when CUDA is available. `train_pipeline.py` also permits skipping optional DL and transformer phases.

58. **What is the purpose of `--sample`?**  
    It randomly selects at most the requested number of rows using the configured seed before preprocessing. This supports a quicker development run, but results from a sample are not interchangeable with full-data evaluation.

59. **How would you run an ML-only quick pipeline?**  
    The README gives `python train_pipeline.py --skip-dl --skip-transformers --sample 2000`. This is a reduced run for development, not evidence that the full or optional model phases have been validated.

60. **What severity metrics does the project track?**  
    `evaluator.evaluate_severity` reports accuracy, macro precision, macro recall, macro F1, a classification report, and a confusion matrix. It can also report Critical-class recall when given class names containing `"Critical"`.

61. **Why is macro F1 useful for four severity classes?**  
    Macro F1 computes F1 per class and averages the classes equally. It avoids allowing a frequent class to completely dominate the summary, which is useful when Critical reviews may be comparatively uncommon.

62. **Why is Critical-class recall a business metric?**  
    It measures the share of truly Critical examples identified by the model. Missing a serious complaint may delay intervention, so the README highlights this metric; it should be considered alongside precision, since excessive false alarms also burden staff.

63. **What risk metrics does the project report?**  
    `evaluate_risk` computes ROC-AUC, PR-AUC, precision, recall, F1, a confusion matrix, false-negative count, and false-negative rate. `ml_trainer.train_risk_models` also records these metrics and train/inference timings.

64. **Why report PR-AUC as well as ROC-AUC?**  
    PR-AUC focuses on the precision-recall tradeoff for the positive risk class and can be more informative when positive cases are rare. Neither number should be interpreted without the class prevalence and the operating threshold.

65. **What does the false-negative rate mean here?**  
    It is `false_negatives / actual_positive_count` in `evaluate_risk`. It tells what fraction of risk-positive examples were missed at the selected classification threshold. The code guards against division by zero using a denominator floor.

66. **How can a risk threshold be chosen responsibly?**  
    Do not assume the default classification threshold is optimal. Use a validation set to compare false-negative cost, precision, workload, and calibration, agree on an operating point with service stakeholders, and then evaluate that fixed threshold on untouched test data.

67. **What is in the model-comparison table?**  
    `build_comparison_table` records model, task, family, feature/input, accuracy, macro F1, recall, ROC-AUC, training time, and inference time. The pipeline writes it to `data/processed/model_comparison_table.csv`.

68. **Can severity and risk models be ranked by one number?**  
    Not meaningfully without a defined business objective. The tasks have different targets and metrics, and the proxy labels have different construction rules. Compare models within each task and consider recall, precision, calibration, runtime, and operational cost together.

69. **What explanation methods are available?**  
    `explainer.py` implements keyword highlighting, linear-model coefficient inspection, optional LIME text explanations, and optional Tree SHAP values. The code's disclaimer correctly says these are associations with predictions, not proof of cause.

70. **How does keyword highlighting work?**  
    `highlight_complaint_phrases` checks configured keywords in the lowercased input, preferring longer matches first so `"cancelled"` is retained instead of its overlapping substring `"cancel"`. It returns found phrases and the original text.

71. **How do linear coefficients help explain a prediction?**  
    `get_linear_top_features` reads a class's coefficient row and returns the largest absolute coefficients with their feature names. Positive or negative sign indicates direction for that class in the estimator's representation; it is not a causal explanation.

72. **What does LIME do in this project?**  
    `get_lime_explanation` perturbs a text instance and calls a supplied probability function to fit a local explanation. It returns the selected label and feature weights, or `None` if LIME is unavailable. The explanation is local and can vary with perturbations.

73. **What does the SHAP helper support?**  
    `get_shap_values` attempts `shap.TreeExplainer` on a tree estimator and returns SHAP values, or `None` if SHAP is unavailable or errors. It is intended for tree-based models, not as a universal explanation method.

74. **What information does `explain_prediction` return?**  
    It packages severity label and confidence, risk label and probability, detected complaint phrases, severity-related and risk-related subsets, and a disclaimer. These signals make an output easier to inspect without claiming causality.

75. **What pages does the Streamlit app provide?**  
    The README describes Introduction, EDA Dashboard, and Severity & Risk Prediction pages. The app entry point sets the page configuration and branding; individual files live under `pages/`.

76. **What can a user do in the prediction page?**  
    `pages/3_Prediction.py` provides a single-review form with optional ratings and a bulk CSV flow. Single predictions display severity, confidence, risk probability, phrase matches, and signals; batch predictions append prediction columns and offer a downloadable CSV.

77. **How are models loaded in the prediction UI?**  
    `load_models`, cached with `st.cache_resource`, first checks local TF-IDF, severity and risk model, and scaler files. If they are not all present, it tries to download the named artifacts from a Hugging Face model repository.

78. **What happens when model loading fails?**  
    The UI catches the exception, displays a warning, and returns an empty model dictionary. Prediction then uses a rule-based fallback. This is a demonstration fallback, not an equivalent substitute for a trained classifier.

79. **How does single-review ML inference work?**  
    It combines and ML-cleans the title and review, transforms the text with the saved TF-IDF vectorizer, gets severity probabilities, and selects the largest probability. For risk it uses the risk classifier and, when available, a scaled structured feature row.

80. **What should a reviewer verify in the current UI feature construction?**  
    Training constructs risk features from TF-IDF plus seven ratings, review length, and keyword count. The current single prediction path builds a structured array but sets its keyword count to zero, and it uses `len(review)` while training adds length on title plus review. These train/inference mismatches should be aligned before relying on risk predictions.

81. **Is the rule-based single-review fallback a calibrated prediction?**  
    No. `predict_single` assigns a placeholder severity confidence of `0.75`, and risk probability is set to 1 or 0 from the rule flag. Those are display values, not statistically calibrated model probabilities; the UI or documentation should make that explicit.

82. **What should be checked in the fallback input row?**  
    The fallback calls `_assign_severity` and `_assign_risk` directly. Its recommendation is currently hard-coded to `"no"` and its `_text` expression should be carefully checked for title/review concatenation precedence. This can cause fallback behavior that differs from the intended rule inputs.

83. **What limitations exist in bulk CSV prediction?**  
    The page checks for `Review` and creates an empty `Review_Title` when absent. In the ML path it transforms text and predicts risk from `X_batch` alone, while the training risk model is built on TF-IDF plus structured features; this dimensional/feature mismatch needs correction for reliable risk inference. The user-facing path should validate optional rating columns and build features consistently.

84. **Why should batch input validation be explicit?**  
    CSVs can have missing, misspelled, or nonnumeric fields and very large row counts. The page currently catches processing errors and displays them, but stronger validation should check schema, types, nulls, file size, and output dimensions before expensive processing.

85. **What is the lightweight Streamlit Cloud entry point?**  
    `app_streamlit_cloud.py` documents a 1-GB-RAM, no-GPU deployment that excludes DL, transformers, and SHAP. It points users to the ML-only pages and says the deployment uses Logistic Regression with TF-IDF-based artifacts.

86. **How is Hugging Face Hub used?**  
    The prediction page uses `HF_MODEL_REPO` (overridable by environment) and `hf_hub_download` to fetch vectorizer, classifier, and scaler files when local artifacts are incomplete. The deployment guide recommends storing large model files in the Hub rather than the app repository.

87. **What does the AWS deployment documentation establish?**  
    The README links to `deployment/aws/README_aws.md` and warns never to commit AWS credentials, recommending IAM roles or AWS Secrets Manager. The presence of deployment documentation is not proof that a production AWS service has been provisioned or load-tested.

88. **What dependencies distinguish the minimal and full environments?**  
    `requirements.txt` targets lightweight ML inference and the Streamlit app. `requirements_full.txt` adds PyTorch, Transformers, Hugging Face datasets/tokenizers, Accelerate, SHAP, and pytest for heavier training and optional explanations.

89. **How does the project organize paths and reproducibility?**  
    `src/utils/config.py` derives `BASE_DIR` from the source location and defines data, model, artifact, and log paths. It sets `RANDOM_SEED=42`, label mappings, rating columns, keyword lists, and model input limits in one place.

90. **Where are training outputs stored?**  
    The README describes scikit-learn pickles under `models/ml`, PyTorch weights under `models/dl`, transformer checkpoints under `models/transformers`, and vectorizers/scaler under `artifacts/vectorizers`. Processed parquet and comparison CSVs go under `data/processed`.

91. **What tests are present?**  
    The repository has `tests/test_data.py`, `tests/test_fixes.py`, and a separate `test cases` directory with smoke, cleaning, labeling, preprocessing, feature, explainability, integration, regression, and edge-case test modules. Describe the test inventory without claiming the suite passes unless it has actually been run.

92. **What regression cases are covered in `test_fixes.py`?**  
    It checks negation preservation and contraction expansion, NaN title handling, string and missing ratings in label generation, categorical normalization, feature shape and mean-imputation behavior, keyword overlap handling, comparison-table accuracy semantics, and optional DL handling of short or padded sequences.

93. **How would you test the data-cleaning function?**  
    Build a small DataFrame with `"3"` and invalid rating strings, missing titles, repeated key rows, and sparse aspect ratings. Assert numeric conversion, missing indicators, median fill, normalized categories, duplicate removal, and retention of rows with optional missing fields.

94. **How would you test an entire pipeline without expensive models?**  
    Use a small synthetic dataset and invoke the data phases plus ML paths with DL and transformer flags skipped. Assert output columns, train/test alignment, vectorizer transform dimensions, artifact creation, and comparison-table schema; keep this distinct from a full-data performance benchmark.

95. **What does the project currently not prove?**  
    The source and README do not establish validated business impact, accuracy against human ground truth, fairness across customer groups, production uptime, or a particular measured score. Interview answers should avoid quoting unverified model results.

96. **What are important model limitations?**  
    Rule-derived targets can encode simplistic thresholds, keyword matching can miss context or sarcasm, the dataset may not represent every airline or language, and sparse models can over-rely on vocabulary. Transformers and DL add compute costs without guaranteed gains.

97. **How would you monitor this system after deployment?**  
    Track input volume, missing fields, class and confidence distributions, latency, error rates, and review language drift. Sample predictions for human review, measure performance against newly adjudicated labels, and version the data, preprocessing, model, and thresholds used for each release.

98. **How would you address privacy and security for review data?**  
    Treat reviews and uploaded CSVs as potentially sensitive: minimize retained data, restrict access, avoid logging raw text, validate uploads, and use secure secret management. The README specifically warns against committing AWS credentials; production deployment should also define retention and access controls.

99. **What are the highest-priority technical improvements?**  
    First align training and inference feature construction—especially risk structured features, text length, and keyword count—and fix the batch feature mismatch. Next reserve an untouched test set, collect human-labeled targets, add group/temporal evaluation, validate probabilities and thresholds, and make fallback estimates clearly non-calibrated.

100. **How would you summarize the project in an interview?**  
    “I built an end-to-end airline-review triage prototype. It cleans structured data, keeps separate text paths for sparse ML, custom neural networks, and pretrained transformers, compares severity and risk classifiers, and exposes predictions in Streamlit. I also distinguish rule-generated proxy labels from human truth and would validate inference parity and independent labeled performance before production use.”
