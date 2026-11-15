# Tests: Airline Complaint AI fixed copy

Run the tests from the nested `airline-complaint-ai` directory:

```powershell
python -m pytest
```

## Test directories

- `tests/test_data.py` — tests data cleaning, severity/risk labels, text preprocessing, and model-interface behavior.
- `tests/test_fixes.py` — regression tests for previously fixed issues such as missing ratings, inference feature dimensions, keyword counts, explanation overlaps, and evaluation metrics.
- `test cases/conftest.py` — shared pytest fixtures and test setup.
- `test cases/TC_001_smoke_tests.py` — checks basic application components.
- `test cases/TC_002_unit_data_cleaning.py` — focused data-cleaning tests.
- `test cases/TC_003_unit_label_generation.py` — severity and risk rule tests.
- `test cases/TC_004_unit_text_preprocessing.py` — tests the three text-cleaning paths.
- `test cases/TC_005_unit_feature_engineering.py` — tests vectorizers and structured features.
- `test cases/TC_006_unit_explainability.py` — tests explanation behavior.
- `test cases/TC_007_integration_pipeline.py` — tests components working together.
- `test cases/TC_008_regression_bug_fixes.py` — tests known bug fixes.
- `test cases/TC_009_boundary_edge_cases.py` — tests unusual or boundary inputs.

The tests are useful for checking expected behavior after code changes. Some tests may need optional model dependencies or model resources; install only the dependencies required by the test that fails.
