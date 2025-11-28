import streamlit as st
import json
import os

# Dark theme CSS
DARK_THEME = """
<style>
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    .main-header {
        text-align: right;
        font-size: 28px;
        font-weight: bold;
        color: #ffffff;
        padding: 10px 0;
    }
    .index-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 5px;
        text-align: center;
    }
    .index-name {
        color: #888;
        font-size: 14px;
    }
    .index-value {
        color: #fff;
        font-size: 20px;
        font-weight: bold;
    }
    .index-change-up {
        color: #00ff88;
        font-size: 14px;
    }
    .index-change-down {
        color: #ff4444;
        font-size: 14px;
    }
    .alert-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #3b82f6;
    }
    .stock-symbol {
        font-size: 18px;
        font-weight: bold;
        color: #fff;
    }
    .stock-price {
        font-size: 24px;
        color: #fff;
    }
    .target-price {
        color: #00ff88;
        font-size: 14px;
    }
    .section-title {
        color: #fff;
        font-size: 20px;
        font-weight: bold;
        text-align: right;
        margin: 20px 0 10px 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 30px;
        font-size: 16px;
        width: 100%;
    }
    .stTextInput > div > div > input {
        background-color: #1a1a2e;
        color: #fff;
        border: 1px solid #333;
        border-radius: 8px;
    }
    .stNumberInput > div > div > input {
        background-color: #1a1a2e;
        color: #fff;
        border: 1px solid #333;
    }
    .progress-bar {
        height: 6px;
        background: #333;
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00ff88, #ff4444);
    }
</style>
"""

RULES_FILE = "rules.json"

def load_rules():
    if not os.path.exists(RULES_FILE):
        return []
    try:
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=2)

if 'rules' not in st.session_state:
    st.session_state.rules = load_rules()
    if not st.session_state.rules:
        st.session_state.rules = [
            {"symbol": "TSLA", "min_price": 145.50, "max_price": 320.0, "target": 189.0, "notify_email": True, "notify_whatsapp": True, "active": True},
            {"symbol": "AAPL", "min_price": 122.50, "max_price": 230.0, "target": 22.50, "notify_email": True, "notify_whatsapp": False, "active": True},
        ]

if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"

st.set_page_config(page_title="Stock Alerts", layout="wide", initial_sidebar_state="collapsed")
st.markdown(DARK_THEME, unsafe_allow_html=True)

# Navigation
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Dashboard", use_container_width=True):
        st.session_state.current_page = "dashboard"
with col2:
    if st.button("Alerts", use_container_width=True):
        st.session_state.current_page = "alerts"
with col3:
    if st.button("Watchlist", use_container_width=True):
        st.session_state.current_page = "watchlist"
with col4:
    if st.button("Settings", use_container_width=True):
        st.session_state.current_page = "settings"

st.divider()

