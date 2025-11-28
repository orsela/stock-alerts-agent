"""Stock Alerts v2.5 - Simple Multi-User"""
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

def login(username, password):
    users = load_users()
    if username in users:
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[username]['password'] == pw_hash:
            return users[username]
    return None

def register(username, password, email):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'email': email,
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
            user = st.text_input("שם משתמש")
            pw = st.text_input("סיסמה", type="password")
            if st.form_submit_button("התחבר"):
                profile = login(user, pw)
                if profile:
                    st.session_state.user = {'username': user, **profile}
                    st.rerun()
                else:
                    st.error("שגיאה בהתחברות")
    
    with tab2:
        with st.form("register"):
            new_user = st.text_input("שם משתמש חדש")
            new_pw = st.text_input("סיסמה חדשה", type="password")
            email = st.text_input("אימייל")
            if st.form_submit_button("הרשם"):
                if register(new_user, new_pw, email):
                    st.success("נרשמת בהצלחה!")
                else:
                    st.error("שם המשתמש תפוס")
else:
    st.sidebar.title(f"שלום {st.session_state.user['username']}")
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
    
    st.caption(f"v2.5 | {datetime.now().strftime('%H:%M:%S')}")
