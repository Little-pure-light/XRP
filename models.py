from app import db
from datetime import datetime
from sqlalchemy import func

class TradingConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spread_threshold = db.Column(db.Float, default=0.003)
    trade_amount = db.Column(db.Float, default=100.0)
    daily_max_volume = db.Column(db.Float, default=5000.0)
    risk_buffer = db.Column(db.Float, default=0.1)
    max_pending_orders = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trade_type = db.Column(db.String(20), nullable=False)  # 'buy' or 'sell'
    pair = db.Column(db.String(20), nullable=False)  # 'XRP/USDT' or 'XRP/USDC'
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    spread = db.Column(db.Float)
    profit_loss = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    order_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(10), nullable=False)  # 'XRP', 'USDT', 'USDC'
    amount = db.Column(db.Float, nullable=False, default=0.0)
    locked = db.Column(db.Float, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ArbitrageOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usdt_price = db.Column(db.Float, nullable=False)
    usdc_price = db.Column(db.Float, nullable=False)
    spread = db.Column(db.Float, nullable=False)
    spread_percentage = db.Column(db.Float, nullable=False)
    opportunity_type = db.Column(db.String(20))  # 'buy_usdt_sell_usdc' or 'buy_usdc_sell_usdt'
    executed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)  # 'INFO', 'WARNING', 'ERROR'
    message = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
