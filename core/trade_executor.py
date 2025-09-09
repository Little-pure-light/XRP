import time
import logging
from datetime import datetime, timedelta
from app import db
from models import Trade
from core.api_connector import APIConnector
from core.balance_manager import BalanceManager

class TradeExecutor:
    """Trade execution logic with sell-first strategy"""
    
    def __init__(self):
        self.api = APIConnector()
        self.balance_manager = BalanceManager()
        self.logger = logging.getLogger(__name__)
        self.pending_orders = {}
        
        # Connect to API
        self.api.connect()
    
    def execute_arbitrage_trade(self, opportunity):
        """
        Execute arbitrage trade: ALWAYS sell first, then buy
        
        Args:
            opportunity: Dict with trade details
                - sell_pair: pair to sell (e.g., 'XRP/USDT')
                - buy_pair: pair to buy (e.g., 'XRP/USDC')
                - amount: XRP amount to trade
                - sell_price: expected sell price
                - buy_price: expected buy price
        """
        try:
            amount = opportunity['amount']
            sell_pair = opportunity['sell_pair']
            buy_pair = opportunity['buy_pair']
            
            self.logger.info(f"Starting arbitrage trade: Sell {amount} {sell_pair}, Buy {amount} {buy_pair}")
            
            # Step 1: Execute sell order first (mandatory)
            sell_trade = self._execute_sell_order(sell_pair, amount, opportunity['sell_price'])
            
            if not sell_trade:
                self.logger.error("Sell order failed, aborting arbitrage")
                return None
            
            # Step 2: Execute buy order
            buy_trade = self._execute_buy_order(buy_pair, amount, opportunity['buy_price'])
            
            if not buy_trade:
                self.logger.error("Buy order failed after successful sell - this is a problem!")
                # In real trading, this would require immediate attention
                return sell_trade
            
            # Calculate profit/loss
            sell_value = sell_trade.total_value
            buy_value = buy_trade.total_value
            profit_loss = sell_value - buy_value
            
            # Update profit/loss for both trades
            sell_trade.profit_loss = profit_loss / 2
            buy_trade.profit_loss = profit_loss / 2
            
            db.session.commit()
            
            self.logger.info(f"Arbitrage trade completed. P&L: {profit_loss:.4f}")
            
            return {
                'sell_trade': sell_trade,
                'buy_trade': buy_trade,
                'profit_loss': profit_loss
            }
            
        except Exception as e:
            self.logger.error(f"Error executing arbitrage trade: {e}")
            db.session.rollback()
            return None
    
    def _execute_sell_order(self, pair, amount, expected_price):
        """Execute a sell order"""
        try:
            # Check if we have sufficient XRP
            if not self.balance_manager.check_sufficient_balance('XRP', amount):
                raise Exception("Insufficient XRP balance for sell order")
            
            # Lock XRP balance
            self.balance_manager.lock_balance('XRP', amount)
            
            # Create trade record
            trade = Trade(
                trade_type='sell',
                pair=pair,
                amount=amount,
                price=expected_price,
                total_value=amount * expected_price,
                status='pending'
            )
            db.session.add(trade)
            db.session.flush()  # Get the trade ID
            
            # Execute order via API
            order = self.api.create_order(
                symbol=pair,
                order_type='market',
                side='sell',
                amount=amount
            )
            
            # Update trade with order details
            trade.order_id = order['id']
            trade.price = order['price']
            trade.total_value = amount * order['price']
            
            # Simulate order completion
            time.sleep(0.1)  # Small delay for realism
            
            # Check order status
            status = self.api.get_order_status(order['id'], pair)
            if status['status'] == 'closed':
                trade.status = 'completed'
                trade.completed_at = datetime.utcnow()
                
                # Update balances
                self.balance_manager.unlock_balance('XRP', amount)
                self.balance_manager.update_balance('XRP', -amount)
                
                # Determine which stablecoin we received
                if 'USDT' in pair:
                    self.balance_manager.update_balance('USDT', trade.total_value)
                else:
                    self.balance_manager.update_balance('USDC', trade.total_value)
                
                self.logger.info(f"Sell order completed: {amount} XRP at {order['price']:.4f}")
            
            db.session.commit()
            return trade
            
        except Exception as e:
            self.logger.error(f"Error executing sell order: {e}")
            db.session.rollback()
            # Unlock balance if it was locked
            try:
                self.balance_manager.unlock_balance('XRP', amount)
            except:
                pass
            return None
    
    def _execute_buy_order(self, pair, amount, expected_price):
        """Execute a buy order"""
        try:
            # Determine which stablecoin we need
            currency = 'USDT' if 'USDT' in pair else 'USDC'
            required_value = amount * expected_price
            
            # Check if we have sufficient stablecoin
            if not self.balance_manager.check_sufficient_balance(currency, required_value):
                raise Exception(f"Insufficient {currency} balance for buy order")
            
            # Lock stablecoin balance
            self.balance_manager.lock_balance(currency, required_value)
            
            # Create trade record
            trade = Trade(
                trade_type='buy',
                pair=pair,
                amount=amount,
                price=expected_price,
                total_value=required_value,
                status='pending'
            )
            db.session.add(trade)
            db.session.flush()  # Get the trade ID
            
            # Execute order via API
            order = self.api.create_order(
                symbol=pair,
                order_type='market',
                side='buy',
                amount=amount
            )
            
            # Update trade with order details
            trade.order_id = order['id']
            trade.price = order['price']
            trade.total_value = amount * order['price']
            
            # Simulate order completion
            time.sleep(0.1)  # Small delay for realism
            
            # Check order status
            status = self.api.get_order_status(order['id'], pair)
            if status['status'] == 'closed':
                trade.status = 'completed'
                trade.completed_at = datetime.utcnow()
                
                # Update balances
                self.balance_manager.unlock_balance(currency, required_value)
                self.balance_manager.update_balance(currency, -trade.total_value)
                self.balance_manager.update_balance('XRP', amount)
                
                self.logger.info(f"Buy order completed: {amount} XRP at {order['price']:.4f}")
            
            db.session.commit()
            return trade
            
        except Exception as e:
            self.logger.error(f"Error executing buy order: {e}")
            db.session.rollback()
            # Unlock balance if it was locked
            try:
                if 'currency' in locals() and 'required_value' in locals():
                    self.balance_manager.unlock_balance(currency, required_value)
            except:
                pass
            return None
    
    def get_pending_orders_count(self):
        """Get count of pending orders"""
        return Trade.query.filter_by(status='pending').count()
    
    def cancel_pending_orders(self):
        """Cancel all pending orders"""
        try:
            pending_trades = Trade.query.filter_by(status='pending').all()
            
            for trade in pending_trades:
                if trade.order_id:
                    try:
                        self.api.cancel_order(trade.order_id, trade.pair)
                    except:
                        pass  # Order might already be completed
                
                trade.status = 'cancelled'
                
                # Unlock balances
                if trade.trade_type == 'sell':
                    self.balance_manager.unlock_balance('XRP', trade.amount)
                else:
                    currency = 'USDT' if 'USDT' in trade.pair else 'USDC'
                    self.balance_manager.unlock_balance(currency, trade.total_value)
            
            db.session.commit()
            self.logger.info(f"Cancelled {len(pending_trades)} pending orders")
            
        except Exception as e:
            self.logger.error(f"Error cancelling pending orders: {e}")
            db.session.rollback()
    
    def check_order_timeouts(self, timeout_seconds=30):
        """Check for and handle order timeouts"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=timeout_seconds)
            
            timed_out_trades = Trade.query.filter(
                Trade.status == 'pending',
                Trade.created_at < cutoff_time
            ).all()
            
            for trade in timed_out_trades:
                self.logger.warning(f"Order timeout detected: {trade.order_id}")
                
                # Try to get final status
                if trade.order_id:
                    try:
                        status = self.api.get_order_status(trade.order_id, trade.pair)
                        if status['status'] == 'closed':
                            trade.status = 'completed'
                            trade.completed_at = datetime.utcnow()
                        else:
                            trade.status = 'timeout'
                            # Unlock balances
                            if trade.trade_type == 'sell':
                                self.balance_manager.unlock_balance('XRP', trade.amount)
                            else:
                                currency = 'USDT' if 'USDT' in trade.pair else 'USDC'
                                self.balance_manager.unlock_balance(currency, trade.total_value)
                    except:
                        trade.status = 'timeout'
            
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f"Error checking order timeouts: {e}")
            db.session.rollback()
