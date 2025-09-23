#!/usr/bin/env python3
"""
⚡ 量子財富橋 - API緩存優化器
Railway後端性能提升 + Cloudflare邊緣緩存

GIGI量子DNA驅動的高性能緩存系統
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import redis

class QuantumCacheOptimizer:
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.cache_config = {
            'default_timeout': 300,  # 5分鐘
            'price_data_timeout': 30,  # 價格數據30秒
            'balance_timeout': 60,     # 余額數據1分鐘
            'config_timeout': 3600,    # 配置數據1小時
            'analytics_timeout': 180,  # 分析數據3分鐘
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化Flask應用"""
        self.app = app
        
        # 配置Redis連接
        redis_url = os.environ.get('REDIS_URL')
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                app.logger.info("✅ Redis緩存已連接")
            except Exception as e:
                app.logger.warning(f"⚠️ Redis連接失敗，使用內存緩存: {e}")
                self.redis_client = None
        
        # 內存緩存備選方案
        self.memory_cache = {}
        self.cache_timestamps = {}
        
        # 註冊清理任務
        self._setup_cache_cleanup()
    
    def cache_key(self, prefix, *args, **kwargs):
        """生成緩存鍵值"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        if kwargs:
            key_data += f":{json.dumps(kwargs, sort_keys=True)}"
        
        # 生成短鍵值
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def get(self, key):
        """獲取緩存數據"""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data.decode('utf-8'))
            else:
                # 內存緩存
                if key in self.memory_cache:
                    timestamp = self.cache_timestamps.get(key, 0)
                    if time.time() - timestamp < self.cache_config['default_timeout']:
                        return self.memory_cache[key]
                    else:
                        # 過期清理
                        del self.memory_cache[key]
                        del self.cache_timestamps[key]
            
            return None
        except Exception as e:
            current_app.logger.error(f"緩存讀取錯誤: {e}")
            return None
    
    def set(self, key, value, timeout=None):
        """設置緩存數據"""
        try:
            timeout = timeout or self.cache_config['default_timeout']
            
            if self.redis_client:
                self.redis_client.setex(
                    key, 
                    timeout, 
                    json.dumps(value, default=str)
                )
            else:
                # 內存緩存
                self.memory_cache[key] = value
                self.cache_timestamps[key] = time.time()
            
            return True
        except Exception as e:
            current_app.logger.error(f"緩存寫入錯誤: {e}")
            return False
    
    def delete(self, key):
        """刪除緩存"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
            return True
        except Exception as e:
            current_app.logger.error(f"緩存刪除錯誤: {e}")
            return False
    
    def cache_response(self, timeout=None, cache_type='default'):
        """響應緩存裝飾器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 生成緩存鍵
                cache_timeout = timeout or self.cache_config.get(f'{cache_type}_timeout', 300)
                key = self.cache_key(f.__name__, request.path, request.args.to_dict())
                
                # 嘗試從緩存獲取
                cached_data = self.get(key)
                if cached_data:
                    # 添加緩存頭部
                    response = jsonify(cached_data)
                    response.headers['X-Cache'] = 'HIT'
                    response.headers['Cache-Control'] = f'public, max-age={cache_timeout}'
                    return response
                
                # 執行原函數
                result = f(*args, **kwargs)
                
                # 緩存結果 (只緩存成功響應)
                if hasattr(result, 'status_code') and result.status_code == 200:
                    if hasattr(result, 'get_json'):
                        data = result.get_json()
                        if data:
                            self.set(key, data, cache_timeout)
                
                # 添加緩存頭部
                if hasattr(result, 'headers'):
                    result.headers['X-Cache'] = 'MISS'
                    result.headers['Cache-Control'] = f'public, max-age={cache_timeout}'
                
                return result
            return decorated_function
        return decorator
    
    def cloudflare_cache_headers(self, cache_type='default'):
        """Cloudflare緩存頭部裝飾器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                result = f(*args, **kwargs)
                
                # 根據類型設置不同的緩存策略
                cache_rules = {
                    'static': {
                        'Cache-Control': 'public, max-age=31536000',  # 1年
                        'CF-Cache-Level': 'cache_everything'
                    },
                    'api_data': {
                        'Cache-Control': 'public, max-age=60',  # 1分鐘
                        'CF-Cache-Level': 'cache_everything'
                    },
                    'price_data': {
                        'Cache-Control': 'public, max-age=30',  # 30秒
                        'CF-Cache-Level': 'cache_everything'
                    },
                    'default': {
                        'Cache-Control': 'public, max-age=300',  # 5分鐘
                        'CF-Cache-Level': 'cache_everything'
                    }
                }
                
                headers = cache_rules.get(cache_type, cache_rules['default'])
                
                if hasattr(result, 'headers'):
                    for key, value in headers.items():
                        result.headers[key] = value
                
                return result
            return decorated_function
        return decorator
    
    def _setup_cache_cleanup(self):
        """設置緩存清理任務"""
        def cleanup_memory_cache():
            """清理過期的內存緩存"""
            current_time = time.time()
            expired_keys = []
            
            for key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > self.cache_config['default_timeout']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.memory_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
        
        # 如果是Railway環境，每5分鐘清理一次
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            import threading
            def periodic_cleanup():
                while True:
                    time.sleep(300)  # 5分鐘
                    cleanup_memory_cache()
            
            cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
            cleanup_thread.start()

