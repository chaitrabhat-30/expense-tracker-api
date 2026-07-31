"""
Smart Expense Tracker API
--------------------------
A simple REST API for tracking personal expenses.
Data is stored in memory (a Python list) - it resets when the server restarts.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import itertools

app = FastAPI(
    title="Smart Expense Tracker API",
    description="A simple API to add, view, filter, total, and delete expenses.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------
# We use a plain Python list of dicts as our storage.
# _id_counter gives every new expense a unique, auto-incrementing id.
expenses: list[dict] = []
_id_counter = itertools.count(1)


# ---------------------------------------------------------------------------
# Pydantic models (these define what valid request/response data looks like)
# ---------------------------------------------------------------------------
class ExpenseCreate(BaseModel):
    """What the client sends us when creating a new expense."""
    title: str = Field(..., min_length=1, description="What the expense was for")
    amount: float = Field(..., gt=0, description="Amount spent, must be positive")
    category: str = Field(..., min_length=1, description="e.g. Food, Travel, Rent")
    date: str = Field(..., description="Date of expense, e.g. 2026-07-31")


class Expense(ExpenseCreate):
    """What we send back to the client - includes the server-generated id."""
    id: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/expenses", response_model=Expense, status_code=201)
def add_expense(expense: ExpenseCreate):
    """Add a new expense."""
    new_expense = Expense(id=next(_id_counter), **expense.model_dump())
    expenses.append(new_expense.model_dump())
    return new_expense


@app.get("/expenses", response_model=list[Expense])
def get_expenses(category: Optional[str] = None):
    """
    View all expenses.
    Optionally filter by category using ?category=Food
    """
    if category:
        # Case-insensitive match so "food" and "Food" both work
        return [e for e in expenses if e["category"].lower() == category.lower()]
    return expenses


@app.get("/expenses/total")
def get_total(category: Optional[str] = None):
    """
    Get total expenses.
    - No query param: returns overall total + breakdown by category
    - ?category=Food: returns total for just that category
    """
    if category:
        matching = [e for e in expenses if e["category"].lower() == category.lower()]
        return {
            "category": category,
            "total": round(sum(e["amount"] for e in matching), 2),
            "count": len(matching),
        }

    overall_total = round(sum(e["amount"] for e in expenses), 2)

    by_category: dict[str, float] = {}
    for e in expenses:
        by_category[e["category"]] = by_category.get(e["category"], 0) + e["amount"]
    by_category = {k: round(v, 2) for k, v in by_category.items()}

    return {
        "overall_total": overall_total,
        "by_category": by_category,
        "count": len(expenses),
    }


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    """Delete an expense by its id."""
    global expenses
    for e in expenses:
        if e["id"] == expense_id:
            expenses.remove(e)
            return
    raise HTTPException(status_code=404, detail=f"Expense with id {expense_id} not found")


@app.get("/")
def root():
    """Simple health check / welcome route."""
    return {"message": "Smart Expense Tracker API is running. See /docs for API docs."}