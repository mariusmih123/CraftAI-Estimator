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
        transition: all 0.2s ease;
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
    </style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL SYSTEM VARIATION TRACKING ---
if 'estimate_broadcasted' not in st.session_state:
    st.session_state['estimate_broadcasted'] = False
if 'current_view_tab' not in st.session_state:
    st.session_state['current_view_tab'] = "📐 New Project Estimate"
if 'markup_annotations' not in st.session_state:
    st.session_state['markup_annotations'] = []

# --- 3. REFINED HOMEPAGE INTRODUCTION ONBOARDING ---
st.write("# ATELIER ALLURE")
st.write("### Welcome to AI Joinery Estimator")
st.markdown("<p style='color: #B3B3B3; font-size: 16px;'>Please describe your project, upload documents (JPEG, PNG, PDF, DXF, DWG, Collada CAD files), and get an instant estimate for your joinery project.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 4. NAVIGATION TAB CONTROL RENDERER ---
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

# --- 5. APPLICATION VIEW WORKFLOW LOGIC ---

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
        
        # Interactive Image Annotation & Markup Simulator Workspace
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
            
            # Simulated visual estimate breakdown graph
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
            <span class='badge-status' style='background-color: #E29578; color: #FFFFFF;'>3 / 5 Workshop Offers Received</span>
            <h4 style='margin-top: 10px;'>📍 White Oak Living Room Media Wall</h4>
            <p style='color: #A3A3A3;'>Submitted: June 20, 2026 | Project Code: #AA-83921</p>
            <p>AI Baseline Projection: <b>£7,200.00</b> | Active Market Low Bid: <b style='color: #00FF00;'>£6,950.00</b></p>
        </div>
        <div class='card-frame'>
            <span class='badge-status'>Completed & Fabricated</span>
            <h4 style='margin-top: 10px;'>📍 Floating Corian Basin Storage Vanity</h4>
            <p style='color: #A3A3A3;'>Closed: May 14, 2026 | Project Code: #AA-72104</p>
            <p>Final Production Bill: <b>£1,850.00</b></p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state['current_view_tab'] == "🏭 Manufacturer Profiles":
    st.subheader("Verified Fabrication Networks")
    st.write("Review the operational capacities and machine specifications of factories bidding on your architectural files.")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
            <div class='card-frame'>
                <h4>🏷️ Apex Precision Joinery Ltd</h4>
                <p><b>Location Bounds:</b> Greater London / Essex</p>
                <p><b>Plant Machinery:</b> Homag 5-Axis CNC Routers, High-Pressure Veneer Presses, Automated Edgebanders</p>
                <span style='color: #FFD700;'>★ 4.9 Platform Trust Score</span>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Apex Portfolios & Certifications", key="btn_m1"):
            st.info("Displaying verified factory inspection passes: ISO 9001 Quality Framework certified, FSC Timber Chain of Custody active.")
            
    with col_m2:
        st.markdown("""
            <div class='card-frame'>
                <h4>🏷️ Coastal Bespoke Millwork Hub</h4>
                <p><b>Location Bounds:</b> West Sussex Workshops</p>
                <p><b>Plant Machinery:</b> Traditional Joinery Tooling, Cleanroom Spray Finishing Chambers, Solid Core Laminators</p>
                <span style='color: #FFD700;'>★ 4.8 Platform Trust Score</span>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Coastal Portfolios & Certifications", key="btn_m2"):
            st.info("Displaying verified factory inspection passes: Fine Guild of Master Craftsmen registered assembly floor.")

elif st.session_state['current_view_tab'] == "💬 Production Q&A Hub":
    st.subheader("Architectural Engineering Thread")
    st.write("Direct clarification log regarding dimensions, tolerances, and hardware requirements with fabrication estimating departments.")
    
    st.info("📬 Your current architectural assets are clear. There are no pending material queries matching your active profile.")
