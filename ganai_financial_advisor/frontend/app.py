from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import requests
import os
import json
from datetime import datetime
import plotly
import plotly.graph_objs as go
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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

def fetch_categories():
    try:
        response = requests.get(f"{BASE_URL}/api/categories", timeout=10)
        if response.status_code == 200:
            return response.json().get("categories", [])
        return []
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        return []

def create_stock_visualization():
    # Sample stock data visualization
    data = {
        'Date': pd.date_range(start='1/1/2023', periods=30, freq='D'),
        'Price': [100 + i + i*i*0.01 for i in range(30)]
    }
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Price'], mode='lines', name='Stock Price'))
    fig.update_layout(
        title='Sample Stock Price Trend',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    if 'history' not in session:
        session['history'] = []
    
    categories = fetch_categories()
    if not categories:
        categories = [
            {"id": "general", "name": "General Financial Advice"},
            {"id": "stocks", "name": "Stocks & Investments"},
            {"id": "savings", "name": "Savings & Budgeting"},
            {"id": "retirement", "name": "Retirement Planning"},
            {"id": "crypto", "name": "Cryptocurrency"}
        ]
    
    selected_category = request.args.get('category', 'general')
    graphJSON = create_stock_visualization() if selected_category == 'stocks' else None
    
    return render_template(
        'index.html',
        categories=categories,
        selected_category=selected_category,
        history=reversed(session['history'][-10:]),
        backend_url=BACKEND_URL,
        base_url=BASE_URL,
        graphJSON=graphJSON
    )

@app.route('/submit', methods=['POST'])
def submit_query():
    query = request.form.get('query')
    category = request.form.get('category', 'general')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        response = requests.post(
            BACKEND_URL,
            json={
                "input_data": query,
                "category": category
            },
            timeout=20,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            response_data = response.json()
            advice = response_data.get("response", "No response")
            category = response_data.get("category", category)
            
            # Add to history
            if 'history' not in session:
                session['history'] = []
            
            session['history'].append({
                "query": query,
                "response": advice,
                "category": category,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            session.modified = True
            
            return jsonify({
                'success': True,
                'response': advice,
                'category': category,
                'graphJSON': create_stock_visualization() if category == 'stocks' else None
            })
        else:
            return jsonify({'error': 'Backend service error'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    session['history'] = []
    session.modified = True
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)