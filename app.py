import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from config import get_config
from flask_cors import CORS

# Configure logging based on environment
config_class = get_config()
log_level = logging.DEBUG if not config_class.IS_PRODUCTION else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://xrpbot.pages.dev"}})

# Load configuration
config_obj = get_config()
app.config.from_object(config_obj)

# Production-ready security configuration
if not app.config['SECRET_KEY'] or app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
    if config_obj.IS_PRODUCTION:
        raise ValueError("SESSION_SECRET environment variable is required in production!")

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Add template global for CDN-aware static URLs
@app.template_global()
def static_url(filename):
    """Template function for CDN-aware static URLs"""
    return config_obj.get_static_url(filename)

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

# Import routes
import routes
