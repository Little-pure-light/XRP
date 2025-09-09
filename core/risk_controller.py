import logging
from datetime import datetime, timedelta
from app import db
from models import Trade, TradingConfig, Balance
from core.balance_manager import BalanceManager

class RiskController:
    """Risk management and safety checks"""
    
    def __init__(self):
        self.balance_manager = BalanceManager()
        self.logger = logging.getLogger(__name__)
    
    def check_trade_risk(self, opportunity, config):
        """
        Comprehensive risk check before executing trade
        
        Args:
            opportunity: Trade opportunity details
            config: Trading configuration
            
        Returns:
            dict: {'safe': bool, 'reason': str}
        """
        try:
            # 1. Check daily volume limits
            volume_check = self._check_daily_volume_limit(
                opportunity['amount'], 
                config.daily_max_volume
            )
            if not volume_check['safe']:
                return volume_check
            
            # 2. Check balance safety margins
            balance_check = self._check_balance_safety(
                opportunity['amount'], 
                config.risk_buffer
            )
            if not balance_check['safe']:
                return balance_check
            
            # 3. Check pending orders limit
            pending_check = self._check_pending_orders_limit(config.max_pending_orders)
            if not pending_check['safe']:
                return pending_check
            
            # 4. Check price volatility
            volatility_check = self._check_price_volatility(opportunity)
            if not volatility_check['safe']:
                return volatility_check
            
            # 5. Check spread validity
            spread_check = self._check_spread_validity(opportunity, config.spread_threshold)
            if not spread_check['safe']:
                return spread_check
            
            # 6. Check trading frequency
            frequency_check = self._check_trading_frequency()
            if not frequency_check['safe']:
                return frequency_check
            
            return {'safe': True, 'reason': 'All risk checks passed'}
            
        except Exception as e:
            self.logger.error(f"Error in risk check: {e}")
            return {'safe': False, 'reason': f'Risk check error: {e}'}
    
    def _check_daily_volume_limit(self, trade_amount, daily_limit):
        """Check if trade would exceed daily volume limit"""
        try:
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # Calculate today's total volume
            today_trades = Trade.query.filter(
                Trade.created_at >= today_start,
                Trade.status.in_(['completed', 'pending'])
            ).all()
            
            today_volume = sum(trade.amount for trade in today_trades)
            
            if today_volume + trade_amount > daily_limit:
                return {
                    'safe': False, 
                    'reason': f'Daily volume limit exceeded: {today_volume + trade_amount:.2f} > {daily_limit}'
                }
            
            return {'safe': True, 'reason': 'Volume limit OK'}
            
        except Exception as e:
            self.logger.error(f"Error checking daily volume: {e}")
            return {'safe': False, 'reason': 'Volume check failed'}
    
    def _check_balance_safety(self, trade_amount, risk_buffer):
        """Check if balances have sufficient safety margins"""
        try:
            balances = self.balance_manager.get_balances()
            
            # Check XRP balance (for sell order)
            xrp_balance = balances.get('XRP', {}).get('free', 0)
            required_xrp = trade_amount * (1 + risk_buffer)
            
            if xrp_balance < required_xrp:
                return {
                    'safe': False,
                    'reason': f'Insufficient XRP balance with safety margin: {xrp_balance:.2f} < {required_xrp:.2f}'
                }
            
            # Check stablecoin balances (for buy order)
            usdt_balance = balances.get('USDT', {}).get('free', 0)
            usdc_balance = balances.get('USDC', {}).get('free', 0)
            
            # Estimate required stablecoin (using approximate price)
            estimated_price = 0.52  # Conservative estimate
            required_stable = trade_amount * estimated_price * (1 + risk_buffer)
            
            if usdt_balance < required_stable and usdc_balance < required_stable:
                return {
                    'safe': False,
                    'reason': f'Insufficient stablecoin balance with safety margin'
                }
            
            return {'safe': True, 'reason': 'Balance safety OK'}
            
        except Exception as e:
            self.logger.error(f"Error checking balance safety: {e}")
            return {'safe': False, 'reason': 'Balance safety check failed'}
    
    def _check_pending_orders_limit(self, max_pending):
        """Check if pending orders limit would be exceeded"""
        try:
            pending_count = Trade.query.filter_by(status='pending').count()
            
            if pending_count >= max_pending:
                return {
                    'safe': False,
                    'reason': f'Too many pending orders: {pending_count} >= {max_pending}'
                }
            
            return {'safe': True, 'reason': 'Pending orders OK'}
            
        except Exception as e:
            self.logger.error(f"Error checking pending orders: {e}")
            return {'safe': False, 'reason': 'Pending orders check failed'}
    
    def _check_price_volatility(self, opportunity):
        """Check if price volatility is within acceptable limits"""
        try:
            # Get recent price movements
            recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
            
            from models import PriceHistory
            recent_prices = PriceHistory.query.filter(
                PriceHistory.timestamp >= recent_cutoff
            ).order_by(PriceHistory.timestamp.desc()).limit(20).all()
            
            if len(recent_prices) < 5:
                return {'safe': True, 'reason': 'Insufficient price history for volatility check'}
            
            # Calculate price volatility
            prices = [p.price for p in recent_prices]
            max_price = max(prices)
            min_price = min(prices)
            volatility = (max_price - min_price) / min_price
            
            # If volatility > 2%, it's too risky
            if volatility > 0.02:
                return {
                    'safe': False,
                    'reason': f'High price volatility detected: {volatility:.4f}'
                }
            
            return {'safe': True, 'reason': 'Price volatility OK'}
            
        except Exception as e:
            self.logger.error(f"Error checking price volatility: {e}")
            return {'safe': True, 'reason': 'Volatility check skipped due to error'}
    
    def _check_spread_validity(self, opportunity, min_spread):
        """Check if spread is still valid and above threshold"""
        try:
            current_spread = opportunity.get('spread_percentage', 0)
            
            if current_spread < min_spread:
                return {
                    'safe': False,
                    'reason': f'Spread too small: {current_spread:.4f} < {min_spread:.4f}'
                }
            
            # Check if spread is not too good to be true (>5% is suspicious)
            if current_spread > 0.05:
                return {
                    'safe': False,
                    'reason': f'Spread too large, possible data error: {current_spread:.4f}'
                }
            
            return {'safe': True, 'reason': 'Spread validity OK'}
            
        except Exception as e:
            self.logger.error(f"Error checking spread validity: {e}")
            return {'safe': False, 'reason': 'Spread validity check failed'}
    
    def _check_trading_frequency(self, min_interval_seconds=30):
        """Check if we're not trading too frequently"""
        try:
            recent_cutoff = datetime.utcnow() - timedelta(seconds=min_interval_seconds)
            
            recent_trades = Trade.query.filter(
                Trade.created_at >= recent_cutoff
            ).count()
            
            # Allow max 1 trade per 30 seconds
            if recent_trades > 0:
                return {
                    'safe': False,
                    'reason': f'Trading too frequently: {recent_trades} trades in last {min_interval_seconds}s'
                }
            
            return {'safe': True, 'reason': 'Trading frequency OK'}
            
        except Exception as e:
            self.logger.error(f"Error checking trading frequency: {e}")
            return {'safe': True, 'reason': 'Frequency check skipped due to error'}
    
    def check_system_health(self):
        """Check overall system health"""
        try:
            health_status = {
                'healthy': True,
                'warnings': [],
                'errors': []
            }
            
            # Check database connectivity
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
            except Exception as e:
                health_status['healthy'] = False
                health_status['errors'].append(f'Database connection error: {e}')
            
            # Check balance consistency
            balances = self.balance_manager.get_balances()
            for currency, balance in balances.items():
                if balance['total'] < 0:
                    health_status['warnings'].append(f'Negative {currency} balance detected')
                
                if balance['locked'] > balance['total']:
                    health_status['healthy'] = False
                    health_status['errors'].append(f'Locked {currency} exceeds total balance')
            
            # Check for stuck pending orders
            old_pending = Trade.query.filter(
                Trade.status == 'pending',
                Trade.created_at < datetime.utcnow() - timedelta(minutes=5)
            ).count()
            
            if old_pending > 0:
                health_status['warnings'].append(f'{old_pending} orders pending for >5 minutes')
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            return {
                'healthy': False,
                'warnings': [],
                'errors': [f'Health check failed: {e}']
            }
    
    def calculate_max_safe_trade_amount(self, config):
        """Calculate maximum safe trade amount based on current conditions"""
        try:
            balances = self.balance_manager.get_balances()
            
            # Base on XRP balance with safety margin
            xrp_balance = balances.get('XRP', {}).get('free', 0)
            max_xrp = xrp_balance * (1 - config.risk_buffer)
            
            # Base on daily volume limit
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            today_trades = Trade.query.filter(
                Trade.created_at >= today_start,
                Trade.status.in_(['completed', 'pending'])
            ).all()
            
            today_volume = sum(trade.amount for trade in today_trades)
            remaining_daily_volume = config.daily_max_volume - today_volume
            
            # Return the minimum of the constraints
            max_safe_amount = min(max_xrp, remaining_daily_volume, config.trade_amount)
            
            return max(0, max_safe_amount)
            
        except Exception as e:
            self.logger.error(f"Error calculating max safe trade amount: {e}")
            return 0
