"""Stock Alerts v2.6 - Email as Username"""
import streamlit as st
import json
import os
import yfinance as yf
import hashlib
from datetime import datetime

st.set_page_config(page_title="Stock Alerts", page_icon="📈", layout="wide")

USERS_FILE = "users.json"
RULES_FILE = "rules.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def login(email, password):
    users = load_users()
    if email in users:
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[email]['password'] == pw_hash:
            return users[email]
    return None

def register(email, password):
    users = load_users()
    if email in users:
        return False
    users[email] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'created': datetime.now().isoformat()
    }
    save_users(users)
    return True

def get_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        if not data.empty:
            return data['Close'].iloc[-1]
    except:
        pass
    return None

if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("📈 Stock Alerts - כניסה")
    tab1, tab2 = st.tabs(["כניסה", "הרשמה"])
    
    with tab1:
        with st.form("login"):
            email = st.text_input("אימייל", placeholder="example@gmail.com")
            pw = st.text_input("סיסמה", type="password")
            if st.form_submit_button("התחבר"):
                profile = login(email, pw)
                if profile:
                    st.session_state.user = {'email': email, **profile}
                    st.rerun()
                else:
                    st.error("אימייל או סיסמה שגויים")
    
    with tab2:
        with st.form("register"):
            new_email = st.text_input("אימייל", placeholder="example@gmail.com")
            new_pw = st.text_input("סיסמה", type="password")
            confirm_pw = st.text_input("אימות סיסמה", type="password")
            if st.form_submit_button("הרשם"):
                if new_pw != confirm_pw:
                    st.error("הסיסמאות לא זהות")
                elif not new_email or '@' not in new_email:
                    st.error("אנא הכנס אימייל תקין")
                elif register(new_email, new_pw):
                    st.success("נרשמת בהצלחה! עבור לכרטיסיית כניסה")
                else:
                    st.error("האימייל כבר רשום")
else:
    st.sidebar.title(f"שלום")
    st.sidebar.caption(st.session_state.user['email'])
    if st.sidebar.button("יציאה"):
        st.session_state.user = None
        st.rerun()
    
    st.title("📊 לוח התראות")
    
    st.subheader("הוסף התראה חדשה")
    col1, col2, col3 = st.columns(3)
    symbol = col1.text_input("סימול", "AAPL")
    min_price = col2.number_input("מחיר מינימום", 0.0)
    max_price = col3.number_input("מחיר מקסימום", 999.0)
    
    if st.button("בדוק מחיר"):
        price = get_price(symbol)
        if price:
            st.metric(symbol, f"${price:.2f}")
            if min_price <= price <= max_price:
                st.success("✅ המחיר בטווח!")
            else:
                st.warning("⚠️ המחיר מחוץ לטווח")
        else:
            st.error("לא נמצא")
    
    st.caption(f"v2.6 | {datetime.now().strftime('%H:%M:%S')}")
