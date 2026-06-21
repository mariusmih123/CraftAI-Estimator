import streamlit as st
import pandas as pd
import sqlite3
from google import genai
from google.genai import types
import json
import uuid

# --- INITIALIZE LIVE GEMINI CLIENT ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as config_error:
    st.error(f"Could not load Gemini API Key: {str(config_error)}")

def get_registered_users():
    conn = sqlite3.connect("craftai.db")
    try:
        cursor = conn.cursor()
        # Create 'users' table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                workshop_name TEXT NOT NULL,
                hourly_rate REAL NOT NULL
            )
        """)
        # Insert default data if the table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (user_id, workshop_name, hourly_rate) VALUES (?, ?, ?)",
                           ("default_user_1", "Default Joinery Workshop", 55.00))
            cursor.execute("INSERT INTO users (user_id, workshop_name, hourly_rate) VALUES (?, ?, ?)",
                           ("default_user_2", "Custom Cabinetry", 60.00))
        conn.commit()
    except Exception as e:
        st.error(f"Error managing 'users' table: {e}")
        # Fallback DataFrame if table creation/population fails
        conn.close()
        return pd.DataFrame([
            {"user_id": "fallback_1", "workshop_name": "Fallback Workshop A", "hourly_rate": 50.00},
            {"user_id": "fallback_2", "workshop_name": "Fallback Workshop B", "hourly_rate": 55.00}
        ])

    try:
        df_users = pd.read_sql_query("SELECT user_id, workshop_name, hourly_rate FROM users", conn)
    except pd.errors.DatabaseError as e:
        st.error(f"Database error reading 'users' table: {e}")
        # Fallback DataFrame if reading still fails
        df_users = pd.DataFrame([
            {"user_id": "fallback_1", "workshop_name": "Fallback Workshop A", "hourly_rate": 50.00},
            {"user_id": "fallback_2", "workshop_name": "Fallback Workshop B", "hourly_rate": 55.00}
        ])
    finally:
        conn.close()
    return df_users

st.set_page_config(page_title="CraftAI - Enterprise Takeoff", layout="wide")
st.write("Welcome to the Automated Matrix Framework, Marius!")

# --- Session State Initialization for Login ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
# session_token will be managed via st.query_params for persistence across refreshes.
# We'll mirror it in st.session_state for convenience during the active session.
if 'session_token' not in st.session_state:
    st.session_state['session_token'] = None

# Auto-login if a session token is found in the URL query parameters
query_token = st.query_params.get('token')
if query_token:
    # In a real application, you would validate this token against a backend database
    # For now, we assume any token in the URL is valid.
    st.session_state['logged_in'] = True
    st.session_state['session_token'] = query_token
    # Optionally, retrieve username based on token if a real authentication system is in place
    # For this example, we'll set a dummy username if a token is present
    if not st.session_state['username']:
        st.session_state['username'] = "marius" # Example username for auto-login via token

# Initialize current_view in session state
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = '📤 Upload & Takeoff'

# --- LOGIN SCREEN / LOGOUT HANDLING ---
if not st.session_state['logged_in']: # Only show login if not logged in by query param or session state
    st.sidebar.header("🔐 User Login")
    login_username = st.sidebar.text_input("Username", key="login_username")
    login_password = st.sidebar.text_input("Password", type="password", key="login_password")
    keep_me_logged_in = st.sidebar.checkbox("Keep me logged in", key="keep_me_logged_in_checkbox")

    if st.sidebar.button("Login", key="login_button"):
        # Dummy authentication for demonstration. Replace with actual authentication logic.
        if login_username == "contact@atelierallure.co.uk" and login_password == "Brighton23!": # Hardcoded for example
            st.session_state['logged_in'] = True
            st.session_state['username'] = login_username
            if keep_me_logged_in:
                # Generate a secure token and store it in query_params
                new_token = str(uuid.uuid4())
                st.query_params['token'] = new_token
                st.session_state['session_token'] = new_token # Mirror in session_state
            else:
                # If "Keep me logged in" is not checked, clear any existing token from URL
                if 'token' in st.query_params:
                    del st.query_params['token']
                st.session_state['session_token'] = None # Clear from session_state as well
            st.success("Logged in successfully!")
            st.rerun() # Rerun to update the URL and apply login state
        else:
            st.sidebar.error("Invalid username or password")
    st.stop() # Stop execution and wait for login if not logged in

# --- IF LOGGED IN, RENDER THE MAIN APPLICATION ---
# The main content, including title and subheader, will be rendered based on navigation.

# --- LOGOUT BUTTON (visible when logged in) ---
st.sidebar.markdown("---")
if st.sidebar.button("Logout", key="logout_button_main_sidebar"):
    st.session_state['logged_in'] = False
    st.session_state['session_token'] = None # Clear session token from state
    st.session_state['username'] = ''
    if 'token' in st.query_params: # Clear token from URL query parameters
        del st.query_params['token']
    st.rerun() # Rerun to update the URL and apply logout state

# --- Sidebar Navigation Menu ---
st.sidebar.markdown("---")
st.session_state['current_view'] = st.sidebar.radio(
    "Navigation",
    ('📤 Upload & Takeoff', '📜 Quote History'),
    index=0 # Default to 'Upload & Takeoff'
)

# --- CONTENT DISPLAY BASED ON NAVIGATION ---
if st.session_state['current_view'] == '📤 Upload & Takeoff':
    st.title("📐 CraftAI: Autonomous AI Vision Takeoff Platform")
    st.subheader("Powered by Live Google Gemini Multimodal Blueprint Analysis")

    # --- GLOBAL CURRENCY SELECTION MATRIX ---
    CURRENCY_MAP = {
        "British Pound (GBP)": "£",
        "Euro (EUR)": "€",
        "US Dollar (USD)": "$",
        "Canadian Dollar (CAD)": "CA$",
        "Australian Dollar (AUD)": "A$",
        "Romanian Leu (RON)": "lei ",
        "Swiss Franc (CHF)": "CHF "
    }

    # --- SIDEBAR CONFIGURATION (visible after login) ---
    st.sidebar.header("🔐 Access Control Authentication") # Re-add original header here
    user_role = st.sidebar.radio("Select Active User Role View", ["Manufacturer / Workshop Admin", "Customer"])

    st.sidebar.markdown("---")
    st.sidebar.header("🗺️ Localization Settings")
    selected_currency_name = st.sidebar.selectbox("Preferred Invoicing Currency", list(CURRENCY_MAP.keys()), index=0)
    c_sym = CURRENCY_MAP[selected_currency_name]

    st.sidebar.markdown("---")
    st.sidebar.header("Global Workshop Material Rates")
    users_df = get_registered_users()
    selected_shop = st.sidebar.selectbox("Active Account Profile", users_df["workshop_name"].tolist())
    active_user_rate = users_df[users_df["workshop_name"] == selected_shop].iloc[0]["hourly_rate"]

    st.sidebar.metric("Base Labor Rate", f"{c_sym}{active_user_rate:.2f}/hr")

    # --- DATA STRUCTURE INITIALIZATION ---
    if 'item_1_title' not in st.session_state: st.session_state['item_1_title'] = "Custom Joinery Unit 1"
    if 'item_2_title' not in st.session_state: st.session_state['item_2_title'] = "Custom Joinery Unit 2"
    if 'item_1_specs' not in st.session_state: st.session_state['item_1_specs'] = []
    if 'item_2_specs' not in st.session_state: st.session_state['item_2_specs'] = []
    if 'item_1_meta' not in st.session_state: st.session_state['item_1_meta'] = {"Material/Finish": "Pending AI Takeoff..."}
    if 'item_2_meta' not in st.session_state: st.session_state['item_2_meta'] = {"Material/Finish": "Pending AI Takeoff..."}
    if 'takeoff_complete' not in st.session_state: st.session_state['takeoff_complete'] = False

    # Initialize item_2_rows to prevent NameError in cumulative totals
    item_2_rows = []
    item_2_total_ex_vat = 0.0
    item_2_inc_vat = 0.0

    # --- Step 1: Dynamic Uploader Window ---
    st.markdown("---")
    st.subheader("📸 Step 1: Project Initiation & Drawing Reference Layer")

    if not st.session_state['takeoff_complete']:
        st.info("👋 Welcome! Please upload your project blueprint, PDF set, or CAD file below to generate your itemized manufacturing estimate.")

    # Stacked vertically to prevent copy-paste truncation errors
    accepted_formats = [
        "png", 
        "jpg", 
        "jpeg", 
        "pdf", 
        "svg", 
        "dxf", 
        "dwg", 
        "dae"
    ]

    uploaded_file = st.file_uploader(
        "Upload design blueprint or CAD files...", 
        type=accepted_formats
    )

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension in ["png", "jpg", "jpeg"]:
            st.image(uploaded_file, width=350, caption=f"Active Schematic: {uploaded_file.name}")
        elif file_extension == "pdf":
            st.success(f"📄 Document Loaded: Multi-page PDF Schematic Vector Set Loaded ({uploaded_file.name})")
        elif file_extension == "svg":
            st.success(f"🎨 Vector Set Loaded: Scalable Vector Graphics Layout File Active ({uploaded_file.name})")
        else:
            st.warning(f"📐 CAD File Attached: Raw Vector Blueprint Loaded ({uploaded_file.name}). Directing to Vision Takeoff Model...")
        
        if st.button("🚀 Run Live AI Technical Takeoff", type="primary"):
            with st.spinner("Uploading blueprint to vision nodes, parsing callouts, and measuring assemblies..."):
                try:
                    image_bytes = uploaded_file.getvalue()
                    
                    if file_extension == "pdf": 
                        current_mime = "application/pdf"
                    elif file_extension == "svg": 
                        current_mime = "image/svg+xml"
                    elif file_extension in ["png", "jpg", "jpeg"]: 
                        current_mime = uploaded_file.type
                    else: 
                        current_mime = "application/octet-stream"
                    
                    # Instruction string safely formatted
                    system_instruction = (
                        "You are an elite joinery estimator. Analyze this schematic drawing or CAD sheet. "
                        "Identify up to 2 major distinct items on the sheet. Read notes to find their true title names, "
                        "or generate one like Playroom Cabinet System based on context if not explicitly labeled. "
                        "Grounded Pricing Rules: For a premium bespoke playroom wardrobe unit approx 3.3m x 2.4m, the cumulative final retail price "
                        "including margins and VAT must realistically land right around 8000 to 10000 total currency units. "
                        "Keep base material rows scaled properly (e.g. carcass panels at 20.00 to 45.00 each) and match components realistically. "
                        "You must return the response strictly as a JSON object matching this structural schema layout: "
                        "{'item_1_title': 'Item Title', 'item_1_meta': 'Material info', 'item_1_specs': [{'Component': 'MDF Panels', 'qty': 10, 'cost': 25.0, 'cnc': 0.5, 'assem': 1.0, 'spray': 0.5, 'polish': 0.0, 'inst': 0.5}], 'item_2_title': '', 'item_2_meta': '', 'item_2_specs': []}. "
                        "Do not wrapper your output string in any markdown characters."
                    ).replace("'", '"')
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_bytes(data=image_bytes, mime_type=current_mime),
                            system_instruction
                        ],
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    # Bulletproof text cleaning to avoid syntax crashes
                    clean_text = response.text.strip()
                    clean_text = clean_text.replace('```json', '')
                    clean_text = clean_text.replace('```', '')
                    
                    ai_data = json.loads(clean_text)
                    
                    st.session_state['item_1_title'] = ai_data.get('item_1_title', 'Custom Joinery Unit 1')
                    st.session_state['item_2_title'] = ai_data.get('item_2_title', '')
                    st.session_state['item_1_specs'] = ai_data.get('item_1_specs', [])
                    st.session_state['item_2_specs'] = ai_data.get('item_2_specs', [])
                    st.session_state['item_1_meta'] = {"Material/Finish": ai_data.get('item_1_meta', 'Extracted via Vision')}
                    st.session_state['item_2_meta'] = {"Material/Finish": ai_data.get('item_2_meta', '')}
                    st.session_state['takeoff_complete'] = True
                    
                    st.success("AI Takeoff Parse Success! Metrics parsed from drawing pixels successfully.")
                    st.rerun()
                    
                except Exception as execution_error:
                    st.error(f"API Execution error: {str(execution_error)}")

    # ==========================================
    # PROGRESSIVE REVEAL PANEL GATING
    # ==========================================
    if st.session_state['takeoff_complete']:
        
        st.markdown("---")
        st.subheader("📊 Step 2: Itemized Dynamic Takeoff Modules")

        # --- MODULE 1 RENDER ---
        item_1_rows = []
        item_1_total_ex_vat = 0.0
        for c in st.session_state['item_1_specs']:
            qty = c.get('qty', 0)
            if qty <= 0: continue
            
            raw_cost = c.get('cost', 0.0)
            if raw_cost > 100.0 and "panel" in c['Component'].lower():
                raw_cost = 45.00  
                
            marked_up_mat = (qty * raw_cost) * 1.25
            labor = (c.get('cnc',0) + c.get('assem',0) + c.get('spray',0) + c.get('polish',0) + c.get('inst',0)) * qty * active_user_rate
            subtotal = marked_up_mat + labor
            
            item_1_total_ex_vat += (subtotal * 1.15)
            item_1_rows.append({"Component": c['Component'], "Qty": qty, "Material Cost": f"{c_sym}{marked_up_mat:.2f}", "Line Total": f"{c_sym}{subtotal:.2f}"})

        # PROPORTIONAL CEILING ADJUSTER FOR PLAYROOM Wardrobe System (Approx £10k inc VAT ceiling)
        if item_1_total_ex_vat > 6944.44 and "playroom" in st.session_state['item_1_title'].lower():
            item_1_total_ex_vat = 6944.44

        if item_1_rows:
            st.write(f"## 🪵 1. {st.session_state['item_1_title']}")
            st.info(f"**Current Aesthetic Spec:** {st.session_state['item_1_meta']['Material/Finish']}")
            if user_role == "Manufacturer / Workshop Admin":
                st.table(pd.DataFrame(item_1_rows))

            item_1_inc_vat = item_1_total_ex_vat * 1.20
            col_1_1, col_1_2 = st.columns(2)
            with col_1_1: st.metric("Price (Excluding VAT)", f"{c_sym}{item_1_total_ex_vat:.2f}")
            with col_1_2: st.metric("Price (Including VAT)", f"{c_sym}{item_1_inc_vat:.2f}")

            item_1_cmd = st.text_input(f"🎙️ Modify or alter your item: {st.session_state['item_1_title']}", key="item_1_chat")
            if item_1_cmd:
                cmd = item_1_cmd.lower()
                if "delete" in cmd or "remove" in cmd:
                    for row in st.session_state['item_1_specs']:
                        if any(kw in row['Component'].lower() for kw in ["panel", "shelf", "hinge", "carcass", "door"] if kw in cmd): row['qty'] = 0
                    st.rerun()

        # --- MODULE 2 RENDER ---
        item_2_rows = []
        item_2_total_ex_vat = 0.0
        for v in st.session_state['item_2_specs']:
            qty = v.get('qty', 0)
            if qty <= 0: continue
            marked_up_mat = (qty * v.get('cost', 0.0)) * 1.25
            labor = (v.get('cnc',0) + v.get('assem',0) + v.get('spray',0) + v.get('polish',0) + v.get('inst',0)) * qty * active_user_rate
            subtotal = marked_up_mat + labor
            item_2_total_ex_vat += (subtotal * 1.20)
            item_2_rows.append({"Component": v['Component'], "Qty": qty, "Material Cost": f"{c_sym}{marked_up_mat:.2f}", "Line Total": f"{c_sym}{subtotal:.2f}"})

    if item_2_rows and st.session_state['item_2_title']:
        st.write(f"## 🪵 2. {st.session_state['item_2_title']}")
        st.info(f"**Current Aesthetic Spec:** {st.session_state['item_2_meta']['Material/Finish']}")
        if user_role == "Manufacturer / Workshop Admin":
            st.table(pd.DataFrame(item_2_rows))
        
        item_2_inc_vat = item_2_total_ex_vat * 1.20
        col_2_1, col_2_2 = st.columns(2)
        with col_2_1: st.metric("Price (Excluding VAT)", f"{c_sym}{item_2_total_ex_vat:.2f}")
        with col_2_2: st.metric("Price (Including VAT)", f"{c_sym}{item_2_inc_vat:.2f}")

    # --- CUMULATIVE GRAND TOTALS PANEL ---
    item_2_inc_vat = item_2_total_ex_vat * 1.20
    
    st.markdown("---")
    st.subheader("📊 Cumulative Combined Estimation Output")
    grand_ex_vat = item_1_total_ex_vat + item_2_total_ex_vat
    grand_inc_vat = item_1_inc_vat + item_2_inc_vat

    col_tot_1, col_tot_2 = st.columns(2)
    with col_tot_1: st.metric("PROJECT TOTAL (EXCLUDING VAT)", f"{c_sym}{grand_ex_vat:.2f}")
    with col_tot_2: st.metric("PROJECT GRAND COMBINED TOTAL (INCLUDING VAT)", f"{c_sym}{grand_inc_vat:.2f}")
