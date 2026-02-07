import streamlit as st
from ui.expense_ui import render

def auth(username, password):
    acc_info = {
        "username": "demo",
        "password": "demo123"
    }

    if username == acc_info["username"]:
        if password == acc_info["password"]:
            return True
    return False

def main():

    st.set_page_config(
        page_title="Household Accounting",
        page_icon="🏠",
        layout="wide"
    )

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        render()
        return

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        st.title("Login Page")

    with st.container(border=True):

        with st.form(key="login_form"):

            username = st.text_input(
                "Username",
                placeholder="Enter Your Username"
            )

            password = st.text_input(
                "Password",
                placeholder="Enter Your Password",
                type="password"
            )

            if st.form_submit_button("Login"):

                status = auth(username, password)

                if status:

                    st.success("Login Successful")

                    # Clear login UI
                    st.session_state["logged_in"] = True
                    st.rerun()

                else:
                    st.error("Username or Password is Incorrect")



if __name__ == "__main__":
    main()