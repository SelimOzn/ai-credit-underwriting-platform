from app.models.state import AgentState
from app.models.outputs import RiskAnalystOutput
from app.tools.registry import TOOL_REGISTRY
from app.tools.executor import execute_tool
from app.tools.financial import calculate_dti,calculate_lti
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from pathlib import Path

import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import shap


root = Path.cwd()
MODEL_PATH = Path(root, "scoring_models", "xgboost_risk_model.json")
PREPROCESSOR_PATH = Path(root, "scoring_models", "preprocessor.pkl")

if not os.path.exists(PREPROCESSOR_PATH) or not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError("The trained XGBoost model or preprocessor object could not be found in "
                            "the scoring_models/ directory.")


model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

preprocessor = joblib.load(PREPROCESSOR_PATH)

explainer = shap.TreeExplainer(model)


async def run(state: AgentState) -> AgentState:
    app = state.application

    past_defaults = state.external_data["past_defaults"]
    cb_person_default_on_file = "Y" if past_defaults>0 else "N"

    credit_score = app.credit_score

    if credit_score > 799:
        loan_grade = "A"
    elif credit_score > 739:
        loan_grade = "B"
    elif credit_score > 669:
        loan_grade = "C"
    elif credit_score > 579:
        loan_grade = "D"
    elif credit_score > 499:
        loan_grade = "E"
    elif credit_score > 399:
        loan_grade = "F"
    else:
        loan_grade = "G"

    loan_percent_income = calculate_lti(app)
    loan_to_emp_length_ratio = app.requested_loan / app.employment_years if app.employment_years>0 else 0
    int_rate_to_loan_amt_ratio = state.external_data["loan_int_rate"] / app.requested_loan if app.requested_loan>0 else 0


    income_group = pd.cut([app.monthly_income],
                          bins=[0, 25000, 50000, 75000, 100000, float("inf")],
                          labels=["low", "low-middle", "middle", "high-middle", "high"])

    loan_amnt_group = pd.cut([app.requested_loan],
                            bins=[0, 5000, 10000, 15000, float("inf")],
                            labels=["small", "medium", "large", "very-large"])


    raw_data = {
        "person_age": app.age,
        "person_income": app.monthly_income*12,
        "person_home_ownership": app.home_ownership,
        "person_emp_length": app.employment_years,
        "loan_intent": app.loan_intent,
        "loan_grade": loan_grade,
        "loan_amnt": app.requested_loan,
        "loan_int_rate": state.external_data["loan_int_rate"],
        "loan_percent_income": loan_percent_income,
        "cb_person_default_on_file": cb_person_default_on_file,
        "cb_person_cred_hist_length": state.external_data["cb_person_cred_hist_length"],
        "income_group": income_group,
        "loan_amount_group": loan_amnt_group,
        "loan_to_emp_length_ratio": loan_to_emp_length_ratio,
        "int_rate_to_loan_amt_ratio": int_rate_to_loan_amt_ratio
    }

    df = pd.DataFrame(raw_data)

    x_processed = preprocessor.transform(df)

    probabilities = model.predict_proba(x_processed)

    risk_score = float(probabilities[0][1])

    shap_values = explainer.shap_values(x_processed)

    if isinstance(shap_values, list):
        current_shap = shap_values[1][0]
    elif len(shap_values.shape) == 3:
        current_shap = shap_values[0, :, 1]
    elif len(shap_values.shape) == 2 and shap_values.shape[0] == 1:
        current_shap = shap_values[0]
    else:
        current_shap = shap_values

    feature_names = preprocessor.get_feature_names_out()
    if len(current_shap) == len(feature_names):
        impacts = list(zip(feature_names, current_shap))
    else:
        impacts = list(zip(feature_names[:len(current_shap)], current_shap))

    impacts = [(name, float(val)) for name, val in impacts]
    impacts.sort(key=lambda x: abs(x[1]), reverse=True)

    top_factors = [f"{name} ({'+' if val>0 else ''}{round(val,4)})" for name, val in impacts[:3]]

    state.risk_score = round(risk_score,4)
    state.reasons.extend([f"{name} ({'+' if val>0 else ''}{round(val,4)})" for name, val in impacts])
    state.shap_factors = impacts

    state.logs.append(f"XGBoost Risk Model executed. Calculated PD: {state.risk_score}")
    state.logs.append(f"Primary risk drivers: {', '.join(top_factors)}")

    return state

