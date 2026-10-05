from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Finbot online! OK", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("Recebido:", data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
