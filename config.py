import os

class Config:
    """Base configuration class"""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///xrp_trading.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Railway/Production detection
    IS_RAILWAY = bool(os.environ.get('RAILWAY_ENVIRONMENT'))
    IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production' or IS_RAILWAY
    
    # CDN Configuration for Cloudflare
    CDN_DOMAIN = os.environ.get('CDN_DOMAIN', '')  # e.g., 'https://your-domain.cloudflare.com'
    USE_CDN = IS_PRODUCTION and bool(CDN_DOMAIN)
    
    # Static files configuration
    @staticmethod
    def get_static_url(filename):
        """Get the appropriate URL for static files (CDN or local)"""
        from flask import current_app
        if current_app.config.get('USE_CDN') and current_app.config.get('CDN_DOMAIN'):
            cdn_domain = current_app.config['CDN_DOMAIN'].rstrip('/')
            return f"{cdn_domain}/static/{filename}"
        else:
            from flask import url_for
            return url_for('static', filename=filename)
    
    # Database connection pool (production optimized)
    if "postgresql" in SQLALCHEMY_DATABASE_URI or "postgres" in SQLALCHEMY_DATABASE_URI:
        # Supabase/PostgreSQL configuration with SSL enforcement
        connect_args = {
            "connect_timeout": 10,
            "application_name": "quantum_wealth_bridge"
        }
        # Ensure SSL for Supabase if not in URL
        if "sslmode" not in SQLALCHEMY_DATABASE_URI:
            connect_args["sslmode"] = "require"
            
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_recycle": 280,  # Railway timeout is 300s
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "connect_args": connect_args
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    USE_CDN = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class RailwayConfig(ProductionConfig):
    """Railway-specific configuration"""
    pass

# Configuration selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'railway': RailwayConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate configuration based on environment"""
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        return config['railway']
    elif os.environ.get('FLASK_ENV') == 'production':
        return config['production']
    else:
        return config['development']