import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def root():
    return "Hello, the API is alive!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway/Cloudflare 會自動帶 PORT
    app.run(host="0.0.0.0", port=port, debug=True)
