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

st.set_page_config(page_title="Tamil Filter Kaapi Simulator", layout="wide")

# -- Custom Background Styling with Overlay and Minimal UI Font --
st.markdown(
    f"""
    <style>
    html, body, [class*="css"]  {{
        font-family: 'Segoe UI', sans-serif;
    }}
    .stApp {{
        background-image: url("https://miro.medium.com/v2/resize:fit:4800/format:webp/1*kIzzLmnb1gBaRexyhI-Wew.jpeg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        padding: 2rem;
    }}
    .title-box {{
        background-color: rgba(255, 255, 255, 0.8);
        padding: 1rem 2rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 2rem;
    }}
    </style>
    <div class="title-box">
        <img src="http://www.bsh-group.de/images/logo.jpg" width="120">
        <h1>Tamil Filter Kaapi Simulator</h1>
        <p><strong>Powered by Home Connect (BSH)</strong></p>
    </div>
    """,
    unsafe_allow_html=True
)

# Step 1: OAuth link
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": "IdentifyAppliance Monitor Settings Control",
    "state": "xyz"
}
auth_url = f"{API_BASE}/security/oauth/authorize?{urlencode(params)}"
st.subheader("1. Get OAuth Code")
st.markdown(f"[Click here to log in and get your authorization code]({auth_url})")

# Step 2: Token exchange helper
st.subheader("2. Exchange Code for Access Token")
code = st.text_input("Paste the code from the redirected URL (after ?code=)", value="", key="code_input")
if st.button("Generate Access Token"):
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
    try:
        resp_json = resp.json()
    except Exception as e:
        st.error(f"Failed to parse response JSON: {e}")
        resp_json = {}

    if resp.status_code == 200:
        token = resp_json.get("access_token")
        st.session_state['access_token'] = token
        st.success("Access Token generated!")
        st.code(token)
    else:
        key = resp_json.get("error", {}).get("key", "Unknown")
        desc = resp_json.get("error", {}).get("description", "No description available")
        st.error(f"{resp.status_code} {key} — {desc}")

# Step 3: Use the token to brew
st.subheader("3. Brew Filter Kaapi")
access_token = st.session_state.get('access_token', '')
if access_token:
    if st.button("Start Brewing"):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/vnd.bsh.sdk.v1+json",
            "Accept": "application/vnd.bsh.sdk.v1+json"
        }
        payload = {"data": {"key": "ConsumerProducts.CoffeeMaker.Program.Coffee.Espresso"}}
        resp = requests.put(f"{API_BASE}/api/homeappliances/{HAID}/programs/active", headers=headers, json=payload)
        if resp.status_code in (200, 204):
            st.success("Brewing started!")
            log = []
            with st.spinner("Brewing..."):
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
            try:
                error = resp.json().get("error", {})
                key = error.get("key", "Unknown")
                desc = error.get("description", "No description available")
                st.error(f"{resp.status_code} {key} — {desc}")
            except Exception as e:
                st.error(f"{resp.status_code} Unexpected error: {e}")
else:
    st.info("Generate an access token above to begin brewing.")
