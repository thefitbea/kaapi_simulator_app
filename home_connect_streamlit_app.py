import streamlit as st
import requests
import time
import pandas as pd

# -- Configuration --
API_BASE = "https://simulator.home-connect.com"
HAID = "BOSCH-HCS06COM1-D70390681C2C"

# -- UI Setup --
st.set_page_config(page_title="Tamil Filter Kaapi Simulator", layout="centered")
st.title("☕ Tamil Filter Kaapi Simulator")
st.markdown("### Powered by Home Connect (BSH)")

# OAuth link section
oauth_url = (
    f"{API_BASE}/security/oauth/authorize"
    "?client_id=5BEDC2D09B31492D1ABD3EB62F95C0135503FD564C3D16643D3039C60D79F526"
    "&response_type=code&redirect_uri=http://localhost"
    "&scope=IdentifyAppliance+Monitor+Settings+Control"
)
st.markdown("#### 1. Get OAuth Code")
st.write("Click the link below to login & copy the `code` from your browser's redirect:")
st.markdown(f"[➡️ Get OAuth Code]({oauth_url})", unsafe_allow_html=True)

# Access token input
st.markdown("#### 2. Paste `access_token`")
access_token = st.text_input("🔑 Paste access token here", type="password")

# Start brewing
if st.button("🚀 Start Brewing Filter Kaapi") and access_token:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.bsh.sdk.v1+json",
        "Accept": "application/vnd.bsh.sdk.v1+json"
    }
    payload = {"data": {"key": "ConsumerProducts.CoffeeMaker.Program.Coffee.Espresso"}}
    response = requests.put(
        f"{API_BASE}/api/homeappliances/{HAID}/programs/active",
        headers=headers, json=payload
    )

    if response.status_code in (200, 204):
        st.success("☕ Brewing started: Filter kaapi is on the way!")
        log = []
        with st.spinner("⏳ Brewing..."):
            for _ in range(10):
                r = requests.get(
                    f"{API_BASE}/api/homeappliances/{HAID}/programs/active",
                    headers=headers
                )
                state = r.json().get("data", {}).get("key", "Unknown") if r.status_code == 200 else "Error"
                log.append({"Time": time.strftime("%H:%M:%S"), "Status": state})
                time.sleep(3)

        df = pd.DataFrame(log)
        st.markdown("### 📋 Brewing Status Log")
        st.dataframe(df, use_container_width=True)
        st.balloons()
    else:
        err = response.json().get("error", {})
        st.error(f"❌ Error {response.status_code}: {err.get('key')} — {err.get('description')}")
elif access_token == "":
    st.info("Please get an OAuth code first and exchange it for an access token.")
