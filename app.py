import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from config import get_config
from flask_cors import CORS

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- SQLAlchemy ----------
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# ---------- Flask App ----------
app = Flask(__name__)
# CORS：允許本地 / Railway / Cloudflare Pages 呼叫
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5000",
            "https://xrp-production-9caf.up.railway.app",
            "https://xrpbot.pages.dev"
        ]
    }
})

# ---------- Config ----------
config_obj = get_config()
app.config.from_object(config_obj)

# ---------- Middleware ----------
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# ---------- Routes (示例) ----------
@app.route("/api/health", methods=["GET"])
def health_check():
    return {"status": "ok", "message": "XRP backend running!"}, 200

# ⚠️ 確保這裡還有你原本的 API，像 /api/start-trading、/api/monitor ……

# ---------- Run ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
