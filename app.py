import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Safely isolate the SDK library to prevent deployment environment blockades
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# --- 1. BRAND DESIGN SYSTEM SETUP (Minimalist Light Black & Brass Profile) ---
st.set_page_config(page_title="CraftAI - Enterprise", page_icon="📐", layout="wide")

st.markdown("<style>.stApp { background-color: #FFFFFF; color: #111111; }</style>", unsafe_allow_html=True)
st.markdown("<style>h1, h2, h3, h4, p, label { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; color: #111111 !important; font-weight: 300 !important; letter-spacing: 1px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.brand-header { font-size: 32px !important; font-weight: 200 !important; letter-spacing: 5px !important; text-transform: uppercase; color: #111111; margin-bottom: 5px; text-align: center; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stButton>button { background-color: #111111 !important; color: #FFFFFF !important; border: 1px solid #111111 !important; border-radius: 0px !important; padding: 12px 24px !important; font-size: 13px !important; text-transform: uppercase !important; letter-spacing: 2px !important; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stButton>button:hover { background-color: #FFFFFF !important; color: #C5A059 !important; border: 1px solid #C5A059 !important; box-shadow: 0px 4px 15px rgba(197, 160, 89, 0.15); }</style>", unsafe_allow_html=True)
st.markdown("<style>.login-card { background-color: #FAFAFA; padding: 40px; border: 1px solid #EAEAEA; margin-top: 10px; border-radius: 0px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.badge-status { background-color: #111111; color: #C5A059; padding: 6px 14px; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 400; display: inline-block; margin-bottom: 10px; }</style>", unsafe_allow_html=True)
st.markdown("<style>[data-testid='stMetricValue'] { color: #C5A059 !important; font-weight: 200 !important; font-size: 40px !important; letter-spacing: -1px; }</style>", unsafe_allow_html=True)
st.markdown("<style>input, textarea { background-color: #FAFAFA !important; border: 1px solid #EAEAEA !important; border-radius: 0px !important; color: #111111 !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>div.row-widget.stRadio > div{justify-content: center;}</style>", unsafe_allow_html=True)

# --- 2. INITIALIZE INTUITIVE GENERATIVE CLIENT NODES ---
client = None
if HAS_GENAI:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        pass

# --- 3. DATABASE ENGINE CAPACITIES ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_db():
    conn = sqlite3.connect("craftai.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, role TEXT,
        is_verified BOOLEAN DEFAULT 0, verification_token TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        user_id INTEGER, name TEXT, postcode TEXT, FOREIGN KEY(user_id) REFERENCES accounts(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS manufacturers (
        user_id INTEGER, company_name TEXT, postcode TEXT, address TEXT, website TEXT, hourly_rate REAL DEFAULT 45.0,
        FOREIGN KEY(user_id) REFERENCES accounts(id))''')
    try: c.execute("ALTER TABLE accounts ADD COLUMN verification_token TEXT")
    except: pass
    try: c.execute("ALTER TABLE accounts ADD COLUMN is_verified BOOLEAN DEFAULT 0")
    except: pass
    conn.commit()
    conn.close()

init_db()

def get_registered_users():
    try:
        conn = sqlite3.connect("craftai.db")
        df_users = pd.read_sql_query("SELECT user_id, company_name as workshop_name, hourly_rate FROM manufacturers", conn)
        conn.close()
        if df_users.empty: return pd.DataFrame([{"user_id": 1, "workshop_name": "Marius Custom Woodworking", "hourly_rate": 45.00}])
        return df_users
    except Exception:
        return pd.DataFrame([{"user_id": 1, "workshop_name": "Marius Custom Woodworking", "hourly_rate": 45.00}])

def send_verification_email(to_email, token):
    try:
        sender_email = st.secrets["EMAIL_ADDRESS"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        verify_link = f"https://craft
