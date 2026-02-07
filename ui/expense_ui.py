import sys
import os

# Add project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

import streamlit as st

from logic.expense_logic import *

def render():
    # ---------------------------
    # Load Data
    # ---------------------------
    data = load_json()


    # ---------------------------
    # Helpers
    # ---------------------------

    def month_selector(data):

        mapping = get_month_mapping(data)

        current_key = current_month_key()
        current_display = f"{current_month_name()} {current_year_name()}"

        if current_key not in data["months"]:
            mapping[current_display] = current_key

        selected = st.selectbox("Select Month", list(mapping.keys()))

        return mapping[selected]


    def show_balance(data, month_key, show=False):
        with st.container():
            st.divider()
            with st.expander("💰 Monthly Balance", expanded=show):
                if month_key in data["months"]:

                    bal = data["months"][month_key]["starting_balance"]

                    st.metric("Current Balance",f"Rs {bal:,}")

                else:
                    st.info("No data for this month.")


    # ---------------------------
    # Overview Page
    # ---------------------------

    def home():
        st.title("📊 Overview")

        month_key = month_selector(data)

        show_balance(data, month_key, True)

        st.divider()

        summary = calculate_total(data, month_key)

        if summary:
            st.write("Spent:", summary["total_expenses"])
            st.write("Remaining:", summary["remaining_balance"])

            st.divider()

            if summary["expenses"]:
                st.table(summary["expenses"])
            else:
                st.info("No expenses")
        else:
            st.info("No Expenses")


    # ---------------------------
    # Monthly Balance Page
    # ---------------------------

    def monthly_balance_ui():

        st.title("💰 Monthly Balance")

        month_key = month_selector(data)

        show_balance(data, month_key, True)

        st.divider()

        # Only allow adding for current month
        if month_key == current_month_key():

            if month_key not in data["months"]:

                balance = st.number_input(
                    "Enter Monthly Balance",
                    min_value=0,
                    step=100
                )

                if st.button("Save Balance"):
                    add_monthly_balance(data, balance)
                    st.success("Saved")
                    st.rerun()

            else:
                st.info("Balance already set")

        else:
            st.info("Only current month is editable")


    # ---------------------------
    # Add Expense Page
    # ---------------------------

    def add_expenses_ui():

        st.title("🛒 Add Expenses")

        month_key = current_month_key()

        show_balance(data, month_key, False)

        if month_key not in data["months"]:
            st.warning("Set balance first")
            return


        # -------------------------
        # Categories
        # -------------------------
        CATEGORIES = [
            "Dairy Products",
            "Vegetables",
            "Meat",
            "Spices",
            "Snacks",
            "Other Items"
        ]


        # -------------------------
        # Initialize Cart
        # -------------------------
        if "temp_expenses" not in st.session_state:
            st.session_state.temp_expenses = []


        # -------------------------
        # Category Grid (Forms)
        # -------------------------
        rows = [
            CATEGORIES[:3],
            CATEGORIES[3:]
        ]


        for r, row in enumerate(rows):

            cols = st.columns(3)

            for c, (col, cat) in enumerate(zip(cols, row)):

                with col:

                    with st.form(key=f"form_{r}_{c}"):

                        st.markdown(f"### {cat}")

                        item = st.text_input("Item")

                        qty = st.number_input(
                            "Qty",
                            min_value=0.1,
                            value=1.0,
                            step=0.1
                        )

                        price = st.number_input(
                            "Price Per Unit (kg/ltr)",
                            min_value=1,
                            step=5
                        )


                        amount = qty * price

                        st.caption(f"Total: Rs {amount:.0f}")


                        submitted = st.form_submit_button("Add")


                        if submitted:

                            if not item.strip():
                                st.error("Enter item")
                                st.stop()


                            st.session_state.temp_expenses.append({
                                "category": cat,
                                "item": item,
                                "quantity": qty,
                                "price": price,
                                "amount": amount,
                                "date": current_date()
                            })


                            st.toast("Added", icon="✅")
                            st.rerun()


        st.divider()


        # -------------------------
        # Cart
        # -------------------------
        st.markdown("## 📝 Cart")

        if not st.session_state.temp_expenses:

            st.info("Cart is empty")

        else:

            for i, exp in enumerate(st.session_state.temp_expenses):

                col1, col2, col3, col4, col5, col6 = st.columns(
                    [2, 2, 1.2, 1.2, 1.5, 1]
                )

                with col1:
                    st.write(exp["category"])

                with col2:
                    st.write(exp["item"])

                with col3:
                    st.write(exp["quantity"])

                with col4:
                    st.write(f"Rs {exp['price']}")

                with col5:
                    st.write(f"Rs {exp['amount']:.0f}")

                with col6:

                    if st.button("❌", key=f"del_{i}"):

                        st.session_state.temp_expenses.pop(i)

                        st.toast("Removed", icon="🗑️")
                        st.rerun()


        st.divider()


        # -------------------------
        # Summary
        # -------------------------
        if st.session_state.temp_expenses:

            total = sum(e["amount"] for e in st.session_state.temp_expenses)

            st.success(f"🧾 Total: Rs {total:.0f}")


        # -------------------------
        # Save All
        # -------------------------
        if st.session_state.temp_expenses:

            if st.button("💾 Save All Expenses"):

                for exp in st.session_state.temp_expenses:

                    add_expense(
                        data,
                        exp["item"],
                        exp["quantity"],
                        exp["amount"]
                    )

                st.session_state.temp_expenses.clear()

                st.success("All saved")
                st.rerun()


    # ---------------------------
    # Edit Expense Page
    # ---------------------------

    def edit_expenses_ui():

        st.title("✏️ Edit Expense")

        month_key = month_selector(data)

        if month_key not in data["months"]:
            st.info("No data")
            return

        expenses = data["months"][month_key]["expenses"]

        if not expenses:
            st.info("No expenses")
            return

        options = [
            f"{e['date']} | {e['item']} | Rs {e['amount']}"
            for e in expenses
        ]

        choice = st.selectbox("Select Expense", options)

        idx = options.index(choice)

        exp = expenses[idx]

        qty = st.number_input("New Quantity", value=exp["quantity"])
        amt = st.number_input("New Amount", value=exp["amount"])

        if st.button("Update"):

            edit_expense(
                data,
                month_key,
                exp["date"],
                exp["item"],
                qty,
                amt
            )

            st.success("Updated")
            st.rerun()


    # ---------------------------
    # Delete Expense Page
    # ---------------------------

    def delete_expenses_ui():

        st.title("🗑️ Delete Expense")
        st.warning("⚠️ This action cannot be undone.")

        month_key = month_selector(data)

        if month_key not in data["months"]:
            st.info("No data")
            return

        expenses = data["months"][month_key]["expenses"]

        if not expenses:
            st.info("No expenses")
            return

        options = [
            f"{e['date']} | {e['item']} | Rs {e['amount']}"
            for e in expenses
        ]

        choice = st.selectbox("Select Expense", options, index=None, placeholder="Choose an option...")

        # Only run this logic if 'choice' is NOT None
        if choice:
            idx = options.index(choice)
            exp = expenses[idx]
        # else:
        #     st.info("Please select an expense from the dropdown to continue.")

        if st.button("Delete"):

            delete_expense(
                data,
                month_key,
                exp["date"],
                exp["item"]
            )

            st.success("Deleted")
            st.rerun()


    # ---------------------------
    # Search / Filter Page
    # ---------------------------

    def search_filter_ui():

        st.title("🔍 Search / Filter")

        month_key = month_selector(data)

        date = st.date_input("Select Date (Optional)")

        if month_key not in data["months"]:
            st.info("No data")
            return

        expenses = data["months"][month_key]["expenses"]

        if date:

            date_str = date.strftime("%d-%m-%Y")

            expenses = [
                e for e in expenses
                if e["date"] == date_str
            ]

        if expenses:
            st.table(expenses)
        else:
            st.info("No results")


    # ---------------------------
    # Sidebar Navigation
    # ---------------------------

    with st.sidebar:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image("image/accounting_image.svg", width=150)
        st.title("💼 Menu")
        st.write("Manage Your Household Expenses")
        st.divider()

        page = st.radio(
            "Navigate",
            [
                "Home",
                "Monthly Balance",
                "Add Expenses",
                "Edit Expenses",
                "Delete Expenses",
                "Search / Filter"
            ]
        )

        st.divider()

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()


    # ---------------------------
    # Page Router
    # ---------------------------

    if page == "Home":
        home()

    elif page == "Monthly Balance":
        monthly_balance_ui()

    elif page == "Add Expenses":
        add_expenses_ui()

    elif page == "Edit Expenses":
        edit_expenses_ui()

    elif page == "Delete Expenses":
        delete_expenses_ui()

    elif page == "Search / Filter":
        search_filter_ui()
