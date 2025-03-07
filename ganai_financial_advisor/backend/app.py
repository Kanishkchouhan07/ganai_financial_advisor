from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)