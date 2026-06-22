import streamlit as st
import sqlite3
import pandas as pd
import time

# --- 1. EMBEDDABLE LUXURY WEB STYLING (Atelier Allure Profile) ---
st.set_page_config(page_title="AI Joinery Estimator", layout="wide")

st.markdown("""
    <style>
    /* Clean Minimalist Web Environment */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    h1, h2, h3, h4 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #FFFFFF !important;
        font-weight: 200 !important;
        letter-spacing: 1px;
    }
    .stButton>button {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFFFFF !important;
        color: #121212 !important;
        border: 1px solid #FFFFFF !important;
    }
    .card-frame {
        background-color: #1A1A1A;
        border: 1px solid #262626;
        padding: 24px;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .badge-status {
        background-color: #2D6A4F;
        color: #D8F3DC;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: bold;
        border-radius: 12px;
    }
    /* Centered Login Box Wrapper */
    .login-container {
        max-width: 450px;
        margin: 60px auto;
        padding: 40px;
        background-color: #1A1A1A;
        border: 1px solid #262626;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL SYSTEM VARIATION TRACKING ---
if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = False
if 'auth_email' not in st.session_state:
    st.session_state['auth_email'] = ""
if 'estimate_broadcasted' not in st.session_state:
    st.session_state['estimate_broadcasted'] = False
if 'current_view_tab' not in st.session_state:
    st.session_state['current_view_tab'] = "📐 New Project Estimate"
if 'markup_annotations' not in st.session_state:
    st.session_state['markup_annotations'] = []

# --- 3. CUSTOMER GATEWAY (LOGIN / REGISTRATION) PANEL ---
if not st.session_state['auth_status']:
    st.write("<div style='text-align: center; margin-top: 60px; margin-bottom: 30px;'><h1 style='font-size: 42px !important; font-weight: 300 !important; letter-spacing: 3px !important;'>AI JOINERY ESTIMATOR PORTAL</h1></div>", unsafe_allow_html=True)
    
    auth_mode = st.radio("Access Mode", ["Sign In to Account", "Create Free Client Account"], horizontal=True, label_visibility="collapsed")
    
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("<div class='card-frame'>", unsafe_allow_html=True)
        if auth_mode == "Sign In to Account":
            st.subheader("Client Login")
            login_email = st.text_input("Email Address", placeholder="name@company.com")
            login_pass = st.text_input("Password", type="password", placeholder="••••••••")
            
            if st.button("Access Dashboard", use_container_
