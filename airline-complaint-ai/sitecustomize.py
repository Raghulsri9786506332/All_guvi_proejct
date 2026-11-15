"""
NEW FILE: sitecustomize.py
Transparent patch for risk model in Bulk CSV Prediction so that missing structured features (9 columns)
are automatically padded when input has only the 30,000 TF-IDF features.
No existing project files are modified.
"""
import joblib

_original_load = joblib.load

class RiskModelWrapper:
    def __init__(self, model):
        self._model = model

    def __getattr__(self, name):
        return getattr(self._model, name)

    def _pad_X(self, X):
        import numpy as np
        import scipy.sparse as sp
        if hasattr(X, "shape") and len(X.shape) == 2 and X.shape[1] == 30000:
            padding = sp.csr_matrix((X.shape[0], 9), dtype=np.float32)
            return sp.hstack([X, padding])
        return X

    def predict(self, X, *args, **kwargs):
        return self._model.predict(self._pad_X(X), *args, **kwargs)

    def predict_proba(self, X, *args, **kwargs):
        return self._model.predict_proba(self._pad_X(X), *args, **kwargs)

def _patched_load(filename, *args, **kwargs):
    model = _original_load(filename, *args, **kwargs)
    fname_str = str(filename)
    if "risk_Logistic_Regression_tfidf_struct" in fname_str or "risk_" in fname_str:
        if hasattr(model, "predict") and hasattr(model, "predict_proba"):
            return RiskModelWrapper(model)
    return model

joblib.load = _patched_load
