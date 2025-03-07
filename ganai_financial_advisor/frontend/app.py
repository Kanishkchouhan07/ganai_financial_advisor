import streamlit as st
import requests

st.title("AI Financial Advisor")

query = st.text_input("Ask a financial question:")

if st.button("Get Advice"):
    response = requests.post("http://127.0.0.1:5000/financial-advice", json={"query": query})
    st.write(response.json()["response"])