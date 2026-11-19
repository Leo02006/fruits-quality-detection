import streamlit as st
from PIL import Image, ImageDraw
import tempfile
import time
import os
from pathlib import Path
from io import BytesIO

cv2 = None

# Page configuration
st.set_page_config(
    page_title="Fruits Quality Detector",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Advanced Visual Styles & Keyframe Animations ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Video preview sizing */
    [data-testid="stVideo"] {
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Global Typography & Smoothing */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.01em;
    }

    /* Ambient Cosmic Dark Background Mesh */
    .stApp {
        background: radial-gradient(circle at 12% 15%, rgba(16, 185, 129, 0.12) 0%, transparent 40%),
                    radial-gradient(circle at 88% 18%, rgba(99, 102, 241, 0.14) 0%, transparent 45%),
                    radial-gradient(circle at 50% 88%, rgba(245, 158, 11, 0.08) 0%, transparent 50%),
                    #080c16 !important;
        background-attachment: fixed !important;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(13, 20, 36, 0.95) 0%, rgba(8, 12, 22, 0.98) 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(24px);
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Keyframe Animations */
    @keyframes floatSlow {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-6px) rotate(3deg); }
    }

    @keyframes pulseEmerald {
        0%, 100% { 
            opacity: 1; 
            transform: scale(1);
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.8), 0 0 20px rgba(16, 185, 129, 0.4); 
        }
        50% { 
            opacity: 0.55; 
            transform: scale(0.85);
            box-shadow: 0 0 4px rgba(16, 185, 129, 0.3); 
        }
    }

    @keyframes pulseCrimson {
        0%, 100% { 
            opacity: 1; 
            transform: scale(1);
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.9), 0 0 24px rgba(239, 68, 68, 0.5); 
        }
        50% { 
            opacity: 0.5; 
            transform: scale(0.85);
            box-shadow: 0 0 5px rgba(239, 68, 68, 0.3); 
        }
    }

    @keyframes cardEntrance {
        from { opacity: 0; transform: translateY(14px) scale(0.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    @keyframes shimmerBar {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @keyframes borderGlow {
        0%, 100% { border-color: rgba(16, 185, 129, 0.3); }
        50% { border-color: rgba(99, 102, 241, 0.5); }
    }

    /* Hero Banner */
    .hero-container {
        position: relative;
        overflow: hidden;
        border-radius: 20px;
        padding: 26px 30px;
        margin-bottom: 28px;
        background: linear-gradient(135deg, rgba(19, 28, 49, 0.75) 0%, rgba(13, 20, 36, 0.88) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        animation: cardEntrance 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10b981 0%, #6366f1 50%, #f59e0b 100%);
        box-shadow: 0 0 16px rgba(16, 185, 129, 0.6);
    }

    .hero-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        flex-wrap: wrap;
    }

    .hero-left {
        display: flex;
        align-items: center;
        gap: 18px;
    }

    .hero-icon-bubble {
        width: 58px;
        height: 58px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
        animation: floatSlow 4s ease-in-out infinite;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #ffffff 0%, #d1fae5 35%, #a5b4fc 70%, #fde68a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 0.92rem;
        color: #94a3b8;
        margin: 6px 0 0 0;
        font-weight: 400;
    }

    .hero-badges-row {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }

    .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #cbd5e1;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
    }

    .hero-tag:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        transform: translateY(-1px);
    }

    .status-badge-online {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        color: #34d399;
        letter-spacing: 0.03em;
        box-shadow: 0 0 16px rgba(16, 185, 129, 0.2);
    }

    .pulse-dot-online {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        animation: pulseEmerald 1.8s infinite ease-in-out;
    }

    .pulse-dot-red {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background-color: #ef4444;
        animation: pulseCrimson 1.3s infinite ease-in-out;
    }

    /* Metric Grid & Luminous Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 14px;
        margin: 22px 0;
        animation: cardEntrance 0.4s ease forwards;
    }

    .minimal-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(145deg, rgba(21, 30, 52, 0.75) 0%, rgba(13, 20, 36, 0.88) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 16px 14px 16px;
        text-align: left;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
    }

    .minimal-card:hover {
        transform: translateY(-4px) scale(1.02);
        border-color: rgba(255, 255, 255, 0.22);
        background: linear-gradient(145deg, rgba(28, 40, 68, 0.85) 0%, rgba(18, 27, 48, 0.95) 100%);
    }

    /* Top Accent Line on Cards */
    .minimal-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }

    .card-total::before { background: linear-gradient(90deg, #6366f1, #a855f7); }
    .card-total:hover { box-shadow: 0 12px 28px -4px rgba(99, 102, 241, 0.4); }

    .card-ripe::before { background: linear-gradient(90deg, #10b981, #34d399); }
    .card-ripe:hover { box-shadow: 0 12px 28px -4px rgba(16, 185, 129, 0.4); }

    .card-unripe::before { background: linear-gradient(90deg, ##32f50b, #32f50b); }
    .card-unripe:hover { box-shadow: 0 12px 28px -4px rgba(245, 158, 11, 0.4); }

    .card-overripe::before { background: linear-gradient(90deg, #f97316, #fb923c); }
    .card-overripe:hover { box-shadow: 0 12px 28px -4px rgba(249, 115, 22, 0.4); }

    .card-rotten::before { background: linear-gradient(90deg, #ef4444, #f87171); }
    .card-rotten:hover { box-shadow: 0 12px 28px -4px rgba(239, 68, 68, 0.4); }

    .card-speed::before { background: linear-gradient(90deg, #06b6d4, #38bdf8); }
    .card-speed:hover { box-shadow: 0 12px 28px -4px rgba(6, 182, 212, 0.4); }

    .card-header-flex {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
    }

    .card-indicator {
        width: 22px;
        height: 3px;
        border-radius: 9999px;
    }

    .card-icon-pill {
        font-size: 1.05rem;
        line-height: 1;
    }

    .ind-total { background: #818cf8; box-shadow: 0 0 10px rgba(129, 140, 248, 0.7); }
    .ind-ripe { background: #34d399; box-shadow: 0 0 10px rgba(52, 211, 153, 0.7); }
    .ind-unripe { background: #fbbf24; box-shadow: 0 0 10px rgba(251, 191, 36, 0.7); }
    .ind-overripe { background: #fb923c; box-shadow: 0 0 10px rgba(251, 146, 60, 0.7); }
    .ind-rotten { background: #f87171; box-shadow: 0 0 10px rgba(248, 113, 113, 0.7); }
    .ind-speed { background: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.7); }

    .minimal-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 4px;
    }

    .minimal-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.1;
    }

    /* Ripeness Visual Distribution Bar */
    .dist-box {
        background: linear-gradient(135deg, rgba(19, 28, 49, 0.6) 0%, rgba(13, 20, 36, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 16px 0 24px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }

    .dist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 8px;
    }

    .dist-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .dist-grade {
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    .grade-prime {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
    }

    .grade-standard {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
    }

    .grade-action {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #f87171;
    }

    .dist-bar-track {
        height: 14px;
        border-radius: 9999px;
        background: rgba(255, 255, 255, 0.06);
        overflow: hidden;
        display: flex;
        gap: 2px;
        margin-bottom: 12px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4);
    }

    .dist-seg {
        height: 100%;
        transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .seg-ripe { background: linear-gradient(90deg, #10b981, #34d399); }
    .seg-unripe { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .seg-overripe { background: linear-gradient(90deg, #f97316, #fb923c); }
    .seg-rotten { background: linear-gradient(90deg, #ef4444, #f87171); }

    .dist-legend {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        font-size: 0.78rem;
        color: #94a3b8;
    }

    .dist-leg-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .leg-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .dot-ripe { background: #10b981; box-shadow: 0 0 6px #10b981; }
    .dot-unripe { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
    .dot-overripe { background: #f97316; box-shadow: 0 0 6px #f97316; }
    .dot-rotten { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

    /* Glass Framing for Images */
    .image-preview-panel {
        background: linear-gradient(145deg, rgba(19, 28, 49, 0.6) 0%, rgba(13, 20, 36, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }

    .image-preview-panel:hover {
        border-color: rgba(255, 255, 255, 0.18);
        transform: translateY(-2px);
    }

    .panel-header-badge {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        padding: 4px 6px;
    }

    .panel-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
    }

    .panel-chip-input {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .panel-chip-ai {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        background: rgba(16, 185, 129, 0.15);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: rgba(15, 23, 42, 0.75) !important;
        padding: 8px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
        margin-bottom: 24px !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 22px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: #94a3b8 !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #f1f5f9 !important;
        background: rgba(255, 255, 255, 0.06) !important;
        transform: translateY(-1px) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(99, 102, 241, 0.22) 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: 1px solid rgba(52, 211, 153, 0.45) !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }

    /* Buttons with Rich Polish */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 10px 24px !important;
        letter-spacing: 0.02em !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        background: rgba(255, 255, 255, 0.09) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3) !important;
        color: #ffffff !important;
    }

    div.stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 45%, #0891b2 100%) !important;
        border: 1px solid rgba(52, 211, 153, 0.5) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 26px rgba(16, 185, 129, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
        background: linear-gradient(135deg, #34d399 0%, #10b981 45%, #06b6d4 100%) !important;
    }

    div.stDownloadButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 10px 24px !important;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%) !important;
        border: 1px solid rgba(129, 140, 248, 0.4) !important;
        color: #c7d2fe !important;
        transition: all 0.25s ease !important;
    }

    div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.35) 0%, rgba(139, 92, 246, 0.35) 100%) !important;
        border-color: rgba(129, 140, 248, 0.7) !important;
        color: #ffffff !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
    }

    /* Class Badges with Fruit Colors in Sidebar */
    .class-chip-ripe {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #34d399;
        margin: 3px 2px;
        transition: all 0.2s ease;
    }

    .class-chip-unripe {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #fbbf24;
        margin: 3px 2px;
        transition: all 0.2s ease;
    }

    .class-chip-overripe {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(249, 115, 22, 0.12);
        border: 1px solid rgba(249, 115, 22, 0.35);
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #fb923c;
        margin: 3px 2px;
        transition: all 0.2s ease;
    }

    .class-chip-rotten {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #f87171;
        margin: 3px 2px;
        transition: all 0.2s ease;
    }

    .class-chip-default {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #a5b4fc;
        margin: 3px 2px;
        transition: all 0.2s ease;
    }

    .class-chip-ripe:hover, .class-chip-unripe:hover, .class-chip-overripe:hover, .class-chip-rotten:hover, .class-chip-default:hover {
        transform: translateY(-1px) scale(1.05);
    }

    /* Evaluation Curve Frame */
    .eval-curve-card {
        background: linear-gradient(145deg, rgba(21, 30, 52, 0.7) 0%, rgba(13, 20, 36, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .eval-curve-card:hover {
        transform: translateY(-3px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
    }

    .eval-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
        padding: 0 4px;
    }

    .eval-tag {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        background: rgba(16, 185, 129, 0.14);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .eval-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #e2e8f0;
    }

    /* Progress bar custom styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #10b981 0%, #06b6d4 100%) !important;
        border-radius: 9999px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Model Discovery & Loading ----------------
def find_default_model_path():
    """Locate best.pt relative to the app directory or workspace."""
    app_dir = Path(__file__).resolve().parent
    candidates = [
        app_dir.parent / "models" / "best.pt",
        Path("models/best.pt").resolve(),
        Path("fruit_ripeness_detection/models/best.pt").resolve(),
        app_dir / "models" / "best.pt",
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return str(p)
    return None

@st.cache_resource
def load_yolo_model(model_path: str):
    global cv2
    import cv2 as cv2_module
    cv2 = cv2_module
    from ultralytics import YOLO
    return YOLO(model_path)

default_weights = find_default_model_path()
model = None

# Helper to classify chips with colors
def render_class_chip(name: str):
    low = name.lower()
    if "ripe" in low and "over" not in low and "un" not in low:
        return f'<span class="class-chip-ripe">🍏 {name}</span>'
    elif "unripe" in low:
        return f'<span class="class-chip-unripe">🍋 {name}</span>'
    elif "overripe" in low:
        return f'<span class="class-chip-overripe">🍑 {name}</span>'
    elif "rotten" in low:
        return f'<span class="class-chip-rotten">🥀 {name}</span>'
    else:
        return f'<span class="class-chip-default">🏷️ {name}</span>'

# ---------------- Beautiful Glassmorphic Sidebar ----------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px; padding: 6px 0;">
            <div style="font-size: 1.8rem; filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4)); animation: floatSlow 3.5s ease-in-out infinite;">🍎</div>
            <div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Fruits Quality Detector
                </div>
                <div style="font-size: 0.74rem; font-weight: 600; color: #10b981; letter-spacing: 0.05em; text-transform: uppercase;">
                    Deep Learning Fruits Quality Detector
                </div>
            </div>
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 18px; line-height: 1.4;">
            Automated multi-stage fruits detection powered by YOLOv11.
        </div>
    """, unsafe_allow_html=True)

    # Optional model upload override
    model_upload = st.file_uploader(
        "Upload Custom Weights (.pt)",
        type=["pt"],
        help="Upload custom YOLO weights if you want to override the default model.",
    )

    if model_upload is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pt") as temp:
                temp.write(model_upload.getvalue())
                temp.flush()
                saved_model_path = temp.name
            model = load_yolo_model(saved_model_path)
            st.markdown("""
                <div style="padding: 12px 16px; border-radius: 8px; background: rgba(16, 185, 129, 0.1); color: #34d399; font-weight: 500;">
                    ✅ Custom model weights loaded successfully!
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
                <div style="padding: 12px 16px; border-radius: 8px; background: rgba(239, 68, 68, 0.1); color: #ef4444; font-weight: 500;">
                    ❌ Failed to load custom model weights.<br>
                    <span style="font-size: 0.85rem; color: #f87171;">{str(e)}</span>
                </div>
            """, unsafe_allow_html=True)

    # Model selection radio
    with st.expander("Model Settings", True):
        model_source = st.radio(
            "Select Model Source",
            options=["Default", "Custom Upload"],
            index=0,
            horizontal=True,
            help="Choose the source of the YOLO model weights.",
        )

        if model_source == "Default":
            st.info("Using the built-in default model weights (`best.pt`).", icon="ℹ️")
            model = load_yolo_model(default_weights)
        else:
            if model_upload is not None:
                st.success("Using the uploaded custom model weights.", icon="✅")
                model = load_yolo_model(saved_model_path)
            else:
                st.warning("No custom model uploaded. Please upload a `.pt` file to use custom weights.", icon="⚠️")

    # Inference settings
    with st.expander("Inference Settings", True):
        conf_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.01, 
            help="Minimum confidence level for detections to be considered valid.")
        iou_threshold = st.slider("IOU Threshold", 0.0, 1.0, 0.45, 0.01, 
            help="Intersection over Union threshold for filtering detections.")

    # About section
    with st.expander("About This App", True):
        st.markdown("""
            ### 🍏 Detecting Fruits Ripeness with YOLOv11
            This app uses a custom YOLOv11 model to detect and evaluate the ripeness of fruits in images.
            - **Ripe**: 🍏
            - **Unripe**: 🍋
            - **Overripe**: 🍑
            - **Rotten**: 🥀
            
            ---
            
            Developed with ❤️ by [Your Name](https://yourwebsite.com) | Source code on [GitHub](https://github.com/yourrepo)
        """)

# ---------------- Main Content Area ----------------
st.markdown("""
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-left">
                <div class="hero-icon-bubble" style="filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.4));">
                    📸
                </div>
                <div>
                    <h1 class="hero-title">Fruits Quality Detector</h1>
                    <p class="hero-subtitle">Deep Learning Fruits Quality Detector</p>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# File uploader for image input
image_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed",
)

# Inference on image upload
if image_file is not None and model is not None:
    # Read and display the image
    image = Image.open(image_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True, clamp=True, channels="RGB")

    # Inference
    with st.spinner("Running inference..."):
        # Convert image to byte array
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()

        # Perform detection
        results = model(
            img_byte_arr,
            conf=conf_threshold,
            iou=iou_threshold,
            agnostic_nms=True,
        )

    # Parse results
    detections = results[0].boxes
    bboxes = detections.xyxy.cpu().numpy()
    scores = detections.conf.cpu().numpy()
    classes = detections.cls.cpu().numpy().astype(int)

    # Draw results on image
    draw = ImageDraw.Draw(image)
    for bbox, score, cls in zip(bboxes, scores, classes):
        x1, y1, x2, y2 = map(int, bbox)
        label = f"{model.names[cls]}: {score:.2f}"
        draw.rectangle([x1, y1, x2, y2], outline="green", width=3)
        draw.text((x1, y1), label, fill="white")

    # Display result image
    st.image(image, caption="Detection Results", use_column_width=True, clamp=True, channels="RGB")

    # Metrics and details
    st.markdown("---")
    st.subheader("Detection Metrics")
    for cls in range(len(model.names)):
        cls_detections = sum(classes == cls)
        cls_score = scores[classes == cls].mean() if cls_detections > 0 else 0
        st.metric(
            label=model.names[cls],
            value=f"{cls_detections} detections",
            delta=f"Avg. confidence: {cls_score:.2f}",
            delta_color="normal" if cls_score > 0.5 else "inverse",
        )

    # Ripeness distribution
    st.markdown("---")
    st.subheader("Ripeness Distribution")
    ripe_count = sum(classes == 0)
    unripe_count = sum(classes == 1)
    overripe_count = sum(classes == 2)
    rotten_count = sum(classes == 3)
    total_count = len(classes)

    # Bar chart
    st.bar_chart({
        "Ripe": ripe_count,
        "Unripe": unripe_count,
        "Overripe": overripe_count,
        "Rotten": rotten_count,
    })

    # Detailed view
    st.markdown("---")
    st.subheader("Detailed Detections")
    for i, (bbox, score, cls) in enumerate(zip(bboxes, scores, classes)):
        x1, y1, x2, y2 = map(int, bbox)
        label = f"{model.names[cls]}: {score:.2f}"
        st.markdown(f"**Detection {i+1}:** {label}")
        st.image(image.crop((x1, y1, x2, y2)), use_column_width=True, caption=label)

        # Class-specific details
        if cls == 0:
            st.write("This fruit is ripe and ready to eat!")
        elif cls == 1:
            st.write("This fruit is unripe. It may be too firm and lacking sweetness.")
        elif cls == 2:
            st.write("This fruit is overripe. It may be too soft and starting to ferment.")
        elif cls == 3:
            st.write("This fruit is rotten. It is no longer edible.")
        st.markdown("---")

    # Download button for results
    with st.expander("Download Results", True):
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="JPEG")
        st.download_button(
            "Download Result Image",
            img_byte_arr.getvalue(),
            file_name="detection_results.jpg",
            mime="image/jpeg",
        )

        # CSV download of metrics
        import pandas as pd
        metrics_df = pd.DataFrame({
            "Class": [model.names[cls] for cls in range(len(model.names))],
            "Detections": [sum(classes == cls) for cls in range(len(model.names))],
            "Avg. Confidence": [scores[classes == cls].mean() if sum(classes == cls) > 0 else 0 for cls in range(len(model.names))],
        })
        csv = metrics_df.to_csv(index=False).encode()
        st.download_button(
            "Download Metrics CSV",
            csv,
            file_name="detection_metrics.csv",
            mime="text/csv",
        )

        # JSON download of results
        import json
        results_json = [{"class": int(cls), "score": float(score), "bbox": bbox.tolist()} for bbox, score, cls in zip(bboxes, scores, classes)]
        json_data = json.dumps(results_json, indent=4)
        st.download_button(
            "Download Results JSON",
            json_data,
            file_name="detection_results.json",
            mime="application/json",
        )

# ---------------- Live Camera Feed Section ----------------
st.markdown("""
    <div style="position: relative; width: 100%; overflow: hidden; border-radius: 16px; margin-bottom: 28px;">
        <div class="image-preview-panel" style="padding: 0; border: none;">
            <video id="liveCamera" width="100%" style="border-radius: 16px;" autoplay></video>
        </div>
        <div style="position: absolute; top: 12px; right: 12px; display: flex; gap: 8px;">
            <button id="captureButton" style="padding: 8px 16px; border-radius: 8px; background: rgba(16, 185, 129, 0.9); color: #fff; border: none; cursor: pointer;">
                📸 Capture
            </button>
            <button id="toggleCamButton" style="padding: 8px 16px; border-radius: 8px; background: rgba(239, 68, 68, 0.9); color: #fff; border: none; cursor: pointer;">
                ❌ Stop Camera
            </button>
        </div>
    </div>
""", unsafe_allow_html=True)

# JavaScript for live camera feed
st.markdown("""
    <script>
        const video = document.getElementById('liveCamera');
        const captureButton = document.getElementById('captureButton');
        const toggleCamButton = document.getElementById('toggleCamButton');
        let mediaRecorder;
        let isCameraActive = true;

        async function startCamera() {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            mediaRecorder = new MediaRecorder(stream);
        }

        function stopCamera() {
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isCameraActive = false;
        }

        captureButton.addEventListener('click', () => {
            if (!isCameraActive) return;
            mediaRecorder.stop();
            mediaRecorder.ondataavailable = async (event) => {
                const imgBlob = event.data;
                const imgUrl = URL.createObjectURL(imgBlob);
                const response = await fetch(imgUrl);
                const imageBlob = await response.blob();
                const file = new File([imageBlob], "captured_image.jpg", { type: "image/jpeg" });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                const fileList = dataTransfer.files;

                // Update the file input element
                const fileInput = document.querySelector('input[type="file"]');
                const dataTransferObj = new DataTransfer();
                dataTransferObj.items.add(file);
                fileInput.files = dataTransferObj.files;

                // Trigger change event
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            };
        });

        toggleCamButton.addEventListener('click', () => {
            if (isCameraActive) {
                stopCamera();
                toggleCamButton.innerText = '▶️ Start Camera';
            } else {
                startCamera();
                toggleCamButton.innerText = '❌ Stop Camera';
            }
        });

        startCamera();
    </script>
""", unsafe_allow_html=True)

# Inference on live camera capture
if st.button("Run Inference on Live Capture"):
    if model is not None:
        # Get the latest captured image from the file input
        file_input = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if file_input is not None:
            # Read and display the image
            image = Image.open(file_input).convert("RGB")
            st.image(image, caption="Captured Image", use_column_width=True, clamp=True, channels="RGB")

            # Inference
            with st.spinner("Running inference on live capture..."):
                # Convert image to byte array
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format="JPEG")
                img_byte_arr = img_byte_arr.getvalue()

                # Perform detection
                results = model(
                    img_byte_arr,
                    conf=conf_threshold,
                    iou=iou_threshold,
                    agnostic_nms=True,
                )

            # Parse results
            detections = results[0].boxes
            bboxes = detections.xyxy.cpu().numpy()
            scores = detections.conf.cpu().numpy()
            classes = detections.cls.cpu().numpy().astype(int)

            # Draw results on image
            draw = ImageDraw.Draw(image)
            for bbox, score, cls in zip(bboxes, scores, classes):
                x1, y1, x2, y2 = map(int, bbox)
                label = f"{model.names[cls]}: {score:.2f}"
                draw.rectangle([x1, y1, x2, y2], outline="green", width=3)
                draw.text((x1, y1), label, fill="white")

            # Display result image
            st.image(image, caption="Detection Results", use_column_width=True, clamp=True, channels="RGB")

            # Metrics and details
            st.markdown("---")
            st.subheader("Detection Metrics")
            for cls in range(len(model.names)):
                cls_detections = sum(classes == cls)
                cls_score = scores[classes == cls].mean() if cls_detections > 0 else 0
                st.metric(
                    label=model.names[cls],
                    value=f"{cls_detections} detections",
                    delta=f"Avg. confidence: {cls_score:.2f}",
                    delta_color="normal" if cls_score > 0.5 else "inverse",
                )

            # Ripeness distribution
            st.markdown("---")
            st.subheader("Ripeness Distribution")
            ripe_count = sum(classes == 0)
            unripe_count = sum(classes == 1)
            overripe_count = sum(classes == 2)
            rotten_count = sum(classes == 3)
            total_count = len(classes);

            # Bar chart
            st.bar_chart({
                "Ripe": ripe_count,
                "Unripe": unripe_count,
                "Overripe": overripe_count,
                "Rotten": rotten_count,
            })

            # Detailed view
            st.markdown("---")
            st.subheader("Detailed Detections")
            for i, (bbox, score, cls) in enumerate(zip(bboxes, scores, classes)):
                x1, y1, x2, y2 = map(int, bbox)
                label = f"{model.names[cls]}: {score:.2f}"
                st.markdown(f"**Detection {i+1}:** {label}")
                st.image(image.crop((x1, y1, x2, y2)), use_column_width=True, caption=label)

                # Class-specific details
                if cls == 0:
                    st.write("This fruit is ripe and ready to eat!")
                elif cls == 1:
                    st.write("This fruit is unripe. It may be too firm and lacking sweetness.")
                elif cls == 2:
                    st.write("This fruit is overripe. It may be too soft and starting to ferment.")
                elif cls == 3:
                    st.write("This fruit is rotten. It is no longer edible.")
                st.markdown("---")

            # Download button for results
            with st.expander("Download Results", True):
                img_byte_arr = BytesIO();
                image.save(img_byte_arr, format="JPEG")
                st.download_button(
                    "Download Result Image",
                    img_byte_arr.getvalue(),
                    file_name="detection_results.jpg",
                    mime="image/jpeg",
                )

                # CSV download of metrics
                import pandas as pd
                metrics_df = pd.DataFrame({
                    "Class": [model.names[cls] for cls in range(len(model.names))],
                    "Detections": [sum(classes == cls) for cls in range(len(model.names))],
                    "Avg. Confidence": [scores[classes == cls].mean() if sum(classes == cls) > 0 else 0 for cls in range(len(model.names))],
                })
                csv = metrics_df.to_csv(index=False).encode()
                st.download_button(
                    "Download Metrics CSV",
                    csv,
                    file_name="detection_metrics.csv",
                    mime="text/csv",
                )

                # JSON download of results
                import json
                results_json = [{"class": int(cls), "score": float(score), "bbox": bbox.tolist()} for bbox, score, cls in zip(bboxes, scores, classes)]
                json_data = json.dumps(results_json, indent=4)
                st.download_button(
                    "Download Results JSON",
                    json_data,
                    file_name="detection_results.json",
                    mime="application/json",
                )
    else:
        st.warning("Please upload an image from the camera capture to run inference.", icon="⚠️")

# ---------------- Footer ----------------
st.markdown("""
    <div style="text-align: center; padding: 12px 0; color: #94a3b8; font-size: 0.8rem;">
        &copy; 2023 Fruits Quality Detector. All rights reserved.
    </div>
""", unsafe_allow_html=True)
