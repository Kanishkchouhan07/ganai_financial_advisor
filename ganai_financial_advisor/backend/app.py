from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        
        # Dummy prediction logic
        response_text = f"Prediction for input: {input_text}"

        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        'version': '1.0'
    })

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
            '/api/predict (POST)'
        ]
    }), 404

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5001))
    # Print startup message
    print(f"Starting backend server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)