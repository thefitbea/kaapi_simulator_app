import streamlit as st
import requests
import time
import pandas as pd
from urllib.parse import urlencode

# -- Configuration --
API_BASE = "https://simulator.home-connect.com"
CLIENT_ID = "5BEDC2D09B31492D1ABD3EB62F95C0135503FD564C3D16643D3039C60D79F526"
CLIENT_SECRET = "72755115996B347174A909149024809A8A1481EDE58B95AF940E834F3CD788BD"
REDIRECT_URI = "http://localhost"
HAID = "BOSCH-HCS06COM1-D70390681C2C"

st.set_page_config(page_title="Tamil Filter Kaapi Simulator", layout="centered")
st.markdown("# ☕ Tamil Filter Kaapi Simulator")
st.markdown("Powered by Home Connect (🔷 Blue Simulator)")

# Step 1: OAuth link
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": "IdentifyAppliance Monitor Settings Control",
    "state": "xyz"
}
auth_url = f"{API_BASE}/security/oauth/authorize?{urlencode(params)}"
st.markdown("## 1. Get OAuth Code")
st.markdown(f"[➡️ Click here to log in and get the **authorization code**]({auth_url})")

# Step 2: Token exchange helper
st.markdown("## 2. Exchange Code for Access Token")
code = st.text_input("Paste the **code** from the URL (without `?code=`)", value="", key="code_input")
if st.button("⚙️ Generate Token"):
    resp = requests.post(
        f"{API_BASE}/security/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code.strip(),
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        st.session_state['access_token'] = token
        st.success("✅ Access Token generated — pasted below!")
        st.code(token)
    else:
        err = resp.json().get("error", {})
        st.error(f"❌ {resp.status_code} {err.get('key')} — {err.get('description')}")

# Step 3: Use the token to brew
st.markdown("## 3. Brew Filter Kaapi")
access_token = st.session_state.get('access_token', '')
if access_token:
    if st.button("🚀 Start Brewing Filter Kaapi"):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/vnd.bsh.sdk.v1+json",
            "Accept": "application/vnd.bsh.sdk.v1+json"
        }
        payload = {"data": {"key": "ConsumerProducts.CoffeeMaker.Program.Coffee.Espresso"}}
        resp = requests.put(f"{API_BASE}/api/homeappliances/{HAID}/programs/active", headers=headers, json=payload)
        if resp.status_code in (200, 204):
            st.success("🍵 Brewing started!")
            log = []
            with st.spinner("⏳ Brewing..."):
                for _ in range(10):
                    r = requests.get(
                        f"{API_BASE}/api/homeappliances/{HAID}/programs/active",
                        headers=headers
                    )
                    status = r.json().get("data", {}).get("key", "Unknown") if r.status_code == 200 else "Error"
                    log.append({"Time": time.strftime("%H:%M:%S"), "Status": status})
                    time.sleep(3)
            st.dataframe(pd.DataFrame(log))
            st.balloons()
        else:
            err = resp.json().get("error", {})
            st.error(f"❌ {resp.status_code} {err.get('key')} — {err.get('description')}")
else:
    st.info("Generate an access token above to begin brewing.")