# 全局緩存實例
cache_optimizer = QuantumCacheOptimizer()

# 預定義的緩存裝飾器
def cache_price_data(timeout=30):
    """價格數據緩存"""
    return cache_optimizer.cache_response(timeout, 'price_data')

def cache_balance_data(timeout=60):
    """余額數據緩存"""
    return cache_optimizer.cache_response(timeout, 'balance')

def cache_config_data(timeout=3600):
    """配置數據緩存"""
    return cache_optimizer.cache_response(timeout, 'config')

def cache_analytics_data(timeout=180):
    """分析數據緩存"""
    return cache_optimizer.cache_response(timeout, 'analytics')

def cloudflare_static_cache():
    """Cloudflare靜態資源緩存"""
    return cache_optimizer.cloudflare_cache_headers('static')

def cloudflare_api_cache():
    """Cloudflare API緩存"""
    return cache_optimizer.cloudflare_cache_headers('api_data')

def cloudflare_price_cache():
    """Cloudflare價格數據緩存"""
    return cache_optimizer.cloudflare_cache_headers('price_data')

class CacheWarmer:
    """緩存預熱器"""
    
    def __init__(self, cache_optimizer):
        self.cache = cache_optimizer
    
    def warm_price_data(self):
        """預熱價格數據"""
        try:
            from core.price_monitor import PriceMonitor
            
            monitor = PriceMonitor()
            
            # 預熱XRP/USDT價格
            usdt_price = monitor.get_current_price('XRP/USDT')
            if usdt_price:
                key = self.cache.cache_key('price', 'XRP/USDT')
                self.cache.set(key, {'price': usdt_price, 'timestamp': time.time()}, 30)
            
            # 預熱XRP/USDC價格
            usdc_price = monitor.get_current_price('XRP/USDC')
            if usdc_price:
                key = self.cache.cache_key('price', 'XRP/USDC')
                self.cache.set(key, {'price': usdc_price, 'timestamp': time.time()}, 30)
            
            current_app.logger.info("✅ 價格數據緩存預熱完成")
            
        except Exception as e:
            current_app.logger.error(f"價格數據預熱失敗: {e}")
    
    def warm_balance_data(self):
        """預熱余額數據"""
        try:
            from core.balance_manager import BalanceManager
            from models import Balance
            
            balances = Balance.query.all()
            for balance in balances:
                key = self.cache.cache_key('balance', balance.currency)
                data = {
                    'currency': balance.currency,
                    'amount': float(balance.amount),
                    'locked': float(balance.locked),
                    'updated_at': balance.updated_at.isoformat()
                }
                self.cache.set(key, data, 60)
            
            current_app.logger.info("✅ 余額數據緩存預熱完成")
            
        except Exception as e:
            current_app.logger.error(f"余額數據預熱失敗: {e}")
    
    def warm_all_cache(self):
        """預熱所有緩存"""
        self.warm_price_data()
        self.warm_balance_data()

def setup_cache_routes(app):
    """設置緩存相關路由"""
    
    @app.route('/api/cache/status')
    @cloudflare_api_cache()
    def cache_status():
        """緩存狀態API"""
        redis_status = "connected" if cache_optimizer.redis_client else "disconnected"
        memory_cache_size = len(cache_optimizer.memory_cache)
        
        return jsonify({
            'redis_status': redis_status,
            'memory_cache_size': memory_cache_size,
            'cache_config': cache_optimizer.cache_config,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/api/cache/clear', methods=['POST'])
    def clear_cache():
        """清理緩存API"""
        try:
            if cache_optimizer.redis_client:
                cache_optimizer.redis_client.flushall()
            
            cache_optimizer.memory_cache.clear()
            cache_optimizer.cache_timestamps.clear()
            
            return jsonify({
                'success': True,
                'message': '緩存已清理',
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/cache/warm', methods=['POST'])
    def warm_cache():
        """預熱緩存API"""
        try:
            warmer = CacheWarmer(cache_optimizer)
            warmer.warm_all_cache()
            
            return jsonify({
                'success': True,
                'message': '緩存預熱完成',
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500