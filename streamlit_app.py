"""Stock Alerts v3.1 - Fixed yfinance errors with caching"""
import streamlit as st
import json, os, hashlib, time
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Stock Alerts", page_icon="📈", layout="wide")

USERS_FILE, RULES_FILE = "users.json", "rules.json"

def load_users():
    return json.load(open(USERS_FILE)) if os.path.exists(USERS_FILE) else {}

def save_users(users):
    with open(USERS_FILE, 'w') as f: json.dump(users, f, indent=2)

def login(email, pw):
    users = load_users()
    if email in users and users[email]['password'] == hashlib.sha256(pw.encode()).hexdigest():
        return users[email]
    return None

def register(email, pw):
    users = load_users()
    if email in users: return False
    users[email] = {'password': hashlib.sha256(pw.encode()).hexdigest(), 'created': datetime.now().isoformat()}
    save_users(users)
    return True

@st.cache_data(ttl=60)
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        prev_close = info.get('previousClose')
        volume = info.get('volume', 0)
        
        if current_price and prev_close:
            change = ((current_price - prev_close) / prev_close * 100)
            return {
                'price': round(current_price, 2), 
                'change': round(change, 2), 
                'volume': int(volume)
            }
    except:
        pass
    return None

def load_rules(email):
    if os.path.exists(RULES_FILE):
        all_rules = json.load(open(RULES_FILE))
        return all_rules.get(email, [])
    return []

def save_rules(email, rules):
    all_rules = json.load(open(RULES_FILE)) if os.path.exists(RULES_FILE) else {}
    all_rules[email] = rules
    with open(RULES_FILE, 'w') as f: json.dump(all_rules, f, indent=2)

if 'user' not in st.session_state: st.session_state.user = None
if 'rules' not in st.session_state: st.session_state.rules = []

if st.session_state.user is None:
    st.title("📈 Stock Alerts")
    tab1, tab2 = st.tabs(["כניסה", "הרשמה"])
    
    with tab1:
        with st.form("login"):
            email = st.text_input("אימייל", placeholder="example@gmail.com")
            pw = st.text_input("סיסמה", type="password")
            if st.form_submit_button("התחבר"):
                profile = login(email, pw)
                if profile:
                    st.session_state.user = {'email': email, **profile}
                    st.session_state.rules = load_rules(email)
                    st.rerun()
                else: st.error("שגיאה")
    
    with tab2:
        with st.form("reg"):
            email = st.text_input("אימייל")
            pw = st.text_input("סיסמה", type="password")
            pw2 = st.text_input("אימות", type="password")
            if st.form_submit_button("הרשם"):
                if pw != pw2: st.error("סיסמאות לא זהות")
                elif register(email, pw): st.success("הצלחה!")
                else: st.error("תפוס")
else:
    with st.sidebar:
        st.caption(st.session_state.user['email'])
        if st.button("יציאה"):
            st.session_state.user = None
            st.rerun()
    
    st.title("📈 לוח בקרה")
    
    # Market indices
    indices = {'^GSPC': 'S&P 500', '^IXIC': 'NASDAQ', 'BTC-USD': 'BITCOIN'}
    cols = st.columns(3)
    for col, (sym, name) in zip(cols, indices.items()):
        with col:
            data = get_stock_data(sym)
            if data:
                col.metric(name, f"${data['price']:,.2f}", f"{data['change']:+.2f}%")
            else:
                col.metric(name, "--", "--")
    
    st.divider()
    st.subheader("התראות שלי")
    
    # Display alerts
    for i, rule in enumerate(st.session_state.rules):
        data = get_stock_data(rule['symbol'])
        if data:
            c1,c2,c3,c4,c5 = st.columns([1,2,2,2,1])
            c1.write(f"**{rule['symbol']}**")
            c2.metric("מחיר", f"${data['price']}")
            c3.caption(f"ווליום: {data['volume']:,}")
            c4.caption(f"טווח: ${rule['min']}-${rule['max']}")
            if c5.button("✖️", key=f"del_{i}"):
                st.session_state.rules.pop(i)
                save_rules(st.session_state.user['email'], st.session_state.rules)
                st.rerun()
    
    st.divider()
    if st.button("➕ הוסף התראה"):
        st.session_state.show_add = True
        st.rerun()
    
    if st.session_state.get('show_add'):
        with st.form("add_alert"):
            sym = st.text_input("סימול")
            price_range = st.slider("טווח מחיר", 0.0, 5000.0, (100.0, 500.0))
            if st.form_submit_button("שמור"):
                st.session_state.rules.append({'symbol': sym, 'min': price_range[0], 'max': price_range[1]})
                save_rules(st.session_state.user['email'], st.session_state.rules)
                st.session_state.show_add = False
                st.rerun()
    
    st.caption(f"v3.1 | {datetime.now().strftime('%H:%M:%S')}")
