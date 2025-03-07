import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5001/api/predict"  # Ensure this matches backend

st.title("GANAI Financial Advisor")

user_input = st.text_input("Enter your query:")

if st.button("Get Advice"):
    if user_input:
        try:
            response = requests.post(BACKEND_URL, json={"input_data": user_input})
            
            # Check status code
            if response.status_code == 200:
                st.write("Response:", response.json().get("response", "No response"))
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Error: Unable to connect to backend. Ensure Flask is running.")
    else:
        st.warning("Please enter some input before submitting.")