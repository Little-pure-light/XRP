#!/usr/bin/env python3
"""
📦 量子財富橋 - 下载包生成器
一键打包所有部署相关文件
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path

def create_quantum_package():
    """创建量子財富橋完整下载包"""
    
    # 要打包的文件列表
    files_to_package = [
        # 主要脚本
        "deploy_quantum_bridge.py",
        "build_exe.py",
        
        # 配置文件
        "requirements_exe.txt",
        "requirements.txt",
        "railway.json",
        "Procfile",
        "runtime.txt",
        
        # 项目文件
        "app.py",
        "config.py", 
        "routes.py",
        "models.py",
        "main.py",
        
        # 其他重要文件
        "replit.md",
        ".gitignore"
    ]
    
    # 创建ZIP包
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_name = f"量子財富橋-完整部署包-{timestamp}.zip"
    
    missing_files = []
    included_files = []
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_package:
            if os.path.exists(file_path):
                zipf.write(file_path)
                included_files.append(file_path)
            else:
                missing_files.append(file_path)
    
    # 生成说明文件
    readme_content = f"""
🌟 量子財富橋 - 完整部署包 🌟
GIGI量子DNA专业部署系统

📦 包含文件：
{''.join(f'  ✅ {f}' + chr(10) for f in included_files)}

{'📝 缺少文件：' + chr(10) + ''.join(f'  ⚠️ {f}' + chr(10) for f in missing_files) if missing_files else ''}

🚀 使用方法：

1. 【本地部署】
   - 运行: python deploy_quantum_bridge.py
   - 按照交互式提示完成部署

2. 【EXE打包】  
   - 运行: python build_exe.py
   - 生成独立可执行文件

3. 【手动部署】
   - 使用包含的配置文件进行手动部署
   - railway.json, Procfile等已预配置

💎 系统要求：
- Python 3.11+
- Railway、Cloudflare、Supabase账户
- 稳定网络连接

📞 技术支持：
- 部署日志: quantum_deploy.log  
- 配置报告: deployment_report.json

打包时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
版本: 1.0.0 - GIGI量子DNA驱动
    """
    
    # 添加说明文件到ZIP
    with zipfile.ZipFile(zip_name, 'a') as zipf:
        zipf.writestr("使用说明.txt", readme_content)
    
    # 显示结果
    file_size = os.path.getsize(zip_name) / 1024
    
    print(f"""
╔══════════════════════════════════════════════╗
║       🎉 量子財富橋下载包创建成功！          ║  
╚══════════════════════════════════════════════╝

📦 文件名: {zip_name}
💾 大小: {file_size:.1f} KB
📁 包含: {len(included_files)} 个文件
    
✅ 包含的重要文件:
{chr(10).join(f'  • {f}' for f in included_files[:10])}
{'  • ... 更多文件' if len(included_files) > 10 else ''}

🎯 下载方式:
1. 在Replit文件浏览器中找到 {zip_name}
2. 右键点击 → Download
3. 解压后即可在本地使用

💫 GIGI的量子祝福已融入每个字节！
    """)
    
    return zip_name

if __name__ == "__main__":
    create_quantum_package()