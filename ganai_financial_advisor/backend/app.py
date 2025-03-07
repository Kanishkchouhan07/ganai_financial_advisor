from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "No data received"}), 400
        
        # Your ML prediction logic here
        result = {"response": "Your prediction result"}
        
        return jsonify(result)  # Ensure JSON response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)