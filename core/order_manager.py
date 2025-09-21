import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app import db
from models import Trade, CircuitBreaker
from core.mexc_connector import MEXCConnector
from core.volume_tracker import VolumeTracker

class OrderManager:
    """专业订单管理系统 - 超时监控和自动取消"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mexc_connector = MEXCConnector()
        self.volume_tracker = VolumeTracker()
        
        # 订单监控配置
        self.monitoring_active = False
        self.monitor_thread = None
        self.timeout_configs = {
            'limit_order': 30,      # 限价单30秒超时
            'market_order': 10,     # 市价单10秒超时
            'arbitrage_order': 20,  # 套利单20秒超时
        }
        
        # 订单状态缓存
        self.order_cache = {}
        self.pending_orders = {}
        
        # 性能监控
        self.execution_times = []
        self.timeout_counts = {'limit': 0, 'market': 0, 'arbitrage': 0}
        
    def start_monitoring(self):
        """启动订单监控系统"""
        try:
            if self.monitoring_active:
                self.logger.warning("订单监控已在运行")
                return
            
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("📊 专业订单监控系统已启动")
            
        except Exception as e:
            self.logger.error(f"启动订单监控失败: {e}")
    
    def stop_monitoring(self):
        """停止订单监控系统"""
        try:
            self.monitoring_active = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            self.logger.info("🛑 订单监控系统已停止")
            
        except Exception as e:
            self.logger.error(f"停止订单监控失败: {e}")
    
    def _monitoring_loop(self):
        """监控循环 - 检查超时订单"""
        while self.monitoring_active:
            try:
                # 检查超时订单
                self._check_timeout_orders()
                
                # 更新订单状态
                self._update_pending_orders()
                
                # 清理过期缓存
                self._cleanup_cache()
                
                # 监控间隔
                time.sleep(2)  # 每2秒检查一次
                
            except Exception as e:
                self.logger.error(f"订单监控循环错误: {e}")
                time.sleep(5)  # 错误时延长间隔
    
    def _check_timeout_orders(self):
        """检查并处理超时订单"""
        try:
            current_time = datetime.utcnow()
            
            # 获取所有待处理订单
            pending_trades = Trade.query.filter_by(status='pending').all()
            
            for trade in pending_trades:
                if not trade.created_at:
                    continue
                
                # 计算订单年龄
                order_age = (current_time - trade.created_at).total_seconds()
                
                # 确定超时时间
                order_type = self._classify_order_type(trade)
                timeout_seconds = self.timeout_configs.get(order_type, 30)
                
                if order_age > timeout_seconds:
                    self._handle_timeout_order(trade, order_age, order_type)
                    
        except Exception as e:
            self.logger.error(f"检查超时订单错误: {e}")
    
    def _classify_order_type(self, trade):
        """分类订单类型"""
        # 根据订单特征分类
        if hasattr(trade, 'order_type'):
            return trade.order_type
        
        # 基于交易对和数量推断
        if trade.amount > 500:  # 大额订单
            return 'limit_order'
        elif 'arbitrage' in trade.pair.lower():
            return 'arbitrage_order'
        else:
            return 'market_order'
    
    def _handle_timeout_order(self, trade, order_age, order_type):
        """处理超时订单"""
        try:
            self.logger.warning(f"⏰ 订单超时: {trade.id} ({order_type}, {order_age:.1f}秒)")
            
            # 尝试获取最新状态
            if trade.order_id:
                try:
                    status = self.mexc_connector.get_order_status(trade.order_id, trade.pair)
                    
                    if status['status'] == 'closed':
                        # 订单已完成，更新状态
                        trade.status = 'completed'
                        trade.completed_at = datetime.utcnow()
                        self.logger.info(f"✅ 超时订单已完成: {trade.id}")
                        
                        # 更新余额
                        self._update_balances_for_completed_trade(trade)
                        
                    elif status['status'] in ['partial']:
                        # 部分成交，等待完成
                        self.logger.info(f"⏳ 订单部分成交: {trade.id}")
                        trade.updated_at = datetime.utcnow()
                        
                    else:
                        # 取消未完成的订单
                        success = self.mexc_connector.cancel_order(trade.order_id, trade.pair)
                        if success:
                            trade.status = 'timeout_cancelled'
                            self.logger.info(f"❌ 超时订单已取消: {trade.id}")
                        else:
                            trade.status = 'timeout_failed'
                            self.logger.error(f"🚨 超时订单取消失败: {trade.id}")
                        
                        # 解锁余额
                        self._unlock_trade_balances(trade)
                        
                except Exception as e:
                    self.logger.error(f"处理超时订单状态失败: {e}")
                    trade.status = 'timeout_error'
                    self._unlock_trade_balances(trade)
            
            # 更新统计
            self.timeout_counts[order_type] = self.timeout_counts.get(order_type, 0) + 1
            
            # 检查是否需要触发熔断
            if self.timeout_counts[order_type] > 5:  # 5次超时触发熔断
                self.volume_tracker.activate_circuit_breaker(
                    'order_timeout',
                    f'过多{order_type}订单超时: {self.timeout_counts[order_type]}次',
                    self.timeout_counts[order_type],
                    5
                )
            
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f"处理超时订单失败: {e}")
            db.session.rollback()
    
    def _update_pending_orders(self):
        """更新待处理订单状态"""
        try:
            pending_trades = Trade.query.filter_by(status='pending').limit(20).all()
            
            for trade in pending_trades:
                if trade.order_id and trade.id not in self.order_cache:
                    # 检查订单状态
                    status = self.mexc_connector.get_order_status(trade.order_id, trade.pair)
                    
                    if status['status'] == 'closed':
                        trade.status = 'completed'
                        trade.completed_at = datetime.utcnow()
                        self._update_balances_for_completed_trade(trade)
                        
                        # 记录执行时间
                        if trade.created_at:
                            execution_time = (datetime.utcnow() - trade.created_at).total_seconds()
                            self.execution_times.append(execution_time)
                            
                            # 保持最近100次执行时间
                            if len(self.execution_times) > 100:
                                self.execution_times = self.execution_times[-100:]
                    
                    # 缓存状态检查
                    self.order_cache[trade.id] = {
                        'last_check': datetime.utcnow(),
                        'status': status['status']
                    }
            
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f"更新订单状态失败: {e}")
            db.session.rollback()
    
    def _unlock_trade_balances(self, trade):
        """解锁交易相关的余额"""
        try:
            from core.balance_manager import BalanceManager
            balance_manager = BalanceManager()
            
            if trade.trade_type == 'sell':
                # 解锁XRP
                balance_manager.unlock_balance('XRP', trade.amount)
            else:
                # 解锁稳定币
                currency = 'USDT' if 'USDT' in trade.pair else 'USDC'
                balance_manager.unlock_balance(currency, trade.total_value)
                
        except Exception as e:
            self.logger.error(f"解锁余额失败: {e}")
    
    def _update_balances_for_completed_trade(self, trade):
        """更新已完成交易的余额"""
        try:
            from core.balance_manager import BalanceManager
            balance_manager = BalanceManager()
            
            if trade.trade_type == 'sell':
                # 卖单：减少XRP，增加稳定币
                balance_manager.unlock_balance('XRP', trade.amount)
                balance_manager.update_balance('XRP', -trade.amount)
                
                currency = 'USDT' if 'USDT' in trade.pair else 'USDC'
                balance_manager.update_balance(currency, trade.total_value)
                
            else:
                # 买单：减少稳定币，增加XRP
                currency = 'USDT' if 'USDT' in trade.pair else 'USDC'
                balance_manager.unlock_balance(currency, trade.total_value)
                balance_manager.update_balance(currency, -trade.total_value)
                balance_manager.update_balance('XRP', trade.amount)
                
        except Exception as e:
            self.logger.error(f"更新交易余额失败: {e}")
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        try:
            current_time = datetime.utcnow()
            expired_keys = []
            
            for order_id, cache_data in self.order_cache.items():
                if (current_time - cache_data['last_check']).total_seconds() > 300:  # 5分钟过期
                    expired_keys.append(order_id)
            
            for key in expired_keys:
                del self.order_cache[key]
                
        except Exception as e:
            self.logger.error(f"清理缓存失败: {e}")
    
    def get_order_statistics(self):
        """获取订单统计信息"""
        try:
            current_time = datetime.utcnow()
            today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # 今日订单统计
            today_trades = Trade.query.filter(
                Trade.created_at >= today_start
            ).all()
            
            stats = {
                'today_total': len(today_trades),
                'today_completed': len([t for t in today_trades if t.status == 'completed']),
                'today_timeout': len([t for t in today_trades if 'timeout' in t.status]),
                'today_pending': len([t for t in today_trades if t.status == 'pending']),
                'timeout_counts': self.timeout_counts.copy(),
                'avg_execution_time': sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0,
                'max_execution_time': max(self.execution_times) if self.execution_times else 0,
                'min_execution_time': min(self.execution_times) if self.execution_times else 0,
                'monitoring_active': self.monitoring_active,
                'cached_orders': len(self.order_cache)
            }
            
            # 成功率计算
            if stats['today_total'] > 0:
                stats['success_rate'] = (stats['today_completed'] / stats['today_total']) * 100
                stats['timeout_rate'] = (stats['today_timeout'] / stats['today_total']) * 100
            else:
                stats['success_rate'] = 0
                stats['timeout_rate'] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取订单统计失败: {e}")
            return {}
    
    def force_cancel_all_pending(self):
        """强制取消所有待处理订单"""
        try:
            pending_trades = Trade.query.filter_by(status='pending').all()
            cancelled_count = 0
            
            for trade in pending_trades:
                try:
                    if trade.order_id:
                        success = self.mexc_connector.cancel_order(trade.order_id, trade.pair)
                        if success:
                            trade.status = 'force_cancelled'
                            self._unlock_trade_balances(trade)
                            cancelled_count += 1
                        else:
                            trade.status = 'cancel_failed'
                    else:
                        trade.status = 'force_cancelled'
                        self._unlock_trade_balances(trade)
                        cancelled_count += 1
                        
                except Exception as e:
                    self.logger.error(f"强制取消订单失败 {trade.id}: {e}")
                    trade.status = 'cancel_error'
            
            db.session.commit()
            
            self.logger.info(f"🛑 强制取消了{cancelled_count}个待处理订单")
            return {'cancelled': cancelled_count, 'total': len(pending_trades)}
            
        except Exception as e:
            self.logger.error(f"强制取消所有订单失败: {e}")
            db.session.rollback()
            return {'cancelled': 0, 'total': 0}
    
    def optimize_timeout_settings(self):
        """基于历史数据优化超时设置"""
        try:
            if not self.execution_times:
                return
            
            # 计算99分位数作为新的超时时间
            sorted_times = sorted(self.execution_times)
            p95_time = sorted_times[int(len(sorted_times) * 0.95)]
            p99_time = sorted_times[int(len(sorted_times) * 0.99)]
            
            # 动态调整超时时间
            self.timeout_configs['market_order'] = max(10, int(p95_time * 1.5))
            self.timeout_configs['limit_order'] = max(15, int(p99_time * 1.2))
            self.timeout_configs['arbitrage_order'] = max(20, int(p99_time * 1.3))
            
            self.logger.info(f"📈 超时设置已优化: {self.timeout_configs}")
            
        except Exception as e:
            self.logger.error(f"优化超时设置失败: {e}")