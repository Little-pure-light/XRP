#!/usr/bin/env python3
"""
🌟 量子財富橋部署脚本 - EXE打包工具 🌟
将交互式部署脚本封装成独立可执行文件

支持：PyInstaller + 自动依赖管理
作者：GIGI量子DNA ✨
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller打包工具"""
    print("🔧 安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['deploy_quantum_bridge.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'requests',
        'urllib3',
        'json',
        'logging',
        'subprocess',
        'socket',
        'ssl',
        'secrets'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QuantumBridge-Deployer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='quantum_icon.ico' if os.path.exists('quantum_icon.ico') else None,
)
'''
    
    with open('quantum_deployer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 配置文件创建成功")

def build_executable():
    """构建可执行文件"""
    print("🚀 开始构建量子財富橋部署器...")
    
    try:
        # 使用spec文件构建
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "quantum_deployer.spec"
        ])
        
        # 检查构建结果
        system = platform.system()
        exe_name = "QuantumBridge-Deployer.exe" if system == "Windows" else "QuantumBridge-Deployer"
        exe_path = Path("dist") / exe_name
        
        if exe_path.exists():
            print(f"✅ 构建成功！")
            print(f"📁 可执行文件位置: {exe_path.absolute()}")
            print(f"💾 文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print("❌ 构建失败，未找到可执行文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def create_installer_script():
    """创建一键安装脚本"""
    system = platform.system()
    
    if system == "Windows":
        installer_content = '''@echo off
title 量子財富橋部署器安装向导
echo.
echo ╔══════════════════════════════════════════════╗
echo ║          🌟 量子財富橋部署器 🌟              ║
echo ║            GIGI量子DNA驱动                   ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 正在安装依赖包...
pip install requests PyInstaller
echo.
echo 正在构建可执行文件...
python build_exe.py
echo.
echo 安装完成！可执行文件位于 dist/ 目录
pause
'''
        with open('install.bat', 'w', encoding='utf-8') as f:
            f.write(installer_content)
        print("✅ Windows安装脚本创建成功: install.bat")
    
    else:  # Linux/macOS
        installer_content = '''#!/bin/bash
echo "╔══════════════════════════════════════════════╗"
echo "║          🌟 量子財富橋部署器 🌟              ║"
echo "║            GIGI量子DNA驱动                   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "正在安装依赖包..."
pip3 install requests PyInstaller
echo ""
echo "正在构建可执行文件..."
python3 build_exe.py
echo ""
echo "安装完成！可执行文件位于 dist/ 目录"
'''
        with open('install.sh', 'w', encoding='utf-8') as f:
            f.write(installer_content)
        os.chmod('install.sh', 0o755)
        print("✅ Linux/macOS安装脚本创建成功: install.sh")

def optimize_executable():
    """优化可执行文件"""
    print("⚡ 正在优化可执行文件...")
    
    # 检查UPX压缩工具
    try:
        subprocess.check_output(["upx", "--version"], stderr=subprocess.DEVNULL)
        upx_available = True
        print("  ✅ UPX压缩可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        upx_available = False
        print("  ⚠️ UPX压缩不可用，跳过压缩优化")
    
    return upx_available

def create_distribution_package():
    """创建分发包"""
    print("📦 创建分发包...")
    
    try:
        import zipfile
        import shutil
        from datetime import datetime
        
        # 创建分发目录
        dist_dir = Path("quantum_bridge_distribution")
        dist_dir.mkdir(exist_ok=True)
        
        # 复制可执行文件
        system = platform.system()
        exe_name = "QuantumBridge-Deployer.exe" if system == "Windows" else "QuantumBridge-Deployer"
        exe_path = Path("dist") / exe_name
        
        if exe_path.exists():
            shutil.copy2(exe_path, dist_dir / exe_name)
        
        # 创建使用说明
        readme_content = f"""
🌟 量子財富橋部署器 🌟
GIGI量子DNA驱动的专业部署工具

📋 使用方法：
1. 双击运行 {exe_name}
2. 按照交互式提示完成配置
3. 享受自动化部署过程

💎 功能特色：
• Railway + Cloudflare + Supabase 三平台集成
• 付费版账户特权自动启用
• 安全配置智能优化
• 实时部署状态监控
• 完整验证与报告生成

🔧 系统要求：
• Windows 10/11 或 Linux/macOS
• 稳定的网络连接
• Railway、Cloudflare、Supabase 账户

📞 技术支持：
• 部署日志：quantum_deploy.log
• 配置报告：deployment_report.json

构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
版本: 1.0.0
"""
        
        with open(dist_dir / "README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # 创建ZIP分发包
        zip_name = f"QuantumBridge-Deployer-{system}-{datetime.now().strftime('%Y%m%d')}.zip"
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in dist_dir.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(dist_dir))
        
        print(f"✅ 分发包创建成功: {zip_name}")
        print(f"📁 包含文件:")
        print(f"   • {exe_name} (部署器主程序)")
        print(f"   • README.txt (使用说明)")
        
        return True
        
    except Exception as e:
        print(f"❌ 分发包创建失败: {e}")
        return False

def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🌟 量子財富橋EXE构建器 🌟                     ║
║                     GIGI量子DNA编译系统                          ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # 检查必要文件
    if not Path("deploy_quantum_bridge.py").exists():
        print("❌ 未找到 deploy_quantum_bridge.py 文件")
        return 1
    
    # 1. 安装PyInstaller
    if not install_pyinstaller():
        return 1
    
    # 2. 创建配置文件
    create_spec_file()
    
    # 3. 优化检查
    optimize_executable()
    
    # 4. 构建可执行文件
    if not build_executable():
        return 1
    
    # 5. 创建安装脚本
    create_installer_script()
    
    # 6. 创建分发包
    create_distribution_package()
    
    print(f"""
🎉 量子財富橋EXE构建完成！

📦 输出文件：
• dist/QuantumBridge-Deployer{"" if platform.system() != "Windows" else ".exe"} (主程序)
• quantum_bridge_distribution/ (分发目录)
• QuantumBridge-Deployer-{platform.system()}-*.zip (分发包)

🚀 使用方法：
• 直接运行EXE文件进行部署
• 或者分发ZIP包给其他用户

💫 GIGI的量子DNA已融入每一个字节！
    """)
    
    return 0

if __name__ == "__main__":
    exit(main())