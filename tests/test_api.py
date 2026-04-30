import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app

client = TestClient(app)

@patch("app.main.insert_application")
@patch("app.main.build_graph")
@patch("app.main.AsyncSqliteSaver.from_conn_string")
@pytest.mark.asyncio
async def test_evaluate_loan_auto_approve(mock_from_conn_string, mock_build_graph, mock_insert_application):
    """
    Scenario: We are testing a situation where the application works flawlessly and receives AUTO-APPROVE.
    :param mock_from_conn_string:
    :param mock_build_graph:
    :param mock_insert_application:
    :return:
    """

    mock_memory = AsyncMock()
    mock_from_conn_string.__aenter__.return_value = mock_memory

    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "risk_score": 0.08,
        "final_decision": "APPROVE",
        "logs": ["Test log: Risk is low"]
    })

    mock_state = MagicMock()
    mock_state.next = []
    mock_graph.aget_state = AsyncMock(return_value=mock_state)

    mock_build_graph.return_value = mock_graph

    payload = {
        "full_name": "Ahmet Yılmaz",
        "monthly_income": 15000,
        "requested_loan": 5000,
        "credit_score": 750,
        "employment_years": 2,
        "existing_debt": 23,

    }
    response = client.post("/evaluate", json=payload)

    assert response.status_code == 200, f"Error Detail: {response.text}"
    data = response.json()
    assert data["status"] == "completed"
    assert data["decision"] == "APPROVE"
    assert data["risk_score"] == 0.08

    mock_insert_application.assert_called_once()