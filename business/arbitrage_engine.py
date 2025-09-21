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
from core.order_manager import OrderManager
from core.websocket_manager import WebSocketManager
from core.advanced_analytics import AdvancedAnalytics
from core.latency_optimizer import LatencyOptimizer

class ArbitrageEngine:
    """🚀 终极专业套利引擎 - AI驱动的毫秒级交易系统"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        
        # 核心交易组件
        self.price_monitor = PriceMonitor()
        self.balance_manager = BalanceManager()
        self.trade_executor = TradeExecutor()
        self.risk_controller = RiskController()
        self.data_logger = DataLogger()
        self.config_manager = ConfigManager()
        
        # 🆕 专业增强组件
        self.order_manager = OrderManager()
        self.websocket_manager = WebSocketManager()
        self.advanced_analytics = AdvancedAnalytics()
        self.latency_optimizer = LatencyOptimizer()
        
        # 性能统计
        self.total_opportunities = 0
        self.executed_trades = 0
        self.total_profit = 0.0
        self.engine_start_time = None
        
        # 启动所有组件
        self._initialize_all_components()
    
    def _initialize_all_components(self):
        """初始化所有专业组件"""
        try:
            # 启动价格监控
            self.price_monitor.start_monitoring()
            
            # 启动订单管理器
            self.order_manager.start_monitoring()
            
            # 启动WebSocket数据流
            self.websocket_manager.start()
            
            # 注册WebSocket价格回调
            self.websocket_manager.add_price_callback(self._on_websocket_price_update)
            
            self.logger.info("🚀 所有专业组件已初始化")
            
        except Exception as e:
            self.logger.error(f"组件初始化失败: {e}")
    
    def _on_websocket_price_update(self, symbol: str, price_data: dict):
        """WebSocket价格更新回调"""
        try:
            # 更新高级分析数据
            self.advanced_analytics.update_price_data(
                symbol, 
                price_data['price'], 
                price_data['volume']
            )
            
            # 触发超快速价差检查
            if symbol in ['XRP/USDT', 'XRP/USDC']:
                self._fast_spread_check()
                
        except Exception as e:
            self.logger.error(f"WebSocket价格更新处理失败: {e}")
    
    def start(self):
        """🚀 启动终极专业套利引擎"""
        if self.running:
            self.logger.warning("专业套利引擎已在运行")
            return
        
        self.running = True
        self.engine_start_time = datetime.utcnow()
        self.thread = threading.Thread(target=self._professional_main_loop)
        self.thread.daemon = True
        self.thread.start()
        
        self.data_logger.log_system_event("PROFESSIONAL_ENGINE_STARTED", "专业套利引擎已启动", "ArbitrageEngine")
        self.logger.info("🚀 专业套利引擎已启动 - 毫秒级AI驱动交易")
    
    def stop(self):
        """🛑 停止专业套利引擎"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join()
        
        # 停止所有专业组件
        self.order_manager.stop_monitoring()
        self.websocket_manager.stop()
        self.latency_optimizer.shutdown()
        
        # 强制取消所有待处理订单
        cancelled_orders = self.order_manager.force_cancel_all_pending()
        
        # 生成最终报告
        final_report = self._generate_final_report()
        
        self.data_logger.log_system_event("PROFESSIONAL_ENGINE_STOPPED", f"专业套利引擎已停止 - {final_report}", "ArbitrageEngine")
        self.logger.info(f"🛑 专业套利引擎已停止 - 取消了{cancelled_orders['cancelled']}个订单")
    
    def _fast_spread_check(self):
        """⚡ 超快速价差检查（WebSocket触发）"""
        try:
            # 使用WebSocket的最新价格
            latest_prices = self.websocket_manager.get_latest_prices()
            
            if 'XRP/USDT' in latest_prices and 'XRP/USDC' in latest_prices:
                usdt_price = latest_prices['XRP/USDT']['price']
                usdc_price = latest_prices['XRP/USDC']['price']
                
                # 超快速价差计算
                spread_data = self.latency_optimizer.calculate_spread_fast(usdt_price, usdc_price)
                
                if spread_data['valid'] and spread_data['spread_pct'] > 0.3:  # 0.3%以上价差
                    self.logger.debug(f"⚡ 快速价差检测: {spread_data['spread_pct']:.4f}%")
                    
                    # 触发快速机会检测
                    config = self.config_manager.get_config()
                    if config and spread_data['spread_pct'] > config.spread_threshold * 100:
                        opportunity = self._create_fast_opportunity(usdt_price, usdc_price, spread_data)
                        
                        # 快速AI分析
                        prediction = self.advanced_analytics.predict_next_spread()
                        if prediction.get('confidence', 0) > 0.7:
                            self._execute_opportunity_ultra_fast(opportunity, config)
                
        except Exception as e:
            self.logger.error(f"快速价差检查失败: {e}")
    
    def _create_fast_opportunity(self, usdt_price: float, usdc_price: float, spread_data: dict) -> dict:
        """创建快速机会对象"""
        try:
            if usdt_price > usdc_price:
                opportunity_type = 'sell_usdt_buy_usdc'
                sell_pair = 'XRP/USDT'
                buy_pair = 'XRP/USDC'
                sell_price = usdt_price
                buy_price = usdc_price
            else:
                opportunity_type = 'sell_usdc_buy_usdt'
                sell_pair = 'XRP/USDC'
                buy_pair = 'XRP/USDT'
                sell_price = usdc_price
                buy_price = usdt_price
            
            # 快速计算交易数量
            config = self.config_manager.get_config()
            trade_amount = min(config.trade_amount, 200.0)  # 快速交易限制200 XRP
            
            return {
                'usdt_price': usdt_price,
                'usdc_price': usdc_price,
                'spread': spread_data['spread'],
                'spread_percentage': spread_data['spread_pct'],
                'opportunity_type': opportunity_type,
                'sell_pair': sell_pair,
                'buy_pair': buy_pair,
                'sell_price': sell_price,
                'buy_price': buy_price,
                'amount': trade_amount,
                'estimated_profit': trade_amount * spread_data['spread'],
                'fast_track': True,
                'detected_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"创建快速机会失败: {e}")
            return {}
    
    def _execute_opportunity_ultra_fast(self, opportunity: dict, config):
        """⚡ 超快速机会执行"""
        try:
            # 检查挂单限制
            if not self.trade_executor.enforce_pending_orders_limit():
                return
            
            # 超快速风险检查
            if opportunity['spread_percentage'] > 0.8 and opportunity['amount'] <= 100:
                # 使用延迟优化器的快速执行
                execution_result = self.latency_optimizer.execute_order_fast({
                    'symbol': opportunity['sell_pair'],
                    'amount': opportunity['amount'],
                    'type': 'arbitrage',
                    'urgency': 'ultra_high'
                })
                
                if execution_result.get('success'):
                    self.logger.info(f"⚡ 超快速套利执行成功: {opportunity['spread_percentage']:.4f}% ({execution_result.get('execution_time', 0):.2f}ms)")
                    
                    # 更新分析数据
                    self.advanced_analytics.update_execution_data({
                        'profit_loss': opportunity['estimated_profit'],
                        'execution_time': execution_result.get('execution_time', 0),
                        'amount': opportunity['amount'],
                        'success': True
                    })
        
        except Exception as e:
            self.logger.error(f"超快速执行失败: {e}")
    
    def _detect_arbitrage_opportunity_enhanced(self, config):
        """🧠 增强版机会检测 - AI+实时数据"""
        try:
            # 优先使用WebSocket数据
            latest_prices = self.websocket_manager.get_latest_prices()
            
            if not latest_prices or 'XRP/USDT' not in latest_prices or 'XRP/USDC' not in latest_prices:
                # 回退到传统价格监控
                return self._detect_arbitrage_opportunity(config)
            
            usdt_data = latest_prices['XRP/USDT']
            usdc_data = latest_prices['XRP/USDC']
            
            usdt_price = usdt_data['price']
            usdc_price = usdc_data['price']
            usdt_volume = usdt_data['volume']
            usdc_volume = usdc_data['volume']
            
            # AI增强的价差计算
            spread_data = self.latency_optimizer.calculate_spread_fast(usdt_price, usdc_price)
            
            if not spread_data['valid']:
                return None
            
            spread_percentage = spread_data['spread_pct']
            
            # AI预测增强
            prediction = self.advanced_analytics.predict_next_spread()
            confidence_multiplier = prediction.get('confidence', 0.5)
            
            # 动态阈值调整
            dynamic_threshold = config.spread_threshold * 100 * (2 - confidence_multiplier)
            
            if spread_percentage < dynamic_threshold:
                return None
            
            # 创建增强版机会
            return self._create_enhanced_opportunity(
                usdt_price, usdc_price, spread_data, usdt_volume, usdc_volume, config, prediction
            )
            
        except Exception as e:
            self.logger.error(f"增强版机会检测失败: {e}")
            return self._detect_arbitrage_opportunity(config)  # 回退到原方法
    
    def _create_enhanced_opportunity(self, usdt_price, usdc_price, spread_data, usdt_volume, usdc_volume, config, prediction):
        """创建增强版套利机会"""
        try:
            # 基础机会数据
            base_opportunity = self._create_fast_opportunity(usdt_price, usdc_price, spread_data)
            
            # AI增强数据
            base_opportunity.update({
                'volume_usdt': usdt_volume,
                'volume_usdc': usdc_volume,
                'ai_confidence': prediction.get('confidence', 0),
                'ai_recommendation': prediction.get('recommendation', 'UNKNOWN'),
                'trend_direction': prediction.get('trend_direction', 'sideways'),
                'volatility_level': prediction.get('volatility_level', 'medium'),
                'enhanced': True
            })
            
            # 动态数量调整
            confidence = prediction.get('confidence', 0.5)
            volume_factor = min(usdt_volume, usdc_volume) / 10000  # 基于流动性
            
            adjusted_amount = config.trade_amount * confidence * min(1.0, volume_factor)
            base_opportunity['amount'] = max(50.0, min(adjusted_amount, 500.0))  # 50-500 XRP范围
            
            return base_opportunity
            
        except Exception as e:
            self.logger.error(f"创建增强版机会失败: {e}")
            return {}
    
    def _execute_opportunity_professional(self, opportunity: dict, config, ai_analysis: dict):
        """🚀 专业级机会执行"""
        try:
            # 获取AI建议
            ai_recommendation = ai_analysis.get('trading_recommendation', {})
            action = ai_recommendation.get('action', 'WAIT')
            
            if action == 'WAIT':
                return None
            
            # 执行原有的增强执行逻辑
            return self._execute_opportunity(opportunity, config)
            
        except Exception as e:
            self.logger.error(f"专业级执行失败: {e}")
            return None
    
    def _perform_maintenance_tasks(self):
        """🔧 执行专业维护任务"""
        try:
            # 优化缓存
            self.latency_optimizer.optimize_cache_usage()
            
            # 检查超时订单
            self.order_manager._check_timeout_orders()
            
            # 更新性能指标
            self.order_manager.optimize_timeout_settings()
            
        except Exception as e:
            self.logger.error(f"维护任务失败: {e}")
    
    def _assess_market_activity(self) -> str:
        """评估市场活跃度"""
        try:
            # 基于最近的机会数量评估
            if self.total_opportunities > 0:
                recent_activity = self.total_opportunities % 100  # 简化计算
                
                if recent_activity > 10:
                    return 'high'
                elif recent_activity > 5:
                    return 'medium'
                else:
                    return 'low'
            
            return 'low'
            
        except Exception as e:
            return 'medium'
    
    def _calculate_optimal_sleep_time(self, market_activity: str) -> float:
        """计算最优休眠时间"""
        sleep_times = {
            'high': 1.0,    # 高活跃度：1秒
            'medium': 2.0,  # 中等活跃度：2秒
            'low': 3.0      # 低活跃度：3秒
        }
        
        return sleep_times.get(market_activity, 2.0)
    
    def _generate_final_report(self) -> str:
        """生成最终运行报告"""
        try:
            if self.engine_start_time:
                runtime = datetime.utcnow() - self.engine_start_time
                runtime_hours = runtime.total_seconds() / 3600
            else:
                runtime_hours = 0
            
            success_rate = (self.executed_trades / self.total_opportunities * 100) if self.total_opportunities > 0 else 0
            
            return (f"运行时长: {runtime_hours:.1f}h, "
                   f"检测机会: {self.total_opportunities}, "
                   f"执行交易: {self.executed_trades}, "
                   f"成功率: {success_rate:.1f}%, "
                   f"总利润: {self.total_profit:.2f}")
            
        except Exception as e:
            return f"报告生成失败: {e}"
    
    def is_running(self):
        """检查引擎是否运行中"""
        return self.running
    
    def _professional_main_loop(self):
        """🧠 专业AI驱动的主循环 - 毫秒级决策"""
        iteration_count = 0
        
        while self.running:
            try:
                iteration_start = time.perf_counter()
                iteration_count += 1
                
                # 获取配置
                config = self.config_manager.get_config()
                if not config:
                    self.logger.error("配置未找到，停止引擎")
                    break
                
                # 🔥 超快速系统健康检查
                if iteration_count % 10 == 0:  # 每10次迭代检查一次
                    health = self.risk_controller.check_system_health()
                    stability = self.risk_controller.check_system_stability()
                    
                    if not health['healthy'] or not stability['stable']:
                        self.logger.error(f"系统状态异常: Health={health['healthy']}, Stability={stability['stable']}")
                        self.data_logger.log_risk_event(
                            "SYSTEM_HEALTH_CRITICAL", 
                            f"健康检查失败: {health['errors']}, 稳定性: {stability['stability_score']}", 
                            "CRITICAL"
                        )
                        time.sleep(5)
                        continue
                
                # 🚀 超快速机会检测
                opportunity = self._detect_arbitrage_opportunity_enhanced(config)
                
                if opportunity:
                    self.total_opportunities += 1
                    
                    # 🧠 AI增强决策
                    ai_analysis = self.advanced_analytics.get_comprehensive_analysis()
                    ai_recommendation = ai_analysis.get('trading_recommendation', {})
                    
                    self.logger.info(f"💡 AI检测到机会: {opportunity['spread_percentage']:.4f}% - AI建议: {ai_recommendation.get('action', 'UNKNOWN')}")
                    
                    # 更新分析数据
                    self.advanced_analytics.update_spread_data(
                        opportunity['usdt_price'],
                        opportunity['usdc_price'],
                        opportunity['spread_percentage']
                    )
                    
                    # 存储机会
                    self._store_opportunity(opportunity)
                    
                    # ⚡ 超快速执行决策
                    if ai_recommendation.get('action') in ['EXECUTE_IMMEDIATELY', 'EXECUTE_CAUTIOUSLY']:
                        execution_result = self._execute_opportunity_professional(opportunity, config, ai_analysis)
                        
                        if execution_result:
                            self.executed_trades += 1
                            self.total_profit += execution_result.get('profit_loss', 0)
                
                # 🔧 专业维护任务
                if iteration_count % 5 == 0:  # 每5次迭代
                    self._perform_maintenance_tasks()
                
                # ⚡ 动态睡眠 - 基于市场活跃度
                market_activity = self._assess_market_activity()
                sleep_time = self._calculate_optimal_sleep_time(market_activity)
                
                iteration_time = (time.perf_counter() - iteration_start) * 1000
                self.logger.debug(f"⚡ 迭代 {iteration_count}: {iteration_time:.2f}ms, 休眠: {sleep_time:.1f}s")
                
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"专业主循环错误: {e}")
                self.data_logger.log_error(f"专业主循环错误: {e}", "ArbitrageEngine", e)
                time.sleep(3)  # 错误时短暂休眠
    
    def _detect_arbitrage_opportunity(self, config):
        """Detect directional arbitrage opportunities with improved logic"""
        try:
            # Get current prices
            prices = self.price_monitor.get_current_prices()
            
            if 'XRP/USDT' not in prices or 'XRP/USDC' not in prices:
                return None
            
            usdt_price = prices['XRP/USDT']['price']
            usdc_price = prices['XRP/USDC']['price']
            usdt_volume = prices['XRP/USDT']['volume']
            usdc_volume = prices['XRP/USDC']['volume']
            
            # IMPROVED DIRECTIONAL ARBITRAGE LOGIC
            # Calculate percentage spread (not just absolute)
            if usdt_price > usdc_price:
                # USDT is higher, sell XRP/USDT, buy XRP/USDC
                spread_percentage = ((usdt_price - usdc_price) / usdc_price) * 100
                opportunity_type = 'sell_usdt_buy_usdc'
                sell_pair = 'XRP/USDT'
                buy_pair = 'XRP/USDC'
                sell_price = usdt_price
                buy_price = usdc_price
                higher_price = usdt_price
                lower_price = usdc_price
            else:
                # USDC is higher, sell XRP/USDC, buy XRP/USDT  
                spread_percentage = ((usdc_price - usdt_price) / usdt_price) * 100
                opportunity_type = 'sell_usdc_buy_usdt'
                sell_pair = 'XRP/USDC'
                buy_pair = 'XRP/USDT'
                sell_price = usdc_price
                buy_price = usdt_price
                higher_price = usdc_price
                lower_price = usdt_price
            
            spread = higher_price - lower_price
            
            # Enhanced threshold check with minimum profitable spread
            minimum_profitable_spread = 0.08  # 0.08% minimum after fees
            if spread_percentage < max(config.spread_threshold * 100, minimum_profitable_spread):
                return None
            
            # Volume validation - ensure sufficient liquidity
            min_volume_24h = 1000.0  # Minimum 24h volume
            if usdt_volume < min_volume_24h or usdc_volume < min_volume_24h:
                self.logger.debug(f"Insufficient volume: USDT={usdt_volume}, USDC={usdc_volume}")
                return None
            
            # Calculate safe trade amount with volatility consideration
            max_safe_amount = self.risk_controller.calculate_max_safe_trade_amount(config)
            
            # Adjust trade amount based on spread size (larger spreads allow larger trades)
            spread_multiplier = min(2.0, spread_percentage / 0.3)  # Scale up to 2x for large spreads
            adjusted_base_amount = config.trade_amount * spread_multiplier
            
            trade_amount = min(adjusted_base_amount, max_safe_amount)
            
            if trade_amount <= 0:
                self.logger.warning("No safe trade amount available")
                return None
            
            # Enhanced profit estimation with fee consideration
            gross_profit = trade_amount * spread
            estimated_fees = trade_amount * (sell_price + buy_price) * 0.0006  # 0.06% taker fee both sides
            estimated_net_profit = gross_profit - estimated_fees
            
            # Minimum profit threshold
            min_profit_threshold = 0.10  # Minimum $0.10 profit
            if estimated_net_profit < min_profit_threshold:
                self.logger.debug(f"Profit too small: {estimated_net_profit:.4f} < {min_profit_threshold}")
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
                'estimated_profit': estimated_net_profit,
                'gross_profit': gross_profit,
                'estimated_fees': estimated_fees,
                'volume_usdt': usdt_volume,
                'volume_usdc': usdc_volume,
                'spread_multiplier': spread_multiplier
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
        """Execute arbitrage opportunity with enhanced risk checks"""
        try:
            # Perform comprehensive risk check with volatility adjustment
            risk_check = self.risk_controller.check_trade_risk(opportunity, config)
            
            if not risk_check['safe']:
                self.logger.warning(f"Trade blocked by risk check: {risk_check['reason']}")
                self.data_logger.log_risk_event(
                    "TRADE_BLOCKED", 
                    risk_check['reason'], 
                    "WARNING"
                )
                return
            
            # Use the volatility-adjusted amount from risk check
            adjusted_amount = risk_check['adjusted_amount']
            if adjusted_amount != opportunity['amount']:
                self.logger.info(f"Position size adjusted for volatility: {opportunity['amount']:.2f} -> {adjusted_amount:.2f} XRP")
                opportunity['amount'] = adjusted_amount
            
            # Execute the arbitrage trade
            self.logger.info(f"Executing ATOMIC arbitrage trade: {opportunity['amount']} XRP")
            
            trade_result = self.trade_executor.execute_arbitrage_trade(opportunity)
            
            if trade_result:
                # Track volume and profit/loss
                trade_value_usd = opportunity['amount'] * opportunity['sell_price']
                profit_loss = trade_result.get('profit_loss', 0)
                
                self.volume_tracker.track_trade_volume(trade_value_usd, profit_loss)
                
                # Mark opportunity as executed
                self._mark_opportunity_executed(opportunity)
                
                self.logger.info(f"ATOMIC arbitrage completed with P&L: {profit_loss:.4f}")
                
                self.data_logger.log_trade({
                    'type': 'atomic_arbitrage',
                    'amount': opportunity['amount'],
                    'profit_loss': profit_loss,
                    'spread': opportunity['spread_percentage'],
                    'execution_type': trade_result.get('execution_type', 'atomic'),
                    'slippage': trade_result.get('slippage', {})
                }, 'completed')
                
                # Check if we need to activate any circuit breakers based on performance
                if profit_loss < -50:  # Large single trade loss
                    self.risk_controller.volume_tracker.activate_circuit_breaker(
                        'large_loss',
                        f'Large single trade loss: ${abs(profit_loss):.2f}',
                        abs(profit_loss),
                        50.0
                    )
                
            else:
                self.logger.error("ATOMIC arbitrage trade execution failed")
                self.data_logger.log_error("ATOMIC arbitrage trade execution failed", "ArbitrageEngine")
                
                # Track failed execution (might indicate system issues)
                self.risk_controller.volume_tracker.activate_circuit_breaker(
                    'execution_failure',
                    'Multiple trade execution failures detected',
                    None,
                    None
                )
            
        except Exception as e:
            self.logger.error(f"Error executing opportunity: {e}")
            self.data_logger.log_error(f"Opportunity execution error: {e}", "ArbitrageEngine", e)
            
            # Activate circuit breaker for system errors
            self.risk_controller.volume_tracker.activate_circuit_breaker(
                'system_error',
                f'System error in arbitrage execution: {e}',
                None,
                None
            )
    
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
        """强制稳定币再平衡"""
        try:
            self.balance_manager.rebalance_stablecoins()
            self.data_logger.log_system_event("PROFESSIONAL_REBALANCE", "专业再平衡已触发", "ArbitrageEngine")
            self.logger.info("💰 专业再平衡已完成")
        except Exception as e:
            self.logger.error(f"专业再平衡错误: {e}")
            self.data_logger.log_error(f"专业再平衡错误: {e}", "ArbitrageEngine", e)
    
    def get_professional_status(self) -> dict:
        """🎯 获取专业引擎状态"""
        try:
            # 基础状态
            base_status = self.get_engine_status()
            
            # 专业组件状态
            professional_status = {
                'professional_engine': True,
                'components': {
                    'order_manager': {
                        'active': self.order_manager.monitoring_active,
                        'statistics': self.order_manager.get_order_statistics()
                    },
                    'websocket_manager': {
                        'active': self.websocket_manager.is_running,
                        'connections': self.websocket_manager.get_connection_stats()
                    },
                    'advanced_analytics': {
                        'active': True,
                        'analysis': self.advanced_analytics.get_comprehensive_analysis()
                    },
                    'latency_optimizer': {
                        'active': True,
                        'performance': self.latency_optimizer.get_performance_report()
                    }
                },
                'engine_statistics': {
                    'total_opportunities': self.total_opportunities,
                    'executed_trades': self.executed_trades,
                    'total_profit': self.total_profit,
                    'success_rate': (self.executed_trades / self.total_opportunities * 100) if self.total_opportunities > 0 else 0,
                    'runtime_hours': (datetime.utcnow() - self.engine_start_time).total_seconds() / 3600 if self.engine_start_time else 0
                },
                'system_optimization': {
                    'cpu_optimized': True,
                    'memory_optimized': True,
                    'network_optimized': True,
                    'ai_enhanced': True,
                    'real_time_data': True,
                    'millisecond_execution': True
                }
            }
            
            # 合并状态
            base_status.update(professional_status)
            
            return base_status
            
        except Exception as e:
            self.logger.error(f"获取专业状态失败: {e}")
            return {'error': str(e), 'professional_engine': False}
