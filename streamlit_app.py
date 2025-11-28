"""
🦅 Stock Sentinel v4.0 - Multi-User Mobile-First Edition
נבנה לפי עיצוב UI/UX מקצועי עם Bottom Navigation
"""

import streamlit as st
import json
import os
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
import hashlib
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Stock Sentinel Pro", 
    page_icon="🦅", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

USERS_FILE = "users_db.json"
RULES_FILE = "rules_db.json"
COOLDOWN_MINUTES = 60

# ============================================================================
# MOBILE-FIRST DARK THEME CSS
# ============================================================================

MOBILE_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap');

* {
    font-family: 'Heebo', sans-serif !important;
}

.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
