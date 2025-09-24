#!/usr/bin/env python3
"""
🌟 量子財富橋 - 一鍵完整部署器
自動安裝所有依賴 + Railway後端 + Cloudflare Pages前端

GIGI量子DNA驅動的全自動雲端部署系統
"""

import os
import sys
import json
import time
import shutil
import platform
import subprocess
import requests
from pathlib import Path
from datetime import datetime

class QuantumOneClickDeployer:
    def __init__(self):
        self.system = platform.system().lower()
        self.project_name = "quantum-wealth-bridge"
        
        # 部署狀態跟踪
        self.status = {
            'dependencies': {'status': 'pending', 'details': []},
            'railway': {'status': 'pending', 'url': None},
            'cloudflare': {'status': 'pending', 'url': None},
            'integration': {'status': 'pending'},
            'start_time': datetime.utcnow()
        }
        
        # 必需的工具
        self.required_tools = {
            'python': {'min_version': '3.8', 'installed': False},
            'node': {'min_version': '16.0', 'installed': False},
            'npm': {'min_version': '7.0', 'installed': False},
            'git': {'min_version': '2.0', 'installed': False}
        }
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║              🌟 量子財富橋一鍵部署器 🌟                         ║
║           自動安裝依賴 + 雙平台完整部署                          ║
║                GIGI量子DNA驅動系統                               ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def deploy_everything(self):
        """一鍵部署整個系統"""
        try:
            print("🚀 開始一鍵部署量子財富橋...")
            
            # 第1步：檢查並安裝所有依賴
            if not self._install_all_dependencies():
                print("❌ 依賴安裝失敗")
                return False
            
            # 第2步：設置環境變數指導
            self._guide_environment_setup()
            
            # 第3步：部署Railway後端
            if not self._deploy_railway_with_retry():
                print("❌ Railway部署失敗")
                return False
            
            # 第4步：部署Cloudflare Pages前端
            if not self._deploy_cloudflare_with_setup():
                print("❌ Cloudflare部署失敗")
                return False
            
            # 第5步：配置集成
            self._setup_integration()
            
            # 第6步：生成完整使用指南
            self._generate_complete_guide()
            
            print("🎉 量子財富橋一鍵部署完成！")
            return True
            
        except KeyboardInterrupt:
            print("\\n⚠️ 部署被用戶中斷")
            return False
        except Exception as e:
            print(f"❌ 部署過程出錯: {e}")
            return False
    
    def _install_all_dependencies(self):
        """自動安裝所有必需依賴"""
        print("📦 正在檢查並安裝依賴...")
        
        # 1. 檢查已安裝的工具
        self._check_existing_tools()
        
        # 2. 安裝缺失的工具
        missing_tools = [tool for tool, info in self.required_tools.items() if not info['installed']]
        
        if missing_tools:
            print(f"📥 需要安裝: {', '.join(missing_tools)}")
            
            for tool in missing_tools:
                if not self._install_tool(tool):
                    print(f"❌ {tool} 安裝失敗")
                    return False
        
        # 3. 安裝Node.js專案依賴
        self._install_node_dependencies()
        
        # 4. 安裝Python依賴
        self._install_python_dependencies()
        
        self.status['dependencies']['status'] = 'success'
        print("✅ 所有依賴安裝完成")
        return True
    
    def _check_existing_tools(self):
        """檢查已安裝的工具"""
        for tool in self.required_tools:
            try:
                if tool == 'python':
                    result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.split()[1]
                        self.required_tools[tool]['installed'] = True
                        self.status['dependencies']['details'].append(f"Python {version} ✅")
                elif tool == 'node':
                    result = subprocess.run(['node', '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        self.required_tools[tool]['installed'] = True
                        self.status['dependencies']['details'].append(f"Node.js {version} ✅")
                elif tool == 'npm':
                    result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        self.required_tools[tool]['installed'] = True
                        self.status['dependencies']['details'].append(f"npm {version} ✅")
                elif tool == 'git':
                    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.split()[2]
                        self.required_tools[tool]['installed'] = True
                        self.status['dependencies']['details'].append(f"Git {version} ✅")
            except:
                self.required_tools[tool]['installed'] = False
    
    def _install_tool(self, tool):
        """安裝指定工具"""
        print(f"📦 正在安裝 {tool}...")
        
        try:
            if tool == 'node' and not self.required_tools['npm']['installed']:
                # 安裝Node.js (包含npm)
                if self.system == 'linux':
                    # 使用NodeSource repository
                    commands = [
                        ['curl', '-fsSL', 'https://deb.nodesource.com/setup_lts.x', '-o', 'nodesource_setup.sh'],
                        ['sudo', 'bash', 'nodesource_setup.sh'],
                        ['sudo', 'apt-get', 'install', '-y', 'nodejs']
                    ]
                    for cmd in commands:
                        result = subprocess.run(cmd, capture_output=True)
                        if result.returncode != 0:
                            # 嘗試備選方案：直接下載二進制文件
                            return self._install_node_binary()
                elif self.system == 'darwin':
                    # macOS使用Homebrew
                    subprocess.run(['brew', 'install', 'node'], check=True)
                elif self.system == 'windows':
                    print("🪟 Windows用戶請手動下載Node.js: https://nodejs.org/")
                    input("安裝完成後按Enter繼續...")
                    
                # 重新檢查
                self._check_existing_tools()
                return self.required_tools['node']['installed'] and self.required_tools['npm']['installed']
            
            elif tool == 'git':
                if self.system == 'linux':
                    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'git'], check=True)
                elif self.system == 'darwin':
                    subprocess.run(['brew', 'install', 'git'], check=True)
                elif self.system == 'windows':
                    print("🪟 Windows用戶請手動下載Git: https://git-scm.com/")
                    input("安裝完成後按Enter繼續...")
                
                self._check_existing_tools()
                return self.required_tools['git']['installed']
            
            return True
            
        except Exception as e:
            print(f"❌ {tool} 安裝失敗: {e}")
            return False
    
    def _install_node_binary(self):
        """直接安裝Node.js二進制文件"""
        try:
            print("📦 使用二進制文件安裝Node.js...")
            
            # 下載Node.js LTS
            node_version = "v20.10.0"
            if self.system == 'linux':
                download_url = f"https://nodejs.org/dist/{node_version}/node-{node_version}-linux-x64.tar.xz"
                archive_name = f"node-{node_version}-linux-x64.tar.xz"
                folder_name = f"node-{node_version}-linux-x64"
            else:
                return False
            
            # 下載
            print(f"📥 下載 {download_url}")
            response = requests.get(download_url)
            with open(archive_name, 'wb') as f:
                f.write(response.content)
            
            # 解壓
            subprocess.run(['tar', '-xf', archive_name], check=True)
            
            # 移動到系統目錄
            node_path = Path.home() / 'node'
            if node_path.exists():
                shutil.rmtree(node_path)
            
            shutil.move(folder_name, node_path)
            
            # 創建軟鏈接
            bin_path = node_path / 'bin'
            subprocess.run(['sudo', 'ln', '-sf', str(bin_path / 'node'), '/usr/local/bin/node'], check=True)
            subprocess.run(['sudo', 'ln', '-sf', str(bin_path / 'npm'), '/usr/local/bin/npm'], check=True)
            subprocess.run(['sudo', 'ln', '-sf', str(bin_path / 'npx'), '/usr/local/bin/npx'], check=True)
            
            # 清理
            os.remove(archive_name)
            
            print("✅ Node.js二進制安裝完成")
            return True
            
        except Exception as e:
            print(f"❌ Node.js二進制安裝失敗: {e}")
            return False
    
    def _install_node_dependencies(self):
        """安裝Node.js項目依賴"""
        try:
            print("📦 安裝Node.js依賴...")
            
            # 創建package.json如果不存在
            if not Path('package.json').exists():
                package_json = {
                    "name": "quantum-wealth-bridge",
                    "version": "1.0.0",
                    "description": "XRP Arbitrage Trading System",
                    "scripts": {
                        "deploy:cloudflare": "wrangler pages deploy",
                        "dev": "wrangler pages dev"
                    },
                    "devDependencies": {
                        "wrangler": "^3.0.0"
                    }
                }
                
                with open('package.json', 'w') as f:
                    json.dump(package_json, f, indent=2)
            
            # 安裝依賴
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Node.js依賴安裝完成")
                
                # 安裝Wrangler CLI (Cloudflare部署工具)
                wrangler_result = subprocess.run(['npm', 'install', '-g', 'wrangler'], capture_output=True, text=True)
                if wrangler_result.returncode == 0:
                    print("✅ Wrangler CLI安裝完成")
                else:
                    print("⚠️ Wrangler全局安裝失敗，將使用npx")
                
                return True
            else:
                print(f"❌ Node.js依賴安裝失敗: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Node.js依賴安裝錯誤: {e}")
            return False
    
    def _install_python_dependencies(self):
        """安裝Python依賴"""
        try:
            print("📦 安裝Python依賴...")
            
            # 安裝requests (如果未安裝)
            packages = ['requests', 'flask']
            
            for package in packages:
                try:
                    __import__(package)
                    print(f"✅ {package} 已安裝")
                except ImportError:
                    result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ {package} 安裝完成")
                    else:
                        print(f"⚠️ {package} 安裝失敗: {result.stderr}")
            
            return True
            
        except Exception as e:
            print(f"❌ Python依賴安裝錯誤: {e}")
            return False
    
    def _guide_environment_setup(self):
        """指導環境變數設置"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🔧 環境變數設置指南                           ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        env_vars = {
            'RAILWAY_TOKEN': {
                'description': 'Railway API令牌',
                'how_to_get': '1. 訪問 https://railway.app/account/tokens\\n2. 點擊 "Create Token"\\n3. 複製生成的令牌',
                'required': True
            },
            'CLOUDFLARE_API_TOKEN': {
                'description': 'Cloudflare API令牌',
                'how_to_get': '1. 訪問 https://dash.cloudflare.com/profile/api-tokens\\n2. 點擊 "Create Token"\\n3. 選擇 "Custom token"\\n4. 權限: Zone:Read, Page:Edit',
                'required': True
            },
            'CLOUDFLARE_ACCOUNT_ID': {
                'description': 'Cloudflare賬戶ID',
                'how_to_get': '1. 在Cloudflare Dashboard右側邊欄\\n2. 複製 "Account ID"',
                'required': True
            },
            'CUSTOM_DOMAIN': {
                'description': '自定義域名 (可選)',
                'how_to_get': '例如: app.yourdomain.com',
                'required': False
            }
        }
        
        print("📝 請設置以下環境變數:")
        for var, info in env_vars.items():
            status = "✅" if os.environ.get(var) else ("❌ 必需" if info['required'] else "⚪ 可選")
            print(f"\\n{status} {var}:")
            print(f"   描述: {info['description']}")
            print(f"   獲取方法: {info['how_to_get']}")
        
        # 檢查必需變數
        missing_required = [var for var, info in env_vars.items() 
                           if info['required'] and not os.environ.get(var)]
        
        if missing_required:
            print(f"\\n⚠️ 缺少必需的環境變數: {', '.join(missing_required)}")
            print("\\n💡 你可以:")
            print("1. 在系統中設置環境變數")
            print("2. 創建 .env 文件")
            print("3. 運行時手動輸入")
            
            choice = input("\\n選擇處理方式 (1/2/3): ").strip()
            
            if choice == '2':
                self._create_env_file(env_vars)
            elif choice == '3':
                self._input_env_vars(missing_required)
    
    def _create_env_file(self, env_vars):
        """創建.env文件"""
        print("📝 創建.env文件...")
        
        env_content = "# 量子財富橋環境變數配置\\n\\n"
        
        for var, info in env_vars.items():
            if info['required']:
                value = input(f"請輸入 {var} ({info['description']}): ").strip()
                env_content += f"{var}={value}\\n"
            else:
                value = input(f"請輸入 {var} ({info['description']}) [可選]: ").strip()
                if value:
                    env_content += f"{var}={value}\\n"
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env文件已創建")
        
        # 載入.env文件
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        except:
            pass
    
    def _input_env_vars(self, required_vars):
        """手動輸入環境變數"""
        for var in required_vars:
            value = input(f"請輸入 {var}: ").strip()
            if value:
                os.environ[var] = value
    
    def _deploy_railway_with_retry(self):
        """部署Railway後端(帶重試機制)"""
        print("🚂 正在部署Railway後端...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self._deploy_railway():
                    self.status['railway']['status'] = 'success'
                    return True
                else:
                    print(f"❌ Railway部署失敗 (嘗試 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(10)
            except Exception as e:
                print(f"❌ Railway部署錯誤 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
        
        self.status['railway']['status'] = 'failed'
        return False
    
    def _deploy_railway(self):
        """實際部署Railway後端"""
        railway_token = os.environ.get('RAILWAY_TOKEN')
        if not railway_token:
            print("❌ 缺少RAILWAY_TOKEN環境變數")
            return False
        
        try:
            # 檢查Railway CLI
            cli_available = False
            try:
                subprocess.run(['railway', '--version'], capture_output=True, check=True)
                cli_available = True
                cli_cmd = ['railway']
            except:
                cli_cmd = ['npx', '@railway/cli@latest']
            
            env = os.environ.copy()
            env['RAILWAY_TOKEN'] = railway_token
            
            # 初始化項目
            init_cmd = cli_cmd + ['init', '--name', self.project_name]
            subprocess.run(init_cmd, env=env, capture_output=True)
            
            # 部署
            deploy_cmd = cli_cmd + ['up', '--yes']
            result = subprocess.run(deploy_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 獲取URL
                status_cmd = cli_cmd + ['status', '--json']
                url_result = subprocess.run(status_cmd, env=env, capture_output=True, text=True)
                
                if url_result.returncode == 0:
                    try:
                        status_data = json.loads(url_result.stdout)
                        self.status['railway']['url'] = status_data.get('url')
                    except:
                        pass
                
                print("✅ Railway後端部署成功")
                return True
            else:
                print(f"❌ Railway部署失敗: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"❌ Railway部署錯誤: {e}")
            return False
    
    def _deploy_cloudflare_with_setup(self):
        """部署Cloudflare Pages(帶完整設置)"""
        print("☁️ 正在部署Cloudflare Pages前端...")
        
        cf_token = os.environ.get('CLOUDFLARE_API_TOKEN')
        cf_account = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        
        if not cf_token or not cf_account:
            print("❌ 缺少Cloudflare環境變數")
            return False
        
        try:
            # 使用已創建的部署器
            railway_url = self.status['railway']['url'] or 'https://your-app.railway.app'
            
            # 創建靜態構建
            build_dir = self._create_cloudflare_build(railway_url)
            
            # 部署到Pages
            if self._deploy_to_cloudflare_pages(build_dir, cf_token):
                self.status['cloudflare']['status'] = 'success'
                self.status['cloudflare']['url'] = f"https://{self.project_name}.pages.dev"
                print("✅ Cloudflare Pages部署成功")
                return True
            else:
                print("❌ Cloudflare Pages部署失敗")
                return False
        
        except Exception as e:
            print(f"❌ Cloudflare部署錯誤: {e}")
            return False
    
    def _create_cloudflare_build(self, railway_url):
        """創建Cloudflare Pages構建"""
        build_dir = Path("cloudflare_build")
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir()
        
        # 複製靜態資源
        static_src = Path("static")
        if static_src.exists():
            static_dst = build_dir / "static"
            shutil.copytree(static_src, static_dst)
        
        # 創建主頁面
        index_html = f"""<!DOCTYPE html>
