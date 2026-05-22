from app.models.state import AgentState
import asyncio
import json
import random
import pandas as pd
from pathlib import Path
import os

async def fetch_kbb_and_tramer_data(applicant_name: str) -> dict:
    await asyncio.sleep(1.5) # Network latency simulation

    is_risky = len(applicant_name.replace(" ","")) % 2 != 0

    mock_response = {
        "source" : "Kredi Kayıt Bürosu & Tramer API",
        "past_defaults": 2 if is_risky else 0,
        "total_credit_cards": random.randint(1,5),
        "total_credit_limit": 50000 if is_risky else 250000,
        "active_loans_count": 3 if is_risky else 1,
        "payment_habit_score": "C (Risky)" if is_risky else "A (Good)",
        "past_insurance_claims": 1 if is_risky else 0,
        "last_inquiry_date": "2023-10-15",
        "loan_int_rate":random.uniform(5.42,22.11),
    }

    return mock_response

async def run(state: AgentState) -> AgentState:
    app = state.application
    state.logs.append(f"[Data Collector] External data sources (APIs) are being queried for {app.full_name}")

    try:
        root = Path.cwd().parent.parent
        data = pd.read_csv(Path(root, "data", "scoring_data", "credit_risk_dataset.csv"))
        data.dropna(axis=0, how='any', inplace=True)

        external_info = await fetch_kbb_and_tramer_data(app.full_name)

        subset = data[(data["person_age"] >=app.age-10)&(data["person_age"]<=app.age+10)]
        cred_hist_len = 0
        if len(subset)>0:
            cred_hist_len = subset["cb_person_cred_hist_length"].sample(1).iloc[0]

        external_info["cb_person_cred_hist_length"] = cred_hist_len
        state.external_data = external_info
        state.logs.append(f"[Data Collector] External System Data Successfully Retrieved")

    except Exception as e:
        state.logs.append("[Data collector] External System Data Failed:\n" + str(e))
        state.external_data = {}

    return state

