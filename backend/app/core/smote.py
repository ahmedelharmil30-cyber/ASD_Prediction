"""Custom SMOTE implementation used by the trained model artifacts."""
from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.neighbors import NearestNeighbors


def smote_resample(X, y, k_neighbors=5, random_state=42):
    """Minority-class oversampling via SMOTE, built from scratch."""
    rng = np.random.RandomState(random_state)
    X = np.asarray(X)
    y = np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    majority_count = counts.max()

    X_parts, y_parts = [X], [y]
    for cls, cnt in zip(classes, counts):
        n_needed = majority_count - cnt
        if n_needed <= 0:
            continue

        X_cls = X[y == cls]
        k = min(k_neighbors, len(X_cls) - 1)
        if k < 1:
            idx = rng.randint(0, len(X_cls), n_needed)
            synth = X_cls[idx]
        else:
            nn = NearestNeighbors(n_neighbors=k + 1).fit(X_cls)
            synth = np.zeros((n_needed, X.shape[1]))
            base_idx = rng.randint(0, len(X_cls), n_needed)
            for i, bi in enumerate(base_idx):
                neighbors = nn.kneighbors(X_cls[bi].reshape(1, -1), return_distance=False)[0]
                neighbors = neighbors[neighbors != bi]
                if len(neighbors) == 0:
                    neighbors = [bi]
                nb = neighbors[rng.randint(0, len(neighbors))]
                gap = rng.rand()
                synth[i] = X_cls[bi] + gap * (X_cls[nb] - X_cls[bi])

        X_parts.append(synth)
        y_parts.append(np.full(n_needed, cls))

    return np.vstack(X_parts), np.concatenate(y_parts)


class SmotePipeline(BaseEstimator, ClassifierMixin):
    """Preprocess -> SMOTE (train-time only) -> classifier."""

    def __init__(self, preprocessor, classifier, k_neighbors=5, random_state=42):
        self.preprocessor = preprocessor
        self.classifier = classifier
        self.k_neighbors = k_neighbors
        self.random_state = random_state

    def fit(self, X, y, **fit_params):
        self.preprocessor_ = clone(self.preprocessor)
        self.classifier_ = clone(self.classifier)
        Xt = self.preprocessor_.fit_transform(X, y)
        if hasattr(Xt, "toarray"):
            Xt = Xt.toarray()
        Xr, yr = smote_resample(Xt, y, self.k_neighbors, self.random_state)
        self.classifier_.fit(Xr, yr)
        return self

    def _transform(self, X):
        Xt = self.preprocessor_.transform(X)
        if hasattr(Xt, "toarray"):
            Xt = Xt.toarray()
        return Xt

    def predict(self, X):
        return self.classifier_.predict(self._transform(X))

    def predict_proba(self, X):
        return self.classifier_.predict_proba(self._transform(X))

    def get_params(self, deep=True):
        out = {
            "preprocessor": self.preprocessor,
            "classifier": self.classifier,
            "k_neighbors": self.k_neighbors,
            "random_state": self.random_state,
        }
        if deep:
            for k, v in self.classifier.get_params(deep=True).items():
                out[f"classifier__{k}"] = v
        return out

    def set_params(self, **params):
        classifier_params = {}
        for key, value in params.items():
            if key.startswith("classifier__"):
                classifier_params[key.split("__", 1)[1]] = value
            else:
                setattr(self, key, value)
        if classifier_params:
            self.classifier.set_params(**classifier_params)
        return self