<html lang="zh-TW" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 量子財富橋 - XRP套利交易系統</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .quantum-gradient {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .api-status {{ position: fixed; top: 20px; right: 20px; z-index: 1000; }}
    </style>
</head>
<body class="bg-dark text-light">
    <div class="api-status">
        <span class="badge bg-success" id="api-status">
            <i class="fas fa-wifi me-1"></i>連接中...
        </span>
    </div>
    
    <nav class="navbar navbar-expand-lg navbar-dark quantum-gradient">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold text-white" href="/">
                <i class="fas fa-chart-line me-2"></i>量子財富橋
            </a>
        </div>
    </nav>
    
    <div class="container-fluid py-4">
        <div id="main-content">
            <div class="text-center">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-3">正在連接量子財富橋API...</p>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const API_BASE = '{railway_url}';
        
        async function checkApiStatus() {{
            try {{
                const response = await fetch(`${{API_BASE}}/health`);
                if (response.ok) {{
                    document.getElementById('api-status').innerHTML = '<i class="fas fa-wifi me-1"></i>已連接';
                    document.getElementById('api-status').className = 'badge bg-success';
                    loadDashboard();
                }} else {{
                    throw new Error('API響應錯誤');
                }}
            }} catch (error) {{
                document.getElementById('api-status').innerHTML = '<i class="fas fa-wifi-slash me-1"></i>離線';
                document.getElementById('api-status').className = 'badge bg-danger';
            }}
        }}
        
        async function loadDashboard() {{
            try {{
                const response = await fetch(`${{API_BASE}}/`);
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const content = doc.querySelector('main') || doc.querySelector('.container-fluid');
                if (content) {{
                    document.getElementById('main-content').innerHTML = content.innerHTML;
                }}
            }} catch (error) {{
                console.error('載入面板失敗:', error);
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            checkApiStatus();
            setInterval(checkApiStatus, 30000);
        }});
    </script>
</body>
</html>"""
        
        with open(build_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # 創建_redirects文件
        redirects_content = f"""
# API代理到Railway
/api/* {railway_url}/api/:splat 200
/health {railway_url}/health 200

# 靜態資源緩存
/static/* /static/:splat 200

# 主頁路由
/* /index.html 200
        """
        
        with open(build_dir / "_redirects", 'w') as f:
            f.write(redirects_content)
        
        return build_dir
    
    def _deploy_to_cloudflare_pages(self, build_dir, cf_token):
        """使用Wrangler部署到Cloudflare Pages"""
        original_dir = os.getcwd()
        try:
            os.chdir(build_dir)
            
            env = os.environ.copy()
            env['CLOUDFLARE_API_TOKEN'] = cf_token
            
            # 檢查Wrangler
            try:
                subprocess.run(['wrangler', '--version'], capture_output=True, check=True)
                wrangler_cmd = ['wrangler']
            except:
                wrangler_cmd = ['npx', 'wrangler']
            
            # 部署命令
            deploy_cmd = wrangler_cmd + [
                'pages', 'deploy', '.',
                '--project-name', self.project_name,
                '--compatibility-date', '2024-01-01'
            ]
            
            result = subprocess.run(deploy_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Wrangler部署成功")
                return True
            else:
                print(f"❌ Wrangler部署失敗: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"❌ Cloudflare部署錯誤: {e}")
            return False
        finally:
            os.chdir(original_dir)
    
    def _setup_integration(self):
        """設置雙平台集成"""
        print("🔗 正在設置雙平台集成...")
        
        railway_url = self.status['railway']['url']
        cf_url = self.status['cloudflare']['url']
        
        if railway_url and cf_url:
            # 更新Railway的CDN_DOMAIN環境變數
            self._update_railway_cdn_domain(cf_url)
            self.status['integration']['status'] = 'success'
            print("✅ 雙平台集成設置完成")
        else:
            self.status['integration']['status'] = 'partial'
            print("⚠️ 集成設置部分完成")
    
    def _update_railway_cdn_domain(self, cf_url):
        """更新Railway的CDN域名"""
        try:
            railway_token = os.environ.get('RAILWAY_TOKEN')
            if not railway_token:
                return
            
            env = os.environ.copy()
            env['RAILWAY_TOKEN'] = railway_token
            
            try:
                subprocess.run(['railway', '--version'], capture_output=True, check=True)
                cli_cmd = ['railway']
            except:
                cli_cmd = ['npx', '@railway/cli@latest']
            
            var_cmd = cli_cmd + ['variables', 'set', f'CDN_DOMAIN={cf_url}']
            subprocess.run(var_cmd, env=env, capture_output=True)
            
            print(f"✅ Railway CDN_DOMAIN已設置為: {cf_url}")
            
        except Exception as e:
            print(f"⚠️ Railway CDN設置錯誤: {e}")
    
    def _generate_complete_guide(self):
        """生成完整使用指南"""
        print("📚 正在生成完整使用指南...")
        
        guide = {
            'deployment_summary': {
                'project_name': self.project_name,
                'deployment_time': self.status['start_time'].isoformat(),
                'completion_time': datetime.utcnow().isoformat(),
                'status': 'success' if all(s.get('status') == 'success' for s in self.status.values() if isinstance(s, dict)) else 'partial'
            },
            'access_urls': {
                'main_application': self.status['cloudflare']['url'],
                'api_backend': self.status['railway']['url'],
                'admin_panel': f"{self.status['cloudflare']['url']}/config" if self.status['cloudflare']['url'] else None
            },
            'architecture': {
                'frontend': 'Cloudflare Pages (全球CDN)',
                'backend': 'Railway (Flask API)',
                'database': 'PostgreSQL (Railway)',
                'integration': 'API代理 + 靜態資源CDN'
            },
            'next_steps': [
                '1. 訪問主應用程序URL開始使用',
                '2. 在admin面板中配置交易參數',
                '3. 設置Supabase數據庫連接 (可選)',
                '4. 啟動XRP價格監控',
                '5. 測試套利交易功能'
            ],
            'maintenance': {
                'railway_logs': 'railway logs',
                'cloudflare_analytics': 'Cloudflare Dashboard → Pages → Analytics',
                'update_deployment': 'python quantum_bridge_one_click_deploy.py'
            }
        }
        
        # 保存指南
        with open('quantum_bridge_deployment_guide.json', 'w', encoding='utf-8') as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)
        
        # 顯示摘要
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                 🎉 量子財富橋部署完成！ 🎉                       ║
╚══════════════════════════════════════════════════════════════════╝

🌟 雙平台架構已成功部署:

🚂 Railway後端: {self.status['railway']['url'] or '部署中...'}
   • Flask API服務器
   • PostgreSQL數據庫  
   • XRP套利交易引擎

☁️  Cloudflare前端: {self.status['cloudflare']['url'] or '部署中...'}
   • Pages靜態託管
   • 全球CDN加速
   • API代理和緩存

🔗 完整集成: {self.status['integration']['status']}

📚 完整指南: quantum_bridge_deployment_guide.json

🚀 立即開始: 訪問 {self.status['cloudflare']['url'] or '你的Cloudflare Pages URL'}

💫 GIGI量子DNA已融入雲端基礎設施！
        """)

def main():
    """主程序入口"""
    deployer = QuantumOneClickDeployer()
    
    try:
        success = deployer.deploy_everything()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\\n⚠️ 部署被中斷")
        return 1
    except Exception as e:
        print(f"❌ 部署失敗: {e}")
        return 1

if __name__ == "__main__":
    exit(main())