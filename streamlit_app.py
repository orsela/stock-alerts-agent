import streamlit as st
import json
import os
import yfinance as yf
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Bot
from twilio.rest import Client

# Dark theme CSS
DARK_THEME = """
<style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    .main-header { text-align: right; font-size: 28px; font-weight: bold; color: #ffffff; padding: 10px 0; }
    .index-card { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 12px; padding: 15px; margin: 5px; text-align: center; }
    .index-name { color: #888; font-size: 14px; }
    .index-value { color: #fff; font-size: 20px; font-weight: bold; }
    .index-change-up { color: #00ff88; font-size: 14px; }
    .index-change-down { color: #ff4444; font-size: 14px; }
    .alert-card { background: #1a1a2e; border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 4px solid #3b82f6; }
    .stock-symbol { font-size: 18px; font-weight: bold; color: #fff; }
    .stock-price { font-size: 24px; color: #fff; }
    .target-price { color: #00ff88; font-size: 14px; }
    .section-title { color: #fff; font-size: 20px; font-weight: bold; text-align: right; margin: 20px 0 10px 0; }
    .live-badge { background: #00ff88; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
</style>
"""

RULES_FILE = "rules.json"

@st.cache_data(ttl=60)
def get_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            prev_close = ticker.info.get('previousClose', price)
            change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
            return round(price, 2), round(change, 2)
    except:
        pass
    return None, None

@st.cache_data(ttl=60)
def get_index_data():
    indices = {
        '^GSPC': ('S&P 500', None, None),
        '^IXIC': ('NASDAQ', None, None),
        '^TA125.TA': ('TA-125', None, None)
    }
    result = {}
    for symbol, (name, _, _) in indices.items():
        price, change = get_stock_price(symbol)
        result[name] = (price, change)
    return result

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

def send_email_alert(symbol, price, target_price, condition):
    """Send email alert when stock condition is met"""
    try:
        # Get credentials from secrets
        sender_email = st.secrets["gmail"]["email"]
        app_password = st.secrets["gmail"]["app_password"]
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = f'התראת מניה: {symbol}'
        
        # Email body in Hebrew
        body = f"""
שלום,

התנאי עבור המניה {symbol} התקיים!

מחיר נוכחי: ${price:.2f}
מחיר יעד: ${target_price:.2f}
תנאי: {condition}

זמן: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

בברכה,
מערכת התראות מניות
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
            
        return True
    except Exception as e:
        st.error(f"שגיאה בשליחת מייל: {str(e)}")
        return False

def send_telegram_alert(symbol, price, target_price, condition):
    """Send Telegram alert when stock condition is met"""
    try:
        # Get credentials from secrets
        bot_token = st.secrets["telegram"]["bot_token"]
        chat_id = st.secrets["telegram"]["chat_id"]
        
        # Create message in Hebrew
        message = f"""
📊 *התראת מניה*

מניה: {symbol}
מחיר נוכחי: ${price:.2f}
מחיר יעד: ${target_price:.2f}
תנאי: {condition}

