import streamlit as st
import requests
import os
import json
import traceback

# Get backend URL from environment variable or use localhost as fallback
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5001/api/predict")

st.title("GANAI Financial Advisor")

# Display the current backend URL and environment info (for debugging)
with st.sidebar.expander("Debug Information"):
    st.write(f"Backend URL: {BACKEND_URL}")
    st.write(f"Environment Variables: {list(os.environ.keys())}")

user_input = st.text_input("Enter your query:")

if st.button("Get Advice"):
    if user_input:
        try:
            st.info(f"Attempting to connect to: {BACKEND_URL}")
            
            # Add timeout to prevent long waiting
            response = requests.post(
                BACKEND_URL, 
                json={"input_data": user_input},
                timeout=10  # 10 second timeout
            )
            
            # Check status code
            if response.status_code == 200:
                st.success("Successfully connected to backend!")
                st.write("Response:", response.json().get("response", "No response"))
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError as e:
            st.error("Error: Unable to connect to backend. Ensure backend service is running.")
            with st.expander("Error Details"):
                st.write(str(e))
        except requests.exceptions.Timeout:
            st.error("Error: Request to backend timed out. The service might be overloaded or down.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            with st.expander("Traceback"):
                st.code(traceback.format_exc())
    else:
        st.warning("Please enter some input before submitting.")