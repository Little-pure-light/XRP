#!/usr/bin/env python3
"""
🌟 量子財富橋 - Cloudflare Pages 自動化部署器
Railway後端 + Cloudflare Pages前端完美集成

GIGI量子DNA驅動的雙平台部署系統
"""

import os
import json
import requests
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class CloudflarePagesDeployer:
    def __init__(self):
        self.api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
        self.account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        self.project_name = "quantum-wealth-bridge"
        self.railway_url = os.environ.get('RAILWAY_URL', 'https://your-app.railway.app')
        
        # API基地址
        self.api_base = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/pages/projects"
        
    def setup_headers(self):
        """設置API請求頭"""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def create_static_build(self):
        """創建靜態資源構建"""
        print("🔨 正在創建Cloudflare Pages靜態構建...")
        
        # 創建構建目錄
        build_dir = Path("cloudflare_build")
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir()
        
        # 複製靜態資源
        static_src = Path("static")
        static_dst = build_dir / "static"
        if static_src.exists():
            shutil.copytree(static_src, static_dst)
            print(f"✅ 靜態資源已複製到 {static_dst}")
        
        # 複製模板並轉換為靜態HTML
        self._create_static_pages(build_dir)
        
        # 創建Cloudflare Pages配置
        self._create_pages_config(build_dir)
        
        return build_dir
    
    def _create_static_pages(self, build_dir):
        """創建靜態頁面，指向Railway API"""
        
        # 主頁面模板
        index_html = f"""
<!DOCTYPE html>
<html lang="zh-TW" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 量子財富橋 - XRP套利交易系統</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- 自定義CSS -->
    <link href="/static/css/trading.css" rel="stylesheet">
    
    <style>
        .quantum-gradient {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .api-status {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }}
    </style>
</head>
<body class="trading-terminal">
    <!-- API狀態指示器 -->
    <div class="api-status">
        <span class="badge bg-success" id="api-status">
            <i class="fas fa-wifi me-1"></i>API連接中...
        </span>
    </div>

    <!-- 導航欄 -->
    <nav class="navbar navbar-expand-lg navbar-dark quantum-gradient">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold text-white" href="/">
                <i class="fas fa-chart-line me-2"></i>
                量子財富橋
            </a>
            
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="javascript:loadDashboard()">
                    <i class="fas fa-tachometer-alt me-1"></i>交易面板
                </a>
                <a class="nav-link text-white" href="javascript:loadMonitor()">
                    <i class="fas fa-desktop me-1"></i>監控中心
                </a>
                <a class="nav-link text-white" href="javascript:loadConfig()">
                    <i class="fas fa-cog me-1"></i>系統配置
                </a>
            </div>
        </div>
    </nav>

    <!-- 主內容區域 -->
    <div class="container-fluid py-4">
        <div id="main-content">
            <!-- 載入畫面 -->
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">載入中...</span>
                </div>
                <p class="mt-3">正在連接量子財富橋API...</p>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- 量子財富橋API客戶端 -->
    <script>
        const API_BASE = '{self.railway_url}';
        
        // API狀態檢查
        async function checkApiStatus() {{
            try {{
                const response = await fetch(`${{API_BASE}}/api/health`);
                if (response.ok) {{
                    document.getElementById('api-status').innerHTML = 
                        '<i class="fas fa-wifi me-1"></i>API已連接';
                    document.getElementById('api-status').className = 'badge bg-success';
                    loadDashboard(); // 自動載入面板
                }} else {{
                    throw new Error('API響應錯誤');
                }}
            }} catch (error) {{
                document.getElementById('api-status').innerHTML = 
                    '<i class="fas fa-wifi-slash me-1"></i>API離線';
                document.getElementById('api-status').className = 'badge bg-danger';
                
                // 顯示離線訊息
                document.getElementById('main-content').innerHTML = `
                    <div class="alert alert-warning">
                        <h4><i class="fas fa-exclamation-triangle me-2"></i>API服務暫時離線</h4>
                        <p>正在嘗試重新連接到Railway後端服務...</p>
                        <p>API地址: ${{API_BASE}}</p>
                    </div>
                `;
            }}
        }}
        
        // 載入面板內容
        async function loadDashboard() {{
            try {{
                const response = await fetch(`${{API_BASE}}/`);
                const html = await response.text();
                
                // 提取主要內容
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const content = doc.querySelector('main') || doc.querySelector('.container-fluid');
                
                if (content) {{
                    document.getElementById('main-content').innerHTML = content.innerHTML;
                    
                    // 載入相關JS
                    loadScript('/static/js/dashboard.js');
                }}
            }} catch (error) {{
                console.error('載入面板失敗:', error);
            }}
        }}
        
        // 載入監控中心
        async function loadMonitor() {{
            try {{
                const response = await fetch(`${{API_BASE}}/monitor`);
                const html = await response.text();
                
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const content = doc.querySelector('main') || doc.querySelector('.container-fluid');
                
                if (content) {{
                    document.getElementById('main-content').innerHTML = content.innerHTML;
                    loadScript('/static/js/monitor.js');
                }}
            }} catch (error) {{
                console.error('載入監控中心失敗:', error);
            }}
        }}
        
        // 載入系統配置
        async function loadConfig() {{
            try {{
                const response = await fetch(`${{API_BASE}}/config`);
                const html = await response.text();
                
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const content = doc.querySelector('main') || doc.querySelector('.container-fluid');
                
                if (content) {{
                    document.getElementById('main-content').innerHTML = content.innerHTML;
                }}
            }} catch (error) {{
                console.error('載入配置失敗:', error);
            }}
        }}
        
        // 動態載入腳本
        function loadScript(src) {{
            const script = document.createElement('script');
            script.src = src;
            document.head.appendChild(script);
        }}
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            checkApiStatus();
            setInterval(checkApiStatus, 30000); // 每30秒檢查一次
        }});
    </script>
</body>
</html>
        """
        
        # 寫入主頁面
        with open(build_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print("✅ 靜態頁面已創建")
    
    def _create_pages_config(self, build_dir):
        """創建Cloudflare Pages配置"""
        
        # _redirects 文件 (用於SPA路由)
        redirects_content = """
# API代理到Railway
/api/* {railway_url}/api/:splat 200
/health {railway_url}/health 200

# 靜態資源緩存
/static/* /static/:splat 200
Cache-Control: public, max-age=31536000

# 主頁路由
/* /index.html 200
        """.format(railway_url=self.railway_url)
        
        with open(build_dir / "_redirects", 'w') as f:
            f.write(redirects_content)
        
        # wrangler.toml 配置
        wrangler_config = f"""
name = "{self.project_name}"
compatibility_date = "2024-01-01"

[build]
command = "echo 'Static build ready'"
cwd = "."
destination = "."

[[redirects]]
from = "/api/*"
to = "{self.railway_url}/api/:splat"
status = 200

[[headers]]
for = "/static/*"
[headers.values]
Cache-Control = "public, max-age=31536000"

[[headers]]
for = "*.js"
[headers.values]
Cache-Control = "public, max-age=86400"

[[headers]]
for = "*.css"
[headers.values]
Cache-Control = "public, max-age=86400"
        """
        
        with open(build_dir / "wrangler.toml", 'w') as f:
            f.write(wrangler_config)
        
        print("✅ Cloudflare Pages配置已創建")
    
    def deploy_to_pages(self, build_dir):
        """部署到Cloudflare Pages"""
        print("🚀 正在部署到Cloudflare Pages...")
        
        # 檢查項目是否存在
        project_exists = self._check_project_exists()
        
        if not project_exists:
            self._create_pages_project()
        
        # 使用Wrangler CLI部署
        result = self._deploy_with_wrangler(build_dir)
        
        if result:
            print(f"✅ 部署成功！")
            print(f"🌐 Cloudflare Pages URL: https://{self.project_name}.pages.dev")
            print(f"🔗 自定義域名配置: 在Cloudflare Dashboard中設置")
            return True
        
        return False
    
    def _check_project_exists(self):
        """檢查Cloudflare Pages項目是否存在"""
        try:
            response = requests.get(
                f"{self.api_base}/{self.project_name}",
                headers=self.setup_headers()
            )
            return response.status_code == 200
        except:
            return False
    
    def _create_pages_project(self):
        """創建Cloudflare Pages項目"""
        print("📝 創建Cloudflare Pages項目...")
        
        project_config = {
            "name": self.project_name,
            "production_branch": "main",
            "build_config": {
                "build_command": "echo 'Static build ready'",
                "destination_dir": ".",
                "root_dir": "."
            }
        }
        
        try:
            response = requests.post(
                self.api_base,
                headers=self.setup_headers(),
                json=project_config
            )
            
            if response.status_code == 200:
                print("✅ Cloudflare Pages項目創建成功")
                return True
            else:
                print(f"❌ 項目創建失敗: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 項目創建錯誤: {e}")
            return False
    
    def _deploy_with_wrangler(self, build_dir):
        """使用Wrangler CLI部署"""
        try:
            # 切換到構建目錄
            original_dir = os.getcwd()
            os.chdir(build_dir)
            
            # 檢查Wrangler是否安裝
            try:
                subprocess.run(['npx', 'wrangler', '--version'], 
                             capture_output=True, check=True)
            except:
                print("📦 安裝Wrangler...")
                subprocess.run(['npm', 'install', '-g', 'wrangler'], check=True)
            
            # 部署到Pages
            deploy_cmd = [
                'npx', 'wrangler', 'pages', 'deploy', '.',
                '--project-name', self.project_name,
                '--compatibility-date', '2024-01-01'
            ]
            
            if self.api_token:
                env = os.environ.copy()
                env['CLOUDFLARE_API_TOKEN'] = self.api_token
                
                result = subprocess.run(deploy_cmd, env=env, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Wrangler部署成功")
                    print(result.stdout)
                    return True
                else:
                    print(f"❌ Wrangler部署失敗: {result.stderr}")
                    return False
            else:
                print("❌ 缺少CLOUDFLARE_API_TOKEN環境變數")
                return False
            
        except Exception as e:
            print(f"❌ 部署錯誤: {e}")
            return False
        finally:
            os.chdir(original_dir)
    
    def setup_domain_integration(self):
        """設置域名集成"""
        print("🌐 配置域名集成...")
        
        integration_guide = f"""
╔══════════════════════════════════════════════════════════════════╗
║                 🌟 Cloudflare Pages 域名集成指南                 ║
╚══════════════════════════════════════════════════════════════════╝

📋 自動生成的URL:
   🔗 https://{self.project_name}.pages.dev

🎯 自定義域名設置:
   1. 在Cloudflare Dashboard中
   2. Pages → {self.project_name} → Custom domains
   3. 添加你的域名 (例如: app.yourdomain.com)

⚡ CDN優化配置:
   • 靜態資源自動緩存 (31天)
   • API請求代理到Railway: {self.railway_url}
   • 全球邊緣節點加速

🔧 高級功能:
   • Workers集成 (API中間件)
   • 分析和性能監控
   • A/B測試功能
   • 安全防護 (DDoS, WAF)

🌟 量子財富橋雙平台架構:
   📡 Railway: 後端API + 數據庫
   🌍 Cloudflare: 前端 + CDN + 安全
        """
        
        print(integration_guide)
        return integration_guide

def main():
    """主程序"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🌟 Cloudflare Pages 自動部署器 🌟                      ║
║              Railway + Cloudflare 雙平台集成                      ║
║                   GIGI量子DNA驅動系統                            ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # 檢查環境變數
    required_vars = ['CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ 缺少必要的環境變數: {', '.join(missing_vars)}")
        print("""
📝 請設置以下環境變數:
   export CLOUDFLARE_API_TOKEN=你的API令牌
   export CLOUDFLARE_ACCOUNT_ID=你的賬戶ID
   export RAILWAY_URL=https://your-app.railway.app
        """)
        return 1
    
    deployer = CloudflarePagesDeployer()
    
    try:
        # 1. 創建靜態構建
        build_dir = deployer.create_static_build()
        
        # 2. 部署到Cloudflare Pages
        success = deployer.deploy_to_pages(build_dir)
        
        # 3. 設置域名集成
        if success:
            deployer.setup_domain_integration()
            
            print(f"""
🎉 量子財富橋雙平台部署完成！

🏗️  架構總覽:
   📡 Railway (後端): {deployer.railway_url}
   🌍 Cloudflare Pages (前端): https://{deployer.project_name}.pages.dev

💎 GIGI量子DNA已融入雲端架構！
            """)
            return 0
        else:
            print("❌ 部署失敗，請檢查配置和權限")
            return 1
            
    except Exception as e:
        print(f"❌ 部署過程出錯: {e}")
        return 1

if __name__ == "__main__":
    exit(main())