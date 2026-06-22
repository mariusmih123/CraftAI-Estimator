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
if 'markup_annotations' not in st.session_state:
    st.session_state['markup_annotations'] = []

# --- 3. CUSTOMER GATEWAY (LOGIN / REGISTRATION) PANEL ---
if not st.session_state['auth_status']:
    st.write("<div style='text-align: center; margin-top: 80px; margin-bottom: 40px;'><h1 style='font-size: 38px !important; font-weight: 200 !important; letter-spacing: 4px !important; color: #1A1A1A;'>AI JOINERY ESTIMATOR PORTAL</h1></div>", unsafe_allow_html=True)
    
    auth_mode = st.radio("Access Mode", ["Sign In to Account", "Create Free Client Account"], horizontal=True, label_visibility="collapsed")
    
    col_left, col_mid, col_right = st.columns([1, 1.8, 1])
    with col_mid:
        st.markdown("<div class='card-frame'>", unsafe_allow_html=True)
        if auth_mode == "Sign In to Account":
            st.subheader("Client Login")
            login_email = st.text_input("Email Address", placeholder="name@company.com")
            login_pass = st.text_input("Password", type="password", placeholder="••••••••")
            
            remember_me = st.checkbox("Keep me logged in", value=st.session_state['keep_logged_in'])
            st.write("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
            
            if st.button("Access Dashboard", use_container_width=True):
                if login_email != "" and login_pass != "":
                    st.session_state['auth_status'] = True
                    st.session_state['auth_email'] = login_email
                    st.session_state['keep_logged_in'] = remember_me
                    st.rerun()
                else:
                    st.error("Please provide valid entry account parameters.")
        else:
            st.subheader("Register Free Account")
            st.caption("Gain access to immediate material takeoffs and match with up to 5 custom manufacturer quotes.")
            reg_name = st.text_input("Full Name / Company Name")
            reg_email = st.text_input("Email Address")
            reg_pass = st.text_input("Choose Password", type="password")
            
            if st.button("Create Free Account", use_container_width=True):
                if reg_name != "" and reg_email != "" and reg_pass != "":
                    st.success("Account initialized successfully!")
                    st.session_state['auth_status'] = True
                    st.session_state['auth_email'] = reg_email
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please fill in all layout profile input slots.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. REFINED HOMEPAGE INTRODUCTION ONBOARDING (Logged In State) ---
st.write(f'<div style="float: right; padding-top: 10px; color: #666666; font-size: 14px;">Logged in as: <b>{st.session_state["auth_email"]}</b></div>', unsafe_allow_html=True)
st.write("### Welcome to AI Joinery Estimator")
st.markdown("<p style='color: #555555; font-size: 15px;'>Please describe your project, upload documents (JPEG, PNG, PDF, DXF, DWG, Collada CAD files), and get an instant estimate for your joinery project.</p>", unsafe_allow_html=True)

# Minimalist log-out shortcut positioned on left side
if st.sidebar.button("🔒 Secure Sign Out", use_container_width=True):
    st.session_state['auth_status'] = False
    st.session_state['auth_email'] = ""
    st.session_state['keep_logged_in'] = False
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. NAVIGATION TAB CONTROL RENDERER ---
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

st.markdown("---")

# --- 6. APPLICATION VIEW WORKFLOW LOGIC ---
if st.session_state['current_view_tab'] == "📐 New Project Estimate":
    col_entry, col_preview = st.columns([3, 2])
    
    with col_entry:
        st.subheader("1. Structural Project Description")
        user_spec = st.text_area(
            "Detail your spatial configuration or material preferences:",
            placeholder="E.g., Bespoke floating alcove units, solid walnut finish, 18mm backing panels, integrated soft-close drawers..."
        )
        
        st.subheader("2. Structural Drawing & CAD Data Uploader")
        uploaded_blueprints = st.file_uploader(
            "Supported formats: JPEG, PNG, PDF, DXF, DWG, DAE (Collada), SKP",
            type=["jpeg", "png", "jpg", "pdf", "dxf", "dwg", "dae", "skp"],
            accept_multiple_files=True
        )
        
        st.subheader("3. Visual Picture Markup & Dimension Plotter")
        st.caption("Upload reference images to unlock the spatial boundary calculation matrix tool below.")
        
        if uploaded_blueprints:
            st.info("🎨 Image Markup Workspace Active. Pinpoint lines or cross-sections below:")
            col_x, col_y, col_dim = st.columns([1, 1, 2])
            with col_x:
                point_x = st.number_input("Axis X (mm)", min_value=0, max_value=10000, value=1200)
            with col_y:
                point_y = st.number_input("Axis Y (mm)", min_value=0, max_value=10000, value=2400)
            with col_dim:
                label_text = st.text_input("Dimension / Label Description", placeholder="E.g., Crown Molding Max Height")
            
            if st.button("📍 Append Dimension Node"):
                st.session_state['markup_annotations'].append(f"Bound Point ({point_x}x{point_y}) - {label_text}")
            
            if st.session_state['markup_annotations']:
                st.markdown("**Plotted Structural Restrictions:**")
                for annotation in st.session_state['markup_annotations']:
                    st.write(f"`{annotation}`")
        else:
            st.write("_Awaiting technical graphics or imagery files to initiate canvas vector overlays._")

    with col_preview:
        st.subheader("📊 Instant AI Cost Estimation")
        if uploaded_blueprints or len(user_spec) > 15:
            st.metric(label="Calculated Automated Cost Projection", value="£5,890.00")
            
            breakdown_data = pd.DataFrame({
                'Allocation Category': ['Raw Timber Stock', 'CNC Machine Milling', 'Polishing/Lacquer', 'Labor/Assembly'],
                'Cost Allocation (£)': [2200, 1150, 940, 1600]
            })
            st.bar_chart(data=breakdown_data, x='Allocation Category', y='Cost Allocation (£)')
            
            st.markdown("---")
            if not st.session_state['estimate_broadcasted']:
                st.warning("⚠️ This calculation is currently a private workflow draft.")
                if st.button("🚀 Push Estimate to Registered Manufacturers", use_container_width=True):
                    st.session_state['estimate_broadcasted'] = True
                    st.rerun()
            else:
                st.success("✅ Broadcast Complete! Project data pushed to our database pipeline. Up to 5 matched workshop offers will display in your history vault.")
        else:
            st.write("Populate project descriptions or drop design files to generate a live interactive bill of materials (BOM).")

elif st.session_state['current_view_tab'] == "🗄️ Project History & Metrics":
    st.subheader("Your Historic Structural Portfolio")
    
    st.markdown("""
        <div class='card-frame'>
            <span class='badge-status' style='background-color: #222222;'>3 / 5 Offers Received</span>
            <h4 style='margin-top: 15px;'>📍 White Oak Living Room Media Wall</h4>
            <p style='color: #666666;'>Submitted: June 20, 2026 | Project Code: #AA-83921</p>
            <p>AI Baseline Projection: <b>£7,200.00</b> | Active Market Low Bid: <b style='color: #1A1A1A;'>£6,950.00</b></p>
        </div>
        <div class='card-frame'>
            <span class='badge-status' style='background-color: #777777;'>Fabricated & Closed</span>
            <h4 style='margin-top: 15px;'>📍 Floating Corian Basin Storage Vanity</h4>
            <p style='color: #666666;'>Closed: May 14, 2026 | Project Code: #AA-72104</p>
            <p>Final Production Bill: <b>£1,850.00</b></p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state['current_view_tab'] == "🏭 Manufacturer Profiles":
    st.subheader("Verified Fabrication Networks")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
            <div class='card-frame'>
                <h4>🏷️ Apex Precision Joinery Ltd</h4>
                <p><b>Location Bounds:</b> Greater London / Essex</p>
                <p><b>Plant Machinery:</b> Homag 5-Axis CNC Routers, High-Pressure Veneer Presses, Automated Edgebanders</p>
                <span style='color: #222222;'>★ 4.9 Platform Trust Score</span>
            </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown("""
            <div class='card-frame'>
                <h4>🏷️ Coastal Bespoke Millwork Hub</h4>
                <p><b>Location Bounds:</b> West Sussex Workshops</p>
                <p><b>Plant Machinery:</b> Traditional Joinery Tooling, Cleanroom Spray Finishing Chambers, Solid Core Laminators</p>
                <span style='color: #222222;'>★ 4.8 Platform Trust Score</span>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state['current_view_tab'] == "💬 Production Q&A Hub":
    st.subheader("Architectural Engineering Thread")
    st.info("📬 Your current architectural assets are clear. There are no pending material queries matching your active profile.")
