import streamlit as st
import requests
import os
import json

st.title("Backend Connection Test")

# TEMPORARY: Hardcoded backend URL for testing
# IMPORTANT: Replace this with your actual backend URL
BACKEND_BASE_URL = "https://your-actual-backend-url.com"

st.write("### Using Hardcoded Backend URL")
st.write(f"Backend URL: {BACKEND_BASE_URL}")

# Manual override option
st.write("### Manual Override")
manual_url = st.text_input("Enter backend URL manually:", 
                          value=BACKEND_BASE_URL,
                          placeholder="https://your-backend-url.com")

if manual_url:
    BACKEND_BASE_URL = manual_url
    if BACKEND_BASE_URL.endswith('/'):
        BACKEND_BASE_URL = BACKEND_BASE_URL[:-1]
    st.write(f"Using manually entered URL: {BACKEND_BASE_URL}")

# Test health endpoint
st.write("### Connection Tests")
if st.button("Test Health Endpoint"):
    try:
        health_url = f"{BACKEND_BASE_URL}/health"
        st.write(f"Connecting to: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            st.success(f"Successfully connected to health endpoint! Response: {response.json()}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to health endpoint: {str(e)}")

# Test test endpoint
if st.button("Test Simple Endpoint"):
    try:
        test_url = f"{BACKEND_BASE_URL}/test"
        st.write(f"Connecting to: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            st.success(f"Successfully connected to test endpoint! Response: {response.json()}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to test endpoint: {str(e)}")

# Test API endpoint
if st.button("Test API Endpoint"):
    try:
        api_url = f"{BACKEND_BASE_URL}/api/predict"
        st.write(f"Connecting to: {api_url}")
        
        response = requests.post(
            api_url, 
            json={"input_data": "Test query"}, 
            timeout=10
        )
        
        if response.status_code == 200:
            st.success(f"Successfully connected to API endpoint! Response: {response.json()}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API endpoint: {str(e)}")

# Environment information
with st.expander("Environment Information"):
    st.write("Environment Variables:")
    env_vars = {}
    for key in sorted(os.environ.keys()):
        if not key.startswith(('_', 'PYTHON')):  # Filter out some system variables
            value = '*' * 8 if 'KEY' in key or 'SECRET' in key else os.environ[key]
            env_vars[key] = value
    
    st.json(env_vars)
    
    st.write("Note: If you don't see BACKEND_URL in the environment variables, it means it's not set in your Streamlit Cloud deployment.") 