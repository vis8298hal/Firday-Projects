import hmac
import os
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
st.set_page_config(page_title="Portal Dashboard", layout="wide")

# 1. Initialize session state safely
st.session_state.setdefault("is_admin", False)
st.session_state.setdefault("show_admin_login", False)


def render_sidebar(sidebar_info:dict):
    """Renders the sidebar with navigation/controls when called."""
    with st.sidebar:
        st.header(sidebar_info["Name"])
        st.divider()

        menu = st.radio(
            sidebar_info["radio_menu"]["name"],
            sidebar_info["radio_menu"]["elements"],
            key=sidebar_info["radio_menu"]["key"]
        )

        st.divider()
        st.caption(sidebar_info["Caption"])

    return menu
# 2. Admin Authentication Helper
def verify_admin(user_id: str, password: str) -> bool:
    expected_user = os.getenv("FRONT_USERNAME")
    expected_pass = os.getenv("FRONT_PASS") 
    # Replace with your actual password or st.secrets
    return (
        hmac.compare_digest(user_id.strip(), expected_user)
        and hmac.compare_digest(password, expected_pass)
    )


# 3. Dashboard Views
def render_admin_dashboard():
    st.title("Admin Dashboard")
    st.caption("Logged in as **developer** (Administrator)")
    st.divider()
    # Add your Admin widgets / chat / management controls here
    st.info("Welcome to the Admin control panel.")


def render_general_dashboard():
    st.title("General Dashboard")
    st.divider()
    sidebar_info = {
        "Name": "General Sidebar",
        "Caption": "streamlit - test",
        "radio_menu":{
            "name": "Yesterday's chats",
            "elements": ["Good", "Better", "Best"],
            "key": "sample_radio_menu"
        }
    }
    render_sidebar(sidebar_info)
    # Add your centered General User chat / widgets here
    _, center_col, _ = st.columns([1.5, 3, 1.5])
    with center_col:
        st.info("Welcome to the General User workspace.")


# 4. Top-Right Header Button (Near Deploy Button)
st.markdown(
    """
    <style>
    .st-key-top_right_btn {
        position: fixed;
        top: 0.65rem;
        right: 9.5rem;
        z-index: 999999;
        width: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Show "Admin User Login" on General Dashboard; show "Logout" on Admin Dashboard
if not st.session_state.get("is_admin"):
    if st.button("Admin User Login", key="top_right_btn"):
        st.session_state["show_admin_login"] = True
        st.rerun()
else:
    if st.button("Logout", key="top_right_btn"):
        st.session_state["is_admin"] = False
        st.session_state["show_admin_login"] = False
        st.rerun()


# 5. Main Routing
if st.session_state.get("show_admin_login"):
    _, form_col, _ = st.columns([2, 2, 2])
    with form_col:
        st.subheader("Admin Login")
        with st.form("admin_login_form"):
            admin_id = st.text_input("Admin User ID")
            admin_pw = st.text_input("Admin Password", type="password")
            if st.form_submit_button("Sign In as Admin", type="primary", use_container_width=True):
                if verify_admin(admin_id, admin_pw):
                    st.session_state["is_admin"] = True
                    st.session_state["show_admin_login"] = False
                    st.rerun()
                else:
                    st.error("Invalid Admin User ID or Password.")

        if st.button("← Back"):
            st.session_state["show_admin_login"] = False
            st.rerun()

elif st.session_state.get("is_admin"):
    render_admin_dashboard()

else:
    render_general_dashboard()