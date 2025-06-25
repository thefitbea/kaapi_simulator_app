
import streamlit as st
import requests
import time
import pandas as pd

st.title("☕ Tamil Filter Coffee Simulator (Home Connect API)")

ACCESS_TOKEN = st.text_input("Access Token", type="password")
HAID = "BOSCH-HCS06COM1-D70390681C2C"

if ACCESS_TOKEN and st.button("Start Brewing (Espresso)"):
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
        st.success("Brewing started!")
        log = []
        for i in range(10):
            status = requests.get(f"https://simulator.home-connect.com/api/homeappliances/{HAID}/programs/active", headers=headers)
            if status.status_code == 200:
                state = status.json().get("data", {}).get("key", "Unknown")
                log.append({"Time": time.strftime("%H:%M:%S"), "Status": state})
                time.sleep(3)
        df = pd.DataFrame(log)
        st.dataframe(df)
    else:
        st.error(f"Failed to start program. Status {r.status_code}: {r.text}")
