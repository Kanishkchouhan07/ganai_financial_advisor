import streamlit as st
import requests
import os
import json
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="GANAI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .response-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .category-button {
        margin-right: 10px;
        margin-bottom: 10px;
    }
    .history-item {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        cursor: pointer;
    }
    .history-item:hover {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing history
if 'history' not in st.session_state:
    st.session_state.history = []

if 'categories' not in st.session_state:
    st.session_state.categories = []

if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "general"

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
    BASE_URL = raw_backend_url.replace('/api/predict', '')
elif raw_backend_url.endswith('/'):
    BACKEND_URL = f"{raw_backend_url}api/predict"
    BASE_URL = raw_backend_url[:-1]
else:
    BACKEND_URL = f"{raw_backend_url}/api/predict"
    BASE_URL = raw_backend_url

# Function to fetch categories from backend
def fetch_categories():
    try:
        response = requests.get(f"{BASE_URL}/api/categories", timeout=10)
        if response.status_code == 200:
            return response.json().get("categories", [])
        return []
    except Exception as e:
        st.error(f"Error fetching categories: {str(e)}")
        return []

# Sidebar for settings and history
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/financial-growth.png", width=100)
    st.markdown("<h2>GANAI Financial Advisor</h2>", unsafe_allow_html=True)
    
    # Connection settings (hidden in expander)
    with st.expander("Connection Settings"):
        st.write(f"Backend URL: {BACKEND_URL}")
        st.write(f"Base URL: {BASE_URL}")
        
        # Show environment variables for debugging
        st.write("Environment Variables:")
        st.write("BACKEND_URL: ", os.environ.get("BACKEND_URL", "Not set"))
        st.write("BACKEND_URL_HOST: ", os.environ.get("BACKEND_URL_HOST", "Not set"))
    
    # History section
    st.markdown("<h3>Query History</h3>", unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("Your query history will appear here")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            # Only show the last 10 items
            if i >= 10:
                break
                
            # Create a clickable history item
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"{item['query'][:30]}...", key=f"history_{i}", help=item['query']):
                    # Set the query and category when clicked
                    st.session_state.query_input = item['query']
                    st.session_state.selected_category = item['category']
                    st.rerun()
            with col2:
                st.caption(item['category'])
    
    # Clear history button
    if st.session_state.history and st.button("Clear History"):
        st.session_state.history = []
        st.success("History cleared!")

# Main content area
st.markdown("<h1 class='main-header'>GANAI Financial Advisor</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Your AI-powered guide to financial success</p>", unsafe_allow_html=True)

# Fetch categories if not already loaded
if not st.session_state.categories:
    with st.spinner("Loading categories..."):
        categories = fetch_categories()
        if categories:
            st.session_state.categories = categories
        else:
            # Default categories if API fails
            st.session_state.categories = [
                {"id": "general", "name": "General Financial Advice"},
                {"id": "stocks", "name": "Stocks & Investments"},
                {"id": "savings", "name": "Savings & Budgeting"},
                {"id": "retirement", "name": "Retirement Planning"},
                {"id": "crypto", "name": "Cryptocurrency"}
            ]

# Category selection
st.markdown("<h3>Select a Category</h3>", unsafe_allow_html=True)
cols = st.columns(len(st.session_state.categories))
for i, category in enumerate(st.session_state.categories):
    with cols[i]:
        if st.button(
            category["name"], 
            key=f"cat_{category['id']}",
            help=f"Get advice about {category['name']}",
            use_container_width=True,
            type="primary" if st.session_state.selected_category == category["id"] else "secondary"
        ):
            st.session_state.selected_category = category["id"]
            st.rerun()

st.markdown(f"<h3>Ask about {next((c['name'] for c in st.session_state.categories if c['id'] == st.session_state.selected_category), 'Financial Advice')}</h3>", unsafe_allow_html=True)

# Initialize query input in session state if it doesn't exist
if 'query_input' not in st.session_state:
    st.session_state.query_input = ""

# Query input
query_input = st.text_area(
    "Enter your financial question:",
    value=st.session_state.query_input,
    height=100,
    placeholder=f"Example: What are some good strategies for {st.session_state.selected_category} investing?"
)

# Submit button
col1, col2 = st.columns([1, 5])
with col1:
    submit_button = st.button("Get Advice", type="primary", use_container_width=True)

# Process the query when the button is clicked
if submit_button and query_input:
    # Reset the session state query input
    st.session_state.query_input = ""
    
    # Show a spinner while processing
    with st.spinner("Consulting the financial experts..."):
        try:
            # Send request to backend
            response = requests.post(
                BACKEND_URL,
                json={
                    "input_data": query_input,
                    "category": st.session_state.selected_category
                },
                timeout=20,
                headers={"Content-Type": "application/json"}
            )
            
            # Check status code
            if response.status_code == 200:
                # Get the response data
                response_data = response.json()
                advice = response_data.get("response", "No response")
                category = response_data.get("category", st.session_state.selected_category)
                
                # Add to history
                st.session_state.history.append({
                    "query": query_input,
                    "response": advice,
                    "category": category,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Display the response
                st.markdown("<div class='response-container'>", unsafe_allow_html=True)
                st.markdown(f"<h3>Financial Advice</h3>", unsafe_allow_html=True)
                st.markdown(advice)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Add a visualization based on the category
                if category == "stocks":
                    st.markdown("<h3>Stock Market Visualization</h3>", unsafe_allow_html=True)
                    # Sample stock data visualization
                    data = {
                        'Date': pd.date_range(start='1/1/2023', periods=30, freq='D'),
                        'Price': [100 + i + i*i*0.01 for i in range(30)]
                    }
                    df = pd.DataFrame(data)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(df['Date'], df['Price'])
                    ax.set_title('Sample Stock Price Trend')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Price ($)')
                    st.pyplot(fig)
                
                elif category == "savings":
                    st.markdown("<h3>Savings Growth Projection</h3>", unsafe_allow_html=True)
                    # Sample savings visualization
                    years = range(1, 31)
                    savings = [1000 * (1.05 ** year) for year in years]
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.bar(years, savings, color='green')
                    ax.set_title('Projected Savings Growth (5% Annual Return)')
                    ax.set_xlabel('Years')
                    ax.set_ylabel('Amount ($)')
                    st.pyplot(fig)
                
                elif category == "retirement":
                    st.markdown("<h3>Retirement Fund Projection</h3>", unsafe_allow_html=True)
                    # Sample retirement visualization
                    years = range(1, 41)
                    retirement_fund = [0] * 40
                    for i in range(40):
                        if i == 0:
                            retirement_fund[i] = 10000
                        else:
                            retirement_fund[i] = retirement_fund[i-1] * 1.07 + 6000
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(years, retirement_fund, marker='o', linestyle='-', color='blue')
                    ax.set_title('Retirement Fund Growth (7% Return, $6000 Annual Contribution)')
                    ax.set_xlabel('Years')
                    ax.set_ylabel('Fund Value ($)')
                    st.pyplot(fig)
                
                elif category == "crypto":
                    st.markdown("<h3>Cryptocurrency Volatility</h3>", unsafe_allow_html=True)
                    # Sample crypto visualization
                    import numpy as np
                    days = range(1, 101)
                    np.random.seed(42)  # For reproducibility
                    crypto_price = [10000]
                    for i in range(1, 100):
                        change = np.random.normal(0, 0.05)  # Mean 0, std 5%
                        crypto_price.append(crypto_price[-1] * (1 + change))
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(days, crypto_price, color='orange')
                    ax.set_title('Simulated Cryptocurrency Price Volatility')
                    ax.set_xlabel('Days')
                    ax.set_ylabel('Price ($)')
                    st.pyplot(fig)
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError as e:
            st.error("Error: Unable to connect to backend. Ensure backend service is running.")
            with st.expander("Error Details"):
                st.write(str(e))
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            with st.expander("Traceback"):
                st.code(traceback.format_exc())
else:
    if submit_button and not query_input:
        st.warning("Please enter a question before submitting.")

# Display some sample questions based on the selected category
st.markdown("<h3>Sample Questions</h3>", unsafe_allow_html=True)

sample_questions = {
    "general": [
        "How can I improve my financial health?",
        "What's the difference between a Roth IRA and a traditional IRA?",
        "How much emergency fund should I have?"
    ],
    "stocks": [
        "What are index funds and why should I consider them?",
        "How do I start investing in the stock market with $1000?",
        "What's the difference between growth and value stocks?"
    ],
    "savings": [
        "What are some effective strategies to save money each month?",
        "How can I save for a down payment on a house?",
        "What's the 50/30/20 budgeting rule?"
    ],
    "retirement": [
        "How much should I be saving for retirement in my 30s?",
        "What are the benefits of a 401(k) employer match?",
        "When should I start taking Social Security benefits?"
    ],
    "crypto": [
        "What is blockchain technology and how does it work?",
        "Is cryptocurrency a good long-term investment?",
        "What's the difference between Bitcoin and Ethereum?"
    ]
}

# Get sample questions for the selected category
current_samples = sample_questions.get(st.session_state.selected_category, sample_questions["general"])

# Display sample questions as clickable buttons
cols = st.columns(len(current_samples))
for i, question in enumerate(current_samples):
    with cols[i]:
        if st.button(question, key=f"sample_{i}"):
            st.session_state.query_input = question
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>GANAI Financial Advisor | Powered by OpenAI | Created with Streamlit</p>
        <p>Disclaimer: This is an AI assistant and not a certified financial advisor. Always consult with a professional for important financial decisions.</p>
    </div>
    """, 
    unsafe_allow_html=True
)