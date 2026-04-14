import streamlit as st
import tempfile
import os
import time
from datetime import datetime

from audio_handler import transcribe_audio
from agent import get_intent_and_params
from tools import execute_tool

# ─────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────
st.set_page_config(
    page_title="VoiceForge — AI Agent",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────
# Premium Design System — CSS
# ─────────────────────────────────────────────────
st.markdown(
    """
<style>
    /* ═══════════════════════════════════════════════
       FOUNDATIONS — Fonts, Resets, Global Theme
       ═══════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-base: #08080c;
        --bg-surface: #0e0e14;
        --bg-elevated: #14141e;
        --bg-glass: rgba(18, 18, 28, 0.6);
        --bg-glass-hover: rgba(24, 24, 38, 0.75);
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-default: rgba(255, 255, 255, 0.09);
        --border-hover: rgba(139, 92, 246, 0.35);
        --border-glow: rgba(139, 92, 246, 0.5);
        --accent-primary: #8b5cf6;
        --accent-secondary: #06b6d4;
        --accent-warm: #f59e0b;
        --accent-success: #10b981;
        --accent-danger: #ef4444;
        --text-primary: rgba(255, 255, 255, 0.92);
        --text-secondary: rgba(255, 255, 255, 0.6);
        --text-muted: rgba(255, 255, 255, 0.35);
        --glow-purple: rgba(139, 92, 246, 0.15);
        --glow-cyan: rgba(6, 182, 212, 0.12);
        --radius-sm: 10px;
        --radius-md: 14px;
        --radius-lg: 20px;
        --radius-xl: 24px;
        --shadow-glow: 0 0 40px rgba(139, 92, 246, 0.08);
        --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-smooth: 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-base) !important;
    }

    /* Hide Streamlit branding but keep sidebar toggle visible */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: none !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.25);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.45); }

    /* ═══════════════════════════════════════════════
       SIDEBAR — Premium Sidebar Design
       ═══════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0c14 0%, #0a0a12 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        color: var(--text-muted) !important;
        margin-bottom: 0.75rem !important;
    }

    /* ═══════════════════════════════════════════════
       HERO SECTION — Animated Gradient Header
       ═══════════════════════════════════════════════ */
    @keyframes aurora-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    @keyframes float-glow {
        0%, 100% { opacity: 0.4; transform: translate(0, 0) scale(1); }
        33% { opacity: 0.6; transform: translate(10px, -15px) scale(1.05); }
        66% { opacity: 0.35; transform: translate(-8px, 8px) scale(0.97); }
    }
    @keyframes subtle-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }

    .hero-container {
        background: linear-gradient(135deg, #0c0a1e 0%, #161233 35%, #1a1040 60%, #0f0d24 100%);
        border-radius: var(--radius-xl);
        padding: 2.75rem 2.5rem;
        margin-bottom: 1.75rem;
        border: 1px solid rgba(139, 92, 246, 0.12);
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 48px rgba(0, 0, 0, 0.4), var(--shadow-glow);
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -60%;
        left: -30%;
        width: 160%;
        height: 220%;
        background: radial-gradient(ellipse at 25% 45%, rgba(139, 92, 246, 0.1) 0%, transparent 55%),
                    radial-gradient(ellipse at 75% 55%, rgba(6, 182, 212, 0.07) 0%, transparent 50%),
                    radial-gradient(ellipse at 50% 20%, rgba(245, 158, 11, 0.04) 0%, transparent 40%);
        animation: float-glow 12s ease-in-out infinite;
        pointer-events: none;
    }
    .hero-container::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, transparent 60%, rgba(8, 8, 12, 0.5) 100%);
        pointer-events: none;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.3rem 0.85rem;
        border-radius: 20px;
        background: rgba(139, 92, 246, 0.12);
        border: 1px solid rgba(139, 92, 246, 0.2);
        font-size: 0.7rem;
        font-weight: 600;
        color: #a78bfa;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    .hero-badge .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #10b981;
        animation: subtle-pulse 2s ease-in-out infinite;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 25%, #8b5cf6 50%, #06b6d4 75%, #22d3ee 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: aurora-shift 8s ease-in-out infinite;
        margin: 0;
        line-height: 1.15;
        position: relative;
        z-index: 1;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0.75rem;
        position: relative;
        z-index: 1;
        line-height: 1.65;
        max-width: 700px;
    }
    .hero-subtitle strong {
        color: var(--text-primary);
        font-weight: 600;
    }
    .hero-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 1.25rem;
        position: relative;
        z-index: 1;
    }
    .hero-chip {
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-size: 0.72rem;
        font-weight: 500;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: var(--text-secondary);
        transition: var(--transition-fast);
    }
    .hero-chip:hover {
        border-color: var(--border-hover);
        background: rgba(139, 92, 246, 0.08);
        color: #c4b5fd;
    }

    /* ═══════════════════════════════════════════════
       PIPELINE — Animated Step Tracker
       ═══════════════════════════════════════════════ */
    @keyframes pulse-ring {
        0% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.35); }
        70% { box-shadow: 0 0 0 8px rgba(139, 92, 246, 0); }
        100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0); }
    }

    .pipeline-container {
        display: flex;
        align-items: center;
        gap: 0;
        margin: 0.5rem 0 1.75rem 0;
        padding: 1.25rem 1.5rem;
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
    }
    .pipeline-step {
        flex: 1;
        text-align: center;
        padding: 0.85rem 0.5rem;
        border-radius: var(--radius-md);
        background: transparent;
        border: 1px solid transparent;
        transition: var(--transition-smooth);
        position: relative;
        cursor: default;
    }
    .pipeline-step:hover {
        background: rgba(255, 255, 255, 0.02);
    }
    .pipeline-step.active {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(6, 182, 212, 0.08));
        border-color: rgba(139, 92, 246, 0.3);
        animation: pulse-ring 2.5s ease-in-out infinite;
    }
    .pipeline-step.completed {
        background: rgba(16, 185, 129, 0.06);
        border-color: rgba(16, 185, 129, 0.2);
    }
    .pipeline-step .step-icon {
        font-size: 1.4rem;
        display: block;
        margin-bottom: 0.35rem;
    }
    .pipeline-step .step-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--text-muted);
        transition: var(--transition-fast);
    }
    .pipeline-step.active .step-label {
        color: #a78bfa;
    }
    .pipeline-step.completed .step-label {
        color: #34d399;
    }
    .pipeline-step.completed .step-icon::after {
        content: '✓';
        font-size: 0.55rem;
        position: absolute;
        bottom: 6px;
        right: 25%;
        background: #10b981;
        color: white;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .pipeline-connector {
        width: 100%;
        max-width: 60px;
        height: 2px;
        background: linear-gradient(90deg, var(--border-subtle), rgba(139, 92, 246, 0.15), var(--border-subtle));
        flex-shrink: 1;
    }

    /* ═══════════════════════════════════════════════
       GLASS CARD — Deep Glassmorphism
       ═══════════════════════════════════════════════ */
    .glass-card {
        background: var(--bg-glass);
        backdrop-filter: blur(16px) saturate(1.3);
        -webkit-backdrop-filter: blur(16px) saturate(1.3);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        transition: var(--transition-smooth);
        position: relative;
        overflow: hidden;
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.2), rgba(6, 182, 212, 0.15), transparent);
        opacity: 0;
        transition: var(--transition-smooth);
    }
    .glass-card:hover {
        border-color: var(--border-hover);
        background: var(--bg-glass-hover);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.06), var(--shadow-glow);
        transform: translateY(-1px);
    }
    .glass-card:hover::before {
        opacity: 1;
    }
    .glass-card h3 {
        margin-top: 0;
        font-weight: 700;
        font-size: 1rem;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-desc {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    /* ═══════════════════════════════════════════════
       INTENT BADGES — Refined Pills
       ═══════════════════════════════════════════════ */
    .intent-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 0.4rem 0.9rem;
        border-radius: 22px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        transition: var(--transition-fast);
        margin: 3px 4px;
    }
    .intent-badge:hover {
        transform: translateY(-1px) scale(1.03);
    }
    .intent-create_file {
        background: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.22);
        box-shadow: 0 2px 12px rgba(59, 130, 246, 0.08);
    }
    .intent-write_code {
        background: rgba(168, 85, 247, 0.1);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.22);
        box-shadow: 0 2px 12px rgba(168, 85, 247, 0.08);
    }
    .intent-summarize {
        background: rgba(245, 158, 11, 0.1);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.22);
        box-shadow: 0 2px 12px rgba(245, 158, 11, 0.08);
    }
    .intent-general_chat {
        background: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.22);
        box-shadow: 0 2px 12px rgba(16, 185, 129, 0.08);
    }

    /* ═══════════════════════════════════════════════
       RESULTS — Success / Error Cards
       ═══════════════════════════════════════════════ */
    .result-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.06), rgba(16, 185, 129, 0.02));
        border: 1px solid rgba(16, 185, 129, 0.18);
        border-radius: var(--radius-md);
        padding: 1.15rem 1.35rem;
        margin: 0.5rem 0;
        transition: var(--transition-fast);
        position: relative;
        overflow: hidden;
    }
    .result-success::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #10b981, #34d399);
        border-radius: 3px 0 0 3px;
    }
    .result-success:hover {
        border-color: rgba(16, 185, 129, 0.3);
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.06);
    }
    .result-error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.06), rgba(239, 68, 68, 0.02));
        border: 1px solid rgba(239, 68, 68, 0.18);
        border-radius: var(--radius-md);
        padding: 1.15rem 1.35rem;
        margin: 0.5rem 0;
        transition: var(--transition-fast);
        position: relative;
        overflow: hidden;
    }
    .result-error::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #ef4444, #f87171);
        border-radius: 3px 0 0 3px;
    }
    .result-error:hover {
        border-color: rgba(239, 68, 68, 0.3);
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.06);
    }

    /* ═══════════════════════════════════════════════
       SIDEBAR — History Entries & Info Cards
       ═══════════════════════════════════════════════ */
    .history-entry {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-sm);
        padding: 0.85rem;
        margin-bottom: 0.6rem;
        font-size: 0.8rem;
        transition: var(--transition-fast);
        position: relative;
        overflow: hidden;
    }
    .history-entry::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #8b5cf6, #06b6d4);
        opacity: 0;
        transition: var(--transition-fast);
    }
    .history-entry:hover {
        background: rgba(139, 92, 246, 0.04);
        border-color: rgba(139, 92, 246, 0.15);
    }
    .history-entry:hover::before {
        opacity: 1;
    }
    .history-entry .timestamp {
        color: var(--text-muted);
        font-size: 0.67rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        font-family: 'JetBrains Mono', monospace;
    }

    .sys-info-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-sm);
        padding: 0.7rem 0.85rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: var(--transition-fast);
    }
    .sys-info-card:hover {
        border-color: rgba(139, 92, 246, 0.15);
        background: rgba(139, 92, 246, 0.03);
    }
    .sys-info-label {
        font-size: 0.68rem;
        color: var(--text-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .sys-info-value {
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ═══════════════════════════════════════════════
       APPROVAL PANEL — Warning Glassmorphism
       ═══════════════════════════════════════════════ */
    .approval-panel {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(249, 115, 22, 0.03));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(245, 158, 11, 0.18);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    .approval-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.3), transparent);
    }
    .approval-panel h3 {
        color: #fbbf24 !important;
    }

    /* ═══════════════════════════════════════════════
       STREAMLIT OVERRIDES — Buttons, Inputs, Others
       ═══════════════════════════════════════════════ */

    /* Primary button */
    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #7c3aed, #8b5cf6, #6d28d9) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 0.65rem 1.5rem !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition-smooth) !important;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.2) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    .stButton > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: linear-gradient(135deg, #6d28d9, #7c3aed, #8b5cf6) !important;
        box-shadow: 0 6px 28px rgba(124, 58, 237, 0.35) !important;
        transform: translateY(-2px) !important;
        border-color: rgba(139, 92, 246, 0.6) !important;
    }
    .stButton > button[kind="primary"]:active,
    div[data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.25) !important;
    }

    /* Secondary buttons */
    .stButton > button:not([kind="primary"]) {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--border-default) !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition-smooth) !important;
        backdrop-filter: blur(8px) !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(139, 92, 246, 0.08) !important;
        border-color: var(--border-hover) !important;
        color: #c4b5fd !important;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.08) !important;
        transform: translateY(-1px) !important;
    }

    /* Radio buttons */
    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.5rem 0.75rem !important;
        transition: var(--transition-fast) !important;
        cursor: pointer !important;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: var(--border-hover) !important;
        background: rgba(139, 92, 246, 0.06) !important;
    }

    /* File uploader */
    section[data-testid="stFileUploader"] {
        border: 1px dashed rgba(139, 92, 246, 0.2) !important;
        border-radius: var(--radius-md) !important;
        background: rgba(139, 92, 246, 0.02) !important;
        transition: var(--transition-fast) !important;
    }
    section[data-testid="stFileUploader"]:hover {
        border-color: rgba(139, 92, 246, 0.35) !important;
        background: rgba(139, 92, 246, 0.04) !important;
    }

    /* Expander */
    details[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition-fast) !important;
    }
    details[data-testid="stExpander"]:hover {
        border-color: rgba(139, 92, 246, 0.2) !important;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        font-size: 0.82rem !important;
    }

    /* Spinner */
    .stSpinner > div { color: #a78bfa !important; }

    /* Code blocks */
    .stCodeBlock {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    /* Dividers */
    hr {
        border-color: var(--border-subtle) !important;
        margin: 1rem 0 !important;
    }

    /* ═══════════════════════════════════════════════
       TIMING BADGE
       ═══════════════════════════════════════════════ */
    .timing-badge {
        text-align: center;
        margin-top: 1.5rem;
        padding: 0.85rem 1.25rem;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.04), rgba(6, 182, 212, 0.03));
        border: 1px solid rgba(139, 92, 246, 0.12);
        font-size: 0.82rem;
        color: var(--text-muted);
    }
    .timing-badge strong {
        color: #a78bfa;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }

    /* ═══════════════════════════════════════════════
       TRANSCRIPT CARD
       ═══════════════════════════════════════════════ */
    .transcript-text {
        color: var(--text-primary);
        font-size: 1.05rem;
        line-height: 1.7;
        margin: 0.75rem 0;
        padding: 1rem 1.25rem;
        background: rgba(139, 92, 246, 0.04);
        border-left: 3px solid rgba(139, 92, 246, 0.3);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        font-style: italic;
    }
    .meta-chips {
        display: flex;
        gap: 1rem;
        margin-top: 0.75rem;
        flex-wrap: wrap;
    }
    .meta-chip {
        font-size: 0.72rem;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
        padding: 0.25rem 0.65rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 6px;
    }

    /* ═══════════════════════════════════════════════
       FOOTER BRAND
       ═══════════════════════════════════════════════ */
    .footer-brand {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: var(--text-muted);
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .footer-brand a {
        color: #a78bfa;
        text-decoration: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "pipeline_stage" not in st.session_state:
    st.session_state.pipeline_stage = 0  # 0=idle, 1=input, 2=stt, 3=intent, 4=execute, 5=done
if "pending_approvals" not in st.session_state:
    st.session_state.pending_approvals = []
if "current_results" not in st.session_state:
    st.session_state.current_results = []

INTENT_ICONS = {
    "create_file": "📄",
    "write_code": "💻",
    "summarize": "📝",
    "general_chat": "💬",
}

INTENT_LABELS = {
    "create_file": "Create File",
    "write_code": "Write Code",
    "summarize": "Summarize",
    "general_chat": "General Chat",
}


# ─────────────────────────────────────────────────
# Pipeline Step Visualization
# ─────────────────────────────────────────────────
def render_pipeline(stage: int):
    steps = [
        ("🎤", "Input"),
        ("🗣️", "Transcribe"),
        ("🧠", "Classify"),
        ("⚙️", "Execute"),
        ("✅", "Output"),
    ]
    html_parts = ['<div class="pipeline-container">']
    for i, (icon, label) in enumerate(steps):
        if i > 0:
            html_parts.append('<div class="pipeline-connector"></div>')
        css_class = "pipeline-step"
        if i + 1 < stage:
            css_class += " completed"
        elif i + 1 == stage:
            css_class += " active"
        html_parts.append(
            f'<div class="{css_class}">'
            f'<span class="step-icon">{icon}</span>'
            f'<span class="step-label">{label}</span>'
            f"</div>"
        )
    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# Sidebar — Session History & System Info
# ─────────────────────────────────────────────────
with st.sidebar:
    # Sidebar brand
    st.markdown(
        """<div style="text-align:center;padding:0.5rem 0 1rem 0;">
            <span style="font-size:1.5rem;">⚡</span>
            <span style="font-size:1rem;font-weight:800;
            background:linear-gradient(135deg,#c4b5fd,#8b5cf6);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            letter-spacing:-0.02em;">VoiceForge</span>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### 🕘 History")
    if not st.session_state.history:
        st.caption("No commands yet — record or upload audio to begin.")
    else:
        for i, entry in enumerate(reversed(st.session_state.history)):
            intents_str = ", ".join(
                [INTENT_LABELS.get(it.get("intent", ""), it.get("intent", "")) for it in entry.get("intents", [])]
            )
            transcript_preview = entry.get('transcript', '')[:70]
            if len(entry.get('transcript', '')) > 70:
                transcript_preview += '…'
            st.markdown(
                f"""<div class="history-entry">
                    <div class="timestamp">{entry.get('timestamp', '')}  ·  {entry.get('total_seconds', '?')}s</div>
                    <div style="margin:5px 0;color:var(--text-primary);font-size:0.78rem;">🗣️ {transcript_preview}</div>
                    <div style="color:#a78bfa;font-weight:600;font-size:0.72rem;">→ {intents_str}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()
    if st.button("🗑️  Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.markdown("### 🔧 System")
    st.markdown(
        """<div class="sys-info-card">
            <span style="font-size:1rem;">🗣️</span>
            <div><div class="sys-info-label">STT Engine</div>
            <div class="sys-info-value">Faster-Whisper · base · int8</div></div>
        </div>
        <div class="sys-info-card">
            <span style="font-size:1rem;">🧠</span>
            <div><div class="sys-info-label">LLM</div>
            <div class="sys-info-value">gemma4:e2b · Ollama</div></div>
        </div>
        <div class="sys-info-card">
            <span style="font-size:1rem;">📁</span>
            <div><div class="sys-info-label">Sandbox</div>
            <div class="sys-info-value">./output/</div></div>
        </div>
        <div class="sys-info-card">
            <span style="font-size:1rem;">🔒</span>
            <div><div class="sys-info-label">Privacy</div>
            <div class="sys-info-value">100% Local · No Cloud</div></div>
        </div>""",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────
# Hero Section
# ─────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-container">
    <div class="hero-badge"><span class="dot"></span> Fully Local · Private · Offline-Ready</div>
    <h1 class="hero-title">⚡ VoiceForge</h1>
    <p class="hero-subtitle">
        <strong>Speak. Understand. Execute.</strong> — A privacy-first AI agent that transforms your voice
        into real actions: file creation, code generation, text summarization, and conversational AI.
        100% on-device. Zero cloud dependency.
    </p>
    <div class="hero-chips">
        <span class="hero-chip">🎤 Faster-Whisper STT</span>
        <span class="hero-chip">🧠 Gemma 4 via Ollama</span>
        <span class="hero-chip">📄 Sandboxed File I/O</span>
        <span class="hero-chip">🔒 Fully Offline</span>
        <span class="hero-chip">🛡️ Human-in-the-Loop</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Pipeline Visualization
render_pipeline(st.session_state.pipeline_stage)

# ─────────────────────────────────────────────────
# 1. INPUT LAYER
# ─────────────────────────────────────────────────
st.markdown(
    """<div class="glass-card">
        <h3>🎤 Audio Input</h3>
        <p class="section-desc">Record a voice command or upload an audio file to begin the pipeline.</p>
    """,
    unsafe_allow_html=True,
)

col_method, col_input = st.columns([1, 3])
with col_method:
    input_method = st.radio(
        "Method",
        ["🎙️ Record", "📁 Upload"],
        label_visibility="collapsed",
    )
with col_input:
    audio_data = None
    audio_ext = ".wav"
    if input_method == "🎙️ Record":
        audio_data = st.audio_input("Record a voice command")
    else:
        audio_data = st.file_uploader(
            "Upload audio file (.wav, .mp3)",
            type=["wav", "mp3"],
        )
        if audio_data is not None and audio_data.name.endswith(".mp3"):
            audio_ext = ".mp3"

st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# 2. PROCESS PIPELINE
# ─────────────────────────────────────────────────
if audio_data is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=audio_ext) as tmp_file:
        tmp_file.write(audio_data.getvalue())
        tmp_file_path = tmp_file.name

    if st.button("⚡ Process Command", type="primary", use_container_width=True):
        total_start = time.time()

        try:
            # ── Stage 1: Transcription ──
            st.session_state.pipeline_stage = 2
            with st.spinner("🗣️ Transcribing audio with Faster-Whisper..."):
                stt_result = transcribe_audio(tmp_file_path)

            if stt_result.get("error"):
                st.error(f"🎤 Transcription Error: {stt_result['error']}")
                st.session_state.pipeline_stage = 0
                st.stop()

            transcript = stt_result.get("text", "")
            if not transcript.strip():
                st.warning("🔇 No speech detected. Try speaking louder or uploading a clearer audio file.")
                st.session_state.pipeline_stage = 0
                st.stop()

            # Display transcription result
            st.markdown(
                f"""<div class="glass-card">
                <h3>🗣️ Transcription</h3>
                <div class="transcript-text">"{transcript}"</div>
                <div class="meta-chips">
                    <span class="meta-chip">⏱️ {stt_result.get('duration_seconds', 0)}s</span>
                    <span class="meta-chip">🌐 {stt_result.get('language', 'unknown')} · {stt_result.get('language_probability', 0)}%</span>
                    <span class="meta-chip">🧩 {stt_result.get('model_size', 'base')}</span>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

            # ── Stage 2: Intent Classification ──
            st.session_state.pipeline_stage = 3
            with st.spinner("🧠 Analyzing intent with Gemma 4..."):
                intent_result = get_intent_and_params(transcript)

            if intent_result.get("error"):
                st.warning(f"⚠️ LLM Warning: {intent_result['error']}")

            intents_list = intent_result.get("intents", [])

            # Display intent cards
            st.markdown('<div class="glass-card"><h3>🧠 Detected Intents</h3>', unsafe_allow_html=True)

            intent_badges_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:0.5rem 0;">'
            for it in intents_list:
                intent_type = it.get("intent", "general_chat")
                icon = INTENT_ICONS.get(intent_type, "❓")
                label = INTENT_LABELS.get(intent_type, intent_type)
                fname = it.get("filename")
                fname_str = f' → <code style="font-size:0.7rem;background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:4px;">{fname}</code>' if fname else ""
                intent_badges_html += (
                    f'<span class="intent-badge intent-{intent_type}">'
                    f"{icon} {label}{fname_str}</span>"
                )
            intent_badges_html += "</div>"

            st.markdown(intent_badges_html, unsafe_allow_html=True)
            st.markdown(
                f'<div class="meta-chips" style="margin-top:0.5rem;">'
                f'<span class="meta-chip">⏱️ {intent_result.get("duration_seconds", 0)}s</span>'
                f'<span class="meta-chip">🧠 {intent_result.get("model", "unknown")}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

            with st.expander("📋 Raw JSON Payload", expanded=False):
                st.json(intent_result)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Stage 3: Execution ──
            st.session_state.pipeline_stage = 4

            # Separate file-write intents (need approval) from immediate intents
            file_intents = [it for it in intents_list if it.get("intent") in ("create_file", "write_code")]
            immediate_intents = [it for it in intents_list if it.get("intent") not in ("create_file", "write_code")]

            all_results = []

            # Execute immediate intents right away
            if immediate_intents:
                with st.spinner("⚙️ Executing non-file intents..."):
                    for it in immediate_intents:
                        result = execute_tool(it)
                        all_results.append({"intent": it, "result": result})

            # Store immediate results in session state
            st.session_state.current_results = all_results

            # Store file intents in session state for approval (persists across reruns)
            if file_intents:
                st.session_state.pending_approvals = file_intents

            # ── Stage 4: Output ──
            st.session_state.pipeline_stage = 5

            if all_results:
                st.markdown('<div class="glass-card"><h3>✅ Pipeline Results</h3>', unsafe_allow_html=True)

                for r in all_results:
                    intent_info = r["intent"]
                    result = r["result"]
                    intent_type = intent_info.get("intent", "unknown")
                    icon = INTENT_ICONS.get(intent_type, "❓")
                    label = INTENT_LABELS.get(intent_type, intent_type)
                    success = result.get("success", True)
                    css_class = "result-success" if success else "result-error"
                    status_icon = "✅" if success else "❌"
                    message = result.get("message", "No output")

                    st.markdown(
                        f"""<div class="{css_class}">
                        <strong>{status_icon} {icon} {label}</strong><br>
                        <span style="color:var(--text-secondary);line-height:1.6;">{message[:500]}{'…' if len(message) > 500 else ''}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                    # For long responses, show full content in expander
                    if len(message) > 500:
                        with st.expander("📖 Full Response"):
                            st.markdown(message)

                st.markdown("</div>", unsafe_allow_html=True)

            # ── Record to Session History ──
            total_elapsed = round(time.time() - total_start, 2)
            history_entry = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "transcript": transcript,
                "intents": intents_list,
                "results": [
                    {
                        "action": r["result"].get("action", r["intent"].get("intent", "")),
                        "success": r["result"].get("success", True),
                        "message": r["result"].get("message", "")[:200],
                    }
                    for r in all_results
                ],
                "total_seconds": total_elapsed,
            }
            st.session_state.history.append(history_entry)

            # Total timing
            st.markdown(
                f"""<div class="timing-badge">
                Pipeline completed in <strong>{total_elapsed}s</strong>
                </div>""",
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.session_state.pipeline_stage = 0
            st.error(f"💥 Pipeline Error: {e}")
            st.info("💡 **Troubleshooting tips:**\n- Make sure Ollama is running (`ollama serve`)\n- Check that FFmpeg is installed\n- Try a different audio file")

        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

# ─────────────────────────────────────────────────
# 3. APPROVAL PANEL (persisted outside the Process button)
# ─────────────────────────────────────────────────
if st.session_state.pending_approvals:
    st.markdown(
        '<div class="approval-panel"><h3>🛡️ Approval Required</h3>'
        "<p style='color:var(--text-secondary);font-size:0.85rem;'>"
        "The following file operations require your confirmation before executing:</p>",
        unsafe_allow_html=True,
    )

    for idx, it in enumerate(st.session_state.pending_approvals):
        intent_type = it.get("intent", "create_file")
        fname = it.get("filename", "unnamed")
        content = it.get("content", "")
        icon = INTENT_ICONS.get(intent_type, "📄")
        label = INTENT_LABELS.get(intent_type, intent_type)

        st.markdown(
            f"**{icon} {label}** → `{fname}`",
            unsafe_allow_html=True,
        )

        with st.expander(f"📄 Preview content of `{fname}`", expanded=False):
            # Detect language for syntax highlighting
            lang = ""
            if fname:
                if fname.endswith(".py"):
                    lang = "python"
                elif fname.endswith(".js"):
                    lang = "javascript"
                elif fname.endswith(".html"):
                    lang = "html"
                elif fname.endswith(".css"):
                    lang = "css"
                elif fname.endswith(".java"):
                    lang = "java"
                elif fname.endswith(".cpp") or fname.endswith(".c"):
                    lang = "c"
            st.code(content, language=lang if lang else None)

        col_approve, col_reject = st.columns(2)
        with col_approve:
            if st.button("✅ Approve", key=f"approve_{idx}", use_container_width=True):
                result = execute_tool(it)
                if result.get("success"):
                    st.success(f"✅ {result.get('message', 'Done')}")
                else:
                    st.error(f"❌ {result.get('message', 'Failed')}")
                # Remove this intent from pending list
                st.session_state.pending_approvals.pop(idx)
                st.rerun()
        with col_reject:
            if st.button("❌ Reject", key=f"reject_{idx}", use_container_width=True):
                st.info("⏭️ Skipped by user.")
                st.session_state.pending_approvals.pop(idx)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    '<div class="footer-brand">Built with ❤️ · Powered by Ollama & Faster-Whisper · 100% Local</div>',
    unsafe_allow_html=True,
)

# Reset pipeline stage when idle
if audio_data is None and not st.session_state.pending_approvals:
    st.session_state.pipeline_stage = 0
