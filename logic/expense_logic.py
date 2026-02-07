import os
import json
from datetime import datetime


# ---------------------------
# Global File Path
# ---------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(BASE_DIR, "data", "expense.json")


# ---------------------------
# File Helpers
# ---------------------------

def load_json():
    """Load data safely"""

    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({"months": {}}, f, indent=4)

    try:
        with open(FILE, "r") as f:
            return json.load(f)

    except json.JSONDecodeError:
        return {"months": {}}


def save_json(data):
    """Save data safely"""

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------
# Date Helpers
# ---------------------------

def current_date():
    return datetime.now().strftime("%d-%m-%Y")


def current_month_key():
    return datetime.now().strftime("%Y-%m")


def current_month_name():
    return datetime.now().strftime("%B")


def current_year_name():
    return str(datetime.now().year)


# ---------------------------
# Month Mapping
# ---------------------------

def get_month_mapping(data):
    """
    Returns:
    {
        "January 2026": "2026-01"
    }
    """

    mapping = {}

    for key in sorted(data["months"].keys(), reverse=True):
        year, month = key.split("-")

        month_name = datetime.strptime(month, "%m").strftime("%B")

        display = f"{month_name} {year}"

        mapping[display] = key

    return mapping


# ---------------------------
# Monthly Balance
# ---------------------------

def add_monthly_balance(data, balance):

    key = current_month_key()

    if key not in data["months"]:
        data["months"][key] = {
            "starting_balance": balance,
            "expenses": []
        }

    save_json(data)


# ---------------------------
# Expenses
# ---------------------------

def add_expense(data, item, quantity, amount):

    key = current_month_key()

    # Ensure month exists
    if key not in data["months"]:
        raise ValueError("Monthly balance not set.")

    expense = {
        "date": current_date(),
        "item": item,
        "quantity": quantity,
        "amount": amount
    }

    data["months"][key]["expenses"].append(expense)

    save_json(data)


def delete_expense(data, month_key, date, item):

    if month_key not in data["months"]:
        return False

    expenses = data["months"][month_key]["expenses"]

    new_list = [
        e for e in expenses
        if not (e["date"] == date and e["item"] == item)
    ]

    data["months"][month_key]["expenses"] = new_list

    save_json(data)

    return True


def edit_expense(data, month_key, date, item,
                 new_quantity=None,
                 new_amount=None):

    if month_key not in data["months"]:
        return False

    for exp in data["months"][month_key]["expenses"]:

        if exp["date"] == date and exp["item"] == item:

            if new_quantity is not None:
                exp["quantity"] = new_quantity

            if new_amount is not None:
                exp["amount"] = new_amount

            save_json(data)

            return True

    return False


def clear_month(data, month_key):

    if month_key in data["months"]:
        data["months"][month_key]["expenses"] = []
        save_json(data)


# ---------------------------
# Calculations
# ---------------------------

def calculate_total(data, month_key):

    if month_key not in data["months"]:
        return None

    month = data["months"][month_key]

    start = month.get("starting_balance", 0)
    expenses = month.get("expenses", [])

    if not len(expenses) == 0:
        total = sum(e["amount"] for e in expenses)
    else:
        return False

    remaining = start - total

    return {
        "starting_balance": start,
        "total_expenses": total,
        "remaining_balance": remaining,
        "expenses": expenses
    }


def get_daily_record(data, month_key, date):

    if month_key not in data["months"]:
        return None

    expenses = data["months"][month_key]["expenses"]

    daily = [e for e in expenses if e["date"] == date]

    total = sum(e["amount"] for e in daily)

    return {
        "total_expenses": total,
        "expenses": daily
    }
