#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 XRP套利交易系统 - 发财王子专用GUI控制中心
简单易用的图形界面，让您轻松操作交易系统
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import webbrowser
import time
import requests
import json
from datetime import datetime

class TradingControlCenter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 XRP套利交易系统 - 发财王子控制中心")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # 设置窗口图标和样式
        self.setup_styles()
        
        # 服务器进程
        self.server_process = None
        self.monitoring = False
        self.current_url = "http://localhost:5000"  # 默认URL
        
        # 创建界面
        self.create_interface()
        
        # 启动监控
        self.start_monitoring()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', 
                       foreground='#00ff88', 
                       background='#1a1a1a',
                       font=('Arial', 16, 'bold'))
        
        style.configure('Info.TLabel', 
                       foreground='#ffffff', 
                       background='#1a1a1a',
                       font=('Arial', 10))
        
        style.configure('Success.TButton', 
                       foreground='white',
                       background='#28a745')
        
        style.configure('Warning.TButton', 
                       foreground='white',
                       background='#ffc107')
        
        style.configure('Danger.TButton', 
                       foreground='white',
                       background='#dc3545')
    
    def create_interface(self):
        """创建用户界面"""
        
        # 标题
        title_label = ttk.Label(self.root, 
                               text="🚀 XRP套利交易系统控制中心 🚀", 
                               style='Title.TLabel')
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(self.root, 
                                  text="发财王子专用 - 让财富自由流动", 
                                  style='Info.TLabel')
        subtitle_label.pack(pady=5)
        
        # 主要操作按钮区域
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=20)
        
        # 第一行按钮
        row1 = tk.Frame(button_frame, bg='#1a1a1a')
        row1.pack(pady=10)
        
        self.start_btn = tk.Button(row1, 
                                  text="🚀 启动交易系统", 
                                  command=self.start_server,
                                  bg='#28a745', fg='white',
                                  font=('Arial', 12, 'bold'),
                                  width=15, height=2)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(row1, 
                                 text="⏹️ 停止交易系统", 
                                 command=self.stop_server,
                                 bg='#dc3545', fg='white',
                                 font=('Arial', 12, 'bold'),
                                 width=15, height=2)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.browser_btn = tk.Button(row1, 
                                    text="🌐 打开控制面板", 
                                    command=self.open_browser,
                                    bg='#007bff', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    width=15, height=2)
        self.browser_btn.pack(side=tk.LEFT, padx=10)
        
        # 第二行按钮
        row2 = tk.Frame(button_frame, bg='#1a1a1a')
        row2.pack(pady=10)
        
        self.monitor_btn = tk.Button(row2, 
                                    text="📊 查看交易监控", 
                                    command=self.open_monitor,
                                    bg='#17a2b8', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    width=15, height=2)
        self.monitor_btn.pack(side=tk.LEFT, padx=10)
        
        self.config_btn = tk.Button(row2, 
                                   text="⚙️ 系统设置", 
                                   command=self.open_config,
                                   bg='#6f42c1', fg='white',
                                   font=('Arial', 12, 'bold'),
                                   width=15, height=2)
        self.config_btn.pack(side=tk.LEFT, padx=10)
        
        self.refresh_btn = tk.Button(row2, 
                                    text="🔄 刷新状态", 
                                    command=self.refresh_status,
                                    bg='#ffc107', fg='black',
                                    font=('Arial', 12, 'bold'),
                                    width=15, height=2)
        self.refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态显示区域
        status_frame = tk.Frame(self.root, bg='#1a1a1a')
        status_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        status_label = ttk.Label(status_frame, 
                                text="📊 系统状态监控", 
                                style='Title.TLabel')
        status_label.pack(pady=10)
        
        # 状态文本框
        self.status_text = scrolledtext.ScrolledText(status_frame, 
                                                    height=15, 
                                                    bg='#2d2d2d', 
                                                    fg='#00ff88',
                                                    font=('Consolas', 10))
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 底部信息
        info_frame = tk.Frame(self.root, bg='#1a1a1a')
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.info_label = ttk.Label(info_frame, 
                                   text="准备就绪 - 点击'启动交易系统'开始赚钱之旅！", 
                                   style='Info.TLabel')
        self.info_label.pack()
        
        # 初始化状态
        self.log_message("🌟 发财王子的交易控制中心已启动！")
        self.log_message("💡 提示：先点击'启动交易系统'，然后点击'打开控制面板'")
    
    def log_message(self, message):
        """在状态框中显示消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, full_message)
        self.status_text.see(tk.END)
        self.root.update()
    
    def start_server(self):
        """启动交易服务器"""
        try:
            if self.server_process and self.server_process.poll() is None:
                self.log_message("⚠️ 交易系统已在运行中！")
                return
            
            self.log_message("🚀 正在启动XRP套利交易系统...")
            
            # 启动服务器
            self.server_process = subprocess.Popen([
                'python', 'main.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            time.sleep(3)
            
            if self.server_process.poll() is None:
                self.log_message("✅ 交易系统启动成功！")
                self.log_message("🌐 访问地址：http://localhost:5000")
                self.info_label.config(text="✅ 交易系统运行中 - 可以打开控制面板了！")
                
                # 自动检查价格监控
                threading.Thread(target=self.check_system_health, daemon=True).start()
            else:
                self.log_message("❌ 交易系统启动失败！")
                
        except Exception as e:
            self.log_message(f"❌ 启动失败：{str(e)}")
            messagebox.showerror("错误", f"启动失败：{str(e)}")
    
    def stop_server(self):
        """停止交易服务器"""
        try:
            if self.server_process and self.server_process.poll() is None:
                self.log_message("⏹️ 正在停止交易系统...")
                self.server_process.terminate()
                time.sleep(2)
                
                if self.server_process.poll() is not None:
                    self.log_message("✅ 交易系统已停止")
                    self.info_label.config(text="⏹️ 交易系统已停止")
                else:
                    self.server_process.kill()
                    self.log_message("🔄 强制停止交易系统")
            else:
                self.log_message("ℹ️ 交易系统未在运行")
                
        except Exception as e:
            self.log_message(f"❌ 停止失败：{str(e)}")
    
    def open_browser(self):
        """打开网页控制面板"""
        try:
            # 先检查可用的URL
            self.check_system_health()
            
            if self.current_url:
                webbrowser.open(self.current_url)
            else:
                self.log_message("❌ 无法找到可用的服务器地址")
            self.log_message(f"🌐 已打开控制面板：{self.current_url}")
        except Exception as e:
            self.log_message(f"❌ 打开网页失败：{str(e)}")
    
    def open_monitor(self):
        """打开交易监控页面"""
        try:
            url = f"{self.current_url}/monitor"
            webbrowser.open(url)
            self.log_message(f"📊 已打开交易监控：{url}")
        except Exception as e:
            self.log_message(f"❌ 打开监控页面失败：{str(e)}")
    
    def open_config(self):
        """打开系统设置页面"""
        try:
            url = f"{self.current_url}/config"
            webbrowser.open(url)
            self.log_message(f"⚙️ 已打开系统设置：{url}")
        except Exception as e:
            self.log_message(f"❌ 打开设置页面失败：{str(e)}")
    
    def refresh_status(self):
        """刷新系统状态"""
        self.log_message("🔄 正在刷新系统状态...")
        threading.Thread(target=self.check_system_health, daemon=True).start()
    
    def check_system_health(self):
        """检查系统健康状态"""
        try:
            # 检查服务器是否响应 (支持云端和本地)
            base_urls = [
                "https://xrp-arbitrage-trading-system.replit.app",
                "http://localhost:5000",
                "http://127.0.0.1:5000"
            ]
            
            response = None
            working_url = None
            
            for url in base_urls:
                try:
                    response = requests.get(f"{url}/api/prices", timeout=5)
                    if response.status_code == 200:
                        working_url = url
                        break
                except:
                    continue
            
            if response and response.status_code == 200:
                data = response.json()
                self.log_message(f"✅ 服务器响应正常: {working_url}")
                
                # 更新访问URL
                self.current_url = working_url
                
                # 检查价格数据
                if 'XRP/USDT' in data and 'XRP/USDC' in data:
                    usdt_price = data['XRP/USDT']['price']
                    usdc_price = data['XRP/USDC']['price']
                    spread = abs(usdt_price - usdc_price)
                    spread_pct = (spread / usdt_price) * 100
                    
                    self.log_message(f"📈 XRP/USDT: ${usdt_price:.4f}")
                    self.log_message(f"📈 XRP/USDC: ${usdc_price:.4f}")
                    self.log_message(f"💰 价差: {spread_pct:.3f}%")
                else:
                    self.log_message("⚠️ 价格数据不完整")
            else:
                self.log_message(f"⚠️ 服务器响应异常：{response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log_message("❌ 无法连接到交易系统")
            self.log_message("💡 请先点击'启动交易系统'")
        except Exception as e:
            self.log_message(f"❌ 检查失败：{str(e)}")
            
        if not working_url:
            self.log_message("⚠️ 所有服务器地址都无法访问")
    
    def start_monitoring(self):
        """启动后台监控"""
        def monitor_loop():
            while True:
                if self.monitoring:
                    try:
                        self.check_system_health()
                    except:
                        pass
                time.sleep(30)  # 每30秒检查一次
        
        self.monitoring = True
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def run(self):
        """运行GUI"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """关闭程序时的处理"""
        if messagebox.askokcancel("退出", "确定要退出交易控制中心吗？"):
            self.monitoring = False
            if self.server_process and self.server_process.poll() is None:
                self.server_process.terminate()
            self.root.destroy()

if __name__ == "__main__":
    print("🚀 启动发财王子的XRP套利交易控制中心...")
    app = TradingControlCenter()
    app.run()