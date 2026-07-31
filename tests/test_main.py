"""
Tests for the Smart Expense Tracker API.
Run with: pytest
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Make sure Python can find src/main.py regardless of where pytest is run from
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app, expenses  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_expenses():
    """Reset in-memory data before every single test, so tests don't affect each other."""
    expenses.clear()
    yield
    expenses.clear()


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_add_expense():
    response = client.post("/expenses", json={
        "title": "Coffee",
        "amount": 4.5,
        "category": "Food",
        "date": "2026-07-30",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Coffee"
    assert data["amount"] == 4.5
    assert data["category"] == "Food"
    assert "id" in data  # id should be auto-generated


def test_add_expense_invalid_amount():
    # amount must be > 0, so this should fail validation
    response = client.post("/expenses", json={
        "title": "Bad expense",
        "amount": -10,
        "category": "Food",
        "date": "2026-07-30",
    })
    assert response.status_code == 422  # FastAPI validation error


def test_get_all_expenses():
    client.post("/expenses", json={"title": "A", "amount": 10, "category": "Food", "date": "2026-07-01"})
    client.post("/expenses", json={"title": "B", "amount": 20, "category": "Travel", "date": "2026-07-02"})

    response = client.get("/expenses")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_by_category():
    client.post("/expenses", json={"title": "A", "amount": 10, "category": "Food", "date": "2026-07-01"})
    client.post("/expenses", json={"title": "B", "amount": 20, "category": "Travel", "date": "2026-07-02"})
    client.post("/expenses", json={"title": "C", "amount": 15, "category": "food", "date": "2026-07-03"})

    response = client.get("/expenses?category=Food")
    assert response.status_code == 200
    data = response.json()
    # Should match both "Food" and "food" (case-insensitive), but not "Travel"
    assert len(data) == 2
    assert all(e["category"].lower() == "food" for e in data)


def test_total_overall():
    client.post("/expenses", json={"title": "A", "amount": 10, "category": "Food", "date": "2026-07-01"})
    client.post("/expenses", json={"title": "B", "amount": 20, "category": "Travel", "date": "2026-07-02"})

    response = client.get("/expenses/total")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_total"] == 30
    assert data["by_category"] == {"Food": 10, "Travel": 20}


def test_total_by_category():
    client.post("/expenses", json={"title": "A", "amount": 10, "category": "Food", "date": "2026-07-01"})
    client.post("/expenses", json={"title": "B", "amount": 5, "category": "Food", "date": "2026-07-02"})
    client.post("/expenses", json={"title": "C", "amount": 20, "category": "Travel", "date": "2026-07-03"})

    response = client.get("/expenses/total?category=Food")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["count"] == 2


def test_delete_expense():
    create_response = client.post("/expenses", json={
        "title": "To delete", "amount": 100, "category": "Misc", "date": "2026-07-01"
    })
    expense_id = create_response.json()["id"]

    delete_response = client.delete(f"/expenses/{expense_id}")
    assert delete_response.status_code == 204

    # Confirm it's actually gone
    get_response = client.get("/expenses")
    assert len(get_response.json()) == 0


def test_delete_nonexistent_expense():
    response = client.delete("/expenses/9999")
    assert response.status_code == 404