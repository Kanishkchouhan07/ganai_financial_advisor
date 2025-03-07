from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import openai
import json

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)
# Enable CORS for all domains to ensure Streamlit can connect
CORS(app, resources={r"/*": {"origins": "*"}})

# Root route for basic verification
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'status': 'online',
        'message': 'GANAI Financial Advisor API is running',
        'endpoints': {
            'health': '/health',
            'test': '/test',
            'predict': '/api/predict (POST)'
        }
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({'error': 'Invalid input data'}), 400
        
        input_text = data['input_data']
        category = data.get('category', 'general')
        
        # Generate financial advice using OpenAI
        response_text = generate_financial_advice(input_text, category)

        return jsonify({
            'response': response_text,
            'category': category
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_financial_advice(query, category="general"):
    """Generate financial advice using OpenAI API based on the query and category."""
    
    # Define system prompts for different categories
    system_prompts = {
        "general": "You are GANAI, an expert financial advisor. Provide helpful, accurate, and concise financial advice.",
        "stocks": "You are GANAI, an expert stock market advisor. Provide helpful, accurate, and concise advice about stocks, investments, and market trends.",
        "savings": "You are GANAI, an expert savings advisor. Provide helpful, accurate, and concise advice about saving money, budgeting, and financial planning.",
        "retirement": "You are GANAI, an expert retirement planning advisor. Provide helpful, accurate, and concise advice about retirement planning, 401(k)s, IRAs, and long-term financial security.",
        "crypto": "You are GANAI, an expert cryptocurrency advisor. Provide helpful, accurate, and concise advice about cryptocurrencies, blockchain, and digital assets."
    }
    
    # Use the appropriate system prompt or default to general
    system_prompt = system_prompts.get(category, system_prompts["general"])
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract and return the response text
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        # Fallback response if API call fails
        return f"I'm sorry, I couldn't generate advice for your query about {query}. Please try again later."

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Simple test endpoint that doesn't require any input
@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Backend is running correctly',
        'environment': os.environ.get('FLASK_ENV', 'not set'),
        'version': '1.0',
        'openai_configured': bool(openai.api_key)
    })

# Get available categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = [
        {"id": "general", "name": "General Financial Advice"},
        {"id": "stocks", "name": "Stocks & Investments"},
        {"id": "savings", "name": "Savings & Budgeting"},
        {"id": "retirement", "name": "Retirement Planning"},
        {"id": "crypto", "name": "Cryptocurrency"}
    ]
    return jsonify({"categories": categories})

# Handle 404 errors
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested URL was not found on the server.',
        'available_endpoints': [
            '/',
            '/health',
            '/test',
            '/api/categories',
            '/api/predict (POST)'
        ]
    }), 404

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5001))
    # Print startup message
    print(f"Starting backend server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)