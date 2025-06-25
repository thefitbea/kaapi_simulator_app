
import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Tamil Filter Kaapi Simulator", layout="centered")

st.markdown("""
<style>
    .title {
        text-align: center;
        font-size: 36px;
        color: #522b1c;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #888;
        margin-top: -10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">☕ Tamil Filter Kaapi Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Powered by Home Connect API</div>', unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Dabara_tumbler_kaapi.jpg/640px-Dabara_tumbler_kaapi.jpg", width=300, caption="Classic Dabara-Tumbler Kaapi")

st.markdown("---")

ACCESS_TOKEN = st.text_input("🔐 Enter your Access Token", type="password")
HAID = "BOSCH-HCS06COM1-D70390681C2C"  # Coffee Maker Simulator

if st.button("🚀 Start Brewing Filter Kaapi (Espresso Style)") and ACCESS_TOKEN:
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/vnd.bsh.sdk.v1+json",
        "Accept": "application/vnd.bsh.sdk.v1+json"
    }
    data = {
        "data": {
            "key": "ConsumerProducts.CoffeeMaker.Program.Coffee.Espresso"
        }
    }
    url = f"https://simulator.home-connect.com/api/homeappliances/{HAID}/programs/active"
    r = requests.put(url, headers=headers, json=data)

    if r.status_code in [200, 204]:
        st.success("☕ Brewing started: Filter kaapi is on the way!")
        log = []
        with st.spinner("Brewing in progress..."):
            for i in range(10):
                status = requests.get(f"https://simulator.home-connect.com/api/homeappliances/{HAID}/programs/active", headers=headers)
                if status.status_code == 200:
                    state = status.json().get("data", {}).get("key", "Unknown")
                    log.append({"Time": time.strftime("%H:%M:%S"), "Status": state})
                    time.sleep(3)
        df = pd.DataFrame(log)
        st.markdown("### 📋 Brewing Log")
        st.dataframe(df)
        st.balloons()
        st.image("https://i.pinimg.com/originals/20/0c/cc/200ccc99e00d2404849f3acb77030536.gif", width=300, caption="Hot Kaapi Served!")
    else:
        st.error(f"❌ Failed to start program.\nStatus {r.status_code}:\n{r.text}")
elif not ACCESS_TOKEN:
    st.warning("Please paste your access token above to begin.")
