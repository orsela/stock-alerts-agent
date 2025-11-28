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
    color: #ffffff;
}

/* Login Screen */
.login-container {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px;
    background: rgba(30, 41, 59, 0.8);
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
}

.app-logo {
    text-align: center;
    margin-bottom: 30px;
}

.app-title {
    font-size: 28px;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Market Cards */
.market-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 15px;
    padding: 15px;
    margin: 10px 5px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    text-align: center;
}

.market-name {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 5px;
}

.market-value {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    margin: 5px 0;
}

.market-change-positive {
    font-size: 14px;
    color: #10b981;
    font-weight: 600;
}

.market-change-negative {
    font-size: 14px;
    color: #ef4444;
    font-weight: 600;
}

/* Stock Cards */
.stock-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 20px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.stock-symbol {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 10px;
}

.stock-price {
    font-size: 28px;
    font-weight: 700;
    color: #3b82f6;
}

.stock-target {
    font-size: 14px;
    color: #94a3b8;
    margin-top: 5px;
}

/* Bottom Navigation */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(59, 130, 246, 0.2);
    padding: 10px 0;
    z-index: 9999;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
}

.nav-items {
    display: flex;
    justify-content: space-around;
    align-items: center;
    max-width: 600px;
    margin: 0 auto;
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #64748b;
    font-size: 11px;
    text-decoration: none;
    cursor: pointer;
    padding: 5px 15px;
    transition: all 0.3s ease;
}

.nav-item:hover, .nav-item.active {
    color: #3b82f6;
}

.nav-icon {
    font-size: 24px;
    margin-bottom: 5px;
}

.nav-add-button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border-radius: 50%;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: white;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    margin-top: -30px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 16px;
    width: 100%;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

/* Forms */
.stTextInput > div > div > input {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: 10px;
    color: white;
    padding: 12px;
    font-size: 16px;
}

/* Header */
.main-header {
    font-size: 24px;
    font-weight: 700;
    text-align: right;
    color: #ffffff;
    padding: 20px 0;
    margin-bottom: 20px;
}

/* Spacing for bottom nav */
.main-content {
    padding-bottom: 100px;
}

/* RTL Support */
.stApp {
    direction: rtl;
}

</style>
"""

# ============================================================================
# DATA MANAGEMENT CLASSES
# ============================================================================

class UserManager:
    @staticmethod
    def _load_users():
        if not os.path.exists(USERS_FILE):
            return {}
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def _save_users(users):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

    @staticmethod
    def register_user(username, password, email, phone=""):
        users = UserManager._load_users()
        if username in users:
            return False, "שם משתמש תפוס"
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        users[username] = {
            "password": hashed_pw,
            "email": email,
            "phone": phone,
            "created_at": datetime.now().isoformat()
        }
        UserManager._save_users(users)
        logger.info(f"✓ New user registered: {username}")
        return True, "המשתמש נוצר בהצלחה!"

    @staticmethod
    def login_user(username, password):
        users = UserManager._load_users()
        if username not in users:
            return None
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password"] == hashed_pw:
            logger.info(f"✓ User logged in: {username}")
            return users[username]
        return None

class DataManager:
    @staticmethod
    def load_user_rules(username):
        if not os.path.exists(RULES_FILE):
            return []
        try:
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                all_rules = json.load(f)
                return all_rules.get(username, [])
        except:
            return []

    @staticmethod
    def save_user_rules(username, rules):
        if not os.path.exists(RULES_FILE):
            all_rules = {}
        else:
            try:
                with open(RULES_FILE, 'r', encoding='utf-8') as f:
                    all_rules = json.load(f)
            except:
                all_rules = {}
        
        all_rules[username] = rules
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_rules, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved {len(rules)} rules for {username}")

    @staticmethod
    def get_price(symbol, max_retries=2):
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(symbol)
                data = stock.history(period="1d")
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    prev_close = stock.info.get('previousClose', price)
                    change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
                    return round(price, 2), round(change, 2)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                logger.error(f"✗ Error fetching {symbol}: {e}")
        return None, None

class NotificationManager:
    def __init__(self):
        try:
            self.sender_email = st.secrets["email"]["sender_email"]
            self.sender_password = st.secrets["email"]["sender_password"]
            self.is_configured = True
            logger.info("✓ Email configured")
        except:
            self.is_configured = False
            logger.warning("⚠ Email not configured - using mock mode")

    def send_email(self, target_email, username, symbol, price, condition):
        if not self.is_configured:
            st.toast(f"📧 Mock: התראה נשלחה ל-{target_email}", icon="✉️")
            return True

        subject = f"🚀 התראת מניה: {symbol}"
        body = f"""
שלום {username},

מניה: {symbol}
מחיר נוכחי: ${price:.2f}
תנאי: {condition}
זמן: {datetime.now().strftime('%d/%m/%Y %H:%M')}

---
Stock Sentinel Pro
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = target_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            logger.info(f"✓ Email sent to {target_email}")
            return True
        except Exception as e:
            logger.error(f"✗ Email failed: {e}")
            return False

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'user' not in st.session_state:
    st.session_state.user = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"

if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False

if 'rules' not in st.session_state:
    st.session_state.rules = []

if 'last_alert_time' not in st.session_state:
    st.session_state.last_alert_time = {}

notifier = NotificationManager()

# ============================================================================
# APPLY THEME
# ============================================================================

st.markdown(MOBILE_THEME, unsafe_allow_html=True)

# ============================================================================
# LOGIN/REGISTER SCREEN
# ============================================================================

if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Logo
        st.markdown('<div class="app-logo">🦅</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-title">Stock Sentinel Pro</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #64748b; font-size: 14px;">מערכת ניהול התראות מניות מ