if st.session_state.current_page == "dashboard":
    st.markdown('<div class="main-header">שלום, משתמש</div>', unsafe_allow_html=True)
    
    # Market indices
    idx1, idx2, idx3 = st.columns(3)
    with idx1:
        st.markdown('''
        <div class="index-card">
            <div class="index-name">ת"א 35</div>
            <div class="index-value">117.45</div>
            <div class="index-change-down">▼ -1.37%</div>
        </div>
        ''', unsafe_allow_html=True)
    with idx2:
        st.markdown('''
        <div class="index-card">
            <div class="index-name">נאסד"ק</div>
            <div class="index-value">+1,233.68</div>
            <div class="index-change-up">▲ +0.93%</div>
        </div>
        ''', unsafe_allow_html=True)
    with idx3:
        st.markdown('''
        <div class="index-card">
            <div class="index-name">S&P 500</div>
            <div class="index-value">222.66</div>
            <div class="index-change-down">▼ -0.93%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">התראות חמות</div>', unsafe_allow_html=True)
    
    hot1, hot2, hot3 = st.columns(3)
    with hot1:
        st.markdown('''
        <div class="alert-card">
            <div class="stock-symbol">TSLA</div>
            <div class="stock-price">132.00</div>
            <div class="target-price">מחיר יעד: 115.00 ↗</div>
        </div>
        ''', unsafe_allow_html=True)
    with hot2:
        st.markdown('''
        <div class="alert-card">
            <div class="stock-symbol">AAPL</div>
            <div class="stock-price">285.00</div>
            <div class="target-price">מחיר יעד: 258.00 ↗</div>
        </div>
        ''', unsafe_allow_html=True)
    with hot3:
        st.markdown('''
        <div class="alert-card">
            <div class="stock-symbol">NVDA</div>
            <div class="stock-price">14.75</div>
            <div class="target-price">מחיר יעד: 138.00 ↗</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">רשימת מעקב</div>', unsafe_allow_html=True)
    
    for rule in st.session_state.rules[:3]:
        col_a, col_b, col_c = st.columns([2, 3, 1])
        with col_a:
            st.markdown(f"**{rule['symbol']}**")
            st.caption("מחיר ויעד")
        with col_b:
            st.write(f"${rule.get('target', 0):.2f}")
        with col_c:
            change = "+213.90" if rule['symbol'] == 'TSLA' else "-68.2%"
            color = "green" if '+' in change else "red"
            st.markdown(f"<span style='color:{color}'>{change}</span>", unsafe_allow_html=True)

elif st.session_state.current_page == "alerts":
    st.markdown('<div class="main-header">התראות</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["הופעלו לאחרונה", "פעילות"])
    
    with tab1:
        for i, rule in enumerate(st.session_state.rules):
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**{rule['symbol']}**")
                with col2:
                    progress = ((rule.get('target', 0) - rule['min_price']) / (rule['max_price'] - rule['min_price'])) * 100 if rule['max_price'] != rule['min_price'] else 50
                    st.markdown(f"{rule['min_price']:.2f}-{rule['max_price']:.2f}")
                    st.progress(min(max(progress/100, 0), 1))
                    st.caption(f"יעד {rule.get('target', 0):.2f}")
                with col3:
                    rule['active'] = st.toggle("פעיל", value=rule.get('active', True), key=f"toggle_{i}")
                st.divider()

elif st.session_state.current_page == "watchlist":
    st.markdown('<div class="main-header">יצירת התראה חדשה</div>', unsafe_allow_html=True)
    
    symbol = st.text_input("חפש מניה...", placeholder="AAPL, TSLA, NVDA...")
    
    col1, col2 = st.columns(2)
    with col1:
        price_type = st.radio("סוג מחיר", ["מחיר יעד", "שינוי באחוזים"], horizontal=True)
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("מתחת ↓", use_container_width=True):
            pass
    with col4:
        if st.button("מעל ↑", use_container_width=True):
            pass
    
    target_price = st.number_input("מחיר יעד", min_value=0.0, value=2580.0, step=0.5)
    st.slider("בחר מחיר", min_value=0.0, max_value=5000.0, value=target_price)
    
    note = st.text_area("הערה אישית", placeholder="הוסף הערה...")
    
    with st.expander("חזרתיות"):
        st.selectbox("תדירות", ["פעם אחת", "יומי", "שבועי"])
    
    if st.button("צור התראה", use_container_width=True, type="primary"):
        if symbol:
            new_rule = {
                "symbol": symbol.upper(),
                "min_price": target_price * 0.9,
                "max_price": target_price * 1.1,
                "target": target_price,
                "notify_email": True,
                "notify_whatsapp": True,
                "active": True,
                "note": note
            }
            st.session_state.rules.append(new_rule)
            save_rules(st.session_state.rules)
            st.success(f"התראה נוצרה עבור {symbol.upper()}!")
            st.rerun()

elif st.session_state.current_page == "settings":
    st.markdown('<div class="main-header">הגדרות</div>', unsafe_allow_html=True)
    
    st.subheader("התראות")
    email_alerts = st.toggle("התראות במייל", value=True)
    whatsapp_alerts = st.toggle("התראות בווטסאפ", value=True)
    
    st.subheader("חשבונות מחוברים")
    st.text_input("אימייל", value="orsela@gmail.com")
    st.text_input("טלפון לווטסאפ", value="+972-523-697-127")
    
    if st.button("שמור הגדרות", type="primary"):
        st.success("ההגדרות נשמרו!")

st.markdown("---")
st.caption("v2.0 | Stock Alerts Agent | Dark Mode")
