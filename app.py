import streamlit as st
import sqlite3
import pandas as pd
import time

# --- 1. LUXURY BLACK & POLISHED BRASS DESIGN SYSTEM ---
st.set_page_config(page_title="AI Joinery Estimator", layout="wide")

# Separating styles into clean individual blocks to prevent any parsing overlap errors
st.markdown("<style>.stApp { background-color: #FFFFFF; color: #111111; }</style>", unsafe_allow_html=True)
st.markdown("<style>h1, h2, h3, h4, p, label { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; color: #111111 !important; font-weight: 300 !important; letter-spacing: 1px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.brand-header { font-size: 36px !important; font-weight: 200 !important; letter-spacing: 4px !important; text-transform: uppercase; color: #111111; margin-bottom: 30px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stButton>button { background-color: #111111 !important; color: #FFFFFF !important; border: 1px solid #111111 !important; border-radius: 0px !important; padding: 12px 24px !important; font-size: 13px !important; text-transform: uppercase !important; letter-spacing: 2px !important; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; width: 100%; }</style>", unsafe_allow_html=True)
st.markdown("<style>.stButton>button:hover { background-color: #FFFFFF !important; color: #C5A059 !important; border: 1px solid #C5A059 !important; box-shadow: 0px 4px 15px rgba(197, 160, 89, 0.15); }</style>", unsafe_allow_html=True)
st.markdown("<style>.card-frame { background-color: #FAFAFA; border-left: 3px solid #C5A059; border-top: 1px solid #EAEAEA; border-right: 1px solid #EAEAEA; border-bottom: 1px solid #EAEAEA; padding: 30px; margin-bottom: 25px; border-radius: 0px; }</style>", unsafe_allow_html=True)
st.markdown("<style>.badge-status { background-color: #111111; color: #C5A059; padding: 6px 14px; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 400; display: inline-block; margin-bottom: 10px; }</style>", unsafe_allow_html=True)
st.markdown("<style>[data-testid='stMetricValue'] { color: #C5A059 !important; font-weight: 200 !important; font-size: 40px !important; letter-spacing: -1px; }</style>", unsafe_allow_html=True)
st.markdown("<style>input, textarea { background-color: #FAFAFA !important; border: 1px solid #EAEAEA !important; border-radius: 0px !important; color: #111111 !important; }</style>", unsafe_allow_html=True)

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
if 'markup_annotations' not in st.session_state:
    st.session_state['markup_annotations'] = []

