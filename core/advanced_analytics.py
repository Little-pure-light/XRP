import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
from app import db
from models import Trade, PriceHistory, ArbitrageOpportunity, DailyVolume

class AdvancedAnalytics:
    """🧠 高级交易分析引擎 - AI驱动的性能优化"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 数据缓存
        self.price_cache = deque(maxlen=1000)  # 最近1000个价格点
        self.spread_cache = deque(maxlen=500)   # 最近500个价差
        self.execution_cache = deque(maxlen=200) # 最近200次执行
        
        # 模型参数
        self.trend_window = 20      # 趋势分析窗口
        self.volatility_window = 50 # 波动率计算窗口
        self.correlation_window = 100 # 相关性分析窗口
        
        # 性能指标
        self.sharpe_ratio = 0.0
        self.max_drawdown = 0.0
        self.win_rate = 0.0
        self.profit_factor = 0.0
        
        # 预测模型参数
        self.alpha = 0.3  # 指数移动平均参数
        self.beta = 0.7   # 趋势权重
        self.gamma = 0.2  # 波动率权重
    
    def update_price_data(self, symbol: str, price: float, volume: float, timestamp: datetime = None):
        """更新价格数据到分析缓存"""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            price_point = {
                'symbol': symbol,
                'price': price,
                'volume': volume,
                'timestamp': timestamp
            }
            
            self.price_cache.append(price_point)
            
            # 实时计算指标
            self._update_real_time_metrics()
            
        except Exception as e:
            self.logger.error(f"更新价格数据失败: {e}")
    
    def update_spread_data(self, usdt_price: float, usdc_price: float, spread_pct: float):
        """更新价差数据"""
        try:
            spread_point = {
                'usdt_price': usdt_price,
                'usdc_price': usdc_price,
                'spread_percentage': spread_pct,
                'spread_abs': abs(usdt_price - usdc_price),
                'timestamp': datetime.utcnow()
            }
            
            self.spread_cache.append(spread_point)
            
            # 触发价差分析
            self._analyze_spread_patterns()
            
        except Exception as e:
            self.logger.error(f"更新价差数据失败: {e}")
    
    def update_execution_data(self, trade_result: dict):
        """更新交易执行数据"""
        try:
            execution_point = {
                'profit_loss': trade_result.get('profit_loss', 0),
                'execution_time': trade_result.get('execution_time', 0),
                'slippage': trade_result.get('slippage', {}),
                'amount': trade_result.get('amount', 0),
                'success': trade_result.get('profit_loss', 0) > 0,
                'timestamp': datetime.utcnow()
            }
            
            self.execution_cache.append(execution_point)
            
            # 更新性能指标
            self._update_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"更新执行数据失败: {e}")
    
    def _update_real_time_metrics(self):
        """更新实时市场指标"""
        try:
            if len(self.price_cache) < self.trend_window:
                return
            
            # 获取最近价格数据
            recent_prices = list(self.price_cache)[-self.trend_window:]
            
            # 按交易对分组
            usdt_prices = [p['price'] for p in recent_prices if 'USDT' in p['symbol']]
            usdc_prices = [p['price'] for p in recent_prices if 'USDC' in p['symbol']]
            
            if len(usdt_prices) >= 10 and len(usdc_prices) >= 10:
                # 计算趋势强度
                usdt_trend = self._calculate_trend_strength(usdt_prices)
                usdc_trend = self._calculate_trend_strength(usdc_prices)
                
                # 计算波动率
                usdt_volatility = self._calculate_volatility(usdt_prices)
                usdc_volatility = self._calculate_volatility(usdc_prices)
                
                # 更新缓存的指标
                self.current_metrics = {
                    'usdt_trend': usdt_trend,
                    'usdc_trend': usdc_trend,
                    'usdt_volatility': usdt_volatility,
                    'usdc_volatility': usdc_volatility,
                    'trend_divergence': abs(usdt_trend - usdc_trend),
                    'volatility_ratio': usdt_volatility / usdc_volatility if usdc_volatility != 0 else 1,
                    'updated_at': datetime.utcnow()
                }
                
        except Exception as e:
            self.logger.error(f"更新实时指标失败: {e}")
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """计算趋势强度 (-1到1，-1强烈下跌，1强烈上涨)"""
        try:
            if len(prices) < 5:
                return 0.0
            
            # 使用线性回归计算趋势
            x = np.arange(len(prices))
            y = np.array(prices)
            
            # 计算斜率
            slope = np.polyfit(x, y, 1)[0]
            
            # 归一化到[-1, 1]范围
            price_range = max(prices) - min(prices)
            if price_range == 0:
                return 0.0
            
            normalized_slope = slope / (price_range / len(prices))
            
            # 限制在[-1, 1]范围内
            return max(-1.0, min(1.0, normalized_slope))
            
        except Exception as e:
            self.logger.error(f"计算趋势强度失败: {e}")
            return 0.0
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """计算价格波动率"""
        try:
            if len(prices) < 2:
                return 0.0
            
            # 计算价格变化率
            returns = []
            for i in range(1, len(prices)):
                return_pct = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(return_pct)
            
            # 计算标准差作为波动率
            volatility = np.std(returns) if returns else 0.0
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"计算波动率失败: {e}")
            return 0.0
    
    def _analyze_spread_patterns(self):
        """分析价差模式"""
        try:
            if len(self.spread_cache) < 20:
                return
            
            recent_spreads = list(self.spread_cache)[-20:]
            spread_values = [s['spread_percentage'] for s in recent_spreads]
            
            # 价差统计
            mean_spread = np.mean(spread_values)
            std_spread = np.std(spread_values)
            max_spread = max(spread_values)
            min_spread = min(spread_values)
            
            # 价差趋势
            spread_trend = self._calculate_trend_strength(spread_values)
            
            # 价差突破检测
            recent_spread = spread_values[-1]
            z_score = (recent_spread - mean_spread) / std_spread if std_spread != 0 else 0
            
            self.spread_analysis = {
                'mean_spread': mean_spread,
                'std_spread': std_spread,
                'max_spread': max_spread,
                'min_spread': min_spread,
                'current_spread': recent_spread,
                'spread_trend': spread_trend,
                'z_score': z_score,
                'is_outlier': abs(z_score) > 2.0,  # 2个标准差外认为是异常值
                'recommendation': self._get_spread_recommendation(z_score, spread_trend),
                'updated_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"分析价差模式失败: {e}")
    
    def _get_spread_recommendation(self, z_score: float, trend: float) -> str:
        """基于价差分析给出交易建议"""
        try:
            if abs(z_score) > 2.5:  # 极端价差
                if z_score > 0:
                    return "STRONG_BUY - 极大价差机会"
                else:
                    return "AVOID - 价差过小"
            
            elif abs(z_score) > 1.5:  # 较大价差
                if z_score > 0 and trend > 0:
                    return "BUY - 价差扩大趋势"
                elif z_score > 0 and trend < 0:
                    return "QUICK_BUY - 价差可能收窄"
                else:
                    return "WAIT - 价差不佳"
            
            else:  # 正常价差
                if trend > 0.3:
                    return "WAIT_EXPANSION - 等待价差扩大"
                else:
                    return "NORMAL - 正常市场条件"
                    
        except Exception as e:
            self.logger.error(f"生成价差建议失败: {e}")
            return "UNKNOWN"
    
    def _update_performance_metrics(self):
        """更新交易性能指标"""
        try:
            if len(self.execution_cache) < 10:
                return
            
            executions = list(self.execution_cache)
            
            # 基础统计
            profits = [e['profit_loss'] for e in executions]
            execution_times = [e['execution_time'] for e in executions]
            
            total_profit = sum(profits)
            winning_trades = [p for p in profits if p > 0]
            losing_trades = [p for p in profits if p < 0]
            
            # 胜率
            self.win_rate = len(winning_trades) / len(profits) * 100 if profits else 0
            
            # 盈利因子
            total_wins = sum(winning_trades) if winning_trades else 0
            total_losses = abs(sum(losing_trades)) if losing_trades else 1
            self.profit_factor = total_wins / total_losses if total_losses != 0 else 0
            
            # 夏普比率 (简化版)
            if len(profits) > 1:
                profit_std = np.std(profits)
                avg_profit = np.mean(profits)
                self.sharpe_ratio = avg_profit / profit_std if profit_std != 0 else 0
            
            # 最大回撤
            cumulative_profit = 0
            peak = 0
            max_dd = 0
            
            for profit in profits:
                cumulative_profit += profit
                if cumulative_profit > peak:
                    peak = cumulative_profit
                drawdown = peak - cumulative_profit
                if drawdown > max_dd:
                    max_dd = drawdown
            
            self.max_drawdown = max_dd
            
            # 平均执行时间
            self.avg_execution_time = np.mean(execution_times) if execution_times else 0
            
        except Exception as e:
            self.logger.error(f"更新性能指标失败: {e}")
    
    def predict_next_spread(self) -> Dict:
        """预测下一个价差机会"""
        try:
            if len(self.spread_cache) < 30:
                return {'prediction': 'insufficient_data', 'confidence': 0}
            
            recent_spreads = list(self.spread_cache)[-30:]
            spread_values = [s['spread_percentage'] for s in recent_spreads]
            
            # 使用指数移动平均预测
            ema_short = self._calculate_ema(spread_values[-10:], 0.4)
            ema_long = self._calculate_ema(spread_values, 0.2)
            
            # 趋势预测
            trend = self._calculate_trend_strength(spread_values[-15:])
            
            # 波动率调整
            volatility = self._calculate_volatility(spread_values[-20:])
            
            # 综合预测
            base_prediction = ema_short
            trend_adjustment = trend * 0.1 * base_prediction
            volatility_adjustment = volatility * 50  # 波动率转换为价差百分比
            
            predicted_spread = base_prediction + trend_adjustment + volatility_adjustment
            
            # 置信度计算
            recent_accuracy = self._calculate_prediction_accuracy()
            trend_consistency = 1 - abs(trend) * 0.2  # 趋势越强，置信度稍降
            volatility_penalty = max(0, 1 - volatility * 20)  # 高波动率降低置信度
            
            confidence = recent_accuracy * trend_consistency * volatility_penalty
            
            return {
                'predicted_spread': predicted_spread,
                'confidence': min(1.0, max(0.1, confidence)),
                'trend_direction': 'up' if trend > 0.1 else 'down' if trend < -0.1 else 'sideways',
                'volatility_level': 'high' if volatility > 0.02 else 'low',
                'recommendation': self._get_prediction_recommendation(predicted_spread, confidence),
                'time_horizon': '2-5分钟',
                'updated_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"预测价差失败: {e}")
            return {'prediction': 'error', 'confidence': 0}
    
    def _calculate_ema(self, values: List[float], alpha: float) -> float:
        """计算指数移动平均"""
        try:
            if not values:
                return 0.0
            
            ema = values[0]
            for value in values[1:]:
                ema = alpha * value + (1 - alpha) * ema
            
            return ema
            
        except Exception as e:
            self.logger.error(f"计算EMA失败: {e}")
            return 0.0
    
    def _calculate_prediction_accuracy(self) -> float:
        """计算预测准确率"""
        try:
            # 简化的准确率计算
            # 在实际应用中，需要存储预测历史并比较实际结果
            
            if len(self.execution_cache) < 5:
                return 0.7  # 默认70%
            
            recent_executions = list(self.execution_cache)[-10:]
            successful_trades = len([e for e in recent_executions if e['success']])
            
            return successful_trades / len(recent_executions)
            
        except Exception as e:
            self.logger.error(f"计算预测准确率失败: {e}")
            return 0.5
    
    def _get_prediction_recommendation(self, predicted_spread: float, confidence: float) -> str:
        """基于预测结果给出建议"""
        try:
            if confidence < 0.3:
                return "LOW_CONFIDENCE - 建议等待更好信号"
            
            if predicted_spread > 0.5:  # 大于0.5%
                if confidence > 0.7:
                    return "STRONG_OPPORTUNITY - 高置信度大价差"
                else:
                    return "MODERATE_OPPORTUNITY - 中等机会"
            
            elif predicted_spread > 0.2:  # 0.2%-0.5%
                if confidence > 0.8:
                    return "ACCEPTABLE_OPPORTUNITY - 可接受的机会"
                else:
                    return "MARGINAL_OPPORTUNITY - 边际机会"
            
            else:
                return "POOR_OPPORTUNITY - 价差预测不佳"
                
        except Exception as e:
            self.logger.error(f"生成预测建议失败: {e}")
            return "UNKNOWN"
    
    def get_comprehensive_analysis(self) -> Dict:
        """获取综合分析报告"""
        try:
            # 获取实时指标
            current_metrics = getattr(self, 'current_metrics', {})
            spread_analysis = getattr(self, 'spread_analysis', {})
            
            # 预测下一个机会
            prediction = self.predict_next_spread()
            
            # 市场状态评估
            market_state = self._assess_market_state(current_metrics, spread_analysis)
            
            # 交易建议
            trading_recommendation = self._generate_trading_recommendation(
                current_metrics, spread_analysis, prediction, market_state
            )
            
            return {
                'performance_metrics': {
                    'sharpe_ratio': round(self.sharpe_ratio, 3),
                    'max_drawdown': round(self.max_drawdown, 3),
                    'win_rate': round(self.win_rate, 1),
                    'profit_factor': round(self.profit_factor, 2),
                    'avg_execution_time': round(getattr(self, 'avg_execution_time', 0), 2)
                },
                'current_metrics': current_metrics,
                'spread_analysis': spread_analysis,
                'prediction': prediction,
                'market_state': market_state,
                'trading_recommendation': trading_recommendation,
                'system_health': {
                    'data_quality': len(self.price_cache) / 1000,  # 数据完整性
                    'analysis_freshness': self._get_analysis_freshness(),
                    'prediction_reliability': prediction.get('confidence', 0)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"生成综合分析失败: {e}")
            return {'error': str(e), 'generated_at': datetime.utcnow().isoformat()}
    
    def _assess_market_state(self, metrics: Dict, spread_analysis: Dict) -> Dict:
        """评估市场状态"""
        try:
            trend_divergence = metrics.get('trend_divergence', 0)
            volatility_ratio = metrics.get('volatility_ratio', 1)
            current_spread = spread_analysis.get('current_spread', 0)
            spread_trend = spread_analysis.get('spread_trend', 0)
            
            # 市场状态分类
            if trend_divergence > 0.5 and current_spread > 0.3:
                state = "DIVERGENT_HIGH_SPREAD"
                description = "市场分化，高价差环境"
                favorability = "excellent"
            elif trend_divergence < 0.2 and abs(volatility_ratio - 1) < 0.1:
                state = "CONVERGENT_STABLE"
                description = "市场收敛，稳定环境"
                favorability = "good"
            elif abs(spread_trend) > 0.3:
                state = "TRENDING_SPREAD"
                description = "价差趋势明显"
                favorability = "moderate"
            else:
                state = "NEUTRAL"
                description = "中性市场环境"
                favorability = "fair"
            
            return {
                'state': state,
                'description': description,
                'favorability': favorability,
                'key_factors': {
                    'trend_divergence': trend_divergence,
                    'volatility_ratio': volatility_ratio,
                    'spread_level': current_spread,
                    'spread_momentum': spread_trend
                }
            }
            
        except Exception as e:
            self.logger.error(f"评估市场状态失败: {e}")
            return {'state': 'UNKNOWN', 'description': '无法评估', 'favorability': 'unknown'}
    
    def _generate_trading_recommendation(self, metrics: Dict, spread_analysis: Dict, 
                                       prediction: Dict, market_state: Dict) -> Dict:
        """生成交易建议"""
        try:
            # 综合评分
            spread_score = min(100, (spread_analysis.get('current_spread', 0) * 100))
            confidence_score = prediction.get('confidence', 0) * 100
            market_score = {'excellent': 100, 'good': 80, 'moderate': 60, 'fair': 40}.get(
                market_state.get('favorability', 'fair'), 40
            )
            
            overall_score = (spread_score * 0.4 + confidence_score * 0.3 + market_score * 0.3)
            
            # 生成建议
            if overall_score >= 80:
                action = "EXECUTE_IMMEDIATELY"
                reasoning = "高价差 + 高置信度 + 优秀市场条件"
                position_size = "FULL"
            elif overall_score >= 60:
                action = "EXECUTE_CAUTIOUSLY"
                reasoning = "良好条件，建议执行"
                position_size = "REDUCED"
            elif overall_score >= 40:
                action = "MONITOR_CLOSELY"
                reasoning = "边际条件，密切观察"
                position_size = "MINIMAL"
            else:
                action = "WAIT"
                reasoning = "条件不佳，建议等待"
                position_size = "NONE"
            
            return {
                'action': action,
                'reasoning': reasoning,
                'position_size': position_size,
                'overall_score': round(overall_score, 1),
                'component_scores': {
                    'spread': round(spread_score, 1),
                    'confidence': round(confidence_score, 1),
                    'market': round(market_score, 1)
                },
                'risk_level': 'LOW' if overall_score >= 70 else 'MEDIUM' if overall_score >= 50 else 'HIGH',
                'expected_duration': '2-5分钟',
                'stop_loss_level': 0.05  # 5%止损
            }
            
        except Exception as e:
            self.logger.error(f"生成交易建议失败: {e}")
            return {'action': 'ERROR', 'reasoning': str(e)}
    
    def _get_analysis_freshness(self) -> float:
        """获取分析数据新鲜度"""
        try:
            if not self.price_cache:
                return 0.0
            
            latest_data = self.price_cache[-1]['timestamp']
            time_diff = (datetime.utcnow() - latest_data).total_seconds()
            
            # 30秒内为1.0，超过5分钟为0
            freshness = max(0.0, 1.0 - time_diff / 300)
            
            return freshness
            
        except Exception as e:
            self.logger.error(f"计算数据新鲜度失败: {e}")
            return 0.0