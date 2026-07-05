"""Train, evaluate, and persist the strongest reproducible candidate."""
from pathlib import Path
import json
import joblib
import pandas as pd
import sys
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.model_pipeline import FeatureBuilder

DATA = ROOT / "data" / "credit_risk_dataset.csv"
OUT = ROOT / "ml" / "artifacts"
REPORTS = ROOT / "ml" / "reports"
TARGET = "loan_status"
QUALITY_GATE = 0.95


def clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df = df[(df.person_age.between(18, 100)) & (df.person_emp_length.fillna(0).between(0, 80))]
    return df.drop_duplicates().copy()


def feature_columns(X: pd.DataFrame):
    preview = FeatureBuilder().fit(X).transform(X.head(20))
    cats = preview.select_dtypes(include=["object", "string"]).columns.tolist()
    nums = [x for x in preview.columns if x not in cats]
    return nums, cats


def preprocessor(X: pd.DataFrame, dense=False):
    nums, cats = feature_columns(X)
    return Pipeline([
        ("features", FeatureBuilder()),
        ("columns", ColumnTransformer([
            ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), nums),
            ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                              ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=not dense))]), cats),
        ], sparse_threshold=0 if dense else 0.3)),
    ])


def catboost_candidate(X: pd.DataFrame):
    try:
        from catboost import CatBoostClassifier
    except ImportError:
        return None

    _, cats = feature_columns(X)
    return Pipeline([
        ("features", FeatureBuilder()),
        ("classifier", CatBoostClassifier(
            loss_function="Logloss",
            eval_metric="Accuracy",
            iterations=1000,
            depth=6,
            learning_rate=0.035,
            l2_leaf_reg=6,
            random_strength=0.8,
            bagging_temperature=0.4,
            cat_features=cats,
            random_seed=42,
            verbose=False,
            allow_writing_files=False,
            thread_count=-1,
        )),
    ])


def evaluate(pipe, X_test, y_test) -> dict:
    pred = pipe.predict(X_test)
    if hasattr(pred, "to_numpy"):
        pred = pred.to_numpy()
    pred = pd.Series(pred).astype(int).to_numpy()
    prob = pipe.predict_proba(X_test)[:, 1]
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, pred, average="binary", zero_division=0)
    return {
        "accuracy": accuracy_score(y_test, pred),
        "roc_auc": roc_auc_score(y_test, prob),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }


def main():
    df = clean_data()
    X, y = df.drop(columns=[TARGET]), df[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)

    candidates = {
        "logistic_regression": Pipeline([
            ("preprocessor", preprocessor(X_train)),
            ("classifier", LogisticRegression(max_iter=2000, C=1.0)),
        ]),
        "random_forest": Pipeline([
            ("preprocessor", preprocessor(X_train)),
            ("classifier", RandomForestClassifier(n_estimators=700, min_samples_leaf=1, max_features="sqrt",
                                                   criterion="entropy", n_jobs=-1, random_state=42)),
        ]),
        "hist_gradient_boosting": Pipeline([
            ("preprocessor", preprocessor(X_train, dense=True)),
            ("classifier", HistGradientBoostingClassifier(random_state=42, learning_rate=.06, max_iter=700,
                                                          max_leaf_nodes=31, l2_regularization=0,
                                                          early_stopping=True, validation_fraction=.1)),
        ]),
        "gradient_boosting": Pipeline([
            ("preprocessor", preprocessor(X_train, dense=True)),
            ("classifier", GradientBoostingClassifier(random_state=42, n_estimators=500,
                                                      learning_rate=.05, max_depth=4, subsample=.9)),
        ]),
    }
    catboost = catboost_candidate(X_train)
    if catboost is not None:
        candidates["catboost"] = catboost

    results, fitted = {}, {}
    for name, pipe in candidates.items():
        pipe.fit(X_train, y_train)
        results[name] = evaluate(pipe, X_test, y_test)
        fitted[name] = pipe
        print(name, results[name])

    best = max(results, key=lambda x: results[x]["accuracy"])
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    results[best]["cross_validation_accuracy"] = cross_val_score(fitted[best], X, y, cv=cv, scoring="accuracy", n_jobs=-1).tolist()

    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = {"quality_gate": QUALITY_GATE, "gate_passed": results[best]["accuracy"] >= QUALITY_GATE,
              "selected_model": best, "training_rows": len(df), "candidates": results}

    if results[best]["accuracy"] < QUALITY_GATE:
        (REPORTS / "metrics_failed_gate.json").write_text(json.dumps(report, indent=2))
        raise RuntimeError(f"Quality gate failed: {results[best]['accuracy']:.3%} < {QUALITY_GATE:.0%}")

    joblib.dump({"pipeline": fitted[best], "model_name": best, "metrics": results[best],
                 "feature_columns": X.columns.tolist()}, OUT / "model.joblib", compress=3)
    (REPORTS / "metrics.json").write_text(json.dumps(report, indent=2))
    print(f"Selected {best}; test accuracy={results[best]['accuracy']:.3%}")


if __name__ == "__main__": main()
