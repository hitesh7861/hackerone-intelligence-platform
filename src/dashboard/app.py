import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
import base64
import os
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.connection import DatabaseConnection
from src import config

st.set_page_config(
    page_title="HackerOne Intelligence Platform",
    page_icon="H1",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background-color: #ffffff;
    }

    /* Top navbar */
    [data-testid="stHeader"] {
        z-index: 999 !important;
    }
    
    /* Align settings menu items inline with Deploy button */
    [data-testid="stToolbar"] {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    
    /* Settings dropdown menu alignment */
    [data-testid="stToolbar"] > div {
        display: flex !important;
        align-items: center !important;
    }
    
    /* Menu items in settings dropdown */
    [data-testid="stToolbar"] button,
    [data-testid="stToolbar"] [role="button"] {
        margin: 0 !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Make Settings dialog close button visible */
    [data-testid="stModal"] button[aria-label="Close"] {
        background-color: #ffffff !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        opacity: 1 !important;
    }
    
    [data-testid="stModal"] button[aria-label="Close"]:hover {
        background-color: #f0f0f0 !important;
        border-color: #d0d0d0 !important;
    }
    
    [data-testid="stModal"] button[aria-label="Close"] svg {
        color: #1a1a1a !important;
        stroke: #1a1a1a !important;
        fill: #1a1a1a !important;
    }
    
    .block-container {
        padding: 1rem 3rem 2rem 3rem;
        max-width: 1800px;
        background-color: #ffffff;
    }

    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        min-width: 21rem !important;
        max-width: 21rem !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #f8f9fa !important;
        min-height: 100vh !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* Collapsed sidebar styling */
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"].st-emotion-cache-1gwvy71 {
        background-color: #ffffff !important;
        min-width: 0 !important;
        max-width: 0 !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] > div,
    [data-testid="stSidebar"].st-emotion-cache-1gwvy71 > div {
        background-color: #ffffff !important;
    }
    
    /* Collapse button */
    button[data-testid="collapsedControl"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        background-image: none !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
    }
    

    
    [data-testid="stSidebar"] [role="radiogroup"] label {
        font-size: 1rem !important;
        line-height: 1.3 !important;
        padding: 0.15rem 0 !important;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.05rem !important;
    }
    
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
        border: 0 !important;
        border-top: 2px solid #d0d0d0 !important;
        opacity: 1 !important;
        height: 0 !important;
        background: transparent !important;
        display: block !important;
        visibility: visible !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        padding: 0.1rem 0 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    
    [data-testid="stSidebar"] p {
        font-size: 0.75rem !important;
    }
    
    /* Disable Sidebar Scrolling */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div:first-child {
        overflow: hidden !important;
    }
    
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] > div {
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    
    /* Fix scrollbar positioning at different zoom levels */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    .main {
        overflow-x: hidden !important;
    }
    
    body {
        overflow-x: hidden !important;
    }
    
    /* Hide anchor link icons on headers */
    .stMarkdown h1 a,
    .stMarkdown h2 a,
    .stMarkdown h3 a,
    h1 a[href^="#"],
    h2 a[href^="#"],
    h3 a[href^="#"] {
        display: none !important;
    }
    
    [data-testid="stSidebar"]::-webkit-scrollbar,
    [data-testid="stSidebar"] *::-webkit-scrollbar {
        display: none !important;
    }
    
    /* Chat Messages - Ensure full visibility */
    [data-testid="stChatMessageContainer"] {
        max-height: none !important;
        overflow: visible !important;
    }
    
    [data-testid="stChatMessage"] {
        max-height: none !important;
        overflow: visible !important;
        margin-bottom: 1rem !important;
    }
    
    /* Code blocks in chat */
    [data-testid="stChatMessage"] pre {
        max-height: none !important;
        overflow-x: auto !important;
        overflow-y: visible !important;
    }
    
    /* DataFrames in chat */
    [data-testid="stChatMessage"] [data-testid="stDataFrame"] {
        max-height: 400px !important;
        overflow: auto !important;
    }
    
    /* Clean, minimal tooltips */
    [role="tooltip"],
    div[data-baseweb="tooltip"] {
        background: #2a2a2a !important;
        color: #ffffff !important;
        font-size: 0.7rem !important;
        padding: 0.3rem 0.6rem !important;
        border-radius: 4px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
        max-width: 120px !important;
        font-weight: 400 !important;
        line-height: 1.3 !important;
    }
    [role="tooltip"] div,
    div[data-baseweb="tooltip"] div {
        color: #ffffff !important;
        font-size: 0.7rem !important;
        font-weight: 400 !important;
    }
    
    /* Fix table search modal - hide ALL inner elements except search input */
    /* Target the container that holds the three white buttons */
    div[class*="gdg-search-bar-inner"] {
        display: flex !important;
    }
    div[class*="gdg-search-bar-inner"] > *:not(input):not([role="searchbox"]) {
        display: none !important;
    }
    /* Hide any divs that contain buttons inside search */
    div[class*="gdg-search"] > div:not([class*="search-bar"]) {
        display: none !important;
    }
    /* More aggressive - hide all children except input */
    div[class*="search-bar"] > div > *:not(input) {
        display: none !important;
    }
    /* Target specific button containers */
    div[class*="gdg-search"] button,
    div[class*="search-bar"] button {
        display: none !important;
    }
    /* Clean up search modal padding */
    div[class*="gdg-search"] {
        padding: 1rem !important;
    }
    
    /* Auto-hide search overlay when focus is lost */
    div[class*="gdg-search"]:not(:focus-within) {
        pointer-events: auto !important;
    }
    
    /* Headers */
    h1 {
        color: #1a1a1a;
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        letter-spacing: -0.02em;
    }
    
    h2 {
        color: #1a1a1a;
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #2d2d2d;
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    p {
        color: #4a4a4a;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Subheaders in content */
    .stMarkdown h2,
    .stMarkdown h3 {
        color: #1a1a1a;
        font-weight: 700;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #1a1a1a;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 600;
        color: #4a4a4a;
    }
    [data-testid="stMetricDelta"] {
        color: #666666;
    }
    div[data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] {
        font-size: 20px;
    }
    
    /* Metric containers */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* DataFrames */
    .dataframe {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px;
    }
    
    .dataframe th {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        padding: 1rem !important;
        border-bottom: 2px solid #e0e0e0 !important;
    }
    
    .dataframe td {
        background-color: #ffffff !important;
        color: #2d2d2d !important;
        font-size: 0.9375rem !important;
        padding: 0.875rem 1rem !important;
        border-bottom: 1px solid #f0f0f0 !important;
    }
    
    .dataframe td,
    .dataframe td *,
    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrame"] td * {
        color: #2d2d2d !important;
    }
    
    .dataframe tr:hover td {
        background-color: #f8f9fa !important;
    }
    
    .dataframe tr:hover td,
    .dataframe tr:hover td * {
        color: #1a1a1a !important;
    }
    
    /* Plotly Charts */
    .js-plotly-plot {
        background-color: transparent !important;
    }
    
    /* Buttons - Nuclear option to override all Streamlit defaults */
    button,
    .stButton button,
    .stButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    button[data-testid],
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"],
    .stDownloadButton button,
    .stFormSubmitButton button {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d0d0d0 !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
    }
    
    button:hover,
    .stButton button:hover,
    .stButton > button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover,
    [data-testid="stSidebar"] button:hover {
        background-color: #f8f9fa !important;
        background: #f8f9fa !important;
        border-color: #a0a0a0 !important;
        color: #1a1a1a !important;
    }
    
    /* Force .stButton text visible (not header buttons) */
    .stButton button *,
    .stButton button p,
    .stButton button span {
        color: #1a1a1a !important;
    }
    
    /* Tooltips - All possible selectors */
    [data-baseweb="tooltip"],
    .stTooltipIcon,
    [role="tooltip"],
    div[role="tooltip"],
    [data-testid="stTooltipHoverTarget"],
    [data-testid="stTooltipContent"],
    .stTooltipContent,
    [class*="tooltip"],
    [id*="tooltip"] {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 6px !important;
        font-size: 0.875rem !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
    }
    
    [data-baseweb="tooltip"] *,
    [role="tooltip"] *,
    div[role="tooltip"] *,
    [data-testid="stTooltipContent"] * {
        color: #ffffff !important;
        opacity: 1 !important;
    }
    
    /* Button title attribute fallback */
    button[title]:hover::after {
        content: attr(title);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #2d2d2d;
        color: #ffffff;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        white-space: nowrap;
        z-index: 1000;
        margin-bottom: 0.5rem;
    }
    
    /* Selectbox / Dropdown */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border-color: #d0d0d0 !important;
    }
    
    /* Dropdown menu */
    [role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    [role="option"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    [role="option"]:hover {
        background-color: #f8f9fa !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        color: #1a1a1a !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    /* Alert boxes - Remove background */
    .stAlert {
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem 0 !important;
    }
    
    [data-testid="stAlert"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f8f9fa;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d0d0d0;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a0a0a0;
    }
    
    /* Fix chat container and input responsiveness */
    .main .block-container {
        max-height: calc(100vh - 100px) !important;
        overflow-y: auto !important;
        padding-bottom: 100px !important;
    }
    
    [data-testid="stChatInput"] {
        position: sticky !important;
        bottom: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        background: transparent !important;
        padding: 10px 0 !important;
        z-index: 100 !important;
    }
    
    [data-testid="stChatInput"] > div {
        width: 100% !important;
    }
    
    /* Force remove blue background from chat input - nuclear option */
    section[data-testid="stChatInput"],
    [data-testid="stChatInput"],
    [data-testid="stChatInput"]::before,
    [data-testid="stChatInput"]::after {
        background-color: #ffffff !important;
        background: #ffffff !important;
        background-image: none !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    
    [data-testid="stChatInput"] *,
    [data-testid="stChatInput"] div,
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] > div > div > div,
    [data-testid="stChatInput"] form,
    [data-testid="stChatInput"] form *,
    [data-testid="stChatInput"] [class*="st-"],
    [data-testid="stChatInput"] [class*="css-"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        background-image: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    
    [data-testid="stChatInput"] input,
    [data-testid="stChatInput"] textarea {
        background-color: #f8f9fa !important;
        background: #f8f9fa !important;
        border: 1px solid #d0d0d0 !important;
        color: #1a1a1a !important;
    }
    
    /* Chat message container */
    [data-testid="stChatMessageContainer"] {
        max-height: none !important;
        overflow: visible !important;
    }
    
    /* Floating AI Chatbot Button */
    .floating-chat-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        animation: pulse 2s infinite;
    }
    
    .floating-chat-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        }
        50% {
            box-shadow: 0 4px 30px rgba(102, 126, 234, 0.7);
        }
    }
    
    /* FINAL OVERRIDE - Buttons must be white */
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] .stButton > button,
    .stButton button[kind="secondary"],
    button[data-testid*="refresh"],
    button[aria-label*="Refresh"],
    button[data-testid="collapsedControl"] {
        background-color: #ffffff !important;
        background-image: none !important;
        background: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    [data-testid="stSidebar"] button:hover,
    [data-testid="stSidebar"] button[kind="secondary"]:hover,
    [data-testid="stSidebar"] .stButton button:hover,
    button[data-testid="collapsedControl"]:hover {
        background-color: #f8f9fa !important;
        background: #f8f9fa !important;
        border-color: #a0a0a0 !important;
    }
    
    /* Target button by its container */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] button {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Collapsed control button - absolute final override */
    button[data-testid="collapsedControl"],
    button[data-testid="collapsedControl"] * {
        background-color: #ffffff !important;
        background: #ffffff !important;
    }
    
    .chat-icon {
        font-size: 28px;
        color: white;
    }
    
    .chat-tooltip {
        position: fixed;
        bottom: 100px;
        right: 30px;
        background: #1a1a1a;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 999;
        white-space: nowrap;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Chat Widget Container */
    .chat-widget {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 400px;
        height: 600px;
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 12px;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-widget-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px 20px;
        color: white;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-widget-body {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
    }
    
    .close-chat {
        cursor: pointer;
        font-size: 20px;
        opacity: 0.8;
        transition: opacity 0.2s;
    }
    
    .close-chat:hover {
        opacity: 1;
    }
</style>
<script>
    function forceLightThemeButtons() {
        // Find ALL buttons and button-like elements
        const allButtons = document.querySelectorAll('button, [role="button"]');
        allButtons.forEach(el => {
            const computed = window.getComputedStyle(el);
            const bg = computed.backgroundColor;
            if (!bg) return;
            const match = bg.match(/\d+/g);
            if (!match) return;
            const [r, g, b] = match.map(Number);
            const brightness = (r * 299 + g * 587 + b * 114) / 1000;
            // If button has a dark background, force it white
            if (brightness < 150 && !(r === 0 && g === 0 && b === 0 && computed.backgroundColor === 'rgba(0, 0, 0, 0)')) {
                el.style.setProperty('background-color', '#ffffff', 'important');
                el.style.setProperty('background', '#ffffff', 'important');
                el.style.setProperty('border', '1px solid #d0d0d0', 'important');
                el.style.setProperty('border-radius', '6px', 'important');
                // Only fix text color, not SVG fills (to avoid black square icons)
                el.style.setProperty('color', '#1a1a1a', 'important');
            }
        });
    }
    
    forceLightThemeButtons();
    setTimeout(forceLightThemeButtons, 200);
    setTimeout(forceLightThemeButtons, 600);
    setTimeout(forceLightThemeButtons, 1200);
    setTimeout(forceLightThemeButtons, 2500);
    
    const observer = new MutationObserver(() => setTimeout(forceLightThemeButtons, 50));
    observer.observe(document.body, { childList: true, subtree: true, attributes: true });
    
    // Close dataframe search on outside click by simulating ESC key
    document.addEventListener('click', function(event) {
        // Check if there's an active search input in any dataframe
        const allInputs = document.querySelectorAll('input[type="text"], input[placeholder*="search" i], input[placeholder*="Type to search" i]');
        
        let searchInputFound = null;
        allInputs.forEach(function(input) {
            // Check if this input is inside a dataframe search overlay
            const parent = input.closest('[class*="search"], [data-testid="stDataFrame"]');
            if (parent && window.getComputedStyle(input).display !== 'none' && input.offsetParent !== null) {
                searchInputFound = input;
            }
        });
        
        if (searchInputFound) {
            // Check if click was outside the search input and its container
            const searchContainer = searchInputFound.closest('[class*="search"], div[style*="position"]');
            const clickedOnSearchButton = event.target.closest('button[title*="Search" i], button[aria-label*="Search" i]');
            
            if (searchContainer && !searchContainer.contains(event.target) && !clickedOnSearchButton) {
                // Simulate ESC key press to close the search
                const escEvent = new KeyboardEvent('keydown', {
                    key: 'Escape',
                    code: 'Escape',
                    keyCode: 27,
                    which: 27,
                    bubbles: true,
                    cancelable: true
                });
                searchInputFound.dispatchEvent(escEvent);
                
                // Also try dispatching to document
                document.dispatchEvent(escEvent);
                
                // Blur the input as fallback
                searchInputFound.blur();
            }
        }
    }, true);
</script>
""", unsafe_allow_html=True)

# Check if database exists and has data, if not run pipeline (only once per session)
if 'db_checked' not in st.session_state:
    st.session_state.db_checked = False

if not st.session_state.db_checked:
    db_path = Path(__file__).parent.parent.parent / "data" / "hackerone.duckdb"
    needs_setup = False

    # Check if database exists and has data
    if not db_path.exists():
        needs_setup = True
    else:
        # Check if database has data and views by querying fact_reports and views
        try:
            import duckdb
            conn = duckdb.connect(str(db_path), read_only=True)
            try:
                # Check if fact_reports table exists and has data
                result = conn.execute("SELECT COUNT(*) FROM fact_reports").fetchone()
                if result[0] == 0:
                    needs_setup = True
                else:
                    # Check if views exist (pipeline completed)
                    try:
                        conn.execute("SELECT COUNT(*) FROM vw_organization_metrics").fetchone()
                    except:
                        # Views don't exist, pipeline didn't complete
                        needs_setup = True
            except:
                # Table doesn't exist
                needs_setup = True
            finally:
                conn.close()
        except:
            needs_setup = True
    
    st.session_state.db_checked = True
else:
    needs_setup = False

if needs_setup:
    st.info("🔄 First time setup: Downloading and processing HackerOne dataset... This takes 2-5 minutes.")
    with st.spinner("Loading data..."):
        try:
            # Delete existing database if it exists but is empty/corrupted
            if db_path.exists():
                db_path.unlink()
            
            from src.elt.pipeline import ELTPipeline
            pipeline = ELTPipeline()
            pipeline.run_full_pipeline()
            st.success("Data loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.info("Try refreshing the page or contact support if the issue persists.")
            st.stop()

@st.cache_resource
def get_db_connection():
    return DatabaseConnection()

db = get_db_connection()

# Clear any stale query params
if st.query_params:
    st.query_params.clear()

def render_table(df, height=400):
    """Render DataFrame with st.data_editor."""
    if df is None or df.empty:
        st.warning("No data to display")
        return
    
    # Use st.data_editor which has better search functionality than st.dataframe
    st.data_editor(
        df,
        use_container_width=True,
        height=height,
        disabled=True,  # Make it read-only
        hide_index=True,
        num_rows="fixed"
    )

# Sidebar
with st.sidebar:
    import base64

    # Load assets
    logo_path    = Path(__file__).parent / "assets" / "h1.jpg"
    bot_path     = Path(__file__).parent / "assets" / "bot.png"
    refresh_path = Path(__file__).parent / "assets" / "refresh.png"
    home_path    = Path(__file__).parent / "assets" / "home-button.png"
    logo_data    = ""
    bot_data     = ""
    refresh_data = ""
    home_data    = ""
    if logo_path.exists():
        with open(str(logo_path), 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode()
    if bot_path.exists():
        with open(str(bot_path), 'rb') as f:
            bot_data = base64.b64encode(f.read()).decode()
    if refresh_path.exists():
        with open(str(refresh_path), 'rb') as f:
            refresh_data = base64.b64encode(f.read()).decode()
    if home_path.exists():
        with open(str(home_path), 'rb') as f:
            home_data = base64.b64encode(f.read()).decode()
    dashboard_path = Path(__file__).parent / "assets" / "dashboard.png"
    dashboard_data = ""
    if dashboard_path.exists():
        with open(str(dashboard_path), 'rb') as f:
            dashboard_data = base64.b64encode(f.read()).decode()

    # Session state init
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'refresh_trigger' not in st.session_state:
        st.session_state.refresh_trigger = False

    current = st.session_state.current_page

    # Button position map: 1=Refresh, 2=Home, 3=AI
    _btn_order = {"Home": 2, "AI Assistant": 3}
    _active_idx = _btn_order.get(current, 99)  # 99 = no button highlighted for dashboard pages

    # ── SIDEBAR THEME CSS ──────────────────────────────────────────
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{
        background: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: #ffffff !important;
        padding: 0 !important;
        min-height: 100vh !important;
        justify-content: flex-start !important;
    }}
    [data-testid="stSidebar"] .element-container {{ margin-bottom: 0 !important; }}

    /* All nav buttons: flat, left-aligned */
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important;
        border: none !important;
        border-left: 2px solid transparent !important;
        border-radius: 0 6px 6px 0 !important;
        color: #374151 !important;
        font-size: 0.855rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 0.48rem 1rem !important;
        width: 100% !important;
        transition: background 0.15s, color 0.15s !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: #f3f4f6 !important;
        color: #111827 !important;
        border-left-color: #d1d5db !important;
    }}
    [data-testid="stSidebar"] .stButton > button:focus {{
        box-shadow: none !important;
    }}

    /* Refresh button — 1st .stButton */
    [data-testid="stSidebar"] :nth-child(1 of .stButton) > button {{
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        color: #6b7280 !important;
        font-size: 0.78rem !important;
        padding: 0.42rem 0.875rem !important;
        background: #f9fafb !important;
    }}
    [data-testid="stSidebar"] :nth-child(1 of .stButton) > button:hover {{
        background: #f3f4f6 !important;
        color: #374151 !important;
        border-color: #d1d5db !important;
    }}
    /* Per-button icons via :has() + sibling selector */
    [data-testid="stSidebar"] .element-container:has(.sb-icon-refresh) + .element-container .stButton > button::before {{
        content: '';
        display: inline-block;
        width: 14px; height: 14px;
        background: url('data:image/png;base64,{refresh_data}') center/contain no-repeat;
        vertical-align: middle; margin-right: 6px; margin-bottom: 1px; opacity: 0.75;
    }}
    [data-testid="stSidebar"] .element-container:has(.sb-icon-home) + .element-container .stButton > button::before {{
        content: '';
        display: inline-block;
        width: 15px; height: 15px;
        background: url('data:image/png;base64,{home_data}') center/contain no-repeat;
        vertical-align: middle; margin-right: 7px; margin-bottom: 2px; opacity: 0.8;
    }}
    [data-testid="stSidebar"] .element-container:has(.sb-icon-bot) + .element-container .stButton > button::before {{
        content: '';
        display: inline-block;
        width: 17px; height: 17px;
        background: url('data:image/png;base64,{bot_data}') center/contain no-repeat;
        vertical-align: middle; margin-right: 7px; margin-bottom: 2px; opacity: 0.9;
    }}

    /* Active nav item */
    [data-testid="stSidebar"] :nth-child({_active_idx} of .stButton) > button {{
        background: #f5f3ff !important;
        color: #6d28d9 !important;
        border-left: 2px solid #7c3aed !important;
        font-weight: 600 !important;
    }}
    [data-testid="stSidebar"] :nth-child({_active_idx} of .stButton) > button:hover {{
        background: #ede9fe !important;
        color: #5b21b6 !important;
    }}

    /* AI Assistant button — targeted via marker */
    [data-testid="stSidebar"] .element-container:has(.sb-icon-bot) + .element-container .stButton > button {{
        background: linear-gradient(135deg,#ede9fe,#f3e8ff) !important;
        color: #6d28d9 !important;
        border: 1px solid #c4b5fd !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }}
    [data-testid="stSidebar"] .element-container:has(.sb-icon-bot) + .element-container .stButton > button:hover {{
        background: linear-gradient(135deg,#ddd6fe,#ede9fe) !important;
        color: #5b21b6 !important;
        border-color: #a78bfa !important;
    }}

    /* Selectbox (dashboard dropdown) styling */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        font-size: 0.8rem !important;
        min-height: 34px !important;
        box-shadow: none !important;
        transition: border-color 0.15s, background 0.15s !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover {{
        border-color: #d1d5db !important;
        background: #f3f4f6 !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {{
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(139,92,246,0.12) !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] span {{
        font-size: 0.8rem !important;
        color: #374151 !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label {{ display: none !important; }}
    [data-testid="stSidebar"] .stSelectbox {{ margin: 0 !important; }}
    /* Dropdown popup list */
    [data-baseweb="popover"] [role="listbox"] {{
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1), 0 2px 6px rgba(0,0,0,0.05) !important;
        overflow: hidden !important;
        padding: 4px !important;
    }}
    [data-baseweb="popover"] [role="option"] {{
        font-size: 0.8rem !important;
        padding: 0.35rem 0.7rem !important;
        min-height: 0 !important;
        line-height: 1.5 !important;
        border-radius: 6px !important;
        margin: 1px 0 !important;
        color: #374151 !important;
    }}
    [data-baseweb="popover"] [role="option"]:hover {{
        background: #f3f4f6 !important;
        color: #111827 !important;
    }}
    [data-baseweb="popover"] [aria-selected="true"] {{
        background: #f5f3ff !important;
        color: #6d28d9 !important;
        font-weight: 600 !important;
    }}
    /* Limit dashboard dropdown height to not overlap AI Assistant */
    [data-baseweb="popover"] {{
        max-height: 330px !important;
        overflow: visible !important;
    }}
    [data-baseweb="popover"] > div {{
        max-height: 330px !important;
        overflow: hidden !important;
    }}
    [data-baseweb="popover"] ul {{
        max-height: 290px !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }}
    [data-baseweb="popover"] * {{
        scrollbar-width: thin !important;
    }}

    /* Dividers */
    [data-testid="stSidebar"] hr {{ border-color: #f0f0f0 !important; margin: 0.35rem 0 !important; }}

    /* Collapse/expand button */
    button[data-testid="collapsedControl"] {{
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
        color: #6b7280 !important;
    }}
    button[data-testid="collapsedControl"]:hover {{
        background: #f3f4f6 !important;
        border-color: #9ca3af !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] {{
        min-width: 0 !important; max-width: 0 !important;
    }}

    /* ── Mini nav ── */
    #mn-root {{
        position: fixed; top: 0; left: 0; width: 52px; height: 100vh;
        background: #fff; border-right: 1px solid #e5e7eb;
        flex-direction: column; align-items: center;
        box-shadow: 2px 0 10px rgba(0,0,0,.08);
        display: none; overflow: visible; z-index: 99999;
        padding-top: 8px;
    }}
    #mn-exp {{
        width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
        cursor: pointer; background: transparent; border: none;
        color: #9ca3af; font-size: 18px; font-family: sans-serif; flex-shrink: 0;
        user-select: none; transition: color .15s; margin-bottom: 4px;
    }}
    #mn-exp:hover {{ color: #374151; }}
    .mn-exp {{
        width: 100%; min-height: 36px; display: flex; align-items: center; justify-content: center;
        cursor: pointer; background: #f9fafb; border-bottom: 1px solid #e5e7eb;
        color: #374151; font-size: 1.4rem; font-weight: 700; flex-shrink: 0;
        transition: background .15s, color .15s; user-select: none; font-family: sans-serif;
    }}
    .mn-exp:hover {{ background: #ede9fe; color: #6d28d9; }}
    .mn-logo-box {{ padding: .55rem 0 .35rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
    .mn-logo {{ width: 30px; height: 30px; border-radius: 7px; object-fit: cover; }}
    .mn-sep {{ width: 32px; height: 1px; background: #f0f0f0; margin: 3px 0; flex-shrink: 0; }}
    .mn-btn {{
        width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
        border-radius: 8px; cursor: pointer; position: relative; transition: background .15s;
        flex-shrink: 0; margin: 2px 0; user-select: none;
    }}
    .mn-btn:hover {{ background: #f3f4f6; }}
    .mn-btn img {{ width: 20px; height: 20px; object-fit: contain; opacity: .65; pointer-events: none; transition: opacity .15s; }}
    .mn-btn:hover img {{ opacity: 1; }}
    .mn-ai {{ background: linear-gradient(135deg,#ede9fe,#f3e8ff); border: 1px solid #c4b5fd; }}
    .mn-ai:hover {{ background: linear-gradient(135deg,#ddd6fe,#ede9fe); }}
    .mn-tip {{
        position: absolute; left: calc(100% + 8px); top: 50%; transform: translateY(-50%);
        background: #1f2937; color: #f9fafb; padding: 4px 9px; border-radius: 5px;
        font-size: 11px; white-space: nowrap; pointer-events: none; opacity: 0;
        transition: opacity .15s; z-index: 10010; font-family: sans-serif; font-weight: 500;
        box-shadow: 0 4px 10px rgba(0,0,0,.2);
    }}
    .mn-btn:hover .mn-tip {{ opacity: 1; }}
    .mn-btn.mn-active .mn-tip {{ opacity: 0 !important; }}
    #mn-popup {{
        position: fixed; left: 56px; width: 200px; background: #fff;
        border: 1px solid #e5e7eb; border-radius: 10px;
        box-shadow: 0 8px 24px rgba(0,0,0,.12); z-index: 1001;
        display: none; overflow: hidden; padding: 4px 0;
    }}
    .mn-popup-title {{
        font-size: 10px; font-weight: 700; color: #9ca3af; text-transform: uppercase;
        letter-spacing: .08em; padding: 6px 10px 4px; font-family: sans-serif;
    }}
    .mn-opt {{
        display: flex; align-items: center; gap: 8px; padding: 7px 10px; font-size: 12px;
        color: #374151; cursor: pointer; transition: background .1s; font-family: sans-serif;
    }}
    .mn-opt:hover {{ background: #f3f4f6; color: #111827; }}
    .mn-opt.mn-active-opt {{ background: #f5f3ff !important; color: #6d28d9 !important; font-weight: 600; }}
    /* Hide the hidden dashboard nav trigger+button pairs */
    [data-testid="stSidebar"] .element-container:has(.mn-dash-nav-trigger),
    [data-testid="stSidebar"] .element-container:has(.mn-dash-nav-trigger) + .element-container {{
        height: 0 !important; min-height: 0 !important;
        overflow: hidden !important; margin: 0 !important; padding: 0 !important;
    }}
    /* CSS fallback: show mini nav when sidebar is collapsed */
    body:has([data-testid="stSidebar"][aria-expanded="false"]) #mn-root {{
        display: flex !important;
    }}
    /* Push content right when mini nav visible */
    body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stAppViewContainer"] {{
        padding-left: 52px !important;
    }}
    /* Hide native collapsed control offscreen but keep it clickable by JS */
    button[data-testid="collapsedControl"] {{
        position: fixed !important;
        left: -9999px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}
    /* Auto-close popup when sidebar opens */
    body:has([data-testid="stSidebar"][aria-expanded="true"]) #mn-popup {{
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── LOGO ────────────────────────────────────────────────────────
    logo_img = (f'<img src="data:image/jpeg;base64,{logo_data}" '
                f'style="width:36px;height:36px;border-radius:8px;object-fit:cover;flex-shrink:0;"/>'
                if logo_data else
                '<div style="width:36px;height:36px;background:linear-gradient(135deg,#7c3aed,#6366f1);'
                'border-radius:8px;display:flex;align-items:center;justify-content:center;'
                'color:#fff;font-weight:800;font-size:0.8rem;">H1</div>')
    st.markdown(f"""
    <div style="padding:0.9rem 1rem 0.8rem;border-bottom:1px solid #e5e7eb;margin-bottom:0.35rem;background:#ffffff;">
      <div style="display:flex;align-items:center;gap:0.65rem;">
        {logo_img}
        <div>
          <div style="color:#111827;font-size:0.9rem;font-weight:700;line-height:1.2;">HackerOne</div>
          <div style="color:#9ca3af;font-size:0.67rem;font-weight:500;letter-spacing:0.02em;">Intelligence Platform</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── REFRESH ─────────────────────────────────────────────────────
    st.markdown('<span class="sb-icon-refresh"></span>', unsafe_allow_html=True)
    refresh_clicked = st.button("Refresh Data", key="refresh-data-btn", use_container_width=True)
    if refresh_clicked:
        with st.spinner("Refreshing data…"):
            try:
                from src.elt.pipeline import ELTPipeline
                ELTPipeline().run_full_pipeline()
                st.success("Data refreshed!")
                st.cache_resource.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")

    # ── NAV: HOME ───────────────────────────────────────────────────
    st.markdown('<span class="sb-icon-home"></span>', unsafe_allow_html=True)
    if st.button("Home", key="nav_Home", use_container_width=True):
        st.session_state.current_page = "Home"
        st.rerun()

    # ── NAV: DASHBOARDS DROPDOWN ───────────────────────────────────
    st.markdown("""<p style='color:#9ca3af;font-size:0.63rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.1em;padding:0.55rem 1rem 0.2rem;margin:0;'>Dashboards</p>""",
        unsafe_allow_html=True)

    _dash_items = [
        ("📊", "Executive Dashboard"), ("🔍", "Threat Intelligence"),
        ("📈", "Program Benchmarks"),  ("👥", "Community Analytics"),
        ("📉", "Market Evolution"),    ("💡", "Strategic Insights"),
        ("📚", "Security Reference"),  ("🔧", "Data Workbench"),
    ]
    _label_map  = {f"{ic} {lb}": lb for ic, lb in _dash_items}
    _rev_map    = {lb: f"{ic} {lb}" for ic, lb in _dash_items}
    _dash_opts  = ["─ Select Dashboard ─"] + [f"{ic} {lb}" for ic, lb in _dash_items]
    _cur_disp   = _rev_map.get(current, "") if current in _rev_map else ""
    _sel_idx    = list(_label_map.keys()).index(_cur_disp) + 1 if _cur_disp else 0
    _selected   = st.selectbox("dash", _dash_opts, index=_sel_idx, label_visibility="collapsed")
    if _selected != "─ Select Dashboard ─":
        _actual = _label_map.get(_selected, _selected)
        if st.session_state.current_page != _actual:
            st.session_state.current_page = _actual
            st.rerun()

    # Hidden nav buttons for mini-sidebar dashboard navigation (CSS collapses them to h=0)
    for _ic, _lb in _dash_items:
        st.markdown('<span class="mn-dash-nav-trigger"></span>', unsafe_allow_html=True)
        if st.button(_lb, key=f"mnav_{_lb.replace(' ', '_')}", use_container_width=False):
            st.session_state.current_page = _lb
            st.rerun()

    st.markdown("---")

    # ── NAV: AI ASSISTANT ───────────────────────────────────────────
    st.markdown("""<p style='color:#9ca3af;font-size:0.63rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.1em;padding:0.4rem 1rem 0.25rem;margin-left:35px;'>AI-Powered</p>""",
        unsafe_allow_html=True)
    st.markdown('<span class="sb-icon-bot"></span>', unsafe_allow_html=True)
    if st.button("AI Assistant", key="nav_AI_Assistant", use_container_width=True):
        st.session_state.current_page = "AI Assistant"
        st.rerun()

    page = st.session_state.current_page
    

# Mini sidebar - injected directly into Streamlit DOM via st.markdown (no iframe)
# CSS :has() rules handle show/hide; inline onclick handles interaction.

_mn_logo    = (f'<img class="mn-logo" src="data:image/jpeg;base64,{logo_data}"/>' if logo_data
               else '<div class="mn-logo" style="background:linear-gradient(135deg,#7c3aed,#6366f1);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:11px;border-radius:7px;">H1</div>')
_mn_refresh = f'<img src="data:image/png;base64,{refresh_data}"/>'  if refresh_data  else '&#x1F504;'
_mn_home    = f'<img src="data:image/png;base64,{home_data}"/>'     if home_data     else '&#x1F3E0;'
_mn_dash    = f'<img src="data:image/png;base64,{dashboard_data}">' if dashboard_data else '&#x1F4CA;'
_mn_bot     = f'<img src="data:image/png;base64,{bot_data}"/>'      if bot_data      else '&#x1F916;'

# Inline JS onclick strings (plain Python strings — no f-string brace escaping needed)
_js_exp   = ("var c=document.querySelector('[data-testid=collapsedControl]');"
             "if(c){c.style.visibility='';c.click();}")
_js_refr  = (_js_exp +
             "setTimeout(function(){document.querySelectorAll('[data-testid=stSidebar] button')"
             ".forEach(function(b){if(b.textContent.trim()==='Refresh Data')b.click();});},500);")
_js_home  = (_js_exp +
             "setTimeout(function(){document.querySelectorAll('[data-testid=stSidebar] button')"
             ".forEach(function(b){if(b.textContent.trim()==='Home')b.click();});},500);")
_js_ai    = (_js_exp +
             "setTimeout(function(){document.querySelectorAll('[data-testid=stSidebar] button')"
             ".forEach(function(b){if(b.textContent.trim()==='AI Assistant')b.click();});},500);")
_js_popup = ("var p=document.getElementById('mn-popup');if(!p)return;"
             "var op=p.style.display==='block';p.style.display=op?'none':'block';"
             "if(!op){var r=this.getBoundingClientRect();p.style.top=r.top+'px';}")

def _js_nav(page):
    return (f"document.getElementById('mn-popup').style.display='none';"
            f"document.querySelectorAll('[data-testid=stSidebar] button')"
            f".forEach(function(b){{if(b.textContent.trim()==='{page}')b.click();}});")

_dash_popup_items = [
    ("&#x1F4CA;", "Executive Dashboard"), ("&#x1F50D;", "Threat Intelligence"),
    ("&#x1F4C8;", "Program Benchmarks"),  ("&#x1F465;", "Community Analytics"),
    ("&#x1F4C9;", "Market Evolution"),    ("&#x1F4A1;", "Strategic Insights"),
    ("&#x1F4DA;", "Security Reference"),  ("&#x1F527;", "Data Workbench"),
]
_popup_opts = "\n".join(
    f'<div class="mn-opt" data-page="{lb}">{ic} {lb}</div>'
    for ic, lb in _dash_popup_items
)

st.markdown(f"""
<div id="mn-root">
  <div id="mn-exp">&#8250;</div>
  <div class="mn-logo-box">{_mn_logo}</div>
  <div class="mn-sep"></div>
  <div class="mn-btn" id="mn-r">{_mn_refresh}<span class="mn-tip">Refresh Data</span></div>
  <div class="mn-btn" id="mn-h">{_mn_home}<span class="mn-tip">Home</span></div>
  <div class="mn-btn" id="mn-d">{_mn_dash}<span class="mn-tip">Dashboards &#9660;</span></div>
  <div class="mn-btn mn-ai" id="mn-a">{_mn_bot}<span class="mn-tip">AI Assistant</span></div>
</div>
<div id="mn-popup">
  <div class="mn-popup-title">Select Dashboard</div>
  {_popup_opts}
</div>
""", unsafe_allow_html=True)

# Attach event listeners via components iframe (DOMPurify strips inline onclick from st.markdown)
import streamlit.components.v1 as _components
_components.html("""
<script>
(function attach() {
  var PD = window.parent.document;

  function clickSidebarBtn(label) {
    var btns = PD.querySelectorAll('[data-testid="stSidebar"] button');
    for (var i = 0; i < btns.length; i++) {
      var t = btns[i].textContent.trim();
      if (t === label || t.includes(label)) { btns[i].click(); return true; }
    }
    return false;
  }

  function expandAndNav(label) {
    var cb = PD.querySelector('[data-testid="collapsedControl"]');
    if (cb) cb.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window.parent}));
    window.parent.setTimeout(function() { clickSidebarBtn(label); }, 500);
  }

  function closePopup() {
    var p = PD.getElementById('mn-popup');
    if (p) p.style.display = 'none';
    var mnD = PD.getElementById('mn-d');
    if (mnD) mnD.classList.remove('mn-active');
  }

  // Move #mn-root and #mn-popup to document.body for root-level stacking context
  function reparentToBody() {
    ['mn-root', 'mn-popup'].forEach(function(id) {
      var all = PD.querySelectorAll('#' + id);
      if (all.length === 0) return;
      var bodyEl = null, reactEl = null;
      for (var i = 0; i < all.length; i++) {
        if (all[i].parentNode === PD.body) bodyEl = all[i];
        else reactEl = all[i];
      }
      if (reactEl) {
        if (bodyEl) PD.body.removeChild(bodyEl);
        PD.body.appendChild(reactEl);
        if (id === 'mn-root') reactEl._mnBound = false;
      } else if (all.length === 1 && all[0].parentNode !== PD.body) {
        PD.body.appendChild(all[0]);
        if (id === 'mn-root') all[0]._mnBound = false;
      }
    });
  }

  function bindAll() {
    var exp = PD.getElementById('mn-exp');
    var mnR = PD.getElementById('mn-r');
    var mnH = PD.getElementById('mn-h');
    var mnD = PD.getElementById('mn-d');
    var mnA = PD.getElementById('mn-a');
    if (!mnR || mnR._mnBound) return;

    mnR._mnBound = true;
    if (exp) exp.addEventListener('click', function(e) {
      e.stopPropagation();
      var cb = PD.querySelector('button[data-testid="collapsedControl"]');
      if (cb) { cb.style.cssText=''; cb.click(); }
    });
    mnR.addEventListener('click', function(e) {
      e.stopPropagation(); expandAndNav('Refresh Data');
    });
    mnH.addEventListener('click', function(e) {
      e.stopPropagation(); expandAndNav('Home');
    });
    mnA.addEventListener('click', function(e) {
      e.stopPropagation(); expandAndNav('AI Assistant');
    });
    mnD.addEventListener('click', function(e) {
      e.stopPropagation();
      var p = PD.getElementById('mn-popup');
      if (!p) return;
      if (p.style.display === 'block') {
        mnD.classList.remove('mn-active');
        closePopup();
        return;
      }
      var r = mnD.getBoundingClientRect();
      p.style.top = r.top + 'px';
      p.style.display = 'block';
      mnD.classList.add('mn-active');
    });
    PD.querySelectorAll('.mn-opt').forEach(function(opt) {
      opt.addEventListener('click', function(e) {
        e.stopPropagation();
        closePopup();
        clickSidebarBtn(this.dataset.page);
      });
    });
    PD.addEventListener('click', function() { closePopup(); });
  }

  // Every tick: reparent to body (escape React stacking context), then bind events
  var timer = window.parent.setInterval(function() {
    reparentToBody();
    if (PD.getElementById('mn-exp')) { bindAll(); }
  }, 300);

  // Initial run on load
  function init() { reparentToBody(); bindAll(); }
  if (PD.readyState === 'loading') {
    PD.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
""", height=1, scrolling=False)

# Home landing page
if page == "Home":
    try:
        metrics = db.execute_query("""
            SELECT COUNT(DISTINCT id) as total_reports,
                   SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                   COUNT(DISTINCT reporter_username) as researchers,
                   COUNT(DISTINCT team_handle) as orgs
            FROM fact_reports
        """).iloc[0]
        bounty_rate = (metrics['bounty_reports'] / metrics['total_reports'] * 100) if metrics['total_reports'] > 0 else 0
        total_r = f"{int(metrics['total_reports']):,}"
        total_o = f"{int(metrics['orgs']):,}"
        total_res = f"{int(metrics['researchers']):,}"
        total_br = f"{bounty_rate:.1f}%"
    except:
        total_r = total_o = total_res = total_br = "—"

    st.markdown(f"""
    <style>
    .home-wrap {{
        width: 100%;
        box-sizing: border-box;
        min-height: calc(100vh - 140px);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    /* Hero */
    .home-hero {{
        background: linear-gradient(160deg, #f5f3ff 0%, #faf5ff 40%, #eff6ff 100%);
        border: 1px solid #e8e0ff;
        border-radius: 14px;
        padding: 1.56rem 3rem 1.46rem 3rem;
        text-align: center;
    }}
    .home-badge {{
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6, #6366f1);
        color: #ffffff;
        border-radius: 20px;
        padding: 0.18rem 0.8rem;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }}
    .home-title {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 0.35rem 0;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }}
    .home-subtitle {{
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.5;
        max-width: 640px;
        margin: 0 auto;
    }}

    /* Stats */
    .home-stats {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        background: #e2e8f0;
        gap: 1px;
    }}
    .home-stat {{
        background: #ffffff;
        padding: 0.87rem 1rem;
        text-align: center;
    }}
    .home-stat-num {{
        font-size: 1.7rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 0.25rem;
    }}
    .home-stat-num.green {{ color: #059669; }}
    .home-stat-label {{
        font-size: 0.7rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    .home-capabilities {{
    }}
    .home-section-label {{
        text-align: center;
        font-size: 0.68rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.6rem;
    }}

    /* Feature cards 2x2 */
    .home-features {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
    }}
    .home-feature {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.87rem 1.5rem;
        transition: box-shadow 0.2s;
    }}
    .home-feature:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.07); }}
    .home-feature-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.4rem;
    }}
    .home-feature-title {{
        font-size: 0.9rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.35rem;
    }}
    .home-feature-desc {{
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.55;
    }}

    /* AI CTA */
    .home-ai-cta {{
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #1d4ed8 100%);
        border-radius: 12px;
        padding: 0.76rem 1.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    </style>

    <div class="home-wrap">

      <!-- HERO -->
      <div class="home-hero">
        <div class="home-badge">✦ Security Intelligence Platform</div>
        <div class="home-title">HackerOne Intelligence Platform</div>
        <div class="home-subtitle">
          Security intelligence with AI-powered insights built on <strong>{total_r} real-world HackerOne disclosures</strong> — visibility into threat patterns, bounty economics, and researcher dynamics across <strong>{total_o} organizations</strong>.
        </div>
      </div>

      <!-- STATS -->
      <div class="home-stats">
        <div class="home-stat">
          <div class="home-stat-num">{total_r}</div>
          <div class="home-stat-label">Vulnerability Reports</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-num">{total_o}</div>
          <div class="home-stat-label">Organizations</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-num">{total_res}</div>
          <div class="home-stat-label">Security Researchers</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-num green">{total_br}</div>
          <div class="home-stat-label">Bounty Rate</div>
        </div>
      </div>

      <!-- CAPABILITIES -->
      <div class="home-capabilities">
      <div class="home-section-label">Platform Capabilities</div>
      <div class="home-features">
        <div class="home-feature">
          <div class="home-feature-icon">📊</div>
          <div class="home-feature-title">Threat Intelligence & Benchmarks</div>
          <div class="home-feature-desc">Top vulnerability types by frequency and bounty rates, attack pattern analysis, severity trends, and cross-program performance benchmarking.</div>
        </div>
        <div class="home-feature">
          <div class="home-feature-icon">📈</div>
          <div class="home-feature-title">Program Performance & Economics</div>
          <div class="home-feature-desc">Bounty investment analysis, program maturity metrics, organization performance scoring, and bug bounty market evolution trends.</div>
        </div>
        <div class="home-feature">
          <div class="home-feature-icon">👥</div>
          <div class="home-feature-title">Community & Researcher Analytics</div>
          <div class="home-feature-desc">Top researcher productivity metrics, report quality scores, bounty success rates, and community engagement patterns across 3,895 contributors.</div>
        </div>
        <div class="home-feature">
          <div class="home-feature-icon">💡</div>
          <div class="home-feature-title">Strategic Insights & Data Workbench</div>
          <div class="home-feature-desc">Data-driven executive recommendations, concentration analysis, program optimization strategies, security knowledge base, and interactive data exploration.</div>
        </div>
      </div>
      </div>

      <!-- AI CTA -->
      <div class="home-ai-cta">
        <div style="font-size: 2rem; flex-shrink:0;">🤖</div>
        <div style="flex:1; text-align:left;">
          <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff; margin-bottom: 0.2rem;">
            Ask Anything — AI-Powered Analyst
          </div>
          <div style="color: #a5b4fc; font-size: 0.8rem; line-height: 1.5;">
            Query {total_r} reports in plain English. Get instant insights powered by GPT-4o-mini.
          </div>
        </div>
      </div>

    </div>
    """, unsafe_allow_html=True)


# Main content - Executive Dashboard page
elif page == "Executive Dashboard":
    st.title("Executive Dashboard")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Comprehensive intelligence platform providing real-time visibility into global vulnerability landscape, bounty economics, and security program performance</p>", unsafe_allow_html=True)
    
    metrics = db.execute_query("""
        SELECT
            COUNT(DISTINCT id) as total_reports,
            SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
            COUNT(DISTINCT reporter_username) as researchers
        FROM fact_reports
    """).iloc[0]
    
    # Get vulnerability types count from dimension table
    vulnerability_types = db.execute_query("SELECT COUNT(*) as count FROM dim_vulnerabilities").iloc[0]['count']
    
    # Get organizations count from dimension table
    organizations = db.execute_query("SELECT COUNT(*) as count FROM dim_organizations").iloc[0]['count']
    
    # Calculate average vote count (excluding zeros for more meaningful metric)
    avg_votes = db.execute_query("SELECT AVG(vote_count) as avg_votes FROM fact_reports WHERE vote_count > 0").iloc[0]['avg_votes']
    
    # First row of metrics
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        st.metric("Total Reports", f"{int(metrics['total_reports']):,}")
    with col2:
        st.metric("Bounty Reports", f"{int(metrics['bounty_reports']):,}")
    with col3:
        bounty_rate = (metrics['bounty_reports'] / metrics['total_reports'] * 100)
        st.metric("Bounty Rate", f"{bounty_rate:.1f}%")
    with col4:
        st.metric("Vulnerability Types", f"{int(vulnerability_types):,}")
    with col5:
        st.metric("Organizations", f"{int(organizations):,}")
    with col6:
        st.metric("Researchers", f"{int(metrics['researchers']):,}")
    with col7:
        st.metric("Avg Vote Count", f"{avg_votes:.1f}")
    
    st.markdown("---")
    
    top_vuln = db.execute_query('SELECT weakness_name FROM vw_vulnerability_metrics ORDER BY total_reports DESC LIMIT 1').iloc[0]['weakness_name']
    
    st.metric("TOP Threat", top_vuln)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 1rem 1.25rem; border-radius: 0.75rem; border-left: 5px solid #1d4ed8; margin-top: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);'>
        <p style='color: #ffffff; font-size: 0.95rem; margin: 0; line-height: 1.6;'><strong style='color: #dbeafe; font-size: 1.05rem;'>{top_vuln}</strong> is the most reported vulnerability type with the highest occurrence across all programs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Threat Landscape")
        top_vulns = db.execute_query("""
            SELECT weakness_name, total_reports, bounty_rate
            FROM vw_vulnerability_metrics
            ORDER BY total_reports DESC
            LIMIT 10
        """)
        
        # Gradient color based on bounty rate
        fig = px.bar(top_vulns, x='total_reports', y='weakness_name',
                     orientation='h',
                     color='bounty_rate',
                     color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                     labels={'total_reports': 'Reports', 'weakness_name': '', 'bounty_rate': 'Bounty %'})
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a1a1a', size=11),
            xaxis=dict(gridcolor='#e0e0e0', showgrid=True),
            yaxis=dict(categoryorder='total ascending', gridcolor='#e0e0e0'),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Bounty %", thickness=10, len=0.7)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight box
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 3px solid #8b5cf6; margin-top: 0.5rem;'>
            <p style='color: #4a4a4a; font-size: 0.85rem; margin: 0;'>
                <strong style='color: #8b5cf6;'>Key Insight:</strong> Color intensity shows bounty success rate. 
                Greener = higher payouts, indicating valuable vulnerabilities.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Program Performance Matrix")
        top_orgs = db.execute_query("""
            SELECT team_name, total_reports, bounty_rate, avg_votes
            FROM vw_organization_metrics
            ORDER BY total_reports DESC
            LIMIT 15
        """)
        
        # Scatter plot: Volume vs Quality
        fig = px.scatter(top_orgs, 
                        x='total_reports', 
                        y='bounty_rate',
                        size='avg_votes',
                        hover_data=['team_name'],
                        color='bounty_rate',
                        color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                        labels={'total_reports': 'Report Volume', 'bounty_rate': 'Bounty Rate (%)', 'avg_votes': 'Community Engagement'})
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a1a1a', size=11),
            xaxis=dict(gridcolor='#e0e0e0', showgrid=True, title='Report Volume'),
            yaxis=dict(gridcolor='#e0e0e0', showgrid=True, title='Bounty Rate (%)'),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Bounty %", thickness=10, len=0.7)
        )
        fig.update_traces(marker=dict(line=dict(width=1, color='#ffffff')))
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight box
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 3px solid #10b981; margin-top: 0.5rem;'>
            <p style='color: #4a4a4a; font-size: 0.85rem; margin: 0;'>
                <strong style='color: #10b981;'>Performance Map:</strong> Top-right quadrant = high volume + high payouts (elite programs). 
                Bubble size = community engagement level.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Recent Activity")
    recent = db.execute_query("""
        SELECT id, title, team_name, weakness_name, created_at, 
               CASE WHEN has_bounty THEN 'Yes' ELSE 'No' END as bounty
        FROM raw_reports
        WHERE created_at IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 15
    """)
    render_table(recent, height=400)

elif page == "Threat Intelligence":
    st.title("Threat Intelligence")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Deep-dive analysis of security weaknesses, attack patterns, and economic incentives driving the vulnerability disclosure ecosystem</p>", unsafe_allow_html=True)
    
    st.markdown("**Filters**")
    col_f1, col_f2 = st.columns([3, 2])
    with col_f1:
        st.markdown("*Minimum Reports*")
        st.caption("Filter to show only vulnerability types with at least this many reports. Higher values focus on more common vulnerabilities.")
        min_reports = st.slider("Minimum Reports", 0, 500, 50, 25, help="Filter vulnerabilities by minimum report count", label_visibility="collapsed")
    with col_f2:
        st.markdown("*Show Top N*")
        st.caption("Limit the number of vulnerability types displayed in charts and tables.")
        top_n = st.selectbox("Show Top N", [10, 20, 50, 100, "All"], index=0, help="Limit number of results", label_visibility="collapsed")
    
    # Fetch data with filters
    vuln_df = db.execute_query("""
        SELECT * FROM vw_vulnerability_metrics
        ORDER BY total_reports DESC
    """)
    
    # Apply minimum reports filter
    vuln_df = vuln_df[vuln_df['total_reports'] >= min_reports]
    
    # Apply top N limit for metrics and charts
    if top_n != "All":
        vuln_df_display = vuln_df.head(int(top_n))
    else:
        vuln_df_display = vuln_df
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Types", len(vuln_df_display))
    with col2:
        st.metric("Avg Bounty Rate", f"{vuln_df_display['bounty_rate'].mean():.1f}%")
    with col3:
        st.metric("Total Reports", f"{vuln_df_display['total_reports'].sum():,}")
    with col4:
        st.metric("Avg Votes", f"{vuln_df_display['avg_votes'].mean():.1f}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Volume vs Bounty Success")
        # Scatter plot
        fig = px.scatter(vuln_df_display.head(30), 
                        x='total_reports', 
                        y='bounty_rate',
                        size='avg_votes',
                        hover_data=['weakness_name'],
                        color='bounty_rate',
                        color_continuous_scale='Turbo',
                        labels={'total_reports': 'Total Reports', 'bounty_rate': 'Bounty Rate (%)', 'avg_votes': 'Avg Votes'})
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a1a1a', size=10),
            xaxis=dict(gridcolor='#e0e0e0', showgrid=True),
            yaxis=dict(gridcolor='#e0e0e0', showgrid=True),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Bounty %", thickness=8, len=0.6)
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color='#ffffff')))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top Threats by Bounty Rate")
        top_bounty = vuln_df_display.nlargest(10, 'bounty_rate')
        fig = px.bar(top_bounty, 
                     x='bounty_rate', 
                     y='weakness_name',
                     orientation='h',
                     color='total_reports',
                     color_continuous_scale='Plasma',
                     labels={'bounty_rate': 'Bounty Rate (%)', 'weakness_name': '', 'total_reports': 'Reports'})
        fig.update_layout(
            height=350,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a1a1a', size=10),
            xaxis=dict(gridcolor='#e0e0e0', showgrid=True),
            yaxis=dict(categoryorder='total ascending', gridcolor='#e0e0e0'),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Reports", thickness=8, len=0.6)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Insight box
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 1.2rem; border-radius: 10px; border-left: 4px solid #6366f1; margin-bottom: 1rem;'>
        <p style='color: #e0e7ff; font-size: 0.9rem; margin: 0; line-height: 1.6;'>
            <strong style='color: #a5b4fc;'>Strategic Insight:</strong> High bounty rates indicate valuable vulnerabilities that organizations prioritize. 
            Focus security efforts on top-right quadrant vulnerabilities (high volume + high bounty rate) for maximum impact.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data table with sort option
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader("Detailed Breakdown")
    with col_t2:
        st.markdown("*Sort By*")
        sort_by = st.selectbox("Sort By", ["Reports", "Bounty Rate"], help="Sort table by metric", label_visibility="collapsed")
    
    # Apply sort to table data
    table_df = vuln_df_display.copy()
    if sort_by == "Bounty Rate":
        table_df = table_df.sort_values('bounty_rate', ascending=False)
    
    render_table(
        table_df[['weakness_name', 'total_reports', 'bounty_reports', 'avg_votes', 'bounty_rate']],
        height=400
    )

elif page == "Program Benchmarks":
    st.title("Program Benchmarks")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Comparative analysis of security program maturity, researcher engagement, and bounty investment across industry leaders</p>", unsafe_allow_html=True)
    
    st.markdown("**Filters**")
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        st.markdown("*Minimum Reports*")
        st.caption("Show organizations with at least this many total reports. Use higher values to focus on more active programs.")
        min_reports_org = st.slider("Minimum Reports", 0, 200, 20, 10, help="Filter organizations by minimum report count", label_visibility="collapsed")
    with col_f2:
        st.markdown("*Minimum Bounty Rate (%)*")
        st.caption("Filter to organizations that award bounties on at least this percentage of reports. Higher values show more generous programs.")
        min_bounty_rate = st.slider("Minimum Bounty Rate (%)", 0, 100, 0, 5, help="Filter by minimum bounty success rate", label_visibility="collapsed")
    
    org_df = db.execute_query("""
        SELECT * FROM vw_organization_metrics
        ORDER BY total_reports DESC
    """)
    
    # Apply filters
    org_df = org_df[(org_df['total_reports'] >= min_reports_org) & (org_df['bounty_rate'] >= min_bounty_rate)]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Organizations", len(org_df))
    with col2:
        st.metric("Avg Reports/Org", f"{org_df['total_reports'].mean():.0f}")
    with col3:
        st.metric("Avg Bounty Rate", f"{org_df['bounty_rate'].mean():.1f}%")
    with col4:
        st.metric("Total Reports", f"{org_df['total_reports'].sum():,}")
    
    st.markdown("---")
    
    # Performance Matrix Scatter Plot
    st.subheader("Program Performance Quadrant Analysis")
    
    fig = px.scatter(org_df.head(50), 
                    x='total_reports', 
                    y='bounty_rate',
                    size='avg_votes',
                    hover_data=['team_name'],
                    color='bounty_rate',
                    color_continuous_scale=['#dc2626', '#f59e0b', '#10b981', '#06b6d4'],
                    labels={'total_reports': 'Report Volume', 'bounty_rate': 'Bounty Rate (%)', 'avg_votes': 'Community Votes'})
    fig.update_layout(
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1a1a1a', size=11),
        xaxis=dict(gridcolor='#e0e0e0', showgrid=True, title='Report Volume'),
        yaxis=dict(gridcolor='#e0e0e0', showgrid=True, title='Bounty Success Rate (%)'),
        margin=dict(l=0, r=20, t=0, b=0),
        coloraxis_colorbar=dict(title="Bounty %", thickness=10, len=0.7)
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='#ffffff')))
    st.plotly_chart(fig, use_container_width=True)
    
    # Insight box
    st.markdown("""
    <div style='background: linear-gradient(135deg, #064e3b 0%, #065f46 100%); padding: 1.2rem; border-radius: 10px; border-left: 4px solid #10b981; margin-bottom: 1rem;'>
        <p style='color: #d1fae5; font-size: 0.9rem; margin: 0; line-height: 1.6;'>
            <strong style='color: #6ee7b7;'>Elite Programs:</strong> Top-right quadrant organizations demonstrate both high volume and high bounty rates - 
            these are mature security programs that attract quality researchers and reward valuable findings generously.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Detailed Organization Data")
    render_table(
        org_df[['team_name', 'total_reports', 'bounty_reports', 'avg_votes', 'bounty_rate']],
        height=400
    )

elif page == "Community Analytics":
    st.title("Community Analytics")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Security researcher ecosystem analysis: contribution patterns, quality metrics, and community engagement dynamics</p>", unsafe_allow_html=True)
    
    researcher_df = db.execute_query("""
        SELECT * FROM vw_reporter_metrics
        ORDER BY total_reports DESC
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Researchers", len(researcher_df))
    with col2:
        st.metric("Avg Reports", f"{researcher_df['total_reports'].mean():.0f}")
    with col3:
        st.metric("Avg Bounty Rate", f"{researcher_df['bounty_rate'].mean():.1f}%")
    with col4:
        st.metric("Total Reports", f"{researcher_df['total_reports'].sum():,}")
    
    st.markdown("---")
    
    render_table(
        researcher_df[['reporter_username', 'total_reports', 'bounty_reports', 'avg_votes', 'bounty_rate']].head(100),
        height=600
    )

elif page == "Market Evolution":
    st.title("Market Evolution")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Temporal analysis of vulnerability disclosure market dynamics, program growth trajectories, and emerging security trends</p>", unsafe_allow_html=True)
    
    trend_df = db.execute_query("""
        SELECT * FROM vw_time_trends
        ORDER BY month
    """)
    
    st.subheader("Report Volume Over Time")
    
    # Add padding columns to prevent toolbar overflow
    col_left, col_chart, col_right = st.columns([0.05, 0.9, 0.05])
    
    with col_chart:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_df['month'], y=trend_df['total_reports'],
                                 mode='lines+markers', name='Total Reports', line=dict(width=3, color='#8b5cf6')))
        fig.add_trace(go.Scatter(x=trend_df['month'], y=trend_df['bounty_reports'],
                                 mode='lines+markers', name='Bounty Reports', line=dict(width=3, color='#10b981')))
        fig.update_layout(
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1a1a1a'),
            xaxis=dict(gridcolor='#e0e0e0'),
            yaxis=dict(gridcolor='#e0e0e0'),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

elif page == "Strategic Insights":
    st.title("Strategic Insights & Recommendations")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Executive intelligence briefings with data-driven recommendations for optimizing security investments and program effectiveness</p>", unsafe_allow_html=True)
    
    # Executive Summary Metrics
    st.markdown("### Executive Summary")
    
    summary_stats = db.execute_query("""
        SELECT 
            (SELECT COUNT(*) FROM raw_reports) as total_reports,
            (SELECT COUNT(*) FROM raw_reports WHERE has_bounty = TRUE) as total_bounties,
            (SELECT COUNT(DISTINCT team_handle) FROM raw_reports WHERE team_handle IS NOT NULL AND team_handle != '') as total_orgs,
            (SELECT COUNT(DISTINCT reporter_username) FROM raw_reports WHERE reporter_username IS NOT NULL AND reporter_username != '') as total_reporters,
            (SELECT COUNT(DISTINCT weakness_name) FROM raw_reports WHERE weakness_name IS NOT NULL AND weakness_name != '') as total_vuln_types
    """).iloc[0]
    
    bounty_rate = (summary_stats['total_bounties'] / summary_stats['total_reports'] * 100) if summary_stats['total_reports'] > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Reports", f"{summary_stats['total_reports']:,}")
    with col2:
        st.metric("Bounties Awarded", f"{summary_stats['total_bounties']:,}")
    with col3:
        st.metric("Overall Bounty Rate", f"{bounty_rate:.1f}%")
    with col4:
        st.metric("Active Organizations", f"{summary_stats['total_orgs']:,}")
    with col5:
        st.metric("Security Researchers", f"{summary_stats['total_reporters']:,}")
    
    st.markdown("---")
    
    st.markdown("### Key Insights")
    high_value_vulns = db.execute_query("""
        SELECT COUNT(*) as count
        FROM vw_vulnerability_metrics
        WHERE bounty_rate > 60 AND total_reports > 100
    """).iloc[0]['count']
    
    top_3_vulns = db.execute_query("""
        SELECT SUM(total_reports) as top_3_reports
        FROM (SELECT total_reports FROM vw_vulnerability_metrics ORDER BY total_reports DESC LIMIT 3)
    """).iloc[0]['top_3_reports']
    
    top_3_concentration = (top_3_vulns / summary_stats['total_reports'] * 100) if summary_stats['total_reports'] > 0 else 0
    
    elite_researchers = db.execute_query("""
        SELECT COUNT(*) as count
        FROM vw_reporter_metrics
        WHERE bounty_rate > 70 AND total_reports >= 10
    """).iloc[0]['count']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color: #e8f4fd; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; margin-bottom: 1rem;'>
            <h4 style='margin-top: 0; color: #1f77b4;'>Market Concentration Analysis</h4>
            <ul style='margin-bottom: 0;'>
                <li>Top 3 vulnerability types account for {:.1f}% of all reports, showing high concentration in specific attack vectors</li>
                <li>{} vulnerability types demonstrate both high volume (100+ reports) and high bounty rates (60%+)</li>
                <li>{} researchers maintain 70%+ bounty rates with 10+ reports, representing the quality tier</li>
                <li>{} distinct vulnerability types identified, with distribution heavily skewed toward common classes</li>
            </ul>
        </div>
        """.format(top_3_concentration, high_value_vulns, elite_researchers, summary_stats['total_vuln_types']), unsafe_allow_html=True)
    
    with col2:
        top_vuln = db.execute_query("""
            SELECT weakness_name, total_reports, bounty_rate
            FROM vw_vulnerability_metrics
            ORDER BY total_reports DESC
            LIMIT 1
        """).iloc[0]
        
        second_vuln = db.execute_query("""
            SELECT weakness_name, total_reports, bounty_rate
            FROM vw_vulnerability_metrics
            ORDER BY total_reports DESC
            LIMIT 1 OFFSET 1
        """).iloc[0]
        
        st.markdown("""
        <div style='background-color: #fff3cd; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #ffc107; margin-bottom: 1rem;'>
            <h4 style='margin-top: 0; color: #856404;'>Critical Focus Areas</h4>
            <p><strong>Primary Threat:</strong> {} accounts for {:,} reports with a {:.1f}% bounty rate</p>
            <p><strong>Secondary Threat:</strong> {} accounts for {:,} reports with a {:.1f}% bounty rate</p>
            <p style='margin-bottom: 0;'>These two categories represent a significant portion of the attack surface. Prioritizing automated detection and preventive controls in these areas will yield maximum return on security investment.</p>
        </div>
        """.format(
            top_vuln['weakness_name'], top_vuln['total_reports'], top_vuln['bounty_rate'],
            second_vuln['weakness_name'], second_vuln['total_reports'], second_vuln['bounty_rate']
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top Security Threats
    st.markdown("### Top Security Threats")
    
    top_vulns = db.execute_query("""
        SELECT weakness_name, total_reports, bounty_rate, avg_votes
        FROM vw_vulnerability_metrics
        ORDER BY total_reports DESC
        LIMIT 5
    """)
    
    for idx, row in top_vulns.iterrows():
        with st.expander(f"{idx+1}. {row['weakness_name']} ({row['total_reports']} reports)"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Reports", f"{row['total_reports']:,}")
                st.metric("Bounty Rate", f"{row['bounty_rate']:.1f}%")
            with col2:
                st.metric("Avg Community Votes", f"{row['avg_votes']:.1f}")
            
            st.markdown(f"""
            **Risk Assessment:**
            - Frequency: {'High' if row['total_reports'] > 500 else 'Medium' if row['total_reports'] > 200 else 'Low'}
            - Bounty Success: {'High' if row['bounty_rate'] > 60 else 'Medium' if row['bounty_rate'] > 40 else 'Low'}
            - Community Interest: {'High' if row['avg_votes'] > 5 else 'Medium' if row['avg_votes'] > 2 else 'Low'}
            
            **Recommendation:** {'High priority - implement automated detection and security controls' if row['bounty_rate'] > 60 else 'Medium priority - enhance testing and code review' if row['bounty_rate'] > 40 else 'Standard security review and monitoring'}
            """)
    
    st.markdown("---")
    
    st.markdown("### Strategic Recommendations")
    low_bounty_orgs = db.execute_query("""
        SELECT COUNT(*) as count
        FROM vw_organization_metrics
        WHERE bounty_rate < 40 AND total_reports >= 10
    """).iloc[0]['count']
    
    high_bounty_orgs = db.execute_query("""
        SELECT COUNT(*) as count
        FROM vw_organization_metrics
        WHERE bounty_rate > 70 AND total_reports >= 10
    """).iloc[0]['count']
    
    low_volume_vulns = db.execute_query("""
        SELECT COUNT(*) as count
        FROM vw_vulnerability_metrics
        WHERE total_reports < 10
    """).iloc[0]['count']
    
    st.markdown("""
    <div style='background-color: #d4edda; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #28a745; margin-bottom: 1rem;'>
        <h4 style='margin-top: 0; color: #155724;'>1. Focus on High-Impact Vulnerability Classes</h4>
        <p><strong>Data Finding:</strong> Top 3 vulnerability types account for {:.1f}% of all reports.</p>
        <p><strong>Action:</strong> Allocate 60-70% of security tooling budget to automated detection and prevention for these high-concentration areas. 
        Deploy SAST/DAST tools specifically configured for these vulnerability patterns.</p>
        <p style='margin-bottom: 0;'><strong>Expected Impact:</strong> Could reduce report volume by 30-40% through proactive detection.</p>
    </div>
    
    <div style='background-color: #d4edda; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #28a745; margin-bottom: 1rem;'>
        <h4 style='margin-top: 0; color: #155724;'>2. Elevate Low-Performing Programs</h4>
        <p><strong>Data Finding:</strong> {} organizations have <40% bounty rates despite 10+ reports, while {} maintain >70% rates.</p>
        <p><strong>Action:</strong> Create a mentorship program pairing high-performing organizations with struggling programs. 
        Share response time metrics, triage processes, and bounty determination frameworks.</p>
        <p style='margin-bottom: 0;'><strong>Expected Impact:</strong> Improving low performers to median (53%) could increase overall platform quality by 15-20%.</p>
    </div>
    
    <div style='background-color: #d4edda; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #28a745; margin-bottom: 1rem;'>
        <h4 style='margin-top: 0; color: #155724;'>3. Cultivate Elite Researcher Tier</h4>
        <p><strong>Data Finding:</strong> {} researchers maintain >70% bounty rates with 10+ reports - these are your quality drivers.</p>
        <p><strong>Action:</strong> Implement tiered incentives: priority triage for elite researchers, bonus multipliers for consistent quality, 
        and exclusive access to high-value programs. Track and prevent elite researcher churn.</p>
        <p style='margin-bottom: 0;'><strong>Expected Impact:</strong> Retaining top 20% of researchers could maintain 40-50% of platform value.</p>
    </div>
    
    <div style='background-color: #d4edda; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #28a745; margin-bottom: 1rem;'>
        <h4 style='margin-top: 0; color: #155724;'>4. Address the Long Tail</h4>
        <p><strong>Data Finding:</strong> {} vulnerability types have <10 reports each - representing emerging or niche threats.</p>
        <p><strong>Action:</strong> Create a "rare vulnerability" bonus program to incentivize discovery of uncommon attack vectors. 
        These may represent zero-day or novel attack patterns that automated tools miss.</p>
        <p style='margin-bottom: 0;'><strong>Expected Impact:</strong> Early detection of emerging threats before they become widespread.</p>
    </div>
    """.format(top_3_concentration, low_bounty_orgs, high_bounty_orgs, elite_researchers, low_volume_vulns), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Key Performance Indicators")
    
    org_stats = db.execute_query("""
        SELECT 
            AVG(bounty_rate) as avg_bounty_rate,
            AVG(total_reports) as avg_reports,
            COUNT(*) as total_programs
        FROM vw_organization_metrics
    """).iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Performance Benchmarks**
        
        - **Current Bounty Rate:** {bounty_rate:.1f}% — Target: Incremental improvement to 60%+
        - **Avg Reports/Organization:** {org_stats['avg_reports']:.0f} — Monitor for program engagement
        - **Active Programs:** {org_stats['total_programs']:,} — Track growth and retention
        - **High-Performing Programs:** Organizations with >70% bounty rates demonstrate excellence
        """)
    
    with col2:
        st.markdown("""
        **Success Indicators**
        
        - **Quality Over Quantity:** Maintain high valid report rates (>85%)
        - **Researcher Retention:** Track repeat contributors and top performers
        - **Response Time:** Organizations responding within 24-48 hours see better engagement
        - **Community Engagement:** Monitor vote counts and researcher feedback
        """)
    
    st.markdown("---")
    
    st.markdown("### Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Organization Guidelines:**
        
        - Maintain clear, comprehensive vulnerability disclosure policies
        - Respond to reports within 24-48 hours
        - Provide detailed, constructive feedback to researchers
        - Offer competitive bounty amounts aligned with severity
        - Engage actively with the security community
        - Track metrics and continuously improve processes
        """)
    
    with col2:
        st.markdown("""
        **Platform Optimization:**
        
        - Focus resources on high-volume vulnerability types
        - Provide training and resources for emerging threats
        - Recognize and reward top-performing researchers
        - Monitor seasonal trends for resource allocation
        - Share success stories and best practices
        - Invest in automated detection and prevention tools
        """)

elif page == "AI Assistant":
    # Header with clean clear button
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title("AI-Powered Assistant")
    with col2:
        # CSS to style Clear button - bigger with border, aligned right
        st.markdown("""
        <style>
        /* Clear button styling - bigger with border */
        div[data-testid="column"]:nth-child(2) {
            display: flex !important;
            justify-content: flex-end !important;
            align-items: flex-start !important;
        }
        div[data-testid="column"]:nth-child(2) button {
            background: #ffffff !important;
            border: 1px solid #d1d5db !important;
            color: #666666 !important;
            font-size: 0.9rem !important;
            padding: 0.5rem 0.75rem !important;
            border-radius: 6px !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s !important;
        }
        div[data-testid="column"]:nth-child(2) button:hover {
            color: #ef4444 !important;
            border-color: #ef4444 !important;
            background: #fef2f2 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear", key="clear-chat"):
            st.session_state.messages = []
            st.rerun()
    
    if not config.AI_ENABLED:
        st.warning("AI features require OpenAI API key. Configure it in your .env file.")
    else:
        st.success("AI Assistant is ready")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Add CSS for chat input with send arrow button
        st.markdown("""
        <style>
        /* Style chat input with send arrow button */
        [data-testid="stChatInput"] {
            position: relative !important;
        }
        [data-testid="stChatInput"] textarea {
            padding-right: 3.5rem !important;
        }
        [data-testid="stChatInput"]::before {
            content: "↑";
            position: absolute;
            right: 1.2rem;
            bottom: 1.2rem;
            font-size: 1.3rem;
            color: #ffffff;
            background: #8b5cf6;
            width: 2rem;
            height: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s, background 0.2s;
            z-index: 10;
        }
        [data-testid="stChatInput"]:focus-within::before {
            opacity: 1;
        }
        [data-testid="stChatInput"]:focus-within:hover::before {
            background: #7c3aed;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if prompt := st.chat_input("Ask about vulnerability data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        from src.ai.nlp_query import NLPQueryEngine
                        nlp_engine = NLPQueryEngine()
                        current_user = {"role": "admin", "organization": None}
                        # Pass conversation history for context
                        result = nlp_engine.process_query(prompt, current_user, st.session_state.messages[:-1])
                        
                        full_response = ""
                        
                        if result.get('sql_generated'):
                            st.markdown(f"**SQL Query:**")
                            st.code(result['sql_generated'], language='sql')
                            full_response += f"**SQL Query:**\n```sql\n{result['sql_generated']}\n```\n\n"
                            
                            if result.get('results') and len(result['results']) > 0:
                                st.markdown(f"**Results:** {len(result['results'])} rows found")
                                import pandas as pd
                                df_results = pd.DataFrame(result['results'])
                                
                                # Dynamic height based on number of rows
                                num_rows = len(df_results)
                                if num_rows == 1:
                                    table_height = 100
                                elif num_rows <= 5:
                                    table_height = 200
                                elif num_rows <= 10:
                                    table_height = 300
                                else:
                                    table_height = 400
                                
                                render_table(df_results, height=table_height)
                                
                                summary = result.get('explanation', 'Query executed successfully.')
                                st.markdown(f"**Summary:** {summary}")
                                
                                full_response += f"**Results:** {len(result['results'])} rows found\n\n"
                                full_response += f"**Summary:** {summary}"
                            else:
                                st.info("No results found for your query.")
                                explanation = result.get('explanation', 'The query executed successfully but returned no data.')
                                st.markdown(f"**Explanation:** {explanation}")
                                
                                full_response += f"No results found.\n\n**Explanation:** {explanation}"
                        else:
                            # Conversational response (no SQL generated)
                            response_text = result.get('explanation', 'I can help you with that!')
                            st.markdown(response_text)
                            full_response = response_text
                        
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

elif page == "Security Reference":
    st.title("Security Reference")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Comprehensive knowledge repository covering vulnerability taxonomies, security metrics, and industry-standard terminology</p>", unsafe_allow_html=True)
    
    st.markdown("Comprehensive glossary of common vulnerability types and security concepts.")
    
    search = st.text_input("Search for a vulnerability type", placeholder="e.g., XSS, SQL Injection...")
    
    vuln_types = db.execute_query("""
        SELECT DISTINCT weakness_name, COUNT(*) as count 
        FROM raw_reports 
        WHERE weakness_name IS NOT NULL AND weakness_name != ''
        GROUP BY weakness_name 
        ORDER BY count DESC
    """)
    
    if search:
        filtered = vuln_types[vuln_types['weakness_name'].str.contains(search, case=False, na=False)]
    else:
        filtered = vuln_types
    
    glossary = {
        "Cross-site Scripting (XSS)": {
            "description": "Malicious scripts injected into trusted websites that execute in users' browsers.",
            "impact": "Steal session cookies, redirect users, deface websites, steal sensitive data",
            "prevention": "Input validation, output encoding, Content Security Policy (CSP)",
            "severity": "Medium to High"
        },
        "SQL Injection": {
            "description": "Attackers insert malicious SQL code into application queries.",
            "impact": "Database breach, data theft, data manipulation, authentication bypass",
            "prevention": "Parameterized queries, input validation, least privilege database access",
            "severity": "Critical"
        },
        "Improper Authorization": {
            "description": "Users can access resources or perform actions they shouldn't be allowed to.",
            "impact": "Unauthorized data access, privilege escalation, account takeover",
            "prevention": "Role-based access control, proper permission checks, session management",
            "severity": "High"
        },
        "Information Disclosure": {
            "description": "Sensitive information exposed to unauthorized users.",
            "impact": "Data leakage, privacy violations, credential exposure",
            "prevention": "Proper error handling, secure configuration, data classification",
            "severity": "Low to High"
        },
        "Cross-Site Request Forgery (CSRF)": {
            "description": "Attackers trick users into performing unwanted actions on authenticated sites.",
            "impact": "Unauthorized transactions, account modifications, data changes",
            "prevention": "CSRF tokens, SameSite cookies, user confirmation for sensitive actions",
            "severity": "Medium"
        },
        "Server-Side Request Forgery (SSRF)": {
            "description": "Attacker forces server to make requests to unintended locations.",
            "impact": "Access internal systems, port scanning, data exfiltration",
            "prevention": "Input validation, whitelist allowed destinations, network segmentation",
            "severity": "High"
        },
        "Remote Code Execution": {
            "description": "Attacker can execute arbitrary code on the target system.",
            "impact": "Complete system compromise, data theft, malware installation",
            "prevention": "Input validation, secure coding practices, sandboxing",
            "severity": "Critical"
        }
    }
    
    st.markdown(f"**Showing {len(filtered)} vulnerability types**")
    
    for vuln_name in filtered['weakness_name'].head(20):
        with st.expander(f"{vuln_name} ({filtered[filtered['weakness_name']==vuln_name]['count'].values[0]} reports)"):
            if vuln_name in glossary:
                info = glossary[vuln_name]
                st.markdown(f"**Description:** {info['description']}")
                st.markdown(f"**Impact:** {info['impact']}")
                st.markdown(f"**Prevention:** {info['prevention']}")
                st.markdown(f"**Severity:** {info['severity']}")
            else:
                st.markdown(f"Common vulnerability type found in {filtered[filtered['weakness_name']==vuln_name]['count'].values[0]} reports.")
                st.markdown("*Check OWASP or CWE for detailed information.*")
    
    st.markdown("---")
    st.subheader("External Resources")
    st.markdown("""
    - [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Most critical web application security risks
    - [CWE Database](https://cwe.mitre.org/) - Common Weakness Enumeration
    - [CVSS Calculator](https://www.first.org/cvss/) - Common Vulnerability Scoring System
    - [HackerOne Hacktivity](https://hackerone.com/hacktivity) - Public disclosed reports
    """)

elif page == "Data Workbench":
    st.title("Data Workbench")
    st.markdown("<p style='color: #666666; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Interactive data exploration workspace with advanced filtering, custom queries, and export capabilities for ad-hoc analysis</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        date_filter = st.selectbox("Time Period", ["All Time", "Last 30 Days", "Last 90 Days", "Last Year"])
    
    with col2:
        org_options = db.execute_query("SELECT DISTINCT team_name FROM raw_reports WHERE team_name IS NOT NULL AND team_name != '' LIMIT 50").values.flatten().tolist()
        org = st.multiselect("Organization", ["All"] + org_options, default=["All"])
    
    search = st.text_input("Search", placeholder="Search in titles...")
    
    query = "SELECT id, title, created_at, team_name, weakness_name, has_bounty, vote_count FROM raw_reports WHERE 1=1"
    
    if date_filter == "Last 30 Days":
        query += " AND created_at >= CURRENT_DATE - INTERVAL '30 days'"
    elif date_filter == "Last 90 Days":
        query += " AND created_at >= CURRENT_DATE - INTERVAL '90 days'"
    elif date_filter == "Last Year":
        query += " AND created_at >= CURRENT_DATE - INTERVAL '1 year'"
    
    if "All" not in org and org:
        org_list = "','".join([o.replace("'", "''") for o in org])
        query += f" AND team_name IN ('{org_list}')"
    
    if search:
        query += f" AND title ILIKE '%{search}%'"
    
    query += " ORDER BY created_at DESC LIMIT 1000"
    
    df = db.execute_query(query)
    
    st.markdown(f"**Found {len(df):,} reports**")
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"hackerone_reports_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    render_table(df, height=600)

