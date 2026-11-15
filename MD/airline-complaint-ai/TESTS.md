# Airline Complaint AI test guide

Run the suite from the airline project directory:

```powershell
python -m pytest
```

## Test areas

- `tests/test_data.py` checks loading/cleaning data, label generation, preprocessing, and explanation behavior.
- `tests/test_fixes.py` checks regressions that were previously corrected, including text handling, feature dimensions, and model/evaluation edge cases.
- `test cases/TC_001_smoke_tests.py` checks that basic project components start and connect.
- `test cases/TC_002_unit_data_cleaning.py` checks cleaning behavior.
- `test cases/TC_003_unit_label_generation.py` checks severity and risk rules.
- `test cases/TC_004_unit_text_preprocessing.py` checks the text-cleaning pipelines.
- `test cases/TC_005_unit_feature_engineering.py` checks vector and structured features.
- `test cases/TC_006_unit_explainability.py` checks explanation outputs.
- `test cases/TC_007_integration_pipeline.py` checks workflows across multiple components.
- `test cases/TC_008_regression_bug_fixes.py` checks known bug fixes.
- `test cases/TC_009_boundary_edge_cases.py` checks unusual and boundary inputs.
- `test cases/conftest.py` provides shared fixtures and test setup.

Test names describe individual cases. Consult those files for the exact inputs and expected results.
