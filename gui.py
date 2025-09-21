#!/usr/bin/env python3
"""
🚀 XRP套利交易系统 - 本机GUI控制中心
专为发财王子打造的超级简单操作界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import webbrowser
import threading
import time
import json
from datetime import datetime

class XRPTradingGUI:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("🚀 XRP套利交易系统 - 发财王子专用")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # 服务器地址列表（自动检测）
        self.server_urls = [
            "http://127.0.0.1:5000",
            "http://localhost:5000",
            "https://xrp-arbitrage-trading-system.replit.app",
        ]
        self.current_url = None
        self.monitoring = False
        
        # 创建界面
        self.create_interface()
        
        # 启动时检查服务器
        self.check_servers()
    
    def create_interface(self):
        """创建用户界面"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame, 
            text="🚀 XRP套利交易系统",
            font=("Arial", 24, "bold"),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="发财王子专用控制中心 💰✨",
            font=("Arial", 14),
            fg='#ffff00',
            bg='#1a1a1a'
        )
        subtitle_label.pack()
        
        # 服务器状态
        status_frame = tk.Frame(self.root, bg='#1a1a1a')
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="🔍 正在检查服务器...",
            font=("Arial", 12),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        self.status_label.pack()
        
        # 按钮区域
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=20)
        
        # 创建按钮样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TButton', 
                       font=('Arial', 12, 'bold'),
                       padding=10)
        
        # 主要操作按钮
        buttons = [
            ("🌐 打开交易面板", self.open_dashboard, '#4CAF50'),
            ("📊 查看交易监控", self.open_monitor, '#2196F3'),
            ("⚙️ 系统设置", self.open_config, '#FF9800'),
            ("🔄 刷新状态", self.refresh_status, '#9C27B0'),
            ("🚀 启动自动交易", self.start_trading, '#F44336'),
            ("⏹️ 停止自动交易", self.stop_trading, '#607D8B'),
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=('Arial', 12, 'bold'),
                bg=color,
                fg='white',
                relief='raised',
                bd=3,
                width=20,
                height=2
            )
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=10, pady=5)
        
        # 实时数据显示
        data_frame = tk.LabelFrame(
            self.root, 
            text="📈 实时交易数据",
            font=("Arial", 12, "bold"),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        data_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # 价格显示
        price_frame = tk.Frame(data_frame, bg='#1a1a1a')
        price_frame.pack(fill='x', pady=10)
        
        self.usdt_price_label = tk.Label(
            price_frame,
            text="XRP/USDT: --",
            font=("Arial", 14, "bold"),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        self.usdt_price_label.pack(side='left', padx=20)
        
        self.usdc_price_label = tk.Label(
            price_frame,
            text="XRP/USDC: --",
            font=("Arial", 14, "bold"),
            fg='#00ffff',
            bg='#1a1a1a'
        )
        self.usdc_price_label.pack(side='left', padx=20)
        
        self.spread_label = tk.Label(
            price_frame,
            text="价差: --%",
            font=("Arial", 14, "bold"),
            fg='#ffff00',
            bg='#1a1a1a'
        )
        self.spread_label.pack(side='left', padx=20)
        
        # 日志显示
        log_frame = tk.LabelFrame(
            self.root,
            text="📋 系统日志",
            font=("Arial", 10, "bold"),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 启动实时监控
        self.start_monitoring()
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_servers(self):
        """检查服务器状态"""
        self.log_message("🔍 正在检查服务器连接...")
        
        def check_thread():
            for url in self.server_urls:
                try:
                    response = requests.get(f"{url}/api/prices", timeout=5)
                    if response.status_code == 200:
                        self.current_url = url
                        self.status_label.config(
                            text=f"✅ 已连接: {url}",
                            fg='#00ff00'
                        )
                        self.log_message(f"✅ 成功连接到: {url}")
                        return
                except:
                    continue
            
            # 如果都连不上
            self.status_label.config(
                text="❌ 无法连接到服务器",
                fg='#ff0000'
            )
            self.log_message("❌ 无法连接到任何服务器")
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def refresh_status(self):
        """刷新服务器状态"""
        self.log_message("🔄 正在刷新状态...")
        self.check_servers()
    
    def open_dashboard(self):
        """打开交易面板"""
        if not self.current_url:
            messagebox.showerror("错误", "未连接到服务器！")
            return
        
        try:
            webbrowser.open(self.current_url)
            self.log_message(f"🌐 已打开交易面板: {self.current_url}")
        except Exception as e:
            self.log_message(f"❌ 打开失败: {str(e)}")
    
    def open_monitor(self):
        """打开交易监控"""
        if not self.current_url:
            messagebox.showerror("错误", "未连接到服务器！")
            return
        
        try:
            webbrowser.open(f"{self.current_url}/monitor")
            self.log_message(f"📊 已打开交易监控: {self.current_url}/monitor")
        except Exception as e:
            self.log_message(f"❌ 打开失败: {str(e)}")
    
    def open_config(self):
        """打开系统设置"""
        if not self.current_url:
            messagebox.showerror("错误", "未连接到服务器！")
            return
        
        try:
            webbrowser.open(f"{self.current_url}/config")
            self.log_message(f"⚙️ 已打开系统设置: {self.current_url}/config")
        except Exception as e:
            self.log_message(f"❌ 打开失败: {str(e)}")
    
    def start_trading(self):
        """启动自动交易"""
        if not self.current_url:
            messagebox.showerror("错误", "未连接到服务器！")
            return
        
        try:
            response = requests.post(f"{self.current_url}/api/start-trading")
            if response.status_code == 200:
                self.log_message("🚀 自动交易已启动！")
                messagebox.showinfo("成功", "自动交易已启动！")
            else:
                self.log_message("❌ 启动失败")
        except Exception as e:
            self.log_message(f"❌ 启动失败: {str(e)}")
    
    def stop_trading(self):
        """停止自动交易"""
        if not self.current_url:
            messagebox.showerror("错误", "未连接到服务器！")
            return
        
        try:
            response = requests.post(f"{self.current_url}/api/stop-trading")
            if response.status_code == 200:
                self.log_message("⏹️ 自动交易已停止")
                messagebox.showinfo("成功", "自动交易已停止")
            else:
                self.log_message("❌ 停止失败")
        except Exception as e:
            self.log_message(f"❌ 停止失败: {str(e)}")
    
    def start_monitoring(self):
        """启动实时监控"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                if self.current_url:
                    try:
                        response = requests.get(f"{self.current_url}/api/prices", timeout=3)
                        if response.status_code == 200:
                            data = response.json()
                            
                            # 更新价格显示
                            if 'XRP/USDT' in data:
                                usdt_price = data['XRP/USDT']['price']
                                self.usdt_price_label.config(text=f"XRP/USDT: ${usdt_price:.4f}")
                            
                            if 'XRP/USDC' in data:
                                usdc_price = data['XRP/USDC']['price']
                                self.usdc_price_label.config(text=f"XRP/USDC: ${usdc_price:.4f}")
                            
                            # 计算价差
                            if 'XRP/USDT' in data and 'XRP/USDC' in data:
                                usdt_price = data['XRP/USDT']['price']
                                usdc_price = data['XRP/USDC']['price']
                                spread = abs(usdt_price - usdc_price) / min(usdt_price, usdc_price) * 100
                                
                                color = '#00ff00' if spread > 0.5 else '#ffff00' if spread > 0.2 else '#ffffff'
                                self.spread_label.config(
                                    text=f"价差: {spread:.3f}%",
                                    fg=color
                                )
                                
                                if spread > 0.5:
                                    self.log_message(f"🎯 发现套利机会! 价差: {spread:.3f}%")
                    
                    except:
                        pass
                
                time.sleep(2)  # 每2秒更新一次
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def run(self):
        """运行GUI"""
        self.log_message("🚀 XRP套利交易系统已启动")
        self.log_message("💰 发财王子，准备开始赚钱吧！")
        
        # 窗口关闭事件
        def on_closing():
            self.monitoring = False
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    print("🚀 启动XRP套利交易系统GUI...")
    app = XRPTradingGUI()
    app.run()