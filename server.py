import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, request, jsonify
from flask_cors import CORS
from src.deepseek import ask

app = Flask(__name__)
CORS(app)

app.config['JSON_AS_ASCII'] = False


@app.route("/ask", methods=["POST"])
def ask_endpoint():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400
    try:
        response = ask(data["text"])
        return jsonify({"response": response}), 200, {"Content-Type": "application/json; charset=utf-8"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)