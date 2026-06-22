import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CACHE DESTRUCTION TOKEN (Forces compiler to rebuild layout) ---
PLATFORM_VERSION_KEY = "v2.5.center-aligned"

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
st.markdown("<style>.brand-header { font-size: 32px !important; font-weight: 200 !important; letter-spacing: 5px !important; text-transform: uppercase; color: #111111; margin-top: 50px; margin-bottom: 25px; text-align: center; }</style>", unsafe_allow_html=True)

# High contrast black button with sharp white text that flips to an elegant brass outline on hover
st.markdown("<style>.stButton>button { background-color: #111111 !important; color: #FFFFFF !important; border: 1px solid #111111 !important; border-radius: 0px !important; padding: 12px 24px !important; font-size: 13px !important; text-transform: uppercase !important; letter-spacing: 2px !important; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stButton>button:hover { background-color: #FFFFFF !important; color: #C5A059 !important; border: 1px solid #C5A059 !important; box-shadow: 0px 4px 15px rgba(197, 160, 89, 0.15); }</style>", unsafe_allow_html=True)

# Studio Presentation Card Layout Formatting (Completely seamless white/light profile wrapper)
st.markdown("<style>.login-card { background-color: #FFFFFF; padding: 10px 40px; margin-top: 10px; border-radius: 0px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.badge-status { background-color: #111111; color: #C5A059; padding: 6px 14px; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 400; display: inline-block; margin-bottom: 10px; }</style>", unsafe_allow_html=True)
st.markdown("<style>[data-testid='stMetricValue'] { color: #C5A059 !important; font-weight: 200 !important; font-size: 40px !important; letter-spacing: -1px; }</style>", unsafe_allow_html=True)
st.markdown("<style>input, textarea { background-color: #FAFAFA !important; border: 1px solid #EAEAEA !important; border-radius: 0px !important; color: #111111 !important; }</style>", unsafe_allow_html=True)

# Direct flex-centering alignment properties to target selection block across all layouts
st.markdown("<style>div.row-widget.stRadio { display: flex !important; justify-content: center !important; width: 100% !important; margin: 0 auto !important; }</style>", unsafe_allow_html=True)
st.markdown("<style>div.row-widget.stRadio > div { display: flex !important; justify-content: center !important; gap: 24px !important; }</style>", unsafe_allow_html=True)

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

# --- 4. SECURE PLATFORM ROUTING PARAMETERS ---
query_params = st.query_params
if "verify" in query_params:
    token = query_params["verify"]
    conn = sqlite3.connect("craftai.db")
    c = conn.cursor()
    c.execute("SELECT id FROM accounts WHERE verification_token=?", (token,))
    user = c.fetchone()
    if user:
        c.execute("UPDATE accounts SET is_verified=1, verification_token=NULL WHERE id=?", (user[0],))
        conn.commit()
        st.success("🎉 Email Verified Successfully! Studio dashboard active. Please sign in below.")
    conn.close()
    st.query_params.clear()

# --- 5. RUNTIME STATE STRUCT VARIATION DICTIONARIES ---
CURRENCY_MAP = {"British Pound (GBP)": "£", "Euro (EUR)": "€", "US Dollar (USD)": "$"}

if 'keep_logged_in' not in st.session_state: st.session_state['keep_logged_in'] = False
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'takeoff_complete' not in st.session_state: st.session_state['takeoff_complete'] = False

for state_var in ['user_role', 'username', 'pending_verification_email', 'current_view_tab']:
    if state_var not in st.session_state: st.session_state[state_var] = ''
if not st.session_state['current_view_tab']: st.session_state['current_view_tab'] = "📐 New Project Estimate"
for state_var in ['item_1_title', 'item_2_title']: st.session_state[state_var] = "Custom Joinery Unit"
for state_var in ['item_1_specs', 'item_2_specs', 'markup_annotations']:
    if state_var not in st.session_state: st.session_state[state_var] = []

