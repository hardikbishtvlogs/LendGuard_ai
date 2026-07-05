import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


GRADE_MAP = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}


class FeatureBuilder(BaseEstimator, TransformerMixin):
    """Build deterministic credit-risk features used by training and inference."""

    def fit(self, X: pd.DataFrame, y=None):
        self.rate_median_ = float(X["loan_int_rate"].median())
        self.emp_median_ = float(X["person_emp_length"].median())
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        z = X.copy()
        grade = z["loan_grade"].map(GRADE_MAP).fillna(4)
        rate = z["loan_int_rate"].fillna(self.rate_median_)
        emp = z["person_emp_length"].fillna(self.emp_median_)

        z["loan_to_income_x_rate"] = z["loan_percent_income"] * rate
        z["loan_to_income_x_grade"] = z["loan_percent_income"] * grade
        z["income_log"] = np.log1p(z["person_income"])
        z["loan_log"] = np.log1p(z["loan_amnt"])
        z["rate_missing"] = z["loan_int_rate"].isna().astype(int)
        z["emp_missing"] = z["person_emp_length"].isna().astype(int)
        z["previous_default_bin"] = (z["cb_person_default_on_file"] == "Y").astype(int)
        z["grade_num"] = grade
        z["emp_to_age"] = emp / z["person_age"].clip(lower=1)
        z["cred_to_age"] = z["cb_person_cred_hist_length"] / z["person_age"].clip(lower=1)
        z["loan_amount_x_rate"] = z["loan_amnt"] * rate
        return z
