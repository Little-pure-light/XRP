import json
import asyncio
import websockets
import threading
import logging
from datetime import datetime
from typing import Dict, Callable, Optional
from urllib.parse import urljoin

class WebSocketManager:
    """专业WebSocket管理器 - 实时价格数据流"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # WebSocket连接配置
        self.mexc_ws_url = 'wss://wbs.mexc.com/ws'
        self.connections = {}
        self.subscriptions = {}
        
        # 数据处理
        self.price_callbacks = []
        self.order_callbacks = []
        self.event_callbacks = []
        
        # 连接状态
        self.is_running = False
        self.reconnect_attempts = {}
        self.max_reconnect_attempts = 10
        
        # 数据缓存
        self.latest_prices = {}
        self.price_history_buffer = {}
        self.connection_stats = {
            'connected_since': None,
            'messages_received': 0,
            'reconnect_count': 0,
            'last_ping': None
        }
        
        # 事件循环
        self.loop = None
        self.websocket_thread = None
    
    def start(self):
        """启动WebSocket连接"""
        try:
            if self.is_running:
                self.logger.warning("WebSocket管理器已在运行")
                return
            
            self.is_running = True
            
            # 在新线程中启动异步事件循环
            self.websocket_thread = threading.Thread(target=self._run_websocket_loop, daemon=True)
            self.websocket_thread.start()
            
            self.logger.info("🌐 专业WebSocket数据流已启动")
            
        except Exception as e:
            self.logger.error(f"启动WebSocket失败: {e}")
            self.is_running = False
    
    def stop(self):
        """停止WebSocket连接"""
        try:
            self.is_running = False
            
            # 关闭所有连接
            if self.loop:
                asyncio.run_coroutine_threadsafe(self._close_all_connections(), self.loop)
            
            if self.websocket_thread and self.websocket_thread.is_alive():
                self.websocket_thread.join(timeout=5)
            
            self.logger.info("🛑 WebSocket数据流已停止")
            
        except Exception as e:
            self.logger.error(f"停止WebSocket失败: {e}")
    
    def _run_websocket_loop(self):
        """运行WebSocket事件循环"""
        try:
            # 创建新的事件循环
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # 启动主要的WebSocket任务
            self.loop.run_until_complete(self._websocket_main())
            
        except Exception as e:
            self.logger.error(f"WebSocket事件循环错误: {e}")
        finally:
            if self.loop:
                self.loop.close()
    
    async def _websocket_main(self):
        """WebSocket主循环"""
        try:
            # 订阅XRP价格数据
            await self.subscribe_to_price_data(['XRPUSDT', 'XRPUSDC'])
            
            # 保持连接活跃
            while self.is_running:
                await asyncio.sleep(1)
                
                # 检查连接健康状态
                await self._check_connection_health()
                
        except Exception as e:
            self.logger.error(f"WebSocket主循环错误: {e}")
    
    async def subscribe_to_price_data(self, symbols: list):
        """订阅价格数据流"""
        try:
            for symbol in symbols:
                await self._create_price_stream(symbol)
                
        except Exception as e:
            self.logger.error(f"订阅价格数据失败: {e}")
    
    async def _create_price_stream(self, symbol: str):
        """创建单个价格数据流"""
        try:
            # 构建订阅消息
            subscribe_msg = {
                "method": "SUBSCRIPTION",
                "params": [f"spot@public.miniTicker.v3.api@{symbol}"],
                "id": f"price_{symbol}"
            }
            
            # 创建WebSocket连接
            uri = self.mexc_ws_url
            
            async def price_stream_handler():
                reconnect_count = 0
                
                while self.is_running and reconnect_count < self.max_reconnect_attempts:
                    try:
                        self.logger.info(f"📡 连接价格数据流: {symbol}")
                        
                        async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as websocket:
                            # 存储连接
                            self.connections[symbol] = websocket
                            self.connection_stats['connected_since'] = datetime.utcnow()
                            
                            # 发送订阅消息
                            await websocket.send(json.dumps(subscribe_msg))
                            
                            # 重置重连计数
                            reconnect_count = 0
                            self.reconnect_attempts[symbol] = 0
                            
                            # 监听消息
                            async for message in websocket:
                                if not self.is_running:
                                    break
                                
                                await self._handle_price_message(symbol, message)
                                
                    except websockets.exceptions.ConnectionClosed:
                        reconnect_count += 1
                        self.connection_stats['reconnect_count'] += 1
                        self.logger.warning(f"⚠️ {symbol} 连接断开，重连中... ({reconnect_count}/{self.max_reconnect_attempts})")
                        await asyncio.sleep(min(reconnect_count * 2, 30))  # 指数退避
                        
                    except Exception as e:
                        reconnect_count += 1
                        self.logger.error(f"❌ {symbol} 连接错误: {e}")
                        await asyncio.sleep(5)
                
                # 清理连接
                if symbol in self.connections:
                    del self.connections[symbol]
                
                self.logger.error(f"🚨 {symbol} 达到最大重连次数，停止连接")
            
            # 启动价格流处理器
            asyncio.create_task(price_stream_handler())
            
        except Exception as e:
            self.logger.error(f"创建价格数据流失败 {symbol}: {e}")
    
    async def _handle_price_message(self, symbol: str, message: str):
        """处理价格消息"""
        try:
            data = json.loads(message)
            
            # 更新统计
            self.connection_stats['messages_received'] += 1
            self.connection_stats['last_ping'] = datetime.utcnow()
            
            # 处理不同类型的消息
            if 'c' in data and 'v' in data:  # 价格和成交量数据
                price_data = {
                    'symbol': symbol,
                    'price': float(data['c']),  # 最新价格
                    'volume': float(data['v']),  # 24小时成交量
                    'high': float(data.get('h', 0)),  # 24小时最高价
                    'low': float(data.get('l', 0)),   # 24小时最低价
                    'change': float(data.get('P', 0)),  # 24小时涨跌幅
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # 更新缓存
                pair_name = f"{symbol[:3]}/{symbol[3:]}"  # XRP/USDT格式
                self.latest_prices[pair_name] = price_data
                
                # 添加到历史缓冲区
                if pair_name not in self.price_history_buffer:
                    self.price_history_buffer[pair_name] = []
                
                self.price_history_buffer[pair_name].append(price_data)
                
                # 保持最近100个价格点
                if len(self.price_history_buffer[pair_name]) > 100:
                    self.price_history_buffer[pair_name] = self.price_history_buffer[pair_name][-100:]
                
                # 调用回调函数
                await self._call_price_callbacks(pair_name, price_data)
                
                self.logger.debug(f"💹 {pair_name}: {price_data['price']:.4f}")
                
        except json.JSONDecodeError:
            self.logger.warning(f"⚠️ 无效JSON消息: {message}")
        except Exception as e:
            self.logger.error(f"处理价格消息失败: {e}")
    
    async def _call_price_callbacks(self, symbol: str, price_data: dict):
        """调用价格更新回调"""
        try:
            for callback in self.price_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(symbol, price_data)
                    else:
                        callback(symbol, price_data)
                except Exception as e:
                    self.logger.error(f"价格回调错误: {e}")
                    
        except Exception as e:
            self.logger.error(f"调用价格回调失败: {e}")
    
    async def _check_connection_health(self):
        """检查连接健康状态"""
        try:
            current_time = datetime.utcnow()
            
            # 检查是否有消息接收
            if (self.connection_stats['last_ping'] and 
                (current_time - self.connection_stats['last_ping']).total_seconds() > 60):
                self.logger.warning("⚠️ 60秒未收到价格数据，可能存在连接问题")
            
            # 发送心跳ping到活跃连接
            for symbol, websocket in self.connections.items():
                try:
                    await websocket.ping()
                except Exception as e:
                    self.logger.warning(f"⚠️ {symbol} ping失败: {e}")
                    
        except Exception as e:
            self.logger.error(f"检查连接健康失败: {e}")
    
    async def _close_all_connections(self):
        """关闭所有WebSocket连接"""
        try:
            for symbol, websocket in self.connections.items():
                try:
                    await websocket.close()
                    self.logger.info(f"🔌 已关闭 {symbol} 连接")
                except Exception as e:
                    self.logger.error(f"关闭连接失败 {symbol}: {e}")
            
            self.connections.clear()
            
        except Exception as e:
            self.logger.error(f"关闭所有连接失败: {e}")
    
    def add_price_callback(self, callback: Callable):
        """添加价格更新回调函数"""
        self.price_callbacks.append(callback)
        self.logger.info(f"📞 已添加价格回调函数")
    
    def remove_price_callback(self, callback: Callable):
        """移除价格更新回调函数"""
        if callback in self.price_callbacks:
            self.price_callbacks.remove(callback)
            self.logger.info(f"📞 已移除价格回调函数")
    
    def get_latest_prices(self) -> Dict:
        """获取最新价格数据"""
        return self.latest_prices.copy()
    
    def get_price_history(self, symbol: str, limit: int = 50) -> list:
        """获取价格历史数据"""
        if symbol in self.price_history_buffer:
            return self.price_history_buffer[symbol][-limit:]
        return []
    
    def get_connection_stats(self) -> Dict:
        """获取连接统计信息"""
        stats = self.connection_stats.copy()
        stats['active_connections'] = len(self.connections)
        stats['subscribed_symbols'] = list(self.connections.keys())
        stats['is_running'] = self.is_running
        
        # 计算连接时长
        if stats['connected_since']:
            uptime = (datetime.utcnow() - stats['connected_since']).total_seconds()
            stats['uptime_seconds'] = uptime
            stats['uptime_formatted'] = f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s"
        
        return stats
    
    def simulate_price_update(self, symbol: str, price: float, volume: float = 1000.0):
        """模拟价格更新（用于测试）"""
        try:
            price_data = {
                'symbol': symbol.replace('/', ''),
                'price': price,
                'volume': volume,
                'high': price * 1.02,
                'low': price * 0.98,
                'change': 0.5,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.latest_prices[symbol] = price_data
            
            # 添加到历史缓冲区
            if symbol not in self.price_history_buffer:
                self.price_history_buffer[symbol] = []
            
            self.price_history_buffer[symbol].append(price_data)
            
            # 保持最近100个价格点
            if len(self.price_history_buffer[symbol]) > 100:
                self.price_history_buffer[symbol] = self.price_history_buffer[symbol][-100:]
            
            # 同步调用回调（模拟模式）
            for callback in self.price_callbacks:
                try:
                    if not asyncio.iscoroutinefunction(callback):
                        callback(symbol, price_data)
                except Exception as e:
                    self.logger.error(f"模拟价格回调错误: {e}")
            
            self.logger.debug(f"🎯 模拟价格更新 {symbol}: {price:.4f}")
            
        except Exception as e:
            self.logger.error(f"模拟价格更新失败: {e}")