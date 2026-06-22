import streamlit as st
import sqlite3
import pandas as pd
import time

# --- 1. LUXURY BLACK & POLISHED BRASS DESIGN SYSTEM ---
st.set_page_config(page_title="AI Joinery Estimator", layout="wide")

st.markdown("""
    <style>
    /* Global Brand Environment */
    .stApp {
        background-color: #FFFFFF;
        color: #111111;
    }
    
    /* Clean Minimalist Typography */
    h1, h2, h3, h4, p, label {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: #111111 !important;
        font-weight: 300 !important;
        letter-spacing: 1px;
    }
    
    /* Luxury Header Typography */
    .brand-header {
        font-size: 36px !important;
        font-weight: 200 !important;
        letter-spacing: 4px !important;
        text-transform: uppercase;
        color: #111111;
        margin-bottom: 30px;
    }

    /* CUSTOM NAVIGATION BUTTONS (Polished Brass Accent Loop) */
    .stButton>button {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #111111 !important;
        border-radius: 0px !important;
        padding: 12px 24px !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        width: 100%;
    }
    
    /* Elegant Hover: Transforms to Polished Brass Outline */
    .stButton>button:hover {
        background-color: #FFFFFF !important;
        color: #C5A059 !important; /* Polished Brass */
        border: 1px solid #C5A059 !important;
        box-shadow: 0px 4px 15px rgba(197, 160, 89, 0.15);
    }

    /* Architectural Studio Presentation Cards */
    .card-frame {
        background-color: #FAFAFA;
        border-left: 3px solid #C5A059; /* Solid Polished Brass Accent Bar */
        border-top: 1px solid #EAEAEA;
        border-right: 1px solid #EAEAEA;
        border-bottom: 1px solid #EAEAEA;
        padding: 30px;
        margin-bottom: 25px;
        border-radius: 0px;
    }

    /* Premium Status Labels */
    .badge-status {
        background-color: #111111;
        color: #C5A059; /* Brass text on deep black badge */
        padding: 6px 14px;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 400;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Polished Brass Custom Metric Overrides */
    [data-testid="stMetricValue"] {
        color: #C5A059 !important; /* Forces the numerical price to render in pure gold/brass */
        font-weight: 200 !important;
        font-size: 40px !important;
        letter-spacing: -
