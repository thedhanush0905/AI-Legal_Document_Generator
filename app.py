"""
Streamlit Web Application for Legal Document Generation & Evaluation Agent.
Clean Theme Architecture: Single source of truth via Streamlit native theme engine.
"""

import json
import os
import sys
from dotenv import load_dotenv
import streamlit as st

# Ensure project root is on sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.pipeline import run_pipeline, PipelineResult

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AffidavitAI — Legal Document Generation & QA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Clean Theme Architecture (Single Source of Truth: Streamlit Native Engine)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* =========================================================================
       1. THEME VARIABLES SYSTEM
       ========================================================================= */

    /* Default Dark Theme Variables */
    :root {
        --app-bg: #090e1a;
        --surface: #0f172a;
        --surface-alt: #162032;
        --card-bg: #0d1424;
        --card-header-bg: #111a2e;
        --border-subtle: #1e293b;
        --border-highlight: #334155;
        
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        
        --gold-primary: #d4af37;
        --gold-light: #f59e0b;
        --gold-subtle: rgba(212, 175, 55, 0.12);
        
        --green-success: #10b981;
        --green-subtle: rgba(16, 185, 129, 0.12);
        
        --red-danger: #ef4444;
        --red-subtle: rgba(239, 68, 68, 0.12);

        --btn-primary-bg: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        --btn-primary-text: #f8fafc;
        --btn-primary-border: #d4af37;

        --badge-loaded-bg: rgba(16, 185, 129, 0.12);
        --badge-loaded-text: #10b981;
        --badge-loaded-border: rgba(16, 185, 129, 0.25);
        
        --code-bg: #141c2e;
        --code-border: #23304a;
        --viewer-bg: #1b2333;

        /* Layer 2: Fixed Legal Document Paper Variables (Always White Paper + Dark Text) */
        --document-bg: #ffffff;
        --document-text: #111827;
    }

    /* Light Theme Variables (System Preference) */
    @media (prefers-color-scheme: light) {
        :root {
            --app-bg: #f4f6f9;
            --surface: #ffffff;
            --surface-alt: #f0f3f8;
            --card-bg: #ffffff;
            --card-header-bg: #f8fafc;
            --border-subtle: #dbe0ea;
            --border-highlight: #cbd5e1;
            
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            
            --gold-primary: #b48a1d;
            --gold-light: #d97706;
            --gold-subtle: rgba(180, 138, 29, 0.1);
            
            --green-success: #059669;
            --green-subtle: rgba(5, 150, 105, 0.1);
            
            --red-danger: #dc2626;
            --red-subtle: rgba(220, 38, 38, 0.1);
            
            --btn-primary-bg: linear-gradient(180deg, #d4af37 0%, #b48a1d 100%);
            --btn-primary-text: #ffffff;
            --btn-primary-border: #946f14;

            --badge-loaded-bg: rgba(5, 150, 105, 0.1);
            --badge-loaded-text: #059669;
            --badge-loaded-border: rgba(5, 150, 105, 0.25);

            --code-bg: #f1f5f9;
            --code-border: #cbd5e1;
            --viewer-bg: #e2e8f0;
        }
    }

    /* Streamlit Native Theme Switcher Overrides (Light Mode) */
    [data-theme="light"],
    [data-theme="Light"],
    [data-testid="stAppViewContainer"][data-theme="light"],
    [data-testid="stAppViewContainer"][data-theme="Light"],
    .stApp[data-theme="light"],
    html[data-theme="light"] body,
    body[data-theme="light"] {
        --app-bg: #f4f6f9 !important;
        --surface: #ffffff !important;
        --surface-alt: #f0f3f8 !important;
        --card-bg: #ffffff !important;
        --card-header-bg: #f8fafc !important;
        --border-subtle: #dbe0ea !important;
        --border-highlight: #cbd5e1 !important;
        
        --text-primary: #0f172a !important;
        --text-secondary: #334155 !important;
        --text-muted: #64748b !important;
        
        --gold-primary: #b48a1d !important;
        --gold-light: #d97706 !important;
        --gold-subtle: rgba(180, 138, 29, 0.1) !important;
        
        --green-success: #059669 !important;
        --green-subtle: rgba(5, 150, 105, 0.1) !important;
        
        --red-danger: #dc2626 !important;
        --red-subtle: rgba(220, 38, 38, 0.1) !important;
        
        --btn-primary-bg: linear-gradient(180deg, #d4af37 0%, #b48a1d 100%) !important;
        --btn-primary-text: #ffffff !important;
        --btn-primary-border: #946f14 !important;

        --badge-loaded-bg: rgba(5, 150, 105, 0.1) !important;
        --badge-loaded-text: #059669 !important;
        --badge-loaded-border: rgba(5, 150, 105, 0.25) !important;

        --code-bg: #f1f5f9 !important;
        --code-border: #cbd5e1 !important;
        --viewer-bg: #e2e8f0 !important;
    }

    /* Streamlit Native Theme Switcher Overrides (Dark Mode) */
    [data-theme="dark"],
    [data-theme="Dark"],
    [data-testid="stAppViewContainer"][data-theme="dark"],
    [data-testid="stAppViewContainer"][data-theme="Dark"],
    .stApp[data-theme="dark"],
    html[data-theme="dark"] body,
    body[data-theme="dark"] {
        --app-bg: #090e1a !important;
        --surface: #0f172a !important;
        --surface-alt: #162032 !important;
        --card-bg: #0d1424 !important;
        --card-header-bg: #111a2e !important;
        --border-subtle: #1e293b !important;
        --border-highlight: #334155 !important;
        
        --text-primary: #f8fafc !important;
        --text-secondary: #cbd5e1 !important;
        --text-muted: #94a3b8 !important;
        
        --gold-primary: #d4af37 !important;
        --gold-light: #f59e0b !important;
        --gold-subtle: rgba(212, 175, 55, 0.12) !important;
        
        --green-success: #10b981 !important;
        --green-subtle: rgba(16, 185, 129, 0.12) !important;
        
        --red-danger: #ef4444 !important;
        --red-subtle: rgba(239, 68, 68, 0.12) !important;

        --btn-primary-bg: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        --btn-primary-text: #f8fafc !important;
        --btn-primary-border: #d4af37 !important;

        --badge-loaded-bg: rgba(16, 185, 129, 0.12) !important;
        --badge-loaded-text: #10b981 !important;
        --badge-loaded-border: rgba(16, 185, 129, 0.25) !important;

        --code-bg: #141c2e !important;
        --code-border: #23304a !important;
        --viewer-bg: #1b2333 !important;
    }

    /* =========================================================================
       2. GLOBAL STREAMLIT CORE LAYOUT & NATIVE HEADER FIX
       ========================================================================= */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }

    .stApp {
        background-color: var(--app-bg) !important;
        color: var(--text-primary) !important;
    }

    /* Fix Streamlit Top Toolbar/Header - Transparent so it blends into app bg without white strip */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1250px !important;
    }

    /* =========================================================================
       3. APPLICATION COMPONENT SURFACES (LAYER 1)
       ========================================================================= */

    /* Hero Section */
    .hero-container {
        background: var(--surface);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    }
    .hero-brand {
        display: flex;
        flex-direction: column;
    }
    .hero-title {
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .hero-title span.accent {
        color: var(--gold-primary);
        font-weight: 400;
    }
    .hero-subtitle {
        font-size: 0.88rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-top: 0.2rem;
    }
    .hero-desc {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
        max-width: 650px;
        line-height: 1.4;
    }
    .hero-meta-group {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.4rem;
    }
    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-status-ready {
        background: var(--green-subtle);
        color: var(--green-success);
        border: 1px solid var(--green-success);
    }
    .badge-status-config {
        background: var(--red-subtle);
        color: var(--red-danger);
        border: 1px solid var(--red-danger);
    }
    .meta-model-info {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--text-secondary);
        background: var(--code-bg);
        border: 1px solid var(--code-border);
        padding: 0.25rem 0.55rem;
        border-radius: 5px;
    }

    /* Section Cards */
    .compact-card {
        background: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .card-header-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.5rem;
    }
    .card-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--gold-primary);
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .card-subtitle {
        font-size: 0.78rem;
        color: var(--text-muted);
    }

    /* Document Input Card Components */
    .doc-input-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 1.1rem 1.2rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        transition: border-color 0.2s ease;
        box-sizing: border-box;
    }
    .doc-input-card:hover {
        border-color: var(--border-highlight);
    }
    .doc-input-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .doc-input-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .doc-input-desc {
        font-size: 0.78rem;
        color: var(--text-muted);
        line-height: 1.45;
        margin-bottom: 0.85rem;
    }
    .doc-loaded-box {
        background-color: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 0.6rem 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-primary);
        font-weight: 500;
        margin-top: auto;
    }

    /* File Uploader Custom Styling */
    div[data-testid="stFileUploader"] {
        width: 100%;
        margin-top: auto;
    }
    div[data-testid="stFileUploader"] section {
        background-color: var(--surface-alt) !important;
        border: 1.5px dashed var(--border-highlight) !important;
        border-radius: 6px !important;
        padding: 0.6rem 0.75rem !important;
    }
    div[data-testid="stFileUploader"] section:hover {
        border-color: var(--gold-primary) !important;
    }
    div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
    }
    div[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"] {
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }
    /* File Uploader Footer / Helper Text High Contrast Fix */
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"],
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] *,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] small,
    div[data-testid="stFileUploader"] section small {
        color: var(--text-muted) !important;
        font-size: 12px !important;
        font-weight: 400 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* Toggle Control Styling */
    div[data-testid="stToggle"] label p {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Input Grid & Status Badges */
    .input-badge-loaded {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--badge-loaded-text);
        background: var(--badge-loaded-bg);
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        border: 1px solid var(--badge-loaded-border);
    }

    /* Sidebar Navigation */
    .sidebar-section-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }
    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    .sidebar-subtitle {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-bottom: 1.25rem;
    }
    .sidebar-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0;
        font-size: 0.8rem;
        color: var(--text-muted);
        border-bottom: 1px solid var(--border-subtle);
    }
    .sidebar-step.completed {
        color: var(--text-primary);
    }
    .sidebar-step-icon-done {
        color: var(--green-success);
        font-weight: 700;
        font-size: 0.8rem;
    }
    .sidebar-step-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--gold-primary);
        font-weight: 600;
    }

    /* Primary CTA Button */
    div.stButton > button[kind="primary"] {
        background: var(--btn-primary-bg) !important;
        color: var(--btn-primary-text) !important;
        border: 1.5px solid var(--btn-primary-border) !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.04em !important;
        padding: 0.65rem 2rem !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: var(--gold-primary) !important;
        color: #090e1a !important;
        border-color: var(--gold-primary) !important;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.4) !important;
        transform: translateY(-1px);
    }

    /* Pipeline Checklist */
    .checklist-container {
        background: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 0.85rem 1.2rem;
        margin: 0.75rem 0 1rem 0;
    }
    .checklist-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.4rem 1rem;
    }
    .checklist-item {
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.45rem;
        color: var(--text-muted);
    }
    .checklist-item.completed {
        color: var(--text-primary);
    }
    .checklist-item.active {
        color: var(--gold-primary);
        font-weight: 600;
    }
    .checklist-icon-done {
        color: var(--green-success);
        font-weight: 700;
    }
    .checklist-icon-active {
        color: var(--gold-primary);
    }
    .checklist-icon-pending {
        color: var(--text-muted);
    }

    /* Quality Hero & Metrics Row */
    .quality-hero-container {
        background: var(--surface);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .quality-hero-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .quality-hero-score {
        font-size: 2.8rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 0.35rem;
    }
    .quality-hero-badge-pass {
        display: inline-block;
        background: var(--green-subtle);
        color: var(--green-success);
        border: 1px solid var(--green-success);
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.2rem 0.75rem;
        border-radius: 9999px;
        letter-spacing: 0.04em;
    }
    .quality-hero-badge-review {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: var(--gold-light);
        border: 1px solid rgba(245, 158, 11, 0.3);
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.2rem 0.75rem;
        border-radius: 9999px;
        letter-spacing: 0.04em;
    }
    .quality-hero-subtag {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.3rem;
    }

    /* Sub-metrics cards */
    .metric-compact-card {
        background: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 0.75rem 1rem;
        text-align: center;
    }
    .metric-compact-val {
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
    }
    .metric-compact-lbl {
        font-size: 0.72rem;
        color: var(--text-muted);
        font-weight: 500;
        margin-top: 0.2rem;
    }

    /* Dimension Cards */
    .dimension-card {
        background: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 0.65rem 0.5rem;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    .dimension-card:hover {
        border-color: var(--border-highlight);
    }
    .dimension-name {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.25rem;
    }
    .dimension-score {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
    }
    .dimension-pct {
        font-size: 0.7rem;
        color: var(--gold-primary);
        font-weight: 600;
        margin: 0.15rem 0 0.3rem 0;
    }
    .dimension-badge {
        font-size: 0.62rem;
        font-weight: 600;
        padding: 0.1rem 0.4rem;
        border-radius: 3px;
        display: inline-block;
    }

    /* =========================================================================
       4. STREAMLIT NATIVE COMPONENTS (TABS, EXPANDERS, JSON, DOWNLOADS)
       ========================================================================= */

    /* Tabs Styling — Crisp, readable active & inactive contrast */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 6px 6px 0 0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1.25rem !important;
        border: none !important;
        opacity: 1 !important;
        transition: all 0.15s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background-color: var(--gold-subtle) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--gold-primary) !important;
        background-color: transparent !important;
        border-bottom: 2.5px solid var(--gold-primary) !important;
        font-weight: 700 !important;
    }

    /* Expanders Styling (Theme-consistent header + body) */
    div[data-testid="stExpander"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stExpander"] summary * {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary) !important;
    }
    div[data-testid="stExpander"] code {
        background-color: var(--code-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--code-border) !important;
    }

    /* JSON viewer */
    div[data-testid="stJson"] {
        background-color: var(--surface-alt) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
        padding: 0.75rem !important;
    }

    /* Validation rows */
    .check-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.55rem 0.85rem;
        border-radius: 6px;
        background: var(--surface-alt);
        border: 1px solid var(--border-subtle);
        margin-bottom: 0.4rem;
        font-size: 0.8rem;
    }
    .check-title {
        font-weight: 500;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }
    .check-badge-pass {
        color: var(--green-success);
        font-weight: 600;
        font-size: 0.7rem;
        background: var(--green-subtle);
        padding: 0.1rem 0.45rem;
        border-radius: 3px;
        border: 1px solid var(--green-success);
    }
    .check-badge-fail {
        color: var(--red-danger);
        font-weight: 600;
        font-size: 0.7rem;
        background: var(--red-subtle);
        padding: 0.1rem 0.45rem;
        border-radius: 3px;
        border: 1px solid var(--red-danger);
    }

    /* Download Buttons */
    div.stDownloadButton > button {
        background: var(--surface-alt) !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.55rem 0.85rem !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
    }
    div.stDownloadButton > button:hover {
        border-color: var(--gold-primary) !important;
        color: var(--gold-primary) !important;
        background: var(--gold-subtle) !important;
    }

    /* =========================================================================
       5. LAYER 2: ISOLATED LEGAL DOCUMENT VIEWER & PAPER SHEET
       ========================================================================= */

    .affidavit-viewer-container {
        background-color: var(--viewer-bg) !important;
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 2.5rem 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
        max-height: none !important;
        overflow-y: visible !important;
    }

    .affidavit-paper-header {
        width: 100%;
        max-width: 820px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        padding: 0 0.25rem;
    }

    /* The Paper Sheet is ALWAYS White with Black Text regardless of application theme */
    .affidavit-paper {
        background-color: #ffffff !important;
        color: #111827 !important;
        width: 100%;
        max-width: 820px;
        padding: 3.5rem 4rem;
        border-radius: 2px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.06);
        font-family: 'Times New Roman', Times, Georgia, serif;
        font-size: 1.05rem;
        line-height: 1.65;
        border: 1px solid #d1d5db;
        box-sizing: border-box;
    }

    .affidavit-paper * {
        color: #111827 !important;
    }

    .doc-heading {
        font-family: 'Times New Roman', Times, Georgia, serif;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        margin-top: 0;
        margin-bottom: 0.35rem;
        color: #000000 !important;
        letter-spacing: 0.02em;
    }

    .doc-subheading {
        font-family: 'Times New Roman', Times, Georgia, serif;
        font-size: 1.05rem;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        margin-top: 0;
        margin-bottom: 0.75rem;
        color: #000000 !important;
    }

    .doc-case-no {
        text-align: center;
        font-weight: bold;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        color: #000000 !important;
    }

    .doc-party-block {
        margin-bottom: 1rem;
        line-height: 1.5;
        color: #111827 !important;
    }

    .doc-versus {
        text-align: center;
        font-weight: bold;
        margin: 1.25rem 0;
        letter-spacing: 0.08em;
        color: #000000 !important;
    }

    .doc-title-container {
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding: 0.75rem 0;
        border-top: 1.5px solid #111827;
        border-bottom: 1.5px solid #111827;
        text-align: center;
    }

    .doc-title {
        font-family: 'Times New Roman', Times, Georgia, serif;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        margin: 0;
        color: #000000 !important;
        letter-spacing: 0.03em;
        line-height: 1.4;
    }

    .doc-deponent-clause {
        font-style: italic;
        margin-bottom: 1.5rem;
        text-align: justify;
        line-height: 1.6;
        color: #111827 !important;
    }

    .doc-body p {
        margin-bottom: 1rem;
        text-align: justify;
        line-height: 1.65;
        color: #111827 !important;
        text-indent: 0;
    }

    .doc-section-heading {
        font-family: 'Times New Roman', Times, Georgia, serif;
        font-size: 1.05rem;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #000000 !important;
        letter-spacing: 0.04em;
    }

    .doc-prayer-intro {
        margin-bottom: 1rem;
        text-align: justify;
        color: #111827 !important;
    }

    .doc-jurat-block {
        margin-top: 2rem;
        line-height: 1.5;
        color: #111827 !important;
    }

    .right-sign {
        text-align: right;
        font-weight: bold;
        margin-top: 1.25rem;
        color: #000000 !important;
    }

    .doc-advocate-block {
        margin-top: 2.25rem;
        border-top: 1px solid #d1d5db;
        padding-top: 1rem;
        line-height: 1.5;
        color: #111827 !important;
    }

    /* Footer */
    .app-footer {
        border-top: 1px solid var(--border-subtle);
        margin-top: 2rem;
        padding-top: 1.25rem;
        text-align: center;
        color: var(--text-muted);
        font-size: 0.78rem;
    }
    .app-footer-brand {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.2rem;
    }
    .app-footer-disclaimer {
        font-size: 0.72rem;
        color: var(--text-muted);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 1. Hero Section
# -----------------------------------------------------------------------------
api_key_set = bool(os.getenv("OPENROUTER_API_KEY"))
active_model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

status_badge_html = (
    '<span class="badge-status badge-status-ready">● SYSTEM READY</span>'
    if api_key_set
    else '<span class="badge-status badge-status-config">● CONFIG REQUIRED</span>'
)

st.markdown(
    f"""
    <div class="hero-container">
        <div class="hero-brand">
            <h1 class="hero-title">AFFIDAVIT<span class="accent">AI</span></h1>
            <div class="hero-subtitle">AI-powered Affidavit in Reply generation &amp; quality assurance</div>
            <div class="hero-desc">
                Generate a structured Affidavit in Reply from the supplied case information and reference format, then validate and audit the result.
            </div>
        </div>
        <div class="hero-meta-group">
            {status_badge_html}
            <span class="meta-model-info">OpenRouter · Model: {active_model}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. Dynamic Sidebar
# -----------------------------------------------------------------------------
has_result = "pipeline_result" in st.session_state

with st.sidebar:
    st.markdown('<div class="sidebar-section-header">PROJECT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">AffidavitAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Deterministic Legal Automation</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-header">WORKFLOW STAGES</div>', unsafe_allow_html=True)
    
    stages = [
        ("01", "Case Extraction"),
        ("02", "Template Analysis"),
        ("03", "Affidavit Generation"),
        ("04", "DOCX Rendering"),
        ("05", "Quality Validation"),
        ("06", "Evaluation"),
    ]
    for num, name in stages:
        if has_result:
            icon_html = '<span class="sidebar-step-icon-done">✓</span>'
            cls = "sidebar-step completed"
        else:
            icon_html = f'<span class="sidebar-step-num">{num}</span>'
            cls = "sidebar-step"
        st.markdown(f'<div class="{cls}">{icon_html} <span>{name}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">TECH STACK</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: var(--text-muted); line-height: 1.4;">Streamlit · Python · OpenRouter · Pydantic · python-docx</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Document Inputs Section (Redesigned 3-Column Layout)
# -----------------------------------------------------------------------------
case_pdf_path = None
format_pdf_path = None
sample_pdf_path = None

default_case = os.path.join("inputs", "case_information.pdf")
default_format = os.path.join("inputs", "format_explained.pdf")
default_sample = os.path.join("inputs", "sample_affidavit.pdf")

demo_files_exist = os.path.exists(default_case) and os.path.exists(default_format) and os.path.exists(default_sample)

# Document Inputs Header & Left-Aligned Demo Toggle
st.markdown(
    '<div style="font-family: \'JetBrains Mono\', monospace; font-size: 0.78rem; font-weight: 700; color: var(--gold-primary); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.6rem;">DOCUMENT INPUTS</div>',
    unsafe_allow_html=True,
)

use_demo_mode = st.toggle("Use assignment demo documents", value=True)
st.markdown(
    '<div style="font-size: 0.78rem; color: var(--text-muted); margin-top: -0.4rem; margin-bottom: 1rem; margin-left: 0.1rem;">'
    'Use the bundled assignment PDFs for the demo'
    '</div>',
    unsafe_allow_html=True,
)

card_col1, card_col2, card_col3 = st.columns(3)

# 1. REFERENCE FORMAT CARD
with card_col1:
    if use_demo_mode and demo_files_exist:
        format_pdf_path = default_format
        st.markdown(
            """
            <div class="doc-input-card">
                <div>
                    <div class="doc-input-header">
                        <span class="doc-input-title">REFERENCE FORMAT</span>
                        <span class="input-badge-loaded">✓ LOADED</span>
                    </div>
                    <div class="doc-input-desc">Upload the affidavit format/rulebook that defines the required structure.</div>
                </div>
                <div class="doc-loaded-box">
                    <span>📄</span>
                    <span>01 Affidavit Format Explained.pdf</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="doc-input-card">
                <div>
                    <div class="doc-input-header">
                        <span class="doc-input-title">REFERENCE FORMAT</span>
                    </div>
                    <div class="doc-input-desc">Upload the affidavit format/rulebook that defines the required structure.</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_format = st.file_uploader("Format Rules", type=["pdf"], label_visibility="collapsed", key="u_fmt", max_upload_size=20)
        st.markdown("</div>", unsafe_allow_html=True)
        temp_dir = os.path.join("outputs", "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        if uploaded_format:
            format_pdf_path = os.path.join(temp_dir, "format_explained.pdf")
            with open(format_pdf_path, "wb") as f:
                f.write(uploaded_format.read())

# 2. SAMPLE AFFIDAVIT CARD
with card_col2:
    if use_demo_mode and demo_files_exist:
        sample_pdf_path = default_sample
        st.markdown(
            """
            <div class="doc-input-card">
                <div>
                    <div class="doc-input-header">
                        <span class="doc-input-title">SAMPLE AFFIDAVIT</span>
                        <span class="input-badge-loaded">✓ LOADED</span>
                    </div>
                    <div class="doc-input-desc">Upload the sample affidavit used as the structural reference.</div>
                </div>
                <div class="doc-loaded-box">
                    <span>📄</span>
                    <span>02 Affidavit in Reply Sample.pdf</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="doc-input-card">
                <div>
                    <div class="doc-input-header">
                        <span class="doc-input-title">SAMPLE AFFIDAVIT</span>
                    </div>
                    <div class="doc-input-desc">Upload the sample affidavit used as the structural reference.</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_sample = st.file_uploader("Sample Affidavit", type=["pdf"], label_visibility="collapsed", key="u_smp", max_upload_size=20)
        st.markdown("</div>", unsafe_allow_html=True)
        temp_dir = os.path.join("outputs", "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        if uploaded_sample:
            sample_pdf_path = os.path.join(temp_dir, "sample_affidavit.pdf")
            with open(sample_pdf_path, "wb") as f:
                f.write(uploaded_sample.read())

# 3. CASE INFORMATION CARD
with card_col3:
    if use_demo_mode and demo_files_exist:
        case_pdf_path = default_case
        st.markdown(
            """
            <div class="doc-input-card">
                <div>
                    <div class="doc-input-header">
                        <span class="doc-input-title">CASE INFORMATION</span>
                        <span class="input-badge-loaded">✓ LOADED</span>
                    </div>
                    <div class="doc-input-desc">Upload the case-specific facts used to generate the new affidavit.</div>
                </div>
                <div class="doc-loaded-box">
                    <span>📄</span>
                    <span>03 Case Information.pdf</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="doc-input-card">
                <div>
                    <div class="doc-input-header">
                        <span class="doc-input-title">CASE INFORMATION</span>
                    </div>
                    <div class="doc-input-desc">Upload the case-specific facts used to generate the new affidavit.</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_case = st.file_uploader("Case Info", type=["pdf"], label_visibility="collapsed", key="u_cas", max_upload_size=20)
        st.markdown("</div>", unsafe_allow_html=True)
        temp_dir = os.path.join("outputs", "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        if uploaded_case:
            case_pdf_path = os.path.join(temp_dir, "case_info.pdf")
            with open(case_pdf_path, "wb") as f:
                f.write(uploaded_case.read())

# -----------------------------------------------------------------------------
# 4. Primary CTA Button & Pipeline Execution
# -----------------------------------------------------------------------------
st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 1.8, 1])
with btn_col2:
    generate_btn = st.button("GENERATE AFFIDAVIT", type="primary", use_container_width=True)

progress_placeholder = st.empty()

WORKFLOW_STEPS = [
    "Case information extracted",
    "Template specification built",
    "Affidavit generated",
    "DOCX rendered",
    "Deterministic validation",
    "Quality evaluation",
]

def render_checklist(active_step: int, completed: bool = False):
    items_html = []
    for i, step_name in enumerate(WORKFLOW_STEPS, 1):
        if completed or i < active_step:
            icon = '<span class="checklist-icon-done">✓</span>'
            cls = "checklist-item completed"
        elif i == active_step:
            icon = '<span class="checklist-icon-active">●</span>'
            cls = "checklist-item active"
        else:
            icon = '<span class="checklist-icon-pending">○</span>'
            cls = "checklist-item"
        items_html.append(f'<div class="{cls}">{icon} <span>{step_name}</span></div>')

    title = "AFFIDAVIT GENERATION COMPLETE" if completed else "GENERATING AFFIDAVIT"
    title_color = "var(--green-success)" if completed else "var(--gold-primary)"
    return f"""
    <div class="checklist-container">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600; color: {title_color}; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.5rem;">
            {title}
        </div>
        <div class="checklist-grid">
            {''.join(items_html)}
        </div>
    </div>
    """

if generate_btn:
    if not os.getenv("OPENROUTER_API_KEY"):
        st.error("Configuration Required: Please set your OPENROUTER_API_KEY in .env before proceeding.")
    elif not case_pdf_path:
        st.error("Input Required: Please select Demo Mode or upload a Case Information PDF.")
    else:
        def update_progress(step: int, total: int, message: str):
            progress_placeholder.markdown(render_checklist(active_step=step, completed=False), unsafe_allow_html=True)

        try:
            with st.spinner("Executing legal document generation pipeline..."):
                result: PipelineResult = run_pipeline(
                    case_info_pdf_path=case_pdf_path,
                    format_explained_pdf_path=format_pdf_path,
                    sample_affidavit_pdf_path=sample_pdf_path,
                    output_dir="outputs",
                    progress_callback=update_progress,
                )

            progress_placeholder.markdown(render_checklist(active_step=6, completed=True), unsafe_allow_html=True)
            st.session_state["pipeline_result"] = result
            st.rerun()

        except Exception as exc:
            progress_placeholder.empty()
            st.error(f"Pipeline execution error: {str(exc)}")

# -----------------------------------------------------------------------------
# 5. Quality Summary Dashboard
# -----------------------------------------------------------------------------
if "pipeline_result" in st.session_state:
    res: PipelineResult = st.session_state["pipeline_result"]

    overall_score = res.evaluation_report.overall_score
    max_score = res.evaluation_report.max_score
    total_eval_issues = len(res.evaluation_report.issues)

    if not res.validation_report.passed or overall_score < 100.0 or total_eval_issues > 0:
        passed_status = "REVIEW REQUIRED"
        status_badge_class = "quality-hero-badge-review"
    else:
        passed_status = "PASSED"
        status_badge_class = "quality-hero-badge-pass"

    total_checks = len(res.validation_report.checks)
    passed_checks = total_checks - len(res.validation_report.issues)
    para_count = len(res.affidavit.body_paragraphs)

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Hero Quality Box
    st.markdown(
        f"""
        <div class="quality-hero-container">
            <div class="quality-hero-title">QUALITY &amp; COMPLIANCE AUDIT</div>
            <div class="quality-hero-score">{overall_score:.0f} <span style="font-size: 1.4rem; color: var(--text-muted); font-weight: 400;">/ {max_score:.0f}</span></div>
            <div>
                <span class="{status_badge_class}">✓ {passed_status}</span>
            </div>
            <div class="quality-hero-subtag">Audit Ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Compact Sub-metrics
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown(
            f"""
            <div class="metric-compact-card">
                <div class="metric-compact-val">{passed_checks} / {total_checks}</div>
                <div class="metric-compact-lbl">Validation Checks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col2:
        st.markdown(
            f"""
            <div class="metric-compact-card">
                <div class="metric-compact-val">{para_count}</div>
                <div class="metric-compact-lbl">Body Paragraphs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col3:
        st.markdown(
            f"""
            <div class="metric-compact-card">
                <div class="metric-compact-val">{total_eval_issues}</div>
                <div class="metric-compact-lbl">Issues Detected</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Six Dimension Cards
    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
    dim_cols = st.columns(6)

    for idx, dim in enumerate(res.evaluation_report.dimensions):
        with dim_cols[idx]:
            is_perfect = (dim.score >= dim.max_score) and (len(dim.issues) == 0)
            badge_text = "✓ PASS" if is_perfect else "⚠️ REVIEW"
            badge_style = "background: var(--green-subtle); color: var(--green-success);" if is_perfect else "background: rgba(245, 158, 11, 0.15); color: var(--gold-light);"
            st.markdown(
                f"""
                <div class="dimension-card">
                    <div class="dimension-name" title="{dim.name}">{dim.name}</div>
                    <div class="dimension-score">{dim.score:.0f} / {dim.max_score:.0f}</div>
                    <div class="dimension-pct">{dim.percentage:.0f}%</div>
                    <span class="dimension-badge" style="{badge_style}">{badge_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------------------------------
    # 6. Content Tabs
    # -----------------------------------------------------------------------------
    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
    tab_affidavit, tab_eval, tab_validation, tab_casedata = st.tabs([
        "📄 Affidavit",
        "🔍 Evaluation",
        "🛡 Validation",
        "🗂 Case Data",
    ])

    # Tab 1: Realistic Legal Paper Viewer Container
    with tab_affidavit:
        body_paras_html = "".join([f"<p><b>{bp.paragraph_number}.</b> {bp.text}</p>" for bp in res.affidavit.body_paragraphs])
        prayer_items_html = "".join([f"<p style='margin-left: 24px;'><b>{pi.letter}</b> {pi.text}</p>" for pi in res.affidavit.prayer.items])
        respondents_html = "".join([f"<div style='margin-bottom: 0.35rem;'><b>{r.name}</b><br/><span style='font-size: 0.9em; font-style: italic;'>...{r.status_tag}</span></div>" for r in res.affidavit.cause_title.respondents])

        raw_document_html = f"""
<div class="affidavit-viewer-container">
    <div class="affidavit-paper-header">
        <span>LEGAL DOCUMENT PREVIEW</span>
        <span>FORMAL AFFIDAVIT IN REPLY</span>
    </div>
    <div class="affidavit-paper">
        <h3 class="doc-heading">{res.affidavit.forum_heading}</h3>
        <h4 class="doc-subheading">{res.affidavit.jurisdiction}</h4>
        <div class="doc-case-no">{res.affidavit.case_number_line}</div>

        <div class="doc-party-block">
            <b>{res.affidavit.cause_title.petitioner.name}</b><br/>
            <span style="font-style: italic;">...Petitioner</span>
        </div>

        <div class="doc-versus">VERSUS</div>

        <div class="doc-party-block">
            {respondents_html}
        </div>

        <div class="doc-title-container">
            <h4 class="doc-title">{res.affidavit.affidavit_title}</h4>
        </div>

        <p class="doc-deponent-clause">{res.affidavit.deponent_clause}</p>

        <div class="doc-body">
            {body_paras_html}
        </div>

        <h4 class="doc-section-heading">PRAYER</h4>
        <p class="doc-prayer-intro">{res.affidavit.prayer.intro_text}</p>
        {prayer_items_html}

        <div class="doc-jurat-block">
            <div>{res.affidavit.jurat.place_line}</div>
            <div>{res.affidavit.jurat.date_line}</div>
            <div style="margin-top: 0.4rem; font-style: italic;">{res.affidavit.jurat.before_me}</div>
            <div class="right-sign">{res.affidavit.jurat.deponent_tag}</div>
        </div>

        <h4 class="doc-section-heading">VERIFICATION</h4>
        <p>{res.affidavit.verification.full_text}</p>
        <p>{res.affidavit.verification.verified_at_line}</p>
        <div class="right-sign">{res.affidavit.verification.deponent_tag}</div>

        <div class="doc-advocate-block">
            <b>{res.affidavit.advocate_block.firm_name}</b><br/>
            <span style="font-size: 0.9em;">{res.affidavit.advocate_block.acting_for}</span>
        </div>
    </div>
</div>
"""
        document_html = "\n".join(line.strip() for line in raw_document_html.strip().splitlines())
        st.markdown(document_html, unsafe_allow_html=True)

    # Tab 2: Evaluation Report
    with tab_eval:
        st.markdown('<div class="sidebar-section-header" style="font-size: 0.75rem; margin-bottom: 0.5rem;">EVALUATION BREAKDOWN</div>', unsafe_allow_html=True)
        for dim in res.evaluation_report.dimensions:
            with st.expander(f"{dim.name.upper()} — {dim.score:.1f} / {dim.max_score:.0f} pts ({dim.percentage:.0f}%)", expanded=True):
                st.markdown(f"**Score:** `{dim.score:.1f} / {dim.max_score:.0f}` &nbsp;|&nbsp; **Percentage:** `{dim.percentage:.0f}%`")
                st.markdown(f"**Explanation:** {dim.explanation}")
                if dim.issues:
                    st.markdown("**Issues Identified:**")
                    for iss in dim.issues:
                        st.markdown(f"- `[{iss.severity.upper()}]` {iss.description} (Source: {iss.source})")
                else:
                    st.markdown("<span style='color: var(--green-success); font-size: 0.85rem;'>✓ Zero defects or omissions found in this dimension.</span>", unsafe_allow_html=True)

        st.markdown(
            f'<div style="background: var(--surface-alt); border: 1px solid var(--border-subtle); padding: 0.65rem 0.9rem; border-radius: 6px; font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.75rem;">'
            f'<b>Evaluation Methodology &amp; Scope:</b> {res.evaluation_report.limitations}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Tab 3: Validation Checks
    with tab_validation:
        st.markdown('<div class="sidebar-section-header" style="font-size: 0.75rem; margin-bottom: 0.5rem;">DETERMINISTIC CHECKS (20/20)</div>', unsafe_allow_html=True)
        v_col1, v_col2 = st.columns(2)
        mid_idx = (len(res.validation_report.checks) + 1) // 2

        with v_col1:
            for check in res.validation_report.checks[:mid_idx]:
                badge = '<span class="check-badge-pass">PASS</span>' if check.passed else '<span class="check-badge-fail">FAIL</span>'
                st.markdown(
                    f'<div class="check-row"><span class="check-title">{check.check_name}</span>{badge}</div>',
                    unsafe_allow_html=True,
                )

        with v_col2:
            for check in res.validation_report.checks[mid_idx:]:
                badge = '<span class="check-badge-pass">PASS</span>' if check.passed else '<span class="check-badge-fail">FAIL</span>'
                st.markdown(
                    f'<div class="check-row"><span class="check-title">{check.check_name}</span>{badge}</div>',
                    unsafe_allow_html=True,
                )

    # Tab 4: Extracted Case Data
    with tab_casedata:
        st.markdown('<div class="sidebar-section-header" style="font-size: 0.75rem; margin-bottom: 0.5rem;">EXTRACTED CASE DATA SCHEMA</div>', unsafe_allow_html=True)
        st.json(res.case_data.model_dump())

    # -----------------------------------------------------------------------------
    # 7. Compact Export Section
    # -----------------------------------------------------------------------------
    st.markdown(
        """
        <div class="compact-card" style="margin-top: 1.25rem;">
            <div class="card-header-line">
                <div>
                    <span class="card-label">EXPORT ARTIFACTS</span>
                    <span class="card-subtitle" style="margin-left: 0.5rem;">Download production legal documents and audit reports</span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    dl1, dl2, dl3, dl4 = st.columns(4)

    # 1. DOCX
    if os.path.exists(res.docx_path):
        with open(res.docx_path, "rb") as f:
            dl1.download_button(
                label="Generated Affidavit (.docx)",
                data=f.read(),
                file_name="generated_affidavit.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

    # 2. Evaluation Report JSON
    if os.path.exists(res.evaluation_report_path):
        with open(res.evaluation_report_path, "r", encoding="utf-8") as f:
            dl2.download_button(
                label="Evaluation Report (.json)",
                data=f.read(),
                file_name="evaluation_report.json",
                mime="application/json",
                use_container_width=True,
            )

    # 3. Evaluation Report Markdown
    if os.path.exists(res.evaluation_report_md_path):
        with open(res.evaluation_report_md_path, "r", encoding="utf-8") as f:
            dl3.download_button(
                label="Evaluation Report (.md)",
                data=f.read(),
                file_name="evaluation_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

    # 4. Case Data JSON
    if os.path.exists(res.extracted_case_data_path):
        with open(res.extracted_case_data_path, "r", encoding="utf-8") as f:
            dl4.download_button(
                label="Case Data (.json)",
                data=f.read(),
                file_name="extracted_case_data.json",
                mime="application/json",
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        <div class="app-footer-brand">AffidavitAI</div>
        <div>AI-assisted document generation and quality assurance.</div>
        <div class="app-footer-disclaimer">For demonstration and evaluation purposes only. Not legal advice.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
