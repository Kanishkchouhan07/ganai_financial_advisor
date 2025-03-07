import streamlit as st
import requests

st.title("GANAI Financial Advisor")

# Example payload (modify as needed)
payload = {"input_data": "test"}

# Send request to backend
response = requests.post("http://127.0.0.1:5000/predict", json=payload)

# Debugging: Print response details
st.write("Response Status Code:", response.status_code)
st.write("Raw Response Text:", response.text)  # Show raw text response

# Attempt to parse JSON (only if response is not empty)
try:
    json_response = response.json()
    st.write(json_response["response"])
except requests.exceptions.JSONDecodeError:
    st.error("Error: Response is not valid JSON. Check the backend.")