import streamlit as st
import sqlite3
import pandas as pd
import time

# --- 1. MINIMALIST GALLERY DESIGN SYSTEM (Atelier Allure Light Theme) ---
st.set_page_config(page_title="AI Joinery Estimator", layout="wide")

st.markdown("""
    <style>
    /* Premium Gallery Light Theme Configuration */
    .stApp {
        background-color: #FFFFFF;
        color: #1A1A1A;
    }
    h1, h2, h3, h4 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1A1A1A !important;
        font-weight: 300 !important;
        letter-spacing: 1.5px;
    }
    /* Minimalist Dark Frame Accents for Buttons */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1px solid #1A1A1A !important;
        border-radius: 0px !important;
        padding: 10px 24px !important;
        font-weight: 400 !important;
        letter-spacing: 1px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .stButton>button:hover {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #1A1A1A !important;
    }
    /* Architectural Fine Line Border Boxes */
    .card-frame {
        background-color: #FAFAFA;
        border: 1px solid #EAEAEA;
        padding: 28px;
        margin-bottom: 24px;
        border-radius: 0px;
    }
    .badge-status {
        background-color: #1A1A1A;
        color: #FFFFFF;
        padding: 5px 12px;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: bold;
    }
    /* Custom spacing fixes for light dashboard metrics */
    [data-testid="stMetricValue"] {
        color: #1A1A1A !important;
        font-weight: 300 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL SYSTEM VARIATION TRACKING ---
if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = False
if 'auth_email' not in st.session_state:
    st.session_state['auth_email'] = ""
if 'keep_logged_in' not in st.session_state:
    st.session_state['keep_logged_in'] = False
if 'estimate_broadcasted' not in st.session_state:
    st.session_state['estimate_broadcasted'] = False
if 'current_view_tab' not in st.session_state:
    st.session_state['current_view_tab'] = "📐 New Project Estimate"
if 'markup_
