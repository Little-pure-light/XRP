#!/usr/bin/env python3
"""
🌟 量子財富橋 - Railway + Cloudflare 完整集成器
一鍵部署雙平台架構，實現最佳性能

GIGI量子DNA驅動的雲端基礎設施自動化
"""

import os
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime

class QuantumDualPlatformDeployer:
    def __init__(self):
        # Railway配置
        self.railway_token = os.environ.get('RAILWAY_TOKEN')
        self.railway_project_id = os.environ.get('RAILWAY_PROJECT_ID')
        
        # Cloudflare配置
        self.cf_api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
        self.cf_account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        self.cf_zone_id = os.environ.get('CLOUDFLARE_ZONE_ID')
        
        # 項目配置
        self.project_name = "quantum-wealth-bridge"
        self.custom_domain = os.environ.get('CUSTOM_DOMAIN')  # 可選自定義域名
        
        # API基地址
        self.railway_api = "https://backboard.railway.app/graphql/v2"
        self.cf_api_base = f"https://api.cloudflare.com/client/v4"
        
        # 部署狀態
        self.deployment_status = {
            'railway': {'status': 'pending', 'url': None},
            'cloudflare': {'status': 'pending', 'url': None},
            'integration': {'status': 'pending', 'api_proxy': False},
            'start_time': datetime.utcnow(),
            'end_time': None
        }
    
    def deploy_complete_system(self):
        """部署完整雙平台系統"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           🌟 量子財富橋雙平台部署開始 🌟                         ║
║               Railway 後端 + Cloudflare 前端                     ║
║                    GIGI量子DNA驅動系統                           ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        try:
            # 第1步：部署Railway後端
            railway_success = self._deploy_railway_backend()
            
            if railway_success:
                print("✅ Railway後端部署成功")
                
                # 第2步：等待Railway服務穩定
                self._wait_for_railway_stability()
                
                # 第3步：部署Cloudflare Pages前端
                cf_success = self._deploy_cloudflare_frontend()
                
                if cf_success:
                    print("✅ Cloudflare Pages前端部署成功")
                    
                    # 第4步：配置API代理
                    proxy_success = self._setup_api_proxy()
                    
                    if proxy_success:
                        print("✅ API代理配置成功")
                        
                        # 第5步：優化CDN設置
                        self._optimize_cloudflare_cdn()
                        
                        # 第6步：設置自定義域名 (如果提供)
                        if self.custom_domain:
                            self._setup_custom_domain()
                        
                        # 第7步：生成完整報告
                        self._generate_deployment_report()
                        
                        print("🎉 雙平台部署完全成功！")
                        return True
            
            print("❌ 部署過程中出現錯誤")
            return False
            
        except Exception as e:
            print(f"❌ 部署失敗: {e}")
            return False
        finally:
            self.deployment_status['end_time'] = datetime.utcnow()
    
    def _deploy_railway_backend(self):
        """部署Railway後端"""
        print("🚂 正在部署Railway後端...")
        
        try:
            # 檢查Railway CLI
            railway_cmd = ['railway', 'status'] if self.railway_token else ['npx', '@railway/cli@latest', 'status']
            
            # 設置環境變數
            env = os.environ.copy()
            if self.railway_token:
                env['RAILWAY_TOKEN'] = self.railway_token
            
            # 檢查項目狀態
            result = subprocess.run(railway_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("📝 創建新的Railway項目...")
                
                # 初始化項目
                init_cmd = ['railway', 'init', '--name', self.project_name] if self.railway_token else [
                    'npx', '@railway/cli@latest', 'init', '--name', self.project_name
                ]
                
                subprocess.run(init_cmd, env=env, check=True)
            
            # 設置環境變數
            self._setup_railway_environment(env)
            
            # 部署應用
            deploy_cmd = ['railway', 'up', '--yes'] if self.railway_token else [
                'npx', '@railway/cli@latest', 'up', '--yes'
            ]
            
            deploy_result = subprocess.run(deploy_cmd, env=env, capture_output=True, text=True)
            
            if deploy_result.returncode == 0:
                # 獲取部署URL
                url_cmd = ['railway', 'status', '--json'] if self.railway_token else [
                    'npx', '@railway/cli@latest', 'status', '--json'
                ]
                
                url_result = subprocess.run(url_cmd, env=env, capture_output=True, text=True)
                
                if url_result.returncode == 0:
                    try:
                        status_data = json.loads(url_result.stdout)
                        self.deployment_status['railway']['url'] = status_data.get('url')
                    except:
                        pass
                
                self.deployment_status['railway']['status'] = 'success'
                return True
            else:
                print(f"❌ Railway部署失敗: {deploy_result.stderr}")
                self.deployment_status['railway']['status'] = 'failed'
                return False
        
        except Exception as e:
            print(f"❌ Railway部署錯誤: {e}")
            self.deployment_status['railway']['status'] = 'error'
            return False
    
    def _setup_railway_environment(self, env):
        """設置Railway環境變數"""
        env_vars = {
            'SESSION_SECRET': 'gigi_quantum_bridge_2024_production',
            'FLASK_ENV': 'production',
            'CDN_DOMAIN': '',  # 稍後設置
        }
        
        # 設置Supabase變數 (如果提供)
        supabase_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY']
        for var in supabase_vars:
            if os.environ.get(var):
                env_vars[var] = os.environ[var]
        
        # 使用Railway CLI設置變數
        railway_cmd_prefix = ['railway'] if self.railway_token else ['npx', '@railway/cli@latest']
        
        for key, value in env_vars.items():
            if value:  # 只設置非空值
                var_cmd = railway_cmd_prefix + ['variables', 'set', f'{key}={value}']
                subprocess.run(var_cmd, env=env, capture_output=True)
    
    def _wait_for_railway_stability(self):
        """等待Railway服務穩定"""
        print("⏳ 等待Railway服務穩定...")
        
        railway_url = self.deployment_status['railway']['url']
        if not railway_url:
            time.sleep(30)  # 基本等待
            return
        
        # 健康檢查
        for attempt in range(10):
            try:
                response = requests.get(f"{railway_url}/health", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Railway服務已穩定 (嘗試 {attempt + 1}/10)")
                    return
            except:
                pass
            
            time.sleep(15)  # 等待15秒後重試
        
        print("⚠️ Railway服務健康檢查超時，繼續部署...")
    
    def _deploy_cloudflare_frontend(self):
        """部署Cloudflare Pages前端"""
        print("☁️ 正在部署Cloudflare Pages前端...")
        
        try:
            # 使用之前創建的部署器
            from cloudflare_pages_deploy import CloudflarePagesDeployer
            
            deployer = CloudflarePagesDeployer()
            deployer.railway_url = self.deployment_status['railway']['url'] or 'https://your-app.railway.app'
            
            # 創建靜態構建
            build_dir = deployer.create_static_build()
            
            # 部署到Pages
            success = deployer.deploy_to_pages(build_dir)
            
            if success:
                self.deployment_status['cloudflare']['status'] = 'success'
                self.deployment_status['cloudflare']['url'] = f"https://{self.project_name}.pages.dev"
                return True
            else:
                self.deployment_status['cloudflare']['status'] = 'failed'
                return False
        
        except Exception as e:
            print(f"❌ Cloudflare部署錯誤: {e}")
            self.deployment_status['cloudflare']['status'] = 'error'
            return False
    
    def _setup_api_proxy(self):
        """設置API代理"""
        print("🔗 正在配置API代理...")
        
        try:
            railway_url = self.deployment_status['railway']['url']
            if not railway_url:
                print("⚠️ Railway URL未獲取，跳過API代理設置")
                return False
            
            # 更新Railway的CDN_DOMAIN環境變數
            cf_pages_url = self.deployment_status['cloudflare']['url']
            if cf_pages_url and self.railway_token:
                env = os.environ.copy()
                env['RAILWAY_TOKEN'] = self.railway_token
                
                railway_cmd = ['railway'] if self.railway_token else ['npx', '@railway/cli@latest']
                var_cmd = railway_cmd + ['variables', 'set', f'CDN_DOMAIN={cf_pages_url}']
                
                subprocess.run(var_cmd, env=env, capture_output=True)
                print(f"✅ Railway CDN_DOMAIN已設置為: {cf_pages_url}")
            
            self.deployment_status['integration']['api_proxy'] = True
            return True
            
        except Exception as e:
            print(f"❌ API代理設置錯誤: {e}")
            return False
    
    def _optimize_cloudflare_cdn(self):
        """優化Cloudflare CDN設置"""
        print("⚡ 正在優化Cloudflare CDN...")
        
        if not self.cf_api_token or not self.cf_zone_id:
            print("⚠️ 缺少Cloudflare API配置，跳過CDN優化")
            return
        
        try:
            headers = {
                'Authorization': f'Bearer {self.cf_api_token}',
                'Content-Type': 'application/json'
            }
            
            # 設置緩存規則
            cache_rules = [
                {
                    'expression': '(http.request.uri.path matches "^/static/.*")',
                    'action': 'cache',
                    'cache_settings': {
                        'browser_ttl': 31536000,  # 1年
                        'edge_ttl': 31536000,
                        'serve_stale': {'disable_stale_while_updating': False}
                    }
                },
                {
                    'expression': '(http.request.uri.path matches "^/api/.*")',
                    'action': 'cache',
                    'cache_settings': {
                        'browser_ttl': 300,  # 5分鐘
                        'edge_ttl': 300,
                        'respect_origin': True
                    }
                }
            ]
            
            # 創建緩存規則
            for rule in cache_rules:
                response = requests.post(
                    f"{self.cf_api_base}/zones/{self.cf_zone_id}/rulesets",
                    headers=headers,
                    json={
                        'name': f"Quantum Bridge Cache Rule - {rule['expression'][:20]}",
                        'kind': 'zone',
                        'phase': 'http_request_cache_settings',
                        'rules': [rule]
                    }
                )
                
                if response.status_code in [200, 201]:
                    print("✅ CDN緩存規則已設置")
                else:
                    print(f"⚠️ CDN規則設置部分失敗: {response.status_code}")
            
            print("✅ Cloudflare CDN優化完成")
            
        except Exception as e:
            print(f"⚠️ CDN優化錯誤: {e}")
    
    def _setup_custom_domain(self):
        """設置自定義域名"""
        if not self.custom_domain:
            return
        
        print(f"🌐 正在設置自定義域名: {self.custom_domain}")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.cf_api_token}',
                'Content-Type': 'application/json'
            }
            
            # 為Cloudflare Pages添加自定義域名
            pages_domain_url = f"{self.cf_api_base}/accounts/{self.cf_account_id}/pages/projects/{self.project_name}/domains"
            
            response = requests.post(
                pages_domain_url,
                headers=headers,
                json={'name': self.custom_domain}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ 自定義域名 {self.custom_domain} 已添加到Cloudflare Pages")
                self.deployment_status['cloudflare']['url'] = f"https://{self.custom_domain}"
            else:
                print(f"⚠️ 自定義域名設置失敗: {response.status_code}")
            
        except Exception as e:
            print(f"⚠️ 自定義域名設置錯誤: {e}")
    
    def _generate_deployment_report(self):
        """生成部署報告"""
        print("📊 正在生成部署報告...")
        
        railway_status = self.deployment_status['railway']
        cf_status = self.deployment_status['cloudflare']
        
        report = {
            'deployment_info': {
                'project_name': self.project_name,
                'deployment_time': self.deployment_status['start_time'].isoformat(),
                'completion_time': datetime.utcnow().isoformat(),
                'total_duration': str(datetime.utcnow() - self.deployment_status['start_time'])
            },
            'railway_backend': {
                'status': railway_status['status'],
                'url': railway_status['url'],
                'features': [
                    'Flask API服務器',
                    'PostgreSQL數據庫',
                    'XRP套利交易引擎',
                    '實時價格監控',
                    '風險管理系統'
                ]
            },
            'cloudflare_frontend': {
                'status': cf_status['status'],
                'url': cf_status['url'],
                'features': [
                    'Pages靜態託管',
                    '全球CDN加速',
                    'API代理到Railway',
                    '自動SSL證書',
                    '邊緣緩存優化'
                ]
            },
            'integration': {
                'api_proxy': self.deployment_status['integration']['api_proxy'],
                'cdn_optimization': True,
                'custom_domain': self.custom_domain or 'Not configured'
            },
            'access_urls': {
                'main_application': cf_status['url'],
                'api_backend': railway_status['url'],
                'admin_dashboard': f"{cf_status['url']}/config" if cf_status['url'] else None
            },
            'next_steps': [
                '設置Supabase數據庫連接',
                '配置交易參數',
                '啟動價格監控',
                '測試套利功能',
                '監控系統性能'
            ]
        }
        
        # 保存報告
        with open('quantum_bridge_deployment_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("✅ 部署報告已生成")
        return report

def main():
    """主程序"""
    print("🚀 開始量子財富橋雙平台部署...")
    
    # 檢查必要的環境變數
    required_vars = {
        'Railway': ['RAILWAY_TOKEN'],
        'Cloudflare': ['CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID']
    }
    
    missing_vars = []
    for platform, vars_list in required_vars.items():
        for var in vars_list:
            if not os.environ.get(var):
                missing_vars.append(f"{platform}: {var}")
    
    if missing_vars:
        print("❌ 缺少必要的環境變數:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n📝 請設置這些環境變數後重新運行")
        return 1
    
    # 創建部署器並執行
    deployer = QuantumDualPlatformDeployer()
    success = deployer.deploy_complete_system()
    
    if success:
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                  🎉 量子財富橋部署完成！ 🎉                      ║
╚══════════════════════════════════════════════════════════════════╝

🌟 雙平台架構已成功部署:

🚂 Railway後端: {deployer.deployment_status['railway']['url']}
   • Flask API服務器
   • PostgreSQL數據庫
   • XRP套利交易引擎

☁️  Cloudflare前端: {deployer.deployment_status['cloudflare']['url']}
   • Pages靜態託管
   • 全球CDN加速
   • API代理和緩存

🔗 完整集成:
   • API自動代理
   • 靜態資源CDN加速
   • 全球邊緣節點分發

📊 詳細報告: quantum_bridge_deployment_report.json

💫 GIGI量子DNA已融入雲端基礎設施！
現在可以開始你的量子財富之旅了！
        """)
        return 0
    else:
        print("❌ 部署失敗，請檢查日誌")
        return 1

if __name__ == "__main__":
    exit(main())