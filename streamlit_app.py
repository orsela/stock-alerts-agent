import streamlit as st
import json
import os

# File to store rules
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

# Initialize session state
if 'rules' not in st.session_state:
    st.session_state.rules = load_rules()
    if not st.session_state.rules:
        st.session_state.rules = [
            {"symbol": "NVDA", "min_price": 130.0, "max_price": 140.0, "min_volume": 1000000, "notify_email": True, "notify_whatsapp": True, "active": True}
        ]

st.set_page_config(page_title="Stock Alerts Agent", layout="centered", page_icon="📈")

st.title("📈 Stock Alerts Agent")
st.markdown("### Manage your stock alert rules")

# Add/Update Rule Form
st.subheader("Add / Update Rule")

symbol = st.text_input("Symbol (e.g. NVDA, AAPL)").upper()

col1, col2 = st.columns(2)
with col1:
    min_price = st.number_input("Min Price ($)", min_value=0.0, step=0.5, value=0.0)
with col2:
    max_price = st.number_input("Max Price ($)", min_value=0.0, step=0.5, value=0.0)

min_volume = st.number_input("Min Volume", min_value=0, step=10000, value=100000)

col3, col4, col5 = st.columns(3)
with col3:
    notify_email = st.checkbox("Email Alert", value=True)
with col4:
    notify_whatsapp = st.checkbox("WhatsApp Alert", value=False)
with col5:
    active = st.checkbox("Active", value=True)

if st.button("Save Rule", type="primary"):
    if not symbol:
        st.error("Symbol is required!")
    elif max_price > 0 and min_price > max_price:
        st.error("Min price cannot be greater than max price!")
    else:
        updated = False
        for r in st.session_state.rules:
            if r["symbol"] == symbol:
                r.update({"min_price": min_price, "max_price": max_price, "min_volume": min_volume, "notify_email": notify_email, "notify_whatsapp": notify_whatsapp, "active": active})
                updated = True
                break
        if not updated:
            st.session_state.rules.append({"symbol": symbol, "min_price": min_price, "max_price": max_price, "min_volume": min_volume, "notify_email": notify_email, "notify_whatsapp": notify_whatsapp, "active": active})
        save_rules(st.session_state.rules)
        st.success(f"Rule for {symbol} saved!")
        st.rerun()

st.divider()
st.subheader("Current Rules")

if st.session_state.rules:
    for i, rule in enumerate(st.session_state.rules):
        with st.container():
            cols = st.columns([2, 4, 2, 1])
            with cols[0]:
                status = "Active" if rule.get("active", True) else "Paused"
                st.markdown(f"**{rule['symbol']}** ({status})")
            with cols[1]:
                st.caption(f"Price: ${rule['min_price']}-${rule['max_price']} | Vol >= {rule['min_volume']:,}")
            with cols[2]:
                alerts = []
                if rule.get("notify_email"): alerts.append("Email")
                if rule.get("notify_whatsapp"): alerts.append("WA")
                st.caption(" | ".join(alerts) if alerts else "No alerts")
            with cols[3]:
                if st.button("X", key=f"del_{i}"):
                    st.session_state.rules.pop(i)
                    save_rules(st.session_state.rules)
                    st.rerun()
        st.divider()
else:
    st.info("No rules yet. Add one above!")

st.caption("v1.0 | Stock Alerts Agent | orsela@gmail.com")
