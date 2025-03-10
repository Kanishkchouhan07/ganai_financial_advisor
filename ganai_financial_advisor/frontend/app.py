from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import requests
import os
import json
from datetime import datetime, timedelta
import plotly
import plotly.graph_objs as go
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24)),
        SESSION_TYPE='filesystem',
        SESSION_FILE_DIR='/tmp/flask_session',
        SESSION_PERMANENT=False,
        PERMANENT_SESSION_LIFETIME=timedelta(days=1)
    )
else:
    app.config.update(
        SECRET_KEY=os.urandom(24),
        SESSION_TYPE='filesystem',
        SESSION_FILE_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session'),
        SESSION_PERMANENT=False,
        PERMANENT_SESSION_LIFETIME=timedelta(days=1)
    )

# Create session directory if it doesn't exist
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize session interface
Session(app)

# Get backend URL from environment variable or use localhost as fallback
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5001/api/predict")
BASE_URL = BACKEND_URL.rsplit('/api/predict', 1)[0]

logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
logger.info(f"Backend URL: {BACKEND_URL}")
logger.info(f"Base URL: {BASE_URL}")

def verify_backend_configuration():
    """Verify backend configuration and connectivity"""
    try:
        # Check if we can reach the backend
        response = requests.get(f"{BASE_URL}/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Backend test response: {data}")
            return data.get('openai_configured', False)
        return False
    except Exception as e:
        logger.error(f"Backend verification failed: {str(e)}")
        return False

# Add error handling for backend connection
def is_backend_healthy():
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        is_healthy = response.status_code == 200
        if is_healthy:
            logger.info("Backend health check: Healthy")
        else:
            logger.warning(f"Backend health check failed with status code: {response.status_code}")
        return is_healthy
    except Exception as e:
        logger.error(f"Backend health check failed: {str(e)}")
        return False

def fetch_categories():
    try:
        logger.info(f"Fetching categories from: {BASE_URL}/api/categories")
        response = requests.get(f"{BASE_URL}/api/categories", timeout=10)
        if response.status_code == 200:
            categories = response.json().get("categories", [])
            logger.info(f"Successfully fetched {len(categories)} categories")
            return categories
        logger.error(f"Failed to fetch categories. Status code: {response.status_code}")
        if response.status_code != 404:  # Don't log 404 response content
            try:
                logger.error(f"Response content: {response.text}")
            except:
                pass
        return []
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
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
    
    # Check backend health and configuration
    backend_healthy = is_backend_healthy()
    openai_configured = verify_backend_configuration() if backend_healthy else False
    
    if not backend_healthy:
        logger.warning("Backend service is not healthy")
    elif not openai_configured:
        logger.warning("OpenAI API is not properly configured")
    
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
        graphJSON=graphJSON,
        backend_healthy=backend_healthy,
        openai_configured=openai_configured
    )

@app.route('/submit', methods=['POST'])
def submit_query():
    query = request.form.get('query')
    category = request.form.get('category', 'general')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Verify backend health before proceeding
    if not is_backend_healthy():
        return jsonify({'error': 'Backend service is not available'}), 503
    
    # Verify OpenAI configuration
    if not verify_backend_configuration():
        return jsonify({'error': 'OpenAI API is not properly configured'}), 503
    
    try:
        logger.info(f"Sending query to backend: {BACKEND_URL}")
        logger.info(f"Query: {query}")
        logger.info(f"Category: {category}")
        
        response = requests.post(
            BACKEND_URL,
            json={
                "input_data": query,
                "category": category
            },
            timeout=20,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"Backend response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            advice = response_data.get("response", "No response")
            category = response_data.get("category", category)
            
            logger.info("Successfully received response from backend")
            
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
            error_msg = f"Backend service error: {response.status_code}"
            logger.error(error_msg)
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_msg)
                logger.error(f"Backend error details: {error_data}")
            except:
                logger.error(f"Raw response: {response.text}")
            return jsonify({'error': error_msg}), response.status_code
            
    except requests.exceptions.Timeout:
        error_msg = "Backend service timeout - please try again"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 504
    except requests.exceptions.ConnectionError:
        error_msg = "Unable to connect to backend service"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 503
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Exception details: {str(e)}")
        return jsonify({'error': error_msg}), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    session['history'] = []
    session.modified = True
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)