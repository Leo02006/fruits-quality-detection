import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import tempfile
import time
import os
import cv2
from pathlib import Path
from io import BytesIO

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
            Automated multi-stage fruits detection powered by YOLOv8.
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
                <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 10px; margin-bottom: 14px;">
                    <span style="font-size: 0.9rem;">✨</span>
                    <span style="font-size: 0.82rem; font-weight: 700; color: #a5b4fc;">Custom Weights Active</span>
                </div>
            """, unsafe_allow_html=True)
        except Exception as exc:
            st.error(f"Error loading model: {exc}")
    elif default_weights:
        try:
            model = load_yolo_model(default_weights)
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; margin-bottom: 14px;">
                    <span class="pulse-dot-online"></span>
                    <span style="font-size: 0.82rem; font-weight: 700; color: #34d399;">models/best.pt Active</span>
                </div>
            """, unsafe_allow_html=True)
        except Exception as exc:
            st.error(f"Failed to load default weights: {exc}")
    else:
        st.warning("No model loaded.")

    if model is not None:
        class_names = list(model.names.values()) if hasattr(model, "names") else []
        st.caption("Active Ripeness Classes")
        class_html = "".join([render_class_chip(c) for c in class_names])
        st.markdown(f'<div style="margin-bottom: 16px;">{class_html}</div>', unsafe_allow_html=True)

    st.markdown("""
        <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent); margin: 16px 0;"></div>
    """, unsafe_allow_html=True)
    st.caption("Inference Threshold Controls")
    confidence = st.slider("Confidence Cutoff", min_value=0.05, max_value=1.0, value=0.35, step=0.05)
    iou_threshold = st.slider("IoU (NMS Threshold)", min_value=0.05, max_value=1.0, value=0.45, step=0.05)

