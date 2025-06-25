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
st.title("Tamil Filter Kaapi Simulator")
st.write("Powered by Home Connect (BSH)")

# Step 1: OAuth Authorization Link
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": "IdentifyAppliance Monitor Settings Control",
    "state": "xyz"
}
auth_url = f"{API_BASE}/security/oauth/authorize?{urlencode(params)}"
st.subheader("Step 1: Get OAuth Code")
st.markdown(f"[Click here to authorize and get the code]({auth_url})")

# Step 2: Token Exchange
st.subheader("Step 2: Exchange Code for Access Token")
code = st.text_input("Paste the code from the redirected URL (after ?code=)", value="")
if st.button("Get Access Token"):
    response = requests.post(
        f"{API_BASE}/security/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code.strip(),
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    if response.status_code == 200:
        token = response.json().get("access_token")
        st.session_state["access_token"] = token
        st.success("Access token generated successfully!")
        st.code(token)
    else:
        error = response.json().get("error", {})
        st.error(f"{response.status_code}: {error.get('key')} - {error.get('description')}")

# Step 3: Brew Program
st.subheader("Step 3: Brew Filter Kaapi")
access_token = st.session_state.get("access_token", "")
if access_token:
    if st.button("Start Brewing"):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/vnd.bsh.sdk.v1+json",
            "Accept": "application/vnd.bsh.sdk.v1+json"
        }
        data = {"data": {"key": "ConsumerProducts.CoffeeMaker.Program.Coffee.Espresso"}}
        start_response = requests.put(
            f"{API_BASE}/api/homeappliances/{HAID}/programs/active",
            headers=headers, json=data
        )
        if start_response.status_code in [200, 204]:
            st.success("Brewing started!")
            logs = []
            with st.spinner("Brewing in progress..."):
                for _ in range(10):
                    status_response = requests.get(
                        f"{API_BASE}/api/homeappliances/{HAID}/programs/active",
                        headers=headers
                    )
                    if status_response.status_code == 200:
                        status = status_response.json().get("data", {}).get("key", "Unknown")
                    else:
                        status = "Error"
                    logs.append({"Time": time.strftime("%H:%M:%S"), "Status": status})
                    time.sleep(3)
            st.dataframe(pd.DataFrame(logs))
        else:
            err = start_response.json().get("error", {})
            st.error(f"{start_response.status_code}: {err.get('key')} - {err.get('description')}")
else:
    st.info("You need to generate an access token first.")
