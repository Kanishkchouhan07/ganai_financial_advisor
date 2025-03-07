import streamlit as st
import requests
import os
import json
import traceback

st.title("GANAI Financial Advisor")

# TEMPORARY: Hardcoded backend URL for testing
# IMPORTANT: Replace this with your actual backend URL
BACKEND_URL = "https://your-actual-backend-url.com/api/predict"

# Comment out the dynamic URL detection for now
"""
# Get backend URL from environment variable, secrets, or use localhost as fallback
default_backend_url = "http://127.0.0.1:5001/api/predict"

# Try to get from secrets first (for Streamlit Cloud)
try:
    BACKEND_URL = st.secrets.get("BACKEND_URL", os.environ.get("BACKEND_URL", default_backend_url))
except Exception:
    # Fall back to environment variable if secrets not available
    BACKEND_URL = os.environ.get("BACKEND_URL", default_backend_url)
"""

# Debug information in sidebar
with st.sidebar:
    st.subheader("Connection Settings")
    
    # Show current backend URL
    st.write(f"Current Backend URL: {BACKEND_URL}")
    
    # Allow manual override for testing
    use_manual_url = st.checkbox("Override backend URL")
    
    if use_manual_url:
        manual_url = st.text_input(
            "Enter backend URL:", 
            value=BACKEND_URL,
            placeholder="https://your-backend-url.com/api/predict"
        )
        if manual_url:
            BACKEND_URL = manual_url
            st.success(f"Using: {BACKEND_URL}")
    
    # Show connection status
    if st.button("Test Connection"):
        try:
            # Extract base URL for health check
            base_url = BACKEND_URL
            if '/api/' in base_url:
                base_url = base_url.split('/api/')[0]
            
            health_url = f"{base_url}/health"
            response = requests.get(health_url, timeout=5)
            
            if response.status_code == 200:
                st.success("Backend connection successful!")
            else:
                st.error(f"Backend returned error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")

# Main app interface
user_input = st.text_input("Enter your query:")

if st.button("Get Advice"):
    if user_input:
        try:
            with st.spinner("Connecting to backend..."):
                # Add timeout to prevent long waiting
                response = requests.post(
                    BACKEND_URL, 
                    json={"input_data": user_input},
                    timeout=15  # 15 second timeout
                )
            
            # Check status code
            if response.status_code == 200:
                st.success("Successfully received advice!")
                st.write("Response:", response.json().get("response", "No response"))
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError as e:
            st.error("Error: Unable to connect to backend. Ensure backend service is running.")
            with st.expander("Error Details"):
                st.write(str(e))
                st.write(f"Attempted to connect to: {BACKEND_URL}")
        except requests.exceptions.Timeout:
            st.error("Error: Request to backend timed out. The service might be overloaded or down.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            with st.expander("Traceback"):
                st.code(traceback.format_exc())
    else:
        st.warning("Please enter some input before submitting.")