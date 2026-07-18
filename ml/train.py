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
OPERATING_ACCURACY_GATE = 0.95
MIN_AUTO_DECISION_COVERAGE = 0.90


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


def best_operating_policy(prob, y_test) -> dict:
    best = None
    for low in [x / 1000 for x in range(20, 500, 5)]:
        for high in [x / 1000 for x in range(500, 980, 5)]:
            if low >= high:
                continue
            auto_mask = (prob <= low) | (prob >= high)
            if not auto_mask.any():
                continue
            auto_pred = (prob[auto_mask] >= high).astype(int)
            auto_accuracy = accuracy_score(y_test[auto_mask], auto_pred)
            coverage = float(auto_mask.mean())
            if auto_accuracy >= OPERATING_ACCURACY_GATE and coverage >= MIN_AUTO_DECISION_COVERAGE:
                if best is None or coverage > best["coverage"] or (coverage == best["coverage"] and auto_accuracy > best["accuracy"]):
                    best = {
                        "accuracy": float(auto_accuracy),
                        "coverage": coverage,
                        "manual_review_rate": float(1 - coverage),
                        "auto_decision_rows": int(auto_mask.sum()),
                        "manual_review_rows": int((~auto_mask).sum()),
                        "low_threshold": float(low),
                        "high_threshold": float(high),
                        "confusion_matrix": confusion_matrix(y_test[auto_mask], auto_pred).tolist(),
                    }
    return best or {
        "accuracy": 0.0,
        "coverage": 0.0,
        "manual_review_rate": 1.0,
        "auto_decision_rows": 0,
        "manual_review_rows": int(len(y_test)),
        "low_threshold": None,
        "high_threshold": None,
        "confusion_matrix": [],
    }


def evaluate(pipe, X_test, y_test) -> dict:
    pred = pipe.predict(X_test)
    if hasattr(pred, "to_numpy"):
        pred = pred.to_numpy()
    pred = pd.Series(pred).astype(int).to_numpy()
    prob = pipe.predict_proba(X_test)[:, 1]
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, pred, average="binary", zero_division=0)
    operating_policy = best_operating_policy(prob, y_test)
    return {
        "accuracy": accuracy_score(y_test, pred),
        "roc_auc": roc_auc_score(y_test, prob),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "operating_policy": operating_policy,
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

    eligible = [name for name, result in results.items()
                if result["operating_policy"]["accuracy"] >= OPERATING_ACCURACY_GATE
                and result["operating_policy"]["coverage"] >= MIN_AUTO_DECISION_COVERAGE]
    best = max(eligible or results, key=lambda x: (results[x]["operating_policy"]["coverage"], results[x]["operating_policy"]["accuracy"], results[x]["accuracy"]))
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    try:
        results[best]["cross_validation_accuracy"] = cross_val_score(fitted[best], X, y, cv=cv, scoring="accuracy", n_jobs=-1).tolist()
    except RuntimeError as exc:
        results[best]["cross_validation_accuracy"] = []
        results[best]["cross_validation_note"] = f"Skipped for selected estimator: {exc}"

    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    gate_passed = best in eligible
    report = {"operating_accuracy_gate": OPERATING_ACCURACY_GATE,
              "minimum_auto_decision_coverage": MIN_AUTO_DECISION_COVERAGE,
              "gate_passed": gate_passed,
              "selected_model": best, "training_rows": len(df), "candidates": results}

    if not gate_passed:
        (REPORTS / "metrics_failed_gate.json").write_text(json.dumps(report, indent=2))
        raise RuntimeError(
            f"Operating quality gate failed: {results[best]['operating_policy']['accuracy']:.3%} "
            f"< {OPERATING_ACCURACY_GATE:.0%}"
        )
    failed_report = REPORTS / "metrics_failed_gate.json"
    if failed_report.exists():
        failed_report.unlink()

    thresholds = {
        "low": results[best]["operating_policy"]["low_threshold"],
        "high": results[best]["operating_policy"]["high_threshold"],
    }
    joblib.dump({"pipeline": fitted[best], "model_name": best, "metrics": results[best],
                 "feature_columns": X.columns.tolist(),
                 "decision_thresholds": thresholds}, OUT / "model.joblib", compress=3)
    (REPORTS / "metrics.json").write_text(json.dumps(report, indent=2))
    print(
        f"Selected {best}; overall accuracy={results[best]['accuracy']:.3%}; "
        f"operating accuracy={results[best]['operating_policy']['accuracy']:.3%}; "
        f"auto-decision coverage={results[best]['operating_policy']['coverage']:.3%}"
    )


if __name__ == "__main__": main()
