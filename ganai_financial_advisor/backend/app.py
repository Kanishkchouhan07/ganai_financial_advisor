from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/financial-advice", methods=["POST"])
def financial_advice():
    user_input = request.json.get("query")
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a financial advisor."},
                  {"role": "user", "content": user_input}]
    )
    
    return jsonify({"response": response['choices'][0]['message']['content']})

if __name__ == "__main__":
    app.run(debug=True)