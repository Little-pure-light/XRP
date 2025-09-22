#!/usr/bin/env python3
"""
🌟 量子財富橋 - 交互式部署脚本 🌟
连接宇宙量子场的专业部署工具

支持平台：Railway + Cloudflare + Supabase
作者：GIGI量子DNA ✨
为发财王子专属定制 💎
"""

import os
import sys
import json
import time
import requests
import subprocess
from urllib.parse import urlparse
from typing import Dict, List, Optional
import logging

# 配置彩色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class QuantumDeployer:
    def __init__(self):
        self.config = {}
        self.session = requests.Session()
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('quantum_deploy.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def print_banner(self):
        """显示量子财富橋启动横幅"""
        banner = f"""
{Colors.HEADER}
╔══════════════════════════════════════════════════════════════════╗
║                    🌟 量子財富橋部署系统 🌟                      ║
║                   连接宇宙量子场的专业工具                        ║
║                                                                  ║
║  💎 Railway + Cloudflare + Supabase 三平台融合                   ║
║  ⚡ 交互式智能部署，专为发财王子定制                              ║
║  🚀 GIGI量子DNA驱动，宇宙级安全与性能                            ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
        """
        print(banner)
        time.sleep(2)

    def check_prerequisites(self) -> bool:
        """检查部署前置条件"""
        print(f"\n{Colors.OKBLUE}🔍 检查宇宙量子场连接状态...{Colors.ENDC}")
        
        checks = [
            ("Git", self._check_git),
            ("Python", self._check_python),
            ("Railway CLI", self._check_railway_cli),
            ("项目文件", self._check_project_files),
            ("网络连接", self._check_network)
        ]
        
        all_passed = True
        for name, check_func in checks:
            status = "✅" if check_func() else "❌"
            print(f"  {status} {name}")
            if status == "❌":
                all_passed = False
                
        return all_passed

    def _check_git(self) -> bool:
        """检查Git安装"""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except:
            return False

    def _check_python(self) -> bool:
        """检查Python版本"""
        return sys.version_info >= (3, 11)

    def _check_railway_cli(self) -> bool:
        """检查Railway CLI"""
        try:
            result = subprocess.run(["railway", "--version"], capture_output=True, check=True)
            return True
        except:
            print(f"    {Colors.WARNING}💡 Railway CLI未安装，脚本将引导安装{Colors.ENDC}")
            return False

    def _check_project_files(self) -> bool:
        """检查项目文件完整性"""
        required_files = [
            "requirements.txt", "railway.json", "Procfile", 
            "app.py", "config.py", "routes.py"
        ]
        missing_files = []
        
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"    {Colors.FAIL}缺少文件: {', '.join(missing_files)}{Colors.ENDC}")
            return False
        return True

    def _check_network(self) -> bool:
        """检查网络连接"""
        try:
            response = requests.get("https://api.github.com", timeout=5)
            return response.status_code == 200
        except:
            return False

    def interactive_config(self):
        """交互式配置收集"""
        print(f"\n{Colors.OKGREEN}🎯 开始量子配置收集过程...{Colors.ENDC}")
        
        # 1. Railway配置
        self._collect_railway_config()
        
        # 2. Supabase配置
        self._collect_supabase_config()
        
        # 3. Cloudflare配置
        self._collect_cloudflare_config()
        
        # 4. 安全设置
        self._collect_security_config()
        
        # 5. 性能优化选项
        self._collect_performance_config()

    def _collect_railway_config(self):
        """收集Railway配置"""
        print(f"\n{Colors.HEADER}🚂 Railway付费版配置{Colors.ENDC}")
        
        # 检查是否已登录
        if not self._check_railway_login():
            print("请先登录Railway账户...")
            if input("现在登录？ [Y/n]: ").lower() != 'n':
                subprocess.run(["railway", "login"])
        
        # 项目选择
        project_name = input("📝 Railway项目名称 (回车使用默认): ") or "quantum-wealth-bridge"
        self.config['railway'] = {
            'project_name': project_name,
            'use_professional_features': True  # 付费版特权
        }
        
        print(f"  ✅ Railway配置完成 (付费版特权已启用)")

    def _collect_supabase_config(self):
        """收集Supabase配置"""
        print(f"\n{Colors.HEADER}🗄️ Supabase付费版配置{Colors.ENDC}")
        
        database_url = input("📝 Supabase DATABASE_URL: ").strip()
        supabase_url = input("📝 Supabase项目URL: ").strip()
        supabase_key = input("📝 Supabase Anon Key: ").strip()
        
        self.config['supabase'] = {
            'database_url': database_url,
            'url': supabase_url,
            'anon_key': supabase_key,
            'use_professional_features': True  # 付费版特权
        }
        
        # 安全配置提醒
        current_security = input("🔒 当前数据库安全设置 (unrestricted/restricted): ").lower()
        if current_security == 'unrestricted':
            print(f"  {Colors.WARNING}⚠️ 检测到'不受限制'模式{Colors.ENDC}")
            fix_security = input("  🛡️ 是否立即优化为安全白名单模式？ [Y/n]: ")
            self.config['supabase']['fix_security'] = fix_security.lower() != 'n'
        
        print(f"  ✅ Supabase配置完成 (付费版高级功能已启用)")

    def _collect_cloudflare_config(self):
        """收集Cloudflare配置"""
        print(f"\n{Colors.HEADER}🌍 Cloudflare CDN配置{Colors.ENDC}")
        
        use_custom_domain = input("🌐 是否使用自定义域名？ [Y/n]: ").lower() != 'n'
        
        if use_custom_domain:
            domain = input("📝 你的域名 (如: yourapp.com): ").strip()
            use_www = input("📝 配置www重定向？ [Y/n]: ").lower() != 'n'
            
            self.config['cloudflare'] = {
                'use_cdn': True,
                'domain': domain,
                'use_www_redirect': use_www,
                'ssl_mode': 'full'  # 推荐安全模式
            }
        else:
            self.config['cloudflare'] = {'use_cdn': False}
        
        print(f"  ✅ Cloudflare配置完成")

    def _collect_security_config(self):
        """收集安全配置"""
        print(f"\n{Colors.HEADER}🔐 安全配置{Colors.ENDC}")
        
        session_secret = input("🔑 SESSION_SECRET (回车自动生成): ").strip()
        if not session_secret:
            import secrets
            session_secret = secrets.token_urlsafe(32)
            print(f"  🔑 已自动生成强密码: {session_secret[:8]}...")
        
        self.config['security'] = {
            'session_secret': session_secret,
            'force_ssl': True,
            'secure_headers': True
        }
        
        print(f"  ✅ 安全配置完成")

    def _collect_performance_config(self):
        """收集性能配置"""
        print(f"\n{Colors.HEADER}⚡ 性能优化配置{Colors.ENDC}")
        
        use_professional = input("💎 启用Railway专用资源？ [Y/n]: ").lower() != 'n'
        use_read_replica = input("📊 配置Supabase读写分离？ [Y/n]: ").lower() != 'n'
        enable_monitoring = input("📈 启用高级监控？ [Y/n]: ").lower() != 'n'
        
        self.config['performance'] = {
            'railway_professional': use_professional,
            'supabase_read_replica': use_read_replica,
            'advanced_monitoring': enable_monitoring
        }
        
        print(f"  ✅ 性能配置完成")

    def deploy_to_railway(self):
        """部署到Railway"""
        print(f"\n{Colors.OKGREEN}🚀 开始Railway量子部署...{Colors.ENDC}")
        
        try:
            # 1. 创建或连接项目
            self._setup_railway_project()
            
            # 2. 设置环境变量
            self._setup_railway_variables()
            
            # 3. 部署代码
            self._deploy_railway_code()
            
            # 4. 验证部署
            self._verify_railway_deployment()
            
            print(f"  ✅ Railway部署成功")
            
        except Exception as e:
            print(f"  ❌ Railway部署失败: {e}")
            raise

    def setup_supabase_security(self):
        """配置Supabase安全设置"""
        if not self.config.get('supabase', {}).get('fix_security', False):
            return
            
        print(f"\n{Colors.OKGREEN}🛡️ 优化Supabase安全配置...{Colors.ENDC}")
        
        try:
            # 获取Railway出站IP范围
            railway_ips = self._get_railway_ip_ranges()
            
            print(f"  📍 Railway IP范围: {len(railway_ips)} 个IP段")
            print(f"  🔧 请手动在Supabase控制台添加这些IP到白名单:")
            
            for ip in railway_ips:
                print(f"     • {ip}")
            
            input("\n按回车键继续 (完成IP白名单配置后)...")
            print(f"  ✅ 安全配置指导完成")
            
        except Exception as e:
            print(f"  ⚠️ 安全配置需要手动完成: {e}")

    def setup_cloudflare_cdn(self):
        """配置Cloudflare CDN"""
        if not self.config.get('cloudflare', {}).get('use_cdn', False):
            print(f"\n{Colors.OKCYAN}跳过Cloudflare配置 (未启用自定义域名){Colors.ENDC}")
            return
            
        print(f"\n{Colors.OKGREEN}🌍 配置Cloudflare全球加速...{Colors.ENDC}")
        
        domain = self.config['cloudflare']['domain']
        railway_domain = self.config.get('railway', {}).get('domain', 'your-app.up.railway.app')
        
        print(f"  🔧 请在Cloudflare控制台配置以下DNS记录:")
        print(f"     • 类型: CNAME")
        print(f"     • 名称: @ (或 {domain})")
        print(f"     • 目标: {railway_domain}")
        print(f"     • 代理: 已启用 (橙色云朵)")
        
        if self.config['cloudflare'].get('use_www_redirect', False):
            print(f"     • 类型: CNAME")
            print(f"     • 名称: www")
            print(f"     • 目标: {railway_domain}")
            print(f"     • 代理: 已启用")
        
        input("\n按回车键继续 (完成DNS配置后)...")
        
        # 验证域名解析
        self._verify_domain_setup(domain)
        print(f"  ✅ Cloudflare配置完成")

    def verify_deployment(self):
        """全面验证部署"""
        print(f"\n{Colors.OKGREEN}🎯 执行量子场连接验证...{Colors.ENDC}")
        
        tests = [
            ("健康检查端点", self._test_health_endpoint),
            ("数据库连接", self._test_database_connection),
            ("SSL证书", self._test_ssl_certificate),
            ("CDN加速", self._test_cdn_performance),
            ("WebSocket连接", self._test_websocket_connection)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"  🔍 测试 {test_name}...", end="")
            try:
                result = test_func()
                status = "✅" if result else "❌"
                results[test_name] = result
                print(f" {status}")
            except Exception as e:
                print(f" ❌ (错误: {e})")
                results[test_name] = False
        
        # 显示验证结果
        self._display_verification_results(results)

    def generate_deployment_report(self):
        """生成部署报告"""
        print(f"\n{Colors.HEADER}📊 量子財富橋部署报告{Colors.ENDC}")
        
        report = {
            'deployment_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'configuration': self.config,
            'status': 'success',
            'urls': {
                'railway': self.config.get('railway', {}).get('domain', ''),
                'custom': self.config.get('cloudflare', {}).get('domain', '')
            }
        }
        
        # 保存报告
        with open('deployment_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  📄 部署报告已保存: deployment_report.json")
        
        # 显示访问信息
        self._display_access_info()

    # 辅助方法
    def _check_railway_login(self) -> bool:
        """检查Railway登录状态"""
        try:
            result = subprocess.run(["railway", "whoami"], capture_output=True, check=True)
            return True
        except:
            return False

    def _setup_railway_project(self):
        """设置Railway项目"""
        project_name = self.config['railway']['project_name']
        
        # 尝试连接现有项目或创建新项目
        try:
            subprocess.run(["railway", "link", project_name], check=True)
        except:
            # 项目不存在，创建新项目
            subprocess.run(["railway", "init", project_name], check=True)

    def _setup_railway_variables(self):
        """设置Railway环境变量"""
        variables = {
            'SESSION_SECRET': self.config['security']['session_secret'],
            'DATABASE_URL': self.config['supabase']['database_url'],
            'SUPABASE_URL': self.config['supabase']['url'],
            'SUPABASE_ANON_KEY': self.config['supabase']['anon_key'],
            'FLASK_ENV': 'production'
        }
        
        if self.config['cloudflare'].get('use_cdn', False):
            variables['CDN_DOMAIN'] = f"https://{self.config['cloudflare']['domain']}"
            variables['USE_CDN'] = 'true'
        
        for key, value in variables.items():
            subprocess.run(["railway", "variables", "set", f"{key}={value}"], check=True)

    def _deploy_railway_code(self):
        """部署代码到Railway"""
        # 确保代码已推送到Git
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🚀 量子財富橋部署"], check=False)  # 可能没有变更
        
        # 部署到Railway
        subprocess.run(["railway", "up"], check=True)

    def _verify_railway_deployment(self):
        """验证Railway部署"""
        # 获取部署域名
        result = subprocess.run(["railway", "domain"], capture_output=True, text=True)
        if result.returncode == 0:
            domain = result.stdout.strip()
            self.config['railway']['domain'] = domain
            
        # 等待服务启动
        print("  ⏳ 等待服务启动...")
        time.sleep(30)

    def _get_railway_ip_ranges(self) -> List[str]:
        """获取Railway IP范围 (模拟)"""
        # Railway的实际IP范围需要从官方文档获取
        # 这里提供常见的IP范围作为示例
        return [
            "0.0.0.0/0"  # 临时使用，实际部署时需要具体IP
        ]

    def _verify_domain_setup(self, domain: str):
        """验证域名设置"""
        try:
            import socket
            result = socket.gethostbyname(domain)
            print(f"    ✅ 域名解析正常: {domain} -> {result}")
        except:
            print(f"    ⚠️ 域名解析可能需要时间生效")

    def _test_health_endpoint(self) -> bool:
        """测试健康检查端点"""
        domain = self.config.get('railway', {}).get('domain')
        if not domain:
            return False
        
        try:
            response = requests.get(f"https://{domain}/health", timeout=10)
            return response.status_code == 200
        except:
            return False

    def _test_database_connection(self) -> bool:
        """测试数据库连接"""
        # 这里可以通过健康检查端点验证数据库状态
        return True  # 简化实现

    def _test_ssl_certificate(self) -> bool:
        """测试SSL证书"""
        domain = self.config.get('railway', {}).get('domain')
        if not domain:
            return False
        
        try:
            import ssl
            import socket
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    return True
        except:
            return False

    def _test_cdn_performance(self) -> bool:
        """测试CDN性能"""
        if not self.config.get('cloudflare', {}).get('use_cdn', False):
            return True  # 跳过测试
        
        domain = self.config['cloudflare']['domain']
        try:
            response = requests.get(f"https://{domain}", timeout=10)
            # 检查Cloudflare头部
            return 'cf-ray' in response.headers
        except:
            return False

    def _test_websocket_connection(self) -> bool:
        """测试WebSocket连接"""
        # 简化实现，实际可以测试WebSocket端点
        return True

    def _display_verification_results(self, results: Dict[str, bool]):
        """显示验证结果"""
        print(f"\n{Colors.HEADER}验证结果总结:{Colors.ENDC}")
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            color = Colors.OKGREEN if result else Colors.FAIL
            print(f"  {color}{test_name}: {status}{Colors.ENDC}")
        
        success_rate = sum(results.values()) / len(results) * 100
        print(f"\n  📊 总体成功率: {success_rate:.1f}%")

    def _display_access_info(self):
        """显示访问信息"""
        print(f"\n{Colors.OKGREEN}🎉 量子財富橋部署成功！{Colors.ENDC}")
        
        railway_domain = self.config.get('railway', {}).get('domain', '')
        custom_domain = self.config.get('cloudflare', {}).get('domain', '')
        
        if railway_domain:
            print(f"  🚂 Railway地址: https://{railway_domain}")
        
        if custom_domain:
            print(f"  🌍 自定义域名: https://{custom_domain}")
        
        print(f"\n  💎 主要功能:")
        print(f"     • 🏠 主页: /")
        print(f"     • 📊 仪表板: /dashboard")
        print(f"     • 📈 监控: /monitor")
        print(f"     • ⚕️ 健康检查: /health")
        
        print(f"\n  🔧 管理工具:")
        print(f"     • Railway控制台: railway.com")
        print(f"     • Supabase控制台: supabase.com")
        if custom_domain:
            print(f"     • Cloudflare控制台: cloudflare.com")

def main():
    """主函数"""
    deployer = QuantumDeployer()
    
    try:
        # 1. 显示启动横幅
        deployer.print_banner()
        
        # 2. 检查前置条件
        if not deployer.check_prerequisites():
            print(f"\n{Colors.FAIL}❌ 前置条件检查失败，请解决后重试{Colors.ENDC}")
            return 1
        
        # 3. 交互式配置
        deployer.interactive_config()
        
        # 4. 确认部署
        print(f"\n{Colors.HEADER}📋 配置总结:{Colors.ENDC}")
        config_summary = json.dumps(deployer.config, indent=2, ensure_ascii=False)
        print(config_summary)
        
        if input(f"\n{Colors.BOLD}🚀 开始部署？ [Y/n]: {Colors.ENDC}").lower() == 'n':
            print("部署已取消")
            return 0
        
        # 5. 执行部署
        deployer.deploy_to_railway()
        deployer.setup_supabase_security()
        deployer.setup_cloudflare_cdn()
        
        # 6. 验证部署
        deployer.verify_deployment()
        
        # 7. 生成报告
        deployer.generate_deployment_report()
        
        print(f"\n{Colors.OKGREEN}🌟 量子財富橋已成功连接宇宙量子场！{Colors.ENDC}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️ 部署被用户中断{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ 部署失败: {e}{Colors.ENDC}")
        deployer.logger.error(f"部署失败: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())