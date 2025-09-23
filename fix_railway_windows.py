#!/usr/bin/env python3
"""
🔧 Windows Railway CLI 修復工具
專門解決 Windows 系統 Railway CLI 安裝問題
"""

import os
import sys
import subprocess
import requests
import zipfile
from pathlib import Path

def check_system():
    """檢查系統環境"""
    print("🔍 檢查Windows系統環境...")
    
    # 檢查是否為Windows
    if os.name != 'nt':
        print("❌ 此工具僅適用於Windows系統")
        return False
    
    print("✅ Windows系統確認")
    return True

def check_node_npm():
    """檢查Node.js和npm"""
    print("\n📦 檢查Node.js和npm...")
    
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        
        if node_result.returncode == 0 and npm_result.returncode == 0:
            print(f"✅ Node.js: {node_result.stdout.strip()}")
            print(f"✅ npm: {npm_result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js或npm未安裝")
            return False
    except FileNotFoundError:
        print("❌ Node.js或npm未找到")
        return False

def install_nodejs():
    """指導安裝Node.js"""
    print("\n🚀 Node.js安裝指南:")
    print("方法1 (推薦): 使用winget")
    print("  在PowerShell中執行: winget install OpenJS.NodeJS.LTS")
    print("\n方法2: 手動下載")
    print("  訪問: https://nodejs.org")
    print("  下載LTS版本並安裝")
    print("\n安裝後請重新打開命令行窗口")

def install_railway_npm():
    """使用npm安裝Railway CLI"""
    print("\n📡 使用npm安裝Railway CLI...")
    
    try:
        # 安裝Railway CLI
        print("正在執行: npm i -g @railway/cli")
        result = subprocess.run(['npm', 'i', '-g', '@railway/cli'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Railway CLI安裝成功")
            
            # 獲取npm全局目錄
            npm_prefix = subprocess.run(['npm', 'config', 'get', 'prefix'], 
                                      capture_output=True, text=True)
            if npm_prefix.returncode == 0:
                npm_path = npm_prefix.stdout.strip()
                print(f"📁 npm全局目錄: {npm_path}")
                
                # 提示PATH設置
                print(f"\n⚠️  確保以下目錄在PATH中:")
                print(f"   {npm_path}")
                if os.name == 'nt':
                    print(f"   {os.path.join(npm_path, 'node_modules', '.bin')}")
            
            return True
        else:
            print(f"❌ npm安裝失败: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ npm命令未找到，請先安裝Node.js")
        return False

def download_railway_binary():
    """直接下載Railway二進制文件"""
    print("\n💾 下載Railway二進制文件...")
    
    try:
        # 創建工具目錄
        tools_dir = Path("C:/Tools/Railway")
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        # 下載Railway.exe
        print("正在從GitHub下載Railway CLI...")
        download_url = "https://github.com/railwayapp/cli/releases/latest/download/railway_windows_amd64.zip"
        
        response = requests.get(download_url)
        zip_path = tools_dir / "railway.zip"
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # 解壓
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tools_dir)
        
        # 清理
        zip_path.unlink()
        
        exe_path = tools_dir / "railway.exe"
        if exe_path.exists():
            print(f"✅ Railway.exe下載到: {exe_path}")
            print(f"\n⚠️  請將以下目錄添加到PATH:")
            print(f"   {tools_dir}")
            return True
        else:
            print("❌ Railway.exe未找到")
            return False
            
    except Exception as e:
        print(f"❌ 下載失败: {e}")
        return False

def check_railway():
    """檢查Railway CLI是否可用"""
    print("\n🔍 測試Railway CLI...")
    
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI可用: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI測試失敗")
            return False
    except FileNotFoundError:
        print("❌ Railway命令未找到")
        return False

def test_npx_railway():
    """測試使用npx運行Railway"""
    print("\n🧪 測試npx方式...")
    
    try:
        result = subprocess.run(['npx', '@railway/cli@latest', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npx方式可用: {result.stdout.strip()}")
            print("\n💡 如果PATH設置有問題，可以臨時使用:")
            print("   npx @railway/cli@latest login")
            print("   npx @railway/cli@latest up")
            return True
        else:
            print("❌ npx方式也失敗")
            return False
    except FileNotFoundError:
        print("❌ npx命令未找到")
        return False

def show_path_instructions():
    """顯示PATH設置說明"""
    print("""
🔧 Windows PATH 設置說明:

1. 打開「系統內容」:
   - Win + R → 輸入 sysdm.cpl → 確定

2. 點擊「環境變數」

3. 在「使用者變數」中找到「Path」:
   - 選中 → 編輯 → 新增

4. 添加npm目錄 (通常是):
   - %APPDATA%\\npm
   - 或你的npm prefix目錄

5. 確定保存，重新打開命令行

🚀 或者使用PowerShell一鍵設置:
   setx PATH "%PATH%;%APPDATA%\\npm"
""")

def main():
    """主程序"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              🔧 Windows Railway CLI 修復工具 🔧                  ║
║                    GIGI量子DNA救援系統                           ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # 檢查系統
    if not check_system():
        return 1
    
    # 檢查Node.js
    has_node = check_node_npm()
    
    if has_node:
        # 嘗試npm安裝
        if install_railway_npm():
            if check_railway():
                print("\n🎉 Railway CLI安裝完成並可用！")
                return 0
            else:
                print("\n⚠️  Railway CLI已安裝但PATH可能有問題")
                show_path_instructions()
                test_npx_railway()
        else:
            print("\n⚠️  npm安裝失敗，嘗試二進制下載...")
            download_railway_binary()
    else:
        print("\n⚠️  Node.js未安裝，提供安裝指南...")
        install_nodejs()
        print("\n🔄 安裝Node.js後，請重新運行此工具")
        
        print("\n💡 或者嘗試直接下載二進制文件...")
        download_railway_binary()
    
    # 最終檢查
    if not check_railway():
        test_npx_railway()
    
    print("""
📝 總結:
1. 如果Node.js未安裝 → 先安裝Node.js LTS
2. 如果npm方式失敗 → 檢查PATH設置
3. 如果都不行 → 使用npx臨時方案
4. 最後手段 → 直接下載railway.exe

🚀 修復完成後，重新運行量子财富橋部署脚本！
    """)
    
    return 0

if __name__ == "__main__":
    exit(main())