import streamlit as st
import sqlite3
import pandas as pd

# --- 1. PREMIUM BRAND STYLING (Atelier Allure Theme) ---
st.set_page_config(page_title="AI Joinery Quote", layout="wide")

st.markdown("""
    <style>
    /* Premium Luxury Dark Mode Styling */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    h1, h2, h3, h4 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #FFFFFF !important;
        font-weight: 300 !important;
        letter-spacing: 1px;
    }
    .stButton>button {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFFFFF !important;
        color: #121212 !important;
        border: 1px solid #FFFFFF !important;
    }
    /* Sidebar styling adjustment */
    section[data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
        border-right: 1px solid #262626;
    }
    </style>
""", unsafe_html=True)

# --- 2. CRITICAL DATABASE & VARIABLE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect("joinery_quote.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            role TEXT,
            workshop_rate REAL DEFAULT 0.0,
            installation_rate REAL DEFAULT 0.0,
            delivery_rate REAL DEFAULT 0.0,
            spray_rate REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Universal baseline variable initialization to prevent NameErrors
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = "Client"

item_2_rows = []
item_1_total_ex_vat = 0.0
item_2_total_ex_vat = 0.0
st.session_state['item_2_title'] = st.session_state.get('item_2_title', "")

# --- 3. AUTHENTICATION SIDEBAR PANEL ---
st.sidebar.title("ATELIER ALLURE")
st.sidebar.subheader("AI Joinery Quote Portal")

if not st.session_state['logged_in']:
    username = st.sidebar.text_input("Email / Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "contact@atelierallure.co.uk" and password == "Brighton23!":
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = "Manufacturer"  # Admin defaults to Manufacturer View
            st.rerun()
        elif username != "" and password != "":
            # Free client instant simulation login
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = "Client"
            st.rerun()
    st.stop()

# Logout Handler
if st.sidebar.button("Log Out"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- 4. DUAL ROUTING DASHBOARD WORKFLOWS ---
if st.session_state['user_role'] == "Client":
    st.title("📐 AI Joinery Quote — Client Dashboard")
    st.write("Submit drawings and 3D architectural models for automated AI estimation.")
    
    # Step 1: Upload Panel
    st.subheader("📸 Step 1: Upload Architectural Drawings / 3D Models")
    uploaded_files = st.file_uploader(
        "Upload project files...", 
        type=["pdf", "png", "jpeg", "jpg", "dxf", "dwg", "dae", "skp"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.info("⚡ System simulation ready to process specifications.")

else:
    st.title("🏭 AI Joinery Quote — Manufacturer Workbench")
    st.write("Configure your internal operational rates and view active market listings.")
    
    # Live Parametric Estimation Control Panel
    st.subheader("⚙️ Workshop Operational Parameters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        workshop_rate = st.slider("Workshop Hourly Rate (£)", 0, 150, 45)
    with col2:
        installation_rate = st.slider("Installation Rate (£)", 0, 150, 50)
    with col3:
        delivery_rate = st.slider("Delivery Flat Fee (£)", 0, 500, 120)
    with col4:
        spray_rate = st.slider("Spray / Finishing Rate (£)", 0, 200, 65)

    st.metric(label="Calculated Base Rate Dynamic Output", value=f"£{workshop_rate + installation_rate:.2f}/hr")
