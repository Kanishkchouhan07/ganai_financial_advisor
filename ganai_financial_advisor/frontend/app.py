import streamlit as st
import requests
import os

# Get backend URL from environment variable or use localhost as fallback
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5001/api/predict")

st.title("GANAI Financial Advisor")

# Display the current backend URL (for debugging)
st.sidebar.write(f"Connected to: {BACKEND_URL}")

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
            st.error("Error: Unable to connect to backend. Ensure backend service is running.")
    else:
        st.warning("Please enter some input before submitting.")