# ---------------- Stunning Glowing Hero Header Banner ----------------
st.markdown("""
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-left">
                <div class="hero-icon-bubble">🍎</div>
                <div>
                    <h1 class="hero-title">Fruits Quality Detection</h1>
                    <p class="hero-subtitle">High-precision YOLOv8 Computer Vision & Fruits Quality Detector.</p>
                </div>
            </div>
            <div class="hero-badges-row">
                <div class="hero-tag">⚡ YOLOv8 Neural Model</div>
                <div class="hero-tag">🎯 4-Stage Classification</div>
                <div class="status-badge-online">
                    <span class="pulse-dot-online"></span> Engine Online
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------- Main Navigation Tabs ----------------
image_tab, video_tab, eda_tab = st.tabs([
    "📸 Image Quality Analysis",
    "🎥 Live Video Stream",
    "📊 Model Performance & Curves"
])

# ---------------- Tab 1: Image Detection ----------------
with image_tab:
    input_source = st.radio(
        "Input Source",
        ["📁 Upload Image", "📸 Camera Capture"],
        horizontal=True,
        label_visibility="collapsed"
    )

    selected_image = None

    if input_source == "📁 Upload Image":
        uploaded_file = st.file_uploader(
            "Select an image file (PNG, JPG, JPEG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            key="main_image_uploader"
        )
        if uploaded_file:
            selected_image = Image.open(uploaded_file).convert("RGB")
    else:
        cam_file = st.camera_input("Capture frame from camera")
        if cam_file:
            selected_image = Image.open(cam_file).convert("RGB")

    if selected_image is not None:
        col_img_in, col_img_out = st.columns(2)
        with col_img_in:
            st.markdown("""
                <div class="panel-header-badge">
                    <span class="panel-title">Original Sample</span>
                    <span class="panel-chip-input">Input Frame</span>
                </div>
            """, unsafe_allow_html=True)
            st.image(selected_image, use_container_width=True)

        run_det = st.button("Detect Quality", type="primary", disabled=(model is None))

        if model is None:
            st.error("Model weights are not loaded. Check the sidebar.")
        elif run_det:
            with st.spinner("Processing image with YOLOv8 neural network..."):
                t0 = time.perf_counter()
                results = model.predict(
                    source=selected_image,
                    imgsz=640,
                    conf=confidence,
                    iou=iou_threshold,
                    verbose=False
                )[0]
                latency = time.perf_counter() - t0

            # Convert BGR to RGB
            annotated_bgr = results.plot()
            annotated_rgb = annotated_bgr[:, :, ::-1]

            with col_img_out:
                st.markdown("""
                    <div class="panel-header-badge">
                        <span class="panel-title">Quality Inspection</span>
                        <span class="panel-chip-ai">YOLOv8 Output</span>
                    </div>
                """, unsafe_allow_html=True)
                st.image(annotated_rgb, use_container_width=True)

            boxes = results.boxes
            total_count = len(boxes) if boxes is not None else 0

            class_tallies = {"overripe": 0, "ripe": 0, "rotten": 0, "unripe": 0}
            detection_data = []

            if total_count > 0:
                for b in boxes:
                    cls_id = int(b.cls[0].item())
                    cls_name = model.names.get(cls_id, f"Class {cls_id}") if isinstance(model.names, dict) else model.names[cls_id]
                    score = float(b.conf[0].item())
                    coords = [round(float(v), 1) for v in b.xyxy[0].tolist()]

                    low_name = str(cls_name).lower()
                    if low_name in class_tallies:
                        class_tallies[low_name] += 1
                    else:
                        class_tallies[low_name] = class_tallies.get(low_name, 0) + 1

                    detection_data.append({
                        "Class": str(cls_name).title(),
                        "Confidence": f"{score:.1%}",
                        "Bounding Box [x1, y1, x2, y2]": str(coords)
                    })

            # Luminous Telemetry KPI Cards
            st.markdown(f"""
                <div class="metric-grid">
                    <div class="minimal-card card-total">
                        <div class="card-header-flex">
                            <div class="card-indicator ind-total"></div>
                            <span class="card-icon-pill">📦</span>
                        </div>
                        <div class="minimal-label">Total Detections</div>
                        <div class="minimal-value">{total_count}</div>
                    </div>
                    <div class="minimal-card card-ripe">
                        <div class="card-header-flex">
                            <div class="card-indicator ind-ripe"></div>
                            <span class="card-icon-pill">🍏</span>
                        </div>
                        <div class="minimal-label">Ripe</div>
                        <div class="minimal-value">{class_tallies.get("ripe", 0)}</div>
                    </div>
                    <div class="minimal-card card-unripe">
                        <div class="card-header-flex">
                            <div class="card-indicator ind-unripe"></div>
                            <span class="card-icon-pill">🍋</span>
                        </div>
                        <div class="minimal-label">Unripe</div>
                        <div class="minimal-value">{class_tallies.get("unripe", 0)}</div>
                    </div>
                    <div class="minimal-card card-overripe">
                        <div class="card-header-flex">
                            <div class="card-indicator ind-overripe"></div>
                            <span class="card-icon-pill">🍑</span>
                        </div>
                        <div class="minimal-label">Overripe</div>
                        <div class="minimal-value">{class_tallies.get("overripe", 0)}</div>
                    </div>
                    <div class="minimal-card card-rotten">
                        <div class="card-header-flex">
                            <div class="card-indicator ind-rotten"></div>
                            <span class="card-icon-pill">🥀</span>
                        </div>
                        <div class="minimal-label">Rotten</div>
                        <div class="minimal-value">{class_tallies.get("rotten", 0)}</div>
                    </div>
                    <div class="minimal-card card-speed">
                        <div class="card-header-flex">
                            <div class="card-indicator ind-speed"></div>
                            <span class="card-icon-pill">⚡</span>
                        </div>
                        <div class="minimal-label">Latency</div>
                        <div class="minimal-value">{latency * 1000:.0f}<span style="font-size: 0.95rem; color: #94a3b8; font-weight: 500;"> ms</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Ripeness Health & Distribution Bar
            if total_count > 0:
                ripe_c = class_tallies.get("ripe", 0)
                unripe_c = class_tallies.get("unripe", 0)
                overripe_c = class_tallies.get("overripe", 0)
                rotten_c = class_tallies.get("rotten", 0)

                ripe_pct = (ripe_c / total_count) * 100
                unripe_pct = (unripe_c / total_count) * 100
                overripe_pct = (overripe_c / total_count) * 100
                rotten_pct = (rotten_c / total_count) * 100

                fresh_pct = ripe_pct + unripe_pct
                if fresh_pct >= 80:
                    grade_cls = "grade-prime"
                    grade_text = "✨ Grade A • Prime Fresh Produce"
                elif fresh_pct >= 50:
                    grade_cls = "grade-standard"
                    grade_text = "⚠️ Grade B • Consume / Process Promptly"
                else:
                    grade_cls = "grade-action"
                    grade_text = "🚨 Grade C • Significant Decay Detected"

                st.markdown(f"""
                    <div class="dist-box">
                        <div class="dist-header">
                            <div class="dist-title">
                                <span>📊 Batch Ripeness Composition</span>
                            </div>
                            <span class="dist-grade {grade_cls}">{grade_text}</span>
                        </div>
                        <div class="dist-bar-track">
                            <div class="dist-seg seg-ripe" style="width: {ripe_pct}%;" title="Ripe: {ripe_pct:.1f}%"></div>
                            <div class="dist-seg seg-unripe" style="width: {unripe_pct}%;" title="Unripe: {unripe_pct:.1f}%"></div>
                            <div class="dist-seg seg-overripe" style="width: {overripe_pct}%;" title="Overripe: {overripe_pct:.1f}%"></div>
                            <div class="dist-seg seg-rotten" style="width: {rotten_pct}%;" title="Rotten: {rotten_pct:.1f}%"></div>
                        </div>
                        <div class="dist-legend">
                            <div class="dist-leg-item"><span class="leg-dot dot-ripe"></span> Ripe ({ripe_pct:.0f}%)</div>
                            <div class="dist-leg-item"><span class="leg-dot dot-unripe"></span> Unripe ({unripe_pct:.0f}%)</div>
                            <div class="dist-leg-item"><span class="leg-dot dot-overripe"></span> Overripe ({overripe_pct:.0f}%)</div>
                            <div class="dist-leg-item"><span class="leg-dot dot-rotten"></span> Rotten ({rotten_pct:.0f}%)</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            if detection_data:
                st.caption("📋 Detailed Fruit Detections")
                st.dataframe(detection_data, use_container_width=True, hide_index=True)
            else:
                st.info("No fruits detected above confidence threshold.")

            # Download annotated image
            out_img = Image.fromarray(annotated_rgb)
            buf = BytesIO()
            out_img.save(buf, format="PNG")
            st.download_button(
                label="📥 Download Annotated Image",
                data=buf.getvalue(),
                file_name="ripeness_detection_output.png",
                mime="image/png"
            )
    else:
        st.markdown("""
            <div style="text-align: center; padding: 40px 20px; background: rgba(15, 23, 42, 0.45); border: 1px dashed rgba(255, 255, 255, 0.12); border-radius: 16px; margin-top: 10px;">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">📷</div>
                <div style="font-size: 1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 4px;">Ready for Inspection</div>
                <div style="font-size: 0.85rem; color: #94a3b8;">Upload an image or capture from camera to view real-time ripeness detection.</div>
            </div>
        """, unsafe_allow_html=True)

# ---------------- Tab 2: Video Detection ----------------
with video_tab:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin:14px 0 18px 0; padding:10px 16px;
                    background:rgba(16,185,129,0.10); border:1px solid rgba(16,185,129,0.28);
                    border-radius:12px; width:fit-content;">
            <span class="pulse-dot-online"></span>
            <span style="font-size:0.82rem; font-weight:700; color:#34d399; letter-spacing:0.04em;">
                VIDEO UPLOAD • YOLOv8 DETECTION
            </span>
        </div>
    """, unsafe_allow_html=True)

    st.caption(
        "Upload a video and YOLOv8 will analyze it frame-by-frame, "
        "draw bounding boxes, and generate a downloadable detection video."
    )

    if model is None:
        st.error("Model is not loaded. Please verify sidebar weights.")
    else:
        vid_file = st.file_uploader(
            "Upload video file (MP4, AVI, MOV, MKV)",
            type=["mp4", "avi", "mov", "mkv"],
            key="video_detection_uploader"
        )

        if vid_file is not None:
            st.video(vid_file)

            video_conf = st.slider(
                "Video Detection Confidence",
                min_value=0.10,
                max_value=0.90,
                value=float(confidence),
                step=0.05,
                key="video_confidence"
            )

            video_iou = st.slider(
                "Video IoU (NMS Threshold)",
                min_value=0.05,
                max_value=1.0,
                value=float(iou_threshold),
                step=0.05,
                key="video_iou"
            )

            process_video = st.button(
                "🚀 Process Video & Detect Ripeness",
                type="primary",
                key="process_video_button"
            )

            if process_video:
                suffix = Path(vid_file.name).suffix.lower() or ".mp4"

                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
                    tfile.write(vid_file.getbuffer())
                    video_path = tfile.name

                output_path = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp4"
                ).name

                vcap = cv2.VideoCapture(video_path)

                if not vcap.isOpened():
                    st.error("Could not open the uploaded video.")
                else:
                    total_frames = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
                    fps_orig = vcap.get(cv2.CAP_PROP_FPS)
                    fps_orig = fps_orig if fps_orig and fps_orig > 0 else 25.0

                    width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    # MP4 output. If H.264 is unavailable in the environment,
                    # the fallback codec below is attempted.
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    writer = cv2.VideoWriter(
                        output_path, fourcc, fps_orig, (width, height)
                    )

                    if not writer.isOpened():
                        vcap.release()
                        st.error("Could not create the output video file.")
                    else:
                        vid_display = st.empty()
                        progress_bar = st.progress(0)
                        status_placeholder = st.empty()

                        processed_count = 0
                        total_detections = 0
                        max_frame_detections = 0

                        # Counts every detected object across processed frames.
                        # This is a frame-based detection total, not a unique-object tracker.
                        cum_counts = {
                            "overripe": 0,
                            "ripe": 0,
                            "rotten": 0,
                            "unripe": 0
                        }

                        try:
                            while vcap.isOpened():
                                ret, frame = vcap.read()
                                if not ret:
                                    break

                                processed_count += 1

                                res = model.predict(
                                    source=frame,
                                    conf=video_conf,
                                    iou=video_iou,
                                    imgsz=640,
                                    verbose=False
                                )[0]

                                annotated = res.plot()
                                writer.write(annotated)

                                # Preview selected processed frames while generating
                                # the final downloadable video.
                                if processed_count == 1 or processed_count % 5 == 0:
                                    preview_rgb = cv2.cvtColor(
                                        annotated, cv2.COLOR_BGR2RGB
                                    )
                                    vid_display.image(
                                        preview_rgb,
                                        channels="RGB",
                                        use_container_width=True
                                    )

                                boxes = res.boxes
                                frame_count = len(boxes) if boxes is not None else 0
                                total_detections += frame_count
                                max_frame_detections = max(
                                    max_frame_detections, frame_count
                                )

                                if boxes is not None:
                                    for b in boxes:
                                        cid = int(b.cls[0].item())
                                        cname = str(
                                            model.names.get(cid, "")
                                        ).lower()

                                        if cname in cum_counts:
                                            cum_counts[cname] += 1

                                if total_frames > 0:
                                    progress = min(
                                        processed_count / total_frames, 1.0
                                    )
                                    progress_bar.progress(progress)

                                status_placeholder.markdown(
                                    f"""
                                    <div class="metric-grid">
                                        <div class="minimal-card card-speed">
                                            <div class="card-header-flex">
                                                <div class="card-indicator ind-speed"></div>
                                                <span class="card-icon-pill">🎞️</span>
                                            </div>
                                            <div class="minimal-label">Frames Processed</div>
                                            <div class="minimal-value">
                                                {processed_count}
                                                <span style="font-size:0.95rem;color:#94a3b8;font-weight:500;">
                                                    / {total_frames}
                                                </span>
                                            </div>
                                        </div>

                                        <div class="minimal-card card-total">
                                            <div class="card-header-flex">
                                                <div class="card-indicator ind-total"></div>
                                                <span class="card-icon-pill">📦</span>
                                            </div>
                                            <div class="minimal-label">Detections</div>
                                            <div class="minimal-value">{total_detections}</div>
                                        </div>

                                        <div class="minimal-card card-ripe">
                                            <div class="card-header-flex">
                                                <div class="card-indicator ind-ripe"></div>
                                                <span class="card-icon-pill">🍏</span>
                                            </div>
                                            <div class="minimal-label">Ripe</div>
                                            <div class="minimal-value">{cum_counts["ripe"]}</div>
                                        </div>

                                        <div class="minimal-card card-unripe">
                                            <div class="card-header-flex">
                                                <div class="card-indicator ind-unripe"></div>
                                                <span class="card-icon-pill">🍋</span>
                                            </div>
                                            <div class="minimal-label">Unripe</div>
                                            <div class="minimal-value">{cum_counts["unripe"]}</div>
                                        </div>

                                        <div class="minimal-card card-overripe">
                                            <div class="card-header-flex">
                                                <div class="card-indicator ind-overripe"></div>
                                                <span class="card-icon-pill">🍑</span>
                                            </div>
                                            <div class="minimal-label">Overripe</div>
                                            <div class="minimal-value">{cum_counts["overripe"]}</div>
                                        </div>

                                        <div class="minimal-card card-rotten">
                                            <div class="card-header-flex">
                                                <div class="card-indicator ind-rotten"></div>
                                                <span class="card-icon-pill">🥀</span>
                                            </div>
                                            <div class="minimal-label">Rotten</div>
                                            <div class="minimal-value">{cum_counts["rotten"]}</div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                        finally:
                            vcap.release()
                            writer.release()

                        progress_bar.progress(1.0)

                        # MP4 produced by OpenCV may use a codec that browsers do
                        # not play reliably. Convert it to H.264 when ffmpeg exists.
                        browser_output = output_path
                        converted_path = output_path.replace(
                            ".mp4", "_h264.mp4"
                        )

                        try:
                            import subprocess

                            ffmpeg_cmd = [
                                "ffmpeg", "-y",
                                "-i", output_path,
                                "-c:v", "libx264",
                                "-pix_fmt", "yuv420p",
                                "-movflags", "+faststart",
                                converted_path
                            ]
                            ffmpeg_result = subprocess.run(
                                ffmpeg_cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=300
                            )

                            if (
                                ffmpeg_result.returncode == 0
                                and os.path.exists(converted_path)
                                and os.path.getsize(converted_path) > 0
                            ):
                                browser_output = converted_path
                        except Exception:
                            pass

                        if os.path.exists(browser_output):
                            st.success(
                                "✅ Video processing completed. "
                                "All detected fruits have bounding boxes and class labels."
                            )

                            st.markdown("""
                                <div class="panel-header-badge">
                                    <span class="panel-title">Processed Detection Video</span>
                                    <span class="panel-chip-ai">YOLOv8 Output</span>
                                </div>
                            """, unsafe_allow_html=True)

                            with open(browser_output, "rb") as output_file:
                                processed_video_bytes = output_file.read()

                            st.video(processed_video_bytes)

                            st.download_button(
                                label="📥 Download Processed Detection Video",
                                data=processed_video_bytes,
                                file_name="fruit_ripeness_detection_output.mp4",
                                mime="video/mp4",
                                type="primary",
                                key="download_processed_video"
                            )

                            st.markdown(
                                f"""
                                <div class="metric-grid">
                                    <div class="minimal-card card-total">
                                        <div class="minimal-label">Total Frame Detections</div>
                                        <div class="minimal-value">{total_detections}</div>
                                    </div>
                                    <div class="minimal-card card-ripe">
                                        <div class="minimal-label">Ripe</div>
                                        <div class="minimal-value">{cum_counts["ripe"]}</div>
                                    </div>
                                    <div class="minimal-card card-unripe">
                                        <div class="minimal-label">Unripe</div>
                                        <div class="minimal-value">{cum_counts["unripe"]}</div>
                                    </div>
                                    <div class="minimal-card card-overripe">
                                        <div class="minimal-label">Overripe</div>
                                        <div class="minimal-value">{cum_counts["overripe"]}</div>
                                    </div>
                                    <div class="minimal-card card-rotten">
                                        <div class="minimal-label">Rotten</div>
                                        <div class="minimal-value">{cum_counts["rotten"]}</div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            st.caption(
                                "Note: counts above represent detections across video frames, "
                                "not unique fruits. The output video contains the bounding boxes "
                                "and class labels produced by YOLOv8."
                            )

                        else:
                            st.error("The processed video could not be created.")

                        # Clean up temporary files after the output has been read.
                        for temp_path in {
                            video_path,
                            output_path,
                            converted_path
                        }:
                            try:
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                            except Exception:
                                pass

# ---------------- Tab 3: Model Evaluation ----------------

with eda_tab:
    st.markdown("""
        <div class="metric-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
            <div class="minimal-card card-ripe">
                <div class="card-header-flex">
                    <div class="card-indicator ind-ripe"></div>
                    <span class="card-icon-pill">🎯</span>
                </div>
                <div class="minimal-label">Precision</div>
                <div class="minimal-value">94.39%</div>
                <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">True positive accuracy</div>
            </div>
            <div class="minimal-card card-unripe">
                <div class="card-header-flex">
                    <div class="card-indicator ind-unripe"></div>
                    <span class="card-icon-pill">🔍</span>
                </div>
                <div class="minimal-label">Recall</div>
                <div class="minimal-value">92.53%</div>
                <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">Detection completeness</div>
            </div>
            <div class="minimal-card card-total">
                <div class="card-header-flex">
                    <div class="card-indicator ind-total"></div>
                    <span class="card-icon-pill">📈</span>
                </div>
                <div class="minimal-label">mAP @ 0.50</div>
                <div class="minimal-value">95.70%</div>
                <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">Mean Average Precision</div>
            </div>
            <div class="minimal-card card-speed">
                <div class="card-header-flex">
                    <div class="card-indicator ind-speed"></div>
                    <span class="card-icon-pill">📊</span>
                </div>
                <div class="minimal-label">mAP @ 0.50–0.95</div>
                <div class="minimal-value">78.40%</div>
                <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">Multi-threshold mAP</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent); margin: 24px 0 20px 0;"></div>
    """, unsafe_allow_html=True)
    st.caption("Training & Validation Analysis Curves")

    plot_dirs = [
        Path(__file__).resolve().parent.parent / "runs" / "detect" / "val",
        Path("runs/detect/val").resolve(),
        Path("fruit_ripeness_detection/runs/detect/val").resolve(),
    ]
    val_dir = next((d for d in plot_dirs if d.exists()), None)

    plot_info = [
        ("confusion_matrix_normalized.png", "Normalized Confusion Matrix", "Matrix"),
        ("confusion_matrix.png", "Raw Confusion Matrix", "Matrix"),
        ("BoxPR_curve.png", "Precision-Recall Curve (PR)", "Curve"),
        ("BoxF1_curve.png", "F1-Confidence Curve", "Curve"),
        ("BoxP_curve.png", "Precision-Confidence Curve", "Curve"),
        ("BoxR_curve.png", "Recall-Confidence Curve", "Curve"),
    ]

    if val_dir:
        col_l, col_r = st.columns(2)
        for i, (fn, title, tag) in enumerate(plot_info):
            fp = val_dir / fn
            target = col_l if i % 2 == 0 else col_r
            with target:
                if fp.exists():
                    st.markdown(f"""
                        <div class="eval-card-header">
                            <span class="eval-title">{title}</span>
                            <span class="eval-tag">{tag}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    st.image(str(fp), use_container_width=True)
    else:
        st.info("Evaluation plots directory not found.")