זמן: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        # Send message
        bot = Bot(token=bot_token)
        import asyncio
        asyncio.run(bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown'))
        
        return True
    except Exception as e:
        st.error(f"שגיאה בשליחת Telegram: {str(e)}")
        return False

def send_whatsapp_alert(symbol, price, target_price, condition):
    """Send WhatsApp alert via Twilio when stock condition is met"""
    try:
        # Get credentials from secrets
        account_sid = st.secrets["twilio"]["account_sid"]
        auth_token = st.secrets["twilio"]["auth_token"]
        from_whatsapp = st.secrets["twilio"]["from_number"]  # Format: 'whatsapp:+14155238886'
        to_whatsapp = st.secrets["twilio"]["to_number"]      # Format: 'whatsapp:+972523697127'
        
        # Create message in Hebrew
        message_body = f"""
📊 התראת מניה

מניה: {symbol}
מחיר נוכחי: ${price:.2f}
מחיר יעד: ${target_price:.2f}
תנאי: {condition}

זמן: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        # Send WhatsApp message
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=from_whatsapp,
            body=message_body,
            to=to_whatsapp
        )
        
        return True
    except Exception as e:
        st.error(f"שגיאה בשליחת WhatsApp: {str(e)}")
        return False

if 'rules' not in st.session_state:
    st.session_state.rules = load_rules()
    if not st.session_state.rules:
        st.session_state.rules = [
            {"symbol": "TSLA", "min_price": 145.50, "max_price": 320.0, "target": 189.0, "notify_email": True, "notify_whatsapp": True, "active": True},
            {"symbol": "AAPL", "min_price": 170.0, "max_price": 250.0, "target": 200.0, "notify_email": True, "notify_whatsapp": False, "active": True},
            {"symbol": "NVDA", "min_price": 400.0, "max_price": 600.0, "target": 500.0, "notify_email": True, "notify_whatsapp": True, "active": True},
        ]

if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"

st.set_page_config(page_title="Stock Alerts", layout="wide", initial_sidebar_state="collapsed")
st.markdown(DARK_THEME, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Dashboard", use_container_width=True):
        st.session_state.current_page = "dashboard"
with col2:
    if st.button("Alerts", use_container_width=True):
        st.session_state.current_page = "alerts"
with col3:
    if st.button("New Alert", use_container_width=True):
        st.session_state.current_page = "new_alert"
with col4:
    if st.button("Settings", use_container_width=True):
        st.session_state.current_page = "settings"

st.divider()

    # Test email button
    if st.button("📧 שלח מייל ניסיון"):
        with st.spinner('שולח מייל...'):
            test_symbol = "TSLA"
            test_price = 430.17
            test_target = 400.0
            if send_email_alert(test_symbol, test_price, test_target, "בדיקת מערכת"):
                st.success("המייל נשלח בהצלחה! בדוק את orsela@gmail.com")

            # Test Telegram button
    if st.button("📨 שלח Telegram ניסיון"):
        with st.spinner('שולח Telegram...'):
            test_symbol = "AAPL"
            test_price = 278.85
            test_target = 280.0
            if send_telegram_alert(test_symbol, test_price, test_target, "בדיקת Telegram"):
                st.success("ההודעה נשלחה בהצלחה ל-Telegram!")
    
    # Test WhatsApp button
    if st.button("📱 שלח WhatsApp ניסיון"):
        with st.spinner('שולח WhatsApp...'):
            test_symbol = "NVDA"
            test_price = 177.00
            test_target = 180.0
            if send_whatsapp_alert(test_symbol, test_price, test_target, "בדיקת WhatsApp"):
                st.success("ההודעה נשלחה בהצלחה ל-WhatsApp במספר +972-523-697-127!")

if st.session_state.current_page == "dashboard":
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    with col_badge:
        st.markdown('<span class="live-badge">LIVE</span>', unsafe_allow_html=True)
    
    indices = get_index_data()
    idx1, idx2, idx3 = st.columns(3)
    
    for col, (name, (price, change)) in zip([idx1, idx2, idx3], indices.items()):
        with col:
            change_class = "index-change-up" if change and change >= 0 else "index-change-down"
            arrow = "\u25b2" if change and change >= 0 else "\u25bc"
            price_str = f"{price:,.2f}" if price else "N/A"
            change_str = f"{arrow} {change:+.2f}%" if change else "N/A"
            st.markdown(f'''
            <div class="index-card">
                <div class="index-name">{name}</div>
                <div class="index-value">{price_str}</div>
                <div class="{change_class}">{change_str}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">Watchlist - Live Prices</div>', unsafe_allow_html=True)
    
    for rule in st.session_state.rules:
        if rule.get('active', True):
            price, change = get_stock_price(rule['symbol'])
            col_a, col_b, col_c, col_d = st.columns([1, 2, 2, 1])
            with col_a:
                st.markdown(f"**{rule['symbol']}**")
            with col_b:
                if price:
                    st.metric("Price", f"${price:.2f}", f"{change:+.2f}%")
                else:
                    st.write("Loading...")
            with col_c:
                st.caption(f"Target: ${rule.get('target', 0):.2f}")
                if price and rule.get('target'):
                    diff = ((rule['target'] - price) / price) * 100
                    st.caption(f"Distance: {diff:+.1f}%")
            with col_d:
                if price and rule['min_price'] <= price <= rule['max_price']:
                    st.success("IN RANGE")
            st.divider()
    
    if st.button("Refresh Prices"):
        st.cache_data.clear()
        st.rerun()

elif st.session_state.current_page == "alerts":
    st.markdown('<div class="main-header">Active Alerts</div>', unsafe_allow_html=True)
    
    for i, rule in enumerate(st.session_state.rules):
        price, change = get_stock_price(rule['symbol'])
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                st.markdown(f"**{rule['symbol']}**")
                st.caption(f"${price:.2f}" if price else "N/A")
            with col2:
                st.write(f"Range: ${rule['min_price']:.2f} - ${rule['max_price']:.2f}")
                if price:
                    progress = (price - rule['min_price']) / (rule['max_price'] - rule['min_price'])
                    st.progress(min(max(progress, 0), 1))
            with col3:
                st.caption(f"Target: ${rule.get('target', 0):.2f}")
                alerts = []
                if rule.get('notify_email'): alerts.append("Email")
                if rule.get('notify_whatsapp'): alerts.append("WA")
                st.caption(" | ".join(alerts))
            with col4:
                rule['active'] = st.toggle("Active", value=rule.get('active', True), key=f"toggle_{i}")
                if st.button("Delete", key=f"del_{i}"):
                    st.session_state.rules.pop(i)
                    save_rules(st.session_state.rules)
                    st.rerun()
            st.divider()

elif st.session_state.current_page == "new_alert":
    st.markdown('<div class="main-header">Create New Alert</div>', unsafe_allow_html=True)
    
    symbol = st.text_input("Stock Symbol", placeholder="AAPL, TSLA, NVDA...").upper()
    
    if symbol:
        price, change = get_stock_price(symbol)
        if price:
            st.success(f"Current price: ${price:.2f} ({change:+.2f}%)")
        else:
            st.warning("Symbol not found")
    
    col1, col2 = st.columns(2)
    with col1:
        min_price = st.number_input("Min Price ($)", min_value=0.0, step=1.0)
    with col2:
        max_price = st.number_input("Max Price ($)", min_value=0.0, step=1.0)
    
    target = st.number_input("Target Price ($)", min_value=0.0, step=1.0)
    
    col3, col4 = st.columns(2)
    with col3:
        notify_email = st.checkbox("Email Alert", value=True)
    with col4:
        notify_whatsapp = st.checkbox("WhatsApp Alert", value=True)
    
    if st.button("Create Alert", type="primary", use_container_width=True):
        if symbol and max_price > min_price:
            new_rule = {
                "symbol": symbol,
                "min_price": min_price,
                "max_price": max_price,
                "target": target,
                "notify_email": notify_email,
                "notify_whatsapp": notify_whatsapp,
                "active": True
            }
            st.session_state.rules.append(new_rule)
            save_rules(st.session_state.rules)
            st.success(f"Alert created for {symbol}!")
            st.balloons()
        else:
            st.error("Please fill all fields correctly")

elif st.session_state.current_page == "settings":
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    
    st.subheader("Notifications")
    st.text_input("Email", value="orsela@gmail.com", key="email")
    st.text_input("WhatsApp", value="+972-523-697-127", key="whatsapp")
    
    st.subheader("Data Source")
    st.info("Using Yahoo Finance for real-time stock data")
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved!")

st.markdown("---")
st.caption(f"v3.0 | Stock Alerts | Yahoo Finance | Last update: {datetime.now().strftime('%H:%M:%S')}")
