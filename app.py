import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from google import genai
from google.genai import types
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CraftAI - Enterprise", page_icon="📐", layout="wide")

st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; transition: all 0.3s ease; }
        [data-testid="stMetricValue"] { font-size: 2rem !important; color: #1E3A8A !important; }
        .login-box { padding: 2rem; border-radius: 10px; background-color: #f8fafc; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE LIVE GEMINI CLIENT ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

# ==========================================
# 🗄️ DATABASE & EMAIL MANAGEMENT
# ==========================================
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
    
    # Safely upgrade old database versions without crashing
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
    except:
        return pd.DataFrame([{"user_id": 1, "workshop_name": "Marius Custom Woodworking", "hourly_rate": 45.00}])

def send_verification_email(to_email, token):
    try:
        sender_email = st.secrets["EMAIL_ADDRESS"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        # Update this URL if you ever change your Streamlit app name!
        verify_link = f"https://craftaimarius.streamlit.app/?verify={token}"

        msg = MIMEMultipart()
        msg['From'] = f"CraftAI Support <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = "Action Required: Verify your CraftAI Account"
        
        body = f"""Welcome to the CraftAI Platform!
        
Please click the secure link below to verify your business details and activate your account:
{verify_link}

If you did not request this account, please ignore this email.

Thanks,
The CraftAI Team"""
        
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email failed to send. Check your Secrets setup! Error: {e}")
        return False

# ==========================================
# 🚦 URL ROUTING (CHECKING FOR CLICKED LINKS)
# ==========================================
# If someone clicks an email link, Streamlit sees the "?verify=TOKEN" in the web address
query_params = st.query_params
if "verify" in query_params:
    token = query_params["verify"]
    conn = sqlite3.connect("craftai.db")
    c = conn.cursor()
    c.execute("SELECT id FROM accounts WHERE verification_token=?", (token,))
    user = c.fetchone()
    
    if user:
        # Mark account as verified and clear the token so it can't be used again
        c.execute("UPDATE accounts SET is_verified=1, verification_token=NULL WHERE id=?", (user[0],))
        conn.commit()
        st.success("🎉 Email Verified Successfully! Your account is now active. Please log in below.")
    else:
        st.error("❌ Invalid or expired verification link.")
    conn.close()
    # Clear the URL so it doesn't keep trying to verify every time they refresh
    st.query_params.clear()

# --- GLOBAL VARIABLES & SESSION STATE ---
CURRENCY_MAP = {"British Pound (GBP)": "£", "Euro (EUR)": "€", "US Dollar (USD)": "$"}
for state_var in ['logged_in', 'takeoff_complete']:
    if state_var not in st.session_state: st.session_state[state_var] = False
for state_var in ['user_role', 'username', 'pending_verification_email']:
    if state_var not in st.session_state: st.session_state[state_var] = ''
for state_var in ['item_1_title', 'item_2_title']:
    if state_var not in st.session_state: st.session_state[state_var] = "Custom Joinery Unit"
for state_var in ['item_1_specs', 'item_2_specs']:
    if state_var not in st.session_state: st.session_state[state_var] = []

# ==========================================
# 🔒 LOGIN & REGISTRATION SCREEN
# ==========================================
def login_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title("📐 CraftAI Portal")
        
        tab_login, tab_register = st.tabs(["🔒 Secure Login", "📝 Register New Account"])
        
        # --- TAB 1: LOGIN ---
        with tab_login:
            st.markdown("Please enter your secure credentials.")
            login_email = st.text_input("Email Address", key="log_email")
            login_password = st.text_input("Password", type="password", key="log_pass")
            
            if st.button("Log In", type="primary"):
                if login_email == "marius" and login_password == "admin123":
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = "Manufacturer / Workshop Admin"
                    st.session_state['username'] = "Master Admin"
                    st.rerun()
                else:
                    conn = sqlite3.connect("craftai.db")
                    c = conn.cursor()
                    c.execute("SELECT id, role, is_verified FROM accounts WHERE email=? AND password=?", (login_email, hash_password(login_password)))
                    user = c.fetchone()
                    
                    if user:
                        # NEW CHECK: Stop them if they haven't clicked the email link!
                        if not user[2]:
                            st.error("🛑 Account Not Verified. Please check your email and click the validation link to activate your account.")
                        else:
                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = user[0]
                            st.session_state['user_role'] = "Customer" if user[1] == 'client' else "Manufacturer / Workshop Admin"
                            
                            if user[1] == 'client':
                                c.execute("SELECT name FROM clients WHERE user_id=?", (user[0],))
                                st.session_state['username'] = c.fetchone()[0]
                            else:
                                c.execute("SELECT company_name FROM manufacturers WHERE user_id=?", (user[0],))
                                st.session_state['username'] = c.fetchone()[0]
                            st.rerun()
                    else:
                        st.error("❌ Incorrect email or password.")
                    conn.close()

        # --- TAB 2: REGISTRATION ---
        with tab_register:
            if st.session_state['pending_verification_email']:
                st.success("✅ Account stored securely in the database!")
                st.info(f"To activate your account and verify your business details, please validate your email address: **{st.session_state['pending_verification_email']}**")
            else:
                reg_role = st.radio("I am registering as a:", ["Client", "Manufacturer"], horizontal=True)
                
                with st.form("registration_form"):
                    reg_email = st.text_input("Email Address*")
                    reg_pass = st.text_input("Password*", type="password")
                    
                    if reg_role == "Client":
                        reg_name = st.text_input("Full Name*")
                        reg_postcode = st.text_input("Postcode*")
                    else:
                        reg_company = st.text_input("Company Name*")
                        reg_address = st.text_input("Address")
                        reg_postcode = st.text_input("Postcode*")
                        reg_website = st.text_input("Website (Required for Verification)*")
                    
                    submit_reg = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if submit_reg:
                        if not reg_email or not reg_pass:
                            st.warning("⚠️ Email and Password are required!")
                        elif reg_role == "Client" and (not reg_name or not reg_postcode):
                            st.warning("⚠️ Name and Postcode are required!")
                        elif reg_role == "Manufacturer" and (not reg_company or not reg_postcode or not reg_website):
                            st.warning("⚠️ Company Name, Postcode, and a valid Website are mandatory!")
                        else:
                            try:
                                conn = sqlite3.connect("craftai.db")
                                c = conn.cursor()
                                role_db = 'client' if reg_role == "Client" else 'manufacturer'
                                
                                # Generate a random secret token for this user
                                secret_token = str(uuid.uuid4())
                                
                                c.execute("INSERT INTO accounts (email, password, role, is_verified, verification_token) VALUES (?, ?, ?, 0, ?)", 
                                          (reg_email, hash_password(reg_pass), role_db, secret_token))
                                new_user_id = c.lastrowid
                                
                                if role_db == 'client':
                                    c.execute("INSERT INTO clients (user_id, name, postcode) VALUES (?, ?, ?)",
                                              (new_user_id, reg_name, reg_postcode))
                                else:
                                    c.execute("INSERT INTO manufacturers (user_id, company_name, postcode, address, website) VALUES (?, ?, ?, ?, ?)",
                                              (new_user_id, reg_company, reg_postcode, reg_address, reg_website))
                                conn.commit()
                                
                                # ACTUALLY SEND THE REAL EMAIL
                                if send_verification_email(reg_email, secret_token):
                                    st.session_state['pending_verification_email'] = reg_email
                                    st.rerun()
                                    
                            except sqlite3.IntegrityError:
                                st.error("❌ An account with that email already exists.")
                            finally:
                                conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 💻 MAIN APPLICATION
# ==========================================
def main_app():
    st.sidebar.title(f"👋 Welcome, {st.session_state['username']}")
    st.sidebar.info(f"**Active Profile Role:**\n{st.session_state['user_role']}")
    
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = ''
        st.session_state['username'] = ''
        st.rerun()

    st.sidebar.markdown("---")
    selected_currency_name = st.sidebar.selectbox("Preferred Currency", list(CURRENCY_MAP.keys()), index=0)
    c_sym = CURRENCY_MAP[selected_currency_name]

    st.sidebar.markdown("---")
    users_df = get_registered_users()
    selected_shop = st.sidebar.selectbox("Active Workshop Rates", users_df["workshop_name"].tolist())
    active_user_rate = users_df[users_df["workshop_name"] == selected_shop].iloc[0]["hourly_rate"]
    st.sidebar.metric("Base Labor Rate", f"{c_sym}{active_user_rate:.2f}/hr")

    st.title("📐 CraftAI: Takeoff Platform")
    
    if not st.session_state['takeoff_complete']:
        st.info("Please upload your project blueprint, PDF set, or CAD file below.")

    uploaded_file = st.file_uploader("Upload design blueprint or CAD files...", type=["png", "jpg", "jpeg", "pdf", "svg"])

    if uploaded_file is not None:
        if st.button("🚀 Run Live AI Technical Takeoff", type="primary"):
            if st.session_state['user_role'] == "Customer":
                st.error("🔒 Only Workshop Admins can run new AI calculations.")
            else:
                with st.spinner("Uploading blueprint to vision nodes..."):
                    try:
                        image_bytes = uploaded_file.getvalue()
                        current_mime = "application/pdf" if uploaded_file.name.endswith('.pdf') else "image/jpeg"
                        
                        system_instruction = (
                            "You are an elite joinery estimator. Analyze this drawing. "
                            "Identify up to 2 items. Return strictly a JSON object matching this schema layout: "
                            "{'item_1_title': 'Item Title', 'item_1_specs': [{'Component': 'MDF Panels', 'qty': 10, 'cost': 25.0, 'cnc': 0.5, 'assem': 1.0, 'spray': 0.5, 'inst': 0.5}], 'item_2_title': '', 'item_2_specs': []}. "
                            "Do not wrapper your output string."
                        ).replace("'", '"')
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[types.Part.from_bytes(data=image_bytes, mime_type=current_mime), system_instruction],
                            config=types.GenerateContentConfig(response_mime_type="application/json")
                        )
                        
                        clean_text = response.text.strip().replace('```json', '').replace('```', '')
                        ai_data = json.loads(clean_text)
                        
                        st.session_state['item_1_title'] = ai_data.get('item_1_title', 'Custom Joinery Unit 1')
                        st.session_state['item_2_title'] = ai_data.get('item_2_title', '')
                        st.session_state['item_1_specs'] = ai_data.get('item_1_specs', [])
                        st.session_state['item_2_specs'] = ai_data.get('item_2_specs', [])
                        st.session_state['takeoff_complete'] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")

    if st.session_state['takeoff_complete']:
        st.markdown("---")
        
        raw_1 = sum([((float(c.get('qty',0)) * float(c.get('cost',0))) * 1.25 + (float(c.get('cnc',0)) + float(c.get('assem',0)) + float(c.get('spray',0)) + float(c.get('inst',0))) * float(c.get('qty',0)) * active_user_rate) * 1.15 for c in st.session_state['item_1_specs']])
        raw_2 = sum([((float(v.get('qty',0)) * float(v.get('cost',0))) * 1.25 + (float(v.get('cnc',0)) + float(v.get('assem',0)) + float(v.get('spray',0)) + float(v.get('inst',0))) * float(v.get('qty',0)) * active_user_rate) * 1.15 for v in st.session_state['item_2_specs']])

        scale_1, scale_2 = 1.0, 1.0

        if st.session_state['user_role'] == "Manufacturer / Workshop Admin":
            st.info("⚖️ **Commercial Calibration:** Adjust target price below.")
            col_cal_1, col_cal_2 = st.columns(2)
            with col_cal_1:
                if st.session_state['item_1_specs']:
                    t1 = st.number_input(f"🎯 Target Price 1 (Inc. VAT)", value=float(raw_1 * 1.20), step=100.0)
                    scale_1 = (t1 / 1.20) / raw_1 if raw_1 > 0 else 1.0
            with col_cal_2:
                if st.session_state['item_2_specs'] and st.session_state['item_2_title']:
                    t2 = st.number_input(f"🎯 Target Price 2 (Inc. VAT)", value=float(raw_2 * 1.20), step=100.0)
                    scale_2 = (t2 / 1.20) / raw_2 if raw_2 > 0 else 1.0
            st.markdown("---")

        item_1_total_ex_vat, item_2_total_ex_vat = 0.0, 0.0
        
        if st.session_state['item_1_specs']:
            st.write(f"## 🪵 1. {st.session_state['item_1_title']}")
            
            if st.session_state['user_role'] == "Manufacturer / Workshop Admin":
                df_1 = pd.DataFrame(st.session_state['item_1_specs'])
                edited_df_1 = st.data_editor(df_1, num_rows="dynamic", use_container_width=True, hide_index=True)
                st.session_state['item_1_specs'] = edited_df_1.to_dict('records')

            client_rows_1 = []
            for row in st.session_state['item_1_specs']:
                try:
                    qty, raw_cost = float(row.get('qty', 0)), float(row.get('cost', 0.0))
                    marked_up_mat = (qty * raw_cost) * 1.25
                    labor = (float(row.get('cnc',0)) + float(row.get('assem',0)) + float(row.get('spray',0)) + float(row.get('inst',0))) * qty * active_user_rate
                    item_1_total_ex_vat += ((marked_up_mat + labor) * 1.15) * scale_1
                    client_rows_1.append({"Component": row.get('Component'), "Qty": qty})
                except: pass

            if st.session_state['user_role'] == "Customer": st.table(pd.DataFrame(client_rows_1))

            c1, c2 = st.columns(2)
            with c1: st.metric("Price (Ex VAT)", f"{c_sym}{item_1_total_ex_vat:.2f}")
            with c2: st.metric("Price (Inc VAT)", f"{c_sym}{item_1_total_ex_vat * 1.20:.2f}")

        if st.session_state['item_2_specs'] and st.session_state['item_2_title']:
            st.markdown("---")
            st.write(f"## 🪵 2. {st.session_state['item_2_title']}")
            
            if st.session_state['user_role'] == "Manufacturer / Workshop Admin":
                df_2 = pd.DataFrame(st.session_state['item_2_specs'])
                edited_df_2 = st.data_editor(df_2, num_rows="dynamic", use_container_width=True, hide_index=True)
                st.session_state['item_2_specs'] = edited_df_2.to_dict('records')

            client_rows_2 = []
            for row in st.session_state['item_2_specs']:
                try:
                    qty, raw_cost = float(row.get('qty', 0)), float(row.get('cost', 0.0))
                    marked_up_mat = (qty * raw_cost) * 1.25
                    labor = (float(row.get('cnc',0)) + float(row.get('assem',0)) + float(row.get('spray',0)) + float(row.get('inst',0))) * qty * active_user_rate
                    item_2_total_ex_vat += ((marked_up_mat + labor) * 1.15) * scale_2
                    client_rows_2.append({"Component": row.get('Component'), "Qty": qty})
                except: pass

            if st.session_state['user_role'] == "Customer": st.table(pd.DataFrame(client_rows_2))

            c1, c2 = st.columns(2)
            with c1: st.metric("Price (Ex VAT)", f"{c_sym}{item_2_total_ex_vat:.2f}")
            with c2: st.metric("Price (Inc VAT)", f"{c_sym}{item_2_total_ex_vat * 1.20:.2f}")

        st.markdown("---")
        st.metric("PROJECT GRAND TOTAL (INC. VAT)", f"{c_sym}{(item_1_total_ex_vat + item_2_total_ex_vat) * 1.20:.2f}")

if st.session_state['logged_in']: main_app()
else: login_screen()
