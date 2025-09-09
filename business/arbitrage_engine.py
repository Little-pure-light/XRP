import time
import threading
import logging
from datetime import datetime
from app import db
from models import ArbitrageOpportunity, TradingConfig
from core.price_monitor import PriceMonitor
from core.balance_manager import BalanceManager
from core.trade_executor import TradeExecutor
from core.risk_controller import RiskController
from core.data_logger import DataLogger
from core.config_manager import ConfigManager

class ArbitrageEngine:
    """Main arbitrage strategy engine"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.price_monitor = PriceMonitor()
        self.balance_manager = BalanceManager()
        self.trade_executor = TradeExecutor()
        self.risk_controller = RiskController()
        self.data_logger = DataLogger()
        self.config_manager = ConfigManager()
        
        # Start price monitoring
        self.price_monitor.start_monitoring()
    
    def start(self):
        """Start the arbitrage engine"""
        if self.running:
            self.logger.warning("Arbitrage engine is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._main_loop)
        self.thread.daemon = True
        self.thread.start()
        
        self.data_logger.log_system_event("STARTED", "Arbitrage engine started", "ArbitrageEngine")
        self.logger.info("Arbitrage engine started")
    
    def stop(self):
        """Stop the arbitrage engine"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join()
        
        # Cancel any pending orders
        self.trade_executor.cancel_pending_orders()
        
        self.data_logger.log_system_event("STOPPED", "Arbitrage engine stopped", "ArbitrageEngine")
        self.logger.info("Arbitrage engine stopped")
    
    def is_running(self):
        """Check if the engine is running"""
        return self.running
    
    def _main_loop(self):
        """Main arbitrage detection and execution loop"""
        while self.running:
            try:
                # Get current configuration
                config = self.config_manager.get_config()
                if not config:
                    self.logger.error("No configuration found, stopping engine")
                    break
                
                # Check system health
                health = self.risk_controller.check_system_health()
                if not health['healthy']:
                    self.logger.error(f"System health check failed: {health['errors']}")
                    self.data_logger.log_risk_event(
                        "SYSTEM_HEALTH", 
                        f"Health check failed: {health['errors']}", 
                        "ERROR"
                    )
                    time.sleep(10)  # Wait before retrying
                    continue
                
                # Check for arbitrage opportunities
                opportunity = self._detect_arbitrage_opportunity(config)
                
                if opportunity:
                    self.logger.info(f"Arbitrage opportunity detected: {opportunity['spread_percentage']:.4f}%")
                    self.data_logger.log_arbitrage_opportunity(opportunity)
                    
                    # Store opportunity in database
                    self._store_opportunity(opportunity)
                    
                    # Execute trade if risk checks pass
                    self._execute_opportunity(opportunity, config)
                
                # Check for order timeouts
                self.trade_executor.check_order_timeouts()
                
                # Rebalance stablecoins if needed
                self.balance_manager.rebalance_stablecoins()
                
                # Sleep between iterations
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in arbitrage main loop: {e}")
                self.data_logger.log_error(f"Main loop error: {e}", "ArbitrageEngine", e)
                time.sleep(10)  # Wait before retrying on error
    
    def _detect_arbitrage_opportunity(self, config):
        """Detect arbitrage opportunities"""
        try:
            # Get current prices
            prices = self.price_monitor.get_current_prices()
            
            if 'XRP/USDT' not in prices or 'XRP/USDC' not in prices:
                return None
            
            usdt_price = prices['XRP/USDT']['price']
            usdc_price = prices['XRP/USDC']['price']
            
            # Calculate spread
            spread = abs(usdt_price - usdc_price)
            spread_percentage = (spread / min(usdt_price, usdc_price)) * 100
            
            # Check if spread exceeds threshold
            if spread_percentage < config.spread_threshold * 100:
                return None
            
            # Determine trade direction
            if usdt_price > usdc_price:
                # Sell XRP for USDT, buy XRP with USDC
                opportunity_type = 'sell_usdt_buy_usdc'
                sell_pair = 'XRP/USDT'
                buy_pair = 'XRP/USDC'
                sell_price = usdt_price
                buy_price = usdc_price
            else:
                # Sell XRP for USDC, buy XRP with USDT
                opportunity_type = 'sell_usdc_buy_usdt'
                sell_pair = 'XRP/USDC'
                buy_pair = 'XRP/USDT'
                sell_price = usdc_price
                buy_price = usdt_price
            
            # Calculate safe trade amount
            max_safe_amount = self.risk_controller.calculate_max_safe_trade_amount(config)
            trade_amount = min(config.trade_amount, max_safe_amount)
            
            if trade_amount <= 0:
                self.logger.warning("No safe trade amount available")
                return None
            
            opportunity = {
                'usdt_price': usdt_price,
                'usdc_price': usdc_price,
                'spread': spread,
                'spread_percentage': spread_percentage,
                'opportunity_type': opportunity_type,
                'sell_pair': sell_pair,
                'buy_pair': buy_pair,
                'sell_price': sell_price,
                'buy_price': buy_price,
                'amount': trade_amount,
                'estimated_profit': trade_amount * spread
            }
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error detecting arbitrage opportunity: {e}")
            return None
    
    def _store_opportunity(self, opportunity):
        """Store arbitrage opportunity in database"""
        try:
            db_opportunity = ArbitrageOpportunity(
                usdt_price=opportunity['usdt_price'],
                usdc_price=opportunity['usdc_price'],
                spread=opportunity['spread'],
                spread_percentage=opportunity['spread_percentage'],
                opportunity_type=opportunity['opportunity_type'],
                executed=False
            )
            
            db.session.add(db_opportunity)
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing opportunity: {e}")
            db.session.rollback()
    
    def _execute_opportunity(self, opportunity, config):
        """Execute arbitrage opportunity with risk checks"""
        try:
            # Perform comprehensive risk check
            risk_check = self.risk_controller.check_trade_risk(opportunity, config)
            
            if not risk_check['safe']:
                self.logger.warning(f"Trade blocked by risk check: {risk_check['reason']}")
                self.data_logger.log_risk_event(
                    "TRADE_BLOCKED", 
                    risk_check['reason'], 
                    "WARNING"
                )
                return
            
            # Execute the arbitrage trade
            self.logger.info(f"Executing arbitrage trade: {opportunity['amount']} XRP")
            
            trade_result = self.trade_executor.execute_arbitrage_trade(opportunity)
            
            if trade_result:
                # Mark opportunity as executed
                self._mark_opportunity_executed(opportunity)
                
                profit_loss = trade_result['profit_loss'] if 'profit_loss' in trade_result else 0
                self.logger.info(f"Arbitrage trade completed with P&L: {profit_loss:.4f}")
                
                self.data_logger.log_trade({
                    'type': 'arbitrage',
                    'amount': opportunity['amount'],
                    'profit_loss': profit_loss,
                    'spread': opportunity['spread_percentage']
                }, 'completed')
                
            else:
                self.logger.error("Arbitrage trade execution failed")
                self.data_logger.log_error("Arbitrage trade execution failed", "ArbitrageEngine")
            
        except Exception as e:
            self.logger.error(f"Error executing opportunity: {e}")
            self.data_logger.log_error(f"Opportunity execution error: {e}", "ArbitrageEngine", e)
    
    def _mark_opportunity_executed(self, opportunity):
        """Mark opportunity as executed in database"""
        try:
            # Find the most recent matching opportunity
            db_opportunity = ArbitrageOpportunity.query.filter(
                ArbitrageOpportunity.usdt_price == opportunity['usdt_price'],
                ArbitrageOpportunity.usdc_price == opportunity['usdc_price'],
                ArbitrageOpportunity.executed == False
            ).order_by(ArbitrageOpportunity.created_at.desc()).first()
            
            if db_opportunity:
                db_opportunity.executed = True
                db.session.commit()
            
        except Exception as e:
            self.logger.error(f"Error marking opportunity as executed: {e}")
            db.session.rollback()
    
    def get_engine_status(self):
        """Get current engine status"""
        try:
            config = self.config_manager.get_config()
            balances = self.balance_manager.get_balances()
            prices = self.price_monitor.get_current_prices()
            
            # Get recent performance
            from core.profit_analyzer import ProfitAnalyzer
            profit_analyzer = ProfitAnalyzer()
            today_stats = profit_analyzer.get_today_stats()
            
            status = {
                'running': self.running,
                'configuration': {
                    'spread_threshold': config.spread_threshold if config else 0.003,
                    'trade_amount': config.trade_amount if config else 100.0,
                    'daily_max_volume': config.daily_max_volume if config else 5000.0
                },
                'balances': balances,
                'current_prices': prices,
                'today_performance': today_stats,
                'pending_orders': self.trade_executor.get_pending_orders_count(),
                'system_health': self.risk_controller.check_system_health(),
                'last_update': datetime.utcnow().isoformat()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting engine status: {e}")
            return {
                'running': self.running,
                'error': str(e),
                'last_update': datetime.utcnow().isoformat()
            }
    
    def force_rebalance(self):
        """Force stablecoin rebalancing"""
        try:
            self.balance_manager.rebalance_stablecoins()
            self.data_logger.log_system_event("REBALANCE", "Manual rebalance triggered", "ArbitrageEngine")
            self.logger.info("Manual rebalance completed")
        except Exception as e:
            self.logger.error(f"Error in manual rebalance: {e}")
            self.data_logger.log_error(f"Manual rebalance error: {e}", "ArbitrageEngine", e)
