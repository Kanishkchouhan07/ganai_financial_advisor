import streamlit as st
import requests
import os
import json
import traceback

st.title("GANAI Financial Advisor")

# Get backend URL from environment variable or use localhost as fallback
default_backend_url = "http://127.0.0.1:5001/api/predict"

# Check for BACKEND_URL environment variable
raw_backend_url = os.environ.get("BACKEND_URL", "")

# If not set, try to construct it from BACKEND_URL_HOST
if not raw_backend_url:
    backend_host = os.environ.get("BACKEND_URL_HOST", "")
    if backend_host:
        raw_backend_url = f"https://{backend_host}/api/predict"
    else:
        raw_backend_url = default_backend_url

# Ensure the backend URL has the correct format
if raw_backend_url.endswith('/api/predict'):
    BACKEND_URL = raw_backend_url
elif raw_backend_url.endswith('/'):
    BACKEND_URL = f"{raw_backend_url}api/predict"
else:
    BACKEND_URL = f"{raw_backend_url}/api/predict"

# Debug information in sidebar
with st.sidebar:
    st.subheader("Connection Settings")
    
    # Show current backend URL
    st.write(f"Raw Backend URL: {raw_backend_url}")
    st.write(f"Formatted Backend URL: {BACKEND_URL}")
    
    # Extract base URL for testing
    base_url = BACKEND_URL.split('/api/')[0]
    st.write(f"Base URL: {base_url}")
    
    # Show environment variables for debugging
    with st.expander("Environment Variables"):
        st.write("BACKEND_URL: ", os.environ.get("BACKEND_URL", "Not set"))
        st.write("BACKEND_URL_HOST: ", os.environ.get("BACKEND_URL_HOST", "Not set"))
    
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
            # Test root endpoint first
            root_url = base_url
            st.write(f"Testing root URL: {root_url}")
            
            root_response = requests.get(root_url, timeout=10)
            if root_response.status_code == 200:
                st.success(f"Root endpoint accessible: {root_response.json()}")
            else:
                st.warning(f"Root endpoint returned: {root_response.status_code}")
                
            # Then test health endpoint
            health_url = f"{base_url}/health"
            st.write(f"Testing health URL: {health_url}")
            
            health_response = requests.get(health_url, timeout=10)
            if health_response.status_code == 200:
                st.success(f"Health endpoint accessible: {health_response.json()}")
            else:
                st.error(f"Health endpoint error: {health_response.status_code}")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
            st.code(traceback.format_exc())

# Main app interface
user_input = st.text_input("Enter your query:")

if st.button("Get Advice"):
    if user_input:
        try:
            with st.spinner("Connecting to backend..."):
                st.write(f"Sending request to: {BACKEND_URL}")
                
                # Add timeout to prevent long waiting
                response = requests.post(
                    BACKEND_URL, 
                    json={"input_data": user_input},
                    timeout=15,  # 15 second timeout
                    headers={"Content-Type": "application/json"}
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