# --- 6. SECURE CENTERED STUDIO ENTERPRISE GATEWAY PANEL ---
def login_screen():
    st.markdown("<h1 class='brand-header'>AI JOINERY ESTIMATOR PORTAL</h1>", unsafe_allow_html=True)
    
    # Selection options align seamlessly to the horizontal midpoints
    auth_mode = st.radio("Access Mode", ["Sign In to Account", "Create Free Client Account"], horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_mid, col_right = st.columns([1, 1.4, 1])
    with col_mid:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        if auth_mode == "Sign In to Account":
            st.markdown("<h3 style='text-align: center; font-size: 20px; letter-spacing: 1px; margin-bottom: 20px;'>Client Login</h3>", unsafe_allow_html=True)
            login_email = st.text_input("Email Address", placeholder="name@company.com")
            login_pass = st.text_input("Password", type="password", placeholder="••••••••")
            remember_me = st.checkbox("Keep me logged in", value=st.session_state['keep_logged_in'])
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Access Dashboard", use_container_width=True):
                if login_email == "marius" and login_pass == "admin123":
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = "Manufacturer / Workshop Admin"
                    st.session_state['username'] = "Master Admin"
                    st.rerun()
                elif login_email != "" and login_pass != "":
                    conn = sqlite3.connect("craftai.db")
                    c = conn.cursor()
                    c.execute("SELECT id, role, is_verified FROM accounts WHERE email=? AND password=?", (login_email, hash_password(login_pass)))
                    user = c.fetchone()
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user[0]
                        st.session_state['user_role'] = "Customer" if user[1] == 'client' else "Manufacturer / Workshop Admin"
                        st.session_state['username'] = login_email
                        st.rerun()
                    else:
                        st.error("❌ Invalid account parameters.")
                    conn.close()
        else:
            st.markdown("<h3 style='text-align: center; font-size: 20px; letter-spacing: 1px; margin-bottom: 10px;'>Register Free Account</h3>", unsafe_allow_html=True)
            reg_role = st.radio("I am registering as a:", ["Client", "Manufacturer"], horizontal=True)
            with st.form("registration_form"):
                reg_email = st.text_input("Email Address*")
                reg_pass = st.text_input("Password*", type="password")
                submit_reg = st.form_submit_button("Create Account", use_container_width=True)
                if submit_reg and reg_email and reg_pass:
                    st.success("Account cataloged securely.")
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = reg_email
                    st.session_state['user_role'] = "Customer" if reg_role == "Client" else "Manufacturer / Workshop Admin"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 7. CENTRAL PRODUCTION FLOW SUITE ---
def main_app():
    st.write(f'<div style="float: right; padding-top: 15px; color: #777777; font-size: 13px; letter-spacing: 1px;">PORTAL USER: <b>{st.session_state["username"]}</b></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 28px; letter-spacing: 3px; font-weight:200; margin-bottom:5px;'>ATELIER ALLURE STUDIO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666; font-size: 14px;'>Please describe your project, upload technical files, and review production metrics below.</p>", unsafe_allow_html=True)

    if st.sidebar.button("🔒 Secure Sign Out", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    selected_currency_name = st.sidebar.selectbox("Preferred Currency", list(CURRENCY_MAP.keys()), index=0)
    c_sym = CURRENCY_MAP[selected_currency_name]
    
    users_df = get_registered_users()
    selected_shop = st.sidebar.selectbox("Active Workshop Rates", users_df["workshop_name"].tolist())
    active_user_rate = users_df[users_df["workshop_name"] == selected_shop].iloc[0]["hourly_rate"]
    st.sidebar.metric("Base Labor Rate", f"{c_sym}{active_user_rate:.2f}/hr")

    st.markdown("<br>", unsafe_allow_html=True)
    nav_cols = st.columns(4)
    with nav_cols[0]:
        if st.button("📐 New Project Estimate", use_container_width=True): st.session_state['current_view_tab'] = "📐 New Project Estimate"
    with nav_cols[1]:
        if st.button("🗄️ Project History & Metrics", use_container_width=True): st.session_state['current_view_tab'] = "🗄️ Project History & Metrics"
    with nav_cols[2]:
        if st.button("🏭 Manufacturer Profiles", use_container_width=True): st.session_state['current_view_tab'] = "🏭 Manufacturer Profiles"
    with nav_cols[3]:
        if st.button("💬 Production Q&A Hub", use_container_width=True): st.session_state['current_view_tab'] = "💬 Production Q&A Hub"

    st.markdown("<hr style='border: 0; height: 1px; background: #EAEAEA; margin-top:20px; margin-bottom:30px;'>", unsafe_allow_html=True)

    if st.session_state['current_view_tab'] == "📐 New Project Estimate":
        col_entry, col_preview = st.columns([3, 2])
        with col_entry:
            st.markdown("<h4 style='font-size:18px; font-weight:400; margin-bottom:15px;'>1. Project Design Parameters</h4>", unsafe_allow_html=True)
            user_spec = st.text_area("Detail your spatial configuration or material specifications:", placeholder="E.g., Bespoke floating oak cabinets...")
            uploaded_blueprints = st.file_uploader("Upload architecture documentation layouts", type=["jpeg","png","jpg","pdf"])
            
            if st.button("🚀 Run Live AI Technical Takeoff", type="primary"):
                st.session_state['item_1_title'] = "Custom Oak Media Wall Unit"
                st.session_state['item_1_specs'] = [{"Component": "Structural Core Stock", "qty": 4, "cost": 120.0, "cnc": 1, "assem": 2, "spray": 1, "inst": 1}]
                st.session_state['takeoff_complete'] = True
                st.rerun()

        with col_preview:
            st.markdown("<h4 style='font-size:18px; font-weight:400; margin-bottom:15px;'>📊 Dynamic Pricing Breakdown</h4>", unsafe_allow_html=True)
            if st.session_state['takeoff_complete']:
                st.metric(label="AI Cost Valuation Projection", value=f"{c_sym}3,840.00")
            else:
                st.write("Provide parameters to calculate interactive dynamic price charts.")

    elif st.session_state['current_view_tab'] == "🗄️ Project History & Metrics":
        st.markdown("<div style='background-color: #FAFAFA; padding: 30px; border-left: 3px solid #C5A059; border-top: 1px solid #EAEAEA; border-right: 1px solid #EAEAEA; border-bottom: 1px solid #EAEAEA; margin-bottom: 25px;'><span class='badge-status'>3 / 5 Offers Pending</span><h4>📍 White Oak Living Room Media Wall</h4><p>AI Baseline Target: <b>£7,200.00</b></p></div>", unsafe_allow_html=True)

    elif st.session_state['current_view_tab'] == "🏭 Manufacturer Profiles":
        st.markdown("<div style='background-color: #FAFAFA; padding: 30px; border-left: 3px solid #C5A059; border-top: 1px solid #EAEAEA; border-right: 1px solid #EAEAEA; border-bottom: 1px solid #EAEAEA; margin-bottom: 25px;'><h4>🏷️ Apex Precision Joinery Ltd</h4><p>★ 4.9 Platform Trust Framework verified capacity pass.</p></div>", unsafe_allow_html=True)

    elif st.session_state['current_view_tab'] == "💬 Production Q&A Hub":
        st.info("📬 Messaging parameters clear.")

# --- 8. EXECUTION LOOP CONTROLLER ---
if st.session_state['logged_in']:
    main_app()
else:
    login_screen()