# --- 3. CUSTOMER GATEWAY (LOGIN / REGISTRATION) PANEL ---
if not st.session_state['auth_status']:
    st.markdown("<div style='text-align: center; margin-top: 100px; margin-bottom: 20px;'><h1 class='brand-header'>AI JOINERY ESTIMATOR PORTAL</h1></div>", unsafe_allow_html=True)
    
    auth_mode = st.radio("Access Mode", ["Sign In to Account", "Create Free Client Account"], horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_mid, col_right = st.columns([1, 1.6, 1])
    with col_mid:
        st.markdown("<div class='card-frame'>", unsafe_allow_html=True)
        if auth_mode == "Sign In to Account":
            st.subheader("Client Login")
            login_email = st.text_input("Email Address", placeholder="name@company.com")
            login_pass = st.text_input("Password", type="password", placeholder="••••••••")
            
            remember_me = st.checkbox("Keep me logged in", value=st.session_state['keep_logged_in'])
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Access Dashboard", use_container_width=True):
                if login_email != "" and login_pass != "":
                    st.session_state['auth_status'] = True
                    st.session_state['auth_email'] = login_email
                    st.session_state['keep_logged_in'] = remember_me
                    st.rerun()
                else:
                    st.error("Please provide valid entry parameters.")
        else:
            st.subheader("Register Free Account")
            st.caption("Gain access to immediate material takeoffs and match with up to 5 custom manufacturer quotes.")
            reg_name = st.text_input("Full Name / Company Name")
            reg_email = st.text_input("Email Address")
            reg_pass = st.text_input("Choose Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create Free Account", use_container_width=True):
                if reg_name != "" and reg_email != "" and reg_pass != "":
                    st.success("Account initialized successfully!")
                    st.session_state['auth_status'] = True
                    st.session_state['auth_email'] = reg_email
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please fill in all layout profile slots.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. PORTAL HEADER (Logged In State) ---
st.write(f'<div style="float: right; padding-top: 15px; color: #777777; font-size: 13px; letter-spacing: 1px;">PORTAL USER: <b>{st.session_state["auth_email"]}</b></div>', unsafe_allow_html=True)
st.markdown("<h1 style='font-size: 28px; letter-spacing: 3px; font-weight:200; margin-bottom:5px;'>ATELIER ALLURE STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #666666; font-size: 14px;'>Please describe your project, upload technical files, and review production metrics below.</p>", unsafe_allow_html=True)

# Minimalist logout option pinned to the sidebar panel
if st.sidebar.button("🔒 Secure Sign Out", use_container_width=True):
    st.session_state['auth_status'] = False
    st.session_state['auth_email'] = ""
    st.session_state['keep_logged_in'] = False
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. HIGH-ENGAGEMENT BRANDED NAVIGATION ---
nav_cols = st.columns(4)
with nav_cols[0]:
    if st.button("📐 New Project Estimate", use_container_width=True):
        st.session_state['current_view_tab'] = "📐 New Project Estimate"
with nav_cols[1]:
    if st.button("🗄️ Project History & Metrics", use_container_width=True):
        st.session_state['current_view_tab'] = "🗄️ Project History & Metrics"
with nav_cols[2]:
    if st.button("🏭 Manufacturer Profiles", use_container_width=True):
        st.session_state['current_view_tab'] = "🏭 Manufacturer Profiles"
with nav_cols[3]:
    if st.button("💬 Production Q&A Hub", use_container_width=True):
        st.session_state['current_view_tab'] = "💬 Production Q&A Hub"

st.markdown("<hr style='border: 0; height: 1px; background: #EAEAEA; margin-top:20px; margin-bottom:30px;'>", unsafe_allow_html=True)

# --- 6. APPLICATION VIEW WORKFLOW LOGIC ---
if st.session_state['current_view_tab'] == "📐 New Project Estimate":
    col_entry, col_preview = st.columns([3, 2])
    
    with col_entry:
        st.markdown("<h4 style='font-size:18px; font-weight:400; margin-bottom:15px;'>1. Project Design Parameters</h4>", unsafe_allow_html=True)
        user_spec = st.text_area(
            "Detail your bespoke spatial specification or material selections:",
            placeholder="E.g., Bespoke floating alcove units, solid walnut finish, 18mm backing panels, integrated soft-close drawers...",
            height=130
        )
        
        st.markdown("<br><h4 style='font-size:18px; font-weight:400; margin-bottom:15px;'>2. Blueprint & CAD Asset Uploader</h4>", unsafe_allow_html=True)
        uploaded_blueprints = st.file_uploader(
            "Supported technical extensions: JPEG, PNG, PDF, DXF, DWG, DAE, SKP",
            type=["jpeg", "png", "jpg", "pdf", "dxf", "dwg", "dae", "skp"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        st.markdown("<br><h4 style='font-size:18px; font-weight:400; margin-bottom:5px;'>3. Image Markup & Dimension Plotter</h4>", unsafe_allow_html=True)
        st.caption("Coordinate pinning system for geometric reference updates.")
        
        if uploaded_blueprints:
            st.info("🎨 Vector canvas mapping activated. Input millimeter constraints below:")
            col_x, col_y, col_dim = st.columns([1, 1, 2])
            with col_x:
                point_x = st.number_input("Axis X (mm)", min_value=0, max_value=10000, value=1200)
            with col_y:
                point_y = st.number_input("Axis Y (mm)", min_value=0, max_value=10000, value=2400)
            with col_dim:
                label_text = st.text_input("Dimension / Label Description", placeholder="E.g., Section Profile Depth")
            
            if st.button("📍 Append Dimension Node"):
                st.session_state['markup_annotations'].append(f"Bound Point ({point_x}x{point_y}) - {label_text}")
            
            if st.session_state['markup_annotations']:
                st.markdown("<br>**Plotted Layout Constraints:**", unsafe_allow_html=True)
                for annotation in st.session_state['markup_annotations']:
                    st.write(f"`{annotation}`")
        else:
            st.write("<p style='color:#888888; font-size:13px; font-style:italic;'>Awaiting architectural drawings to deploy canvas measurement overlays.</p>", unsafe_allow_html=True)

    with col_preview:
        st.markdown("<h4 style='font-size:18px; font-weight:400; margin-bottom:15px;'>📊 Dynamic Pricing Breakdown</h4>", unsafe_allow_html=True)
        if uploaded_blueprints or len(user_spec) > 15:
            st.metric(label="AI Cost Valuation Projection", value="£5,890.00")
            st.caption("Calculated via algorithmic structural panel volume metrics.")
            
            breakdown_data = pd.DataFrame({
                'Allocation Category': ['Timber Stock', 'Milling/CNC', 'Lacquer/Finish', 'Assembly'],
                'Cost Allocation (£)': [2200, 1150, 940, 1600]
            })
            st.bar_chart(data=breakdown_data, x='Allocation Category', y='Cost Allocation (£)')
            
            st.markdown("<br>", unsafe_allow_html=True)
            if not st.session_state['estimate_broadcasted']:
                if st.button("🚀 Push to Registered Manufacturers", use_container_width=True):
                    st.session_state['estimate_broadcasted'] = True
                    st.rerun()
            else:
                st.success("✅ Pushed successfully! Matching tenders will display inside your archive panel.")
        else:
            st.write("<div style='background-color:#FAFAFA; border:1px solid #EAEAEA; padding:20px; color:#777777; font-size:14px; text-align:center;'>Supply project parameters or architectural schematics to populate the live pricing ledger.</div>", unsafe_allow_html=True)

elif st.session_state['current_view_tab'] == "🗄️ Project History & Metrics":
    st.markdown("<h4 style='font-size:18px; font-weight:400; margin-bottom:20px;'>Your Historic Structural Portfolio</h4>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='card-frame'>
            <span class='badge-status'>3 / 5 Offers Pending</span>
            <h4 style='margin-top: 5px; font-size:18px; font-weight:400;'>📍 White Oak Living Room Media Wall</h4>
            <p style='color: #666666; font-size:13px; margin-bottom:15px;'>Submitted: June 20, 2026 | Reference: #AA-83921</p>
            <p style='font-size:15px;'>AI Baseline Target: <b>£7,200.00</b> | Active Best Market Offer: <b style='color:#C5A059;'>£6,950.00</b></p>
        </div>
        <div class='card-frame'>
            <span class='badge-status' style='background-color:#C5A059; color:#FFFFFF;'>Fabricated & Closed</span>
            <h4 style='margin-top: 5px; font-size:18px; font-weight:400;'>📍 Floating Corian Basin Storage Vanity</h4>
            <p style='color: #666666; font-size:13px; margin-bottom:15px;'>Closed: May 14, 2026 | Reference: #AA-72104</p>
            <p style='font-size:15px;'>Final Commission Bill: <b>£1,850.00</b></p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state['current_view_tab'] == "🏭 Manufacturer Profiles":
    st.markdown("<h4 style='font-size:18px; font-weight:400; margin-bottom:20px;'>Verified Architectural Networks</h4>", unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
            <div class='card-frame'>
                <h4 style='font-size:18px; font-weight:400;'>🏷️ Apex Precision Joinery Ltd</h4>
                <p style='font-size:14px; margin-bottom:8px;'><b>Workshop Bounds:</b> Greater London / Essex</p>
                <p style='font-size:14px; color:#555555; line-height:1.4;'><b>Plant Capacity:</b> Homag 5-Axis CNC Routers, High-Pressure Veneer Presses, Automated Edgebanders</p>
                <span style='color: #C5A059; font-size:13px; font-weight:400;'>★ 4.9 Platform Quality Score</span>
            </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown("""
            <div class='card-frame'>
                <h4 style='font-size:18px; font-weight:400;'>🏷️ Coastal Bespoke Millwork Hub</h4>
                <p style='font-size:14px; margin-bottom:8px;'><b>Workshop Bounds:</b> West Sussex Production</p>
                <p style='font-size:14px; color:#555555; line-height:1.4;'><b>Plant Capacity:</b> Traditional Joinery Tooling, Cleanroom Spray Finishing Chambers, Solid Core Laminators</p>
                <span style='color: #C5A059; font-size:13px; font-weight:400;'>★ 4.8 Platform Quality Score</span>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state['current_view_tab'] == "💬 Production Q&A Hub":
    st.markdown("<h4 style='font-size:18px; font-weight:400; margin-bottom:20px;'>Architectural Engineering Threads</h4>", unsafe_allow_html=True)
    st.write("<div style='background-color:#FAFAFA; border:1px solid #EAEAEA; padding:25px; color:#777777; font-size:14px;'>📬 Communication logs clear. No structural clarification items pending response matching this user profile.</div>", unsafe_allow_html=True)
