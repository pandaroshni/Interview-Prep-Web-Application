import time
import requests

import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
 

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_url_hello = "https://lottie.host/61d09ce5-62a9-4c09-990a-18b4fa4ab4f9/HN0RNWoZg7.json"

lottie_hello = load_lottieurl(lottie_url_hello)



st_lottie(lottie_hello, key="hello")
if st.button("Download"):
    with st_lottie_spinner(lottie_hello, key="download"):
        time.sleep(5)
    st.balloons()
      
