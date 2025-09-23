#!/usr/bin/env node
/**
 * 🌟 量子財富橋 - GitHub上傳器 🌟
 * GIGI量子DNA驅動的專業GitHub部署系統
 */

import { Octokit } from '@octokit/rest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let connectionSettings;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found for repl/depl');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=github',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('GitHub not connected');
  }
  return accessToken;
}

// WARNING: Never cache this client.
// Access tokens expire, so a new client must be created each time.
// Always call this function again to get a fresh client.
async function getUncachableGitHubClient() {
  const accessToken = await getAccessToken();
  return new Octokit({ auth: accessToken });
}

// 要上傳的文件列表
const filesToUpload = [
  // 核心部署文件
  'deploy_quantum_bridge.py',
  'build_exe.py',
  'create_download_package.py',
  
  // Flask應用文件
  'app.py',
  'main.py',
  'config.py',
  'routes.py', 
  'models.py',
  
  // 配置文件
  'requirements.txt',
  'requirements_exe.txt',
  'railway.json',
  'Procfile',
  'runtime.txt',
  'pyproject.toml',
  
  // 項目文檔
  'replit.md',
  
  // 前端資源
  'templates/base.html',
  'templates/dashboard.html',
  'templates/monitor.html',
  'templates/config.html',
  'static/css/trading.css',
  'static/js/dashboard.js',
  'static/js/monitor.js',
  'static/js/charts.js',
  
  // 核心模組
  'core/price_monitor.py',
  'core/balance_manager.py',
  'core/risk_controller.py',
  'core/profit_analyzer.py',
  'core/data_logger.py',
  'core/order_manager.py',
  'core/mexc_connector.py',
  'core/api_connector.py',
  'core/config_manager.py',
  'core/security_manager.py',
  'core/latency_optimizer.py',
  'core/advanced_analytics.py'
];

async function encodeFileContent(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return Buffer.from(content).toString('base64');
  } catch (error) {
    console.log(`⚠️  無法讀取文件: ${filePath} - ${error.message}`);
    return null;
  }
}

async function createRepository(octokit, repoName) {
  console.log(`🔧 創建GitHub倉庫: ${repoName}...`);
  
  try {
    const response = await octokit.repos.createForAuthenticatedUser({
      name: repoName,
      description: '🌟 量子財富橋 - GIGI量子DNA驅動的XRP套利交易系統 | Railway + Cloudflare + Supabase三平台集成部署',
      private: false,
      auto_init: true,
      license_template: 'mit'
    });
    
    console.log(`✅ 倉庫創建成功: ${response.data.html_url}`);
    return response.data;
  } catch (error) {
    if (error.status === 422) {
      console.log(`📁 倉庫 ${repoName} 已存在，將使用現有倉庫`);
      const response = await octokit.repos.get({
        owner: (await octokit.users.getAuthenticated()).data.login,
        repo: repoName
      });
      return response.data;
    }
    throw error;
  }
}

async function uploadFile(octokit, owner, repo, filePath, githubPath) {
  const content = await encodeFileContent(filePath);
  if (!content) return false;
  
  try {
    // 檢查文件是否已存在
    let sha;
    try {
      const existing = await octokit.repos.getContent({
        owner,
        repo,
        path: githubPath
      });
      sha = existing.data.sha;
    } catch (error) {
      // 文件不存在，沒問題
    }
    
    await octokit.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: githubPath,
      message: `🌟 量子DNA更新: ${githubPath}`,
      content,
      sha
    });
    
    console.log(`  ✅ ${githubPath}`);
    return true;
  } catch (error) {
    console.log(`  ❌ ${githubPath} - ${error.message}`);
    return false;
  }
}

async function createReadme(octokit, owner, repo) {
  const readmeContent = `# 🌟 量子財富橋 (Quantum Wealth Bridge)

*GIGI量子DNA驅動的專業XRP套利交易系統*

## 🚀 系統特色

### 💎 核心功能
- **智能套利引擎**: 監控XRP/USDT和XRP/USDC價差，自動執行獲利交易
- **三平台集成**: Railway + Cloudflare + Supabase完整部署架構
- **風險管控**: 多層次安全機制，最小化交易風險
- **實時監控**: Web界面實時顯示價格、余額、交易狀態

### 🔧 技術架構
- **後端**: Flask + SQLAlchemy + PostgreSQL
- **前端**: Bootstrap 5 + Chart.js響應式界面
- **部署**: 一鍵自動化部署到Railway平台
- **安全**: 企業級密鑰管理和SSL配置

## 📦 快速部署

### 方法一：交互式部署器
\`\`\`bash
python deploy_quantum_bridge.py
\`\`\`

### 方法二：EXE一鍵部署
\`\`\`bash
python build_exe.py
./dist/QuantumBridge-Deployer
\`\`\`

### 方法三：手動部署
1. 配置環境變量
2. 安裝依賴: \`pip install -r requirements.txt\`
3. 運行應用: \`gunicorn --bind 0.0.0.0:5000 main:app\`

## 🌐 在線演示

部署成功後，訪問你的Railway應用URL查看：
- 📊 實時交易面板
- 📈 價格監控圖表
- ⚙️ 系統配置界面
- 📋 交易記錄分析

## 🔐 環境要求

### 必需賬戶
- Railway (生產部署)
- Cloudflare (CDN加速)
- Supabase (數據庫)

### 系統要求
- Python 3.11+
- PostgreSQL數據庫
- 穩定網絡連接

## 📚 項目結構

\`\`\`
quantum-wealth-bridge/
├── deploy_quantum_bridge.py    # 一鍵部署腳本
├── build_exe.py               # EXE打包工具
├── app.py                     # Flask應用主文件
├── config.py                  # 配置管理
├── routes.py                  # 路由處理
├── models.py                  # 數據模型
├── core/                      # 核心交易引擎
│   ├── price_monitor.py       # 價格監控
│   ├── balance_manager.py     # 余額管理
│   ├── risk_controller.py     # 風險控制
│   └── profit_analyzer.py     # 利潤分析
├── templates/                 # HTML模板
├── static/                    # 靜態資源
└── requirements.txt           # Python依賴
\`\`\`

## 🎯 使用指南

### 1. 系統配置
在Web界面中設置：
- 價差閾值 (建議 0.005-0.02)
- 交易金額 (建議從小額開始)
- 風險參數 (保守設置)

### 2. 監控面板
- 實時價格顯示
- 套利機會檢測
- 余額變化追蹤
- 交易執行狀態

### 3. 風險管理
- 每日交易限額
- 余額安全邊際
- 市場波動監控
- 自動停損機制

## 💡 最佳實踐

1. **起始設置**: 從小額測試開始
2. **監控頻率**: 保持適度監控，避免過度交易
3. **風險控制**: 設置合理的停損和限額
4. **數據分析**: 定期查看交易報告優化策略

## 🔧 技術支持

### 日誌文件
- \`quantum_deploy.log\` - 部署日誌
- \`trading_system.log\` - 交易系統日誌
- \`deployment_report.json\` - 配置報告

### 故障排除
1. 檢查網絡連接
2. 驗證API密鑰配置
3. 查看系統日誌
4. 重啟交易引擎

## 📄 開源協議

MIT License - 自由使用和修改

## 🙏 致謝

感謝GIGI量子DNA的智慧指導，讓這個項目從構想變為現實。

---

*🌟 量子財富，智慧橋樑 | GIGI量子DNA驅動 🌟*`;

  const content = Buffer.from(readmeContent).toString('base64');
  
  try {
    // 檢查README是否已存在
    let sha;
    try {
      const existing = await octokit.repos.getContent({
        owner,
        repo,
        path: 'README.md'
      });
      sha = existing.data.sha;
    } catch (error) {
      // README不存在，沒問題
    }
    
    await octokit.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: 'README.md',
      message: '🌟 量子財富橋 - 專業README文檔',
      content,
      sha
    });
    
    console.log('  ✅ README.md');
  } catch (error) {
    console.log(`  ❌ README.md - ${error.message}`);
  }
}

async function main() {
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║                    🌟 量子財富橋GitHub上傳器 🌟                  ║
║                     GIGI量子DNA驅動系統                          ║
╚══════════════════════════════════════════════════════════════════╝
  `);
  
  try {
    // 獲取GitHub客戶端
    const octokit = await getUncachableGitHubClient();
    const user = await octokit.users.getAuthenticated();
    console.log(`🔐 已連接GitHub用戶: ${user.data.login}`);
    
    // 創建倉庫
    const repoName = 'quantum-wealth-bridge';
    const repo = await createRepository(octokit, repoName);
    const owner = user.data.login;
    
    console.log(`\n📤 開始上傳文件到 ${owner}/${repoName}...`);
    
    let successCount = 0;
    let totalCount = 0;
    
    // 上傳所有文件
    for (const filePath of filesToUpload) {
      if (fs.existsSync(filePath)) {
        totalCount++;
        const success = await uploadFile(octokit, owner, repoName, filePath, filePath);
        if (success) successCount++;
      }
    }
    
    // 創建README
    console.log(`\n📝 創建README文檔...`);
    await createReadme(octokit, owner, repoName);
    
    // 完成報告
    console.log(`
╔══════════════════════════════════════════════════════════════════╗
║                    🎉 量子財富橋上傳完成！ 🎉                    ║
╚══════════════════════════════════════════════════════════════════╝

📊 上傳統計:
  ✅ 成功: ${successCount}/${totalCount} 個文件
  🔗 倉庫地址: ${repo.html_url}
  📁 克隆命令: git clone ${repo.clone_url}

🌟 量子橋樑已重新搭建！
💎 GIGI的量子DNA已注入每一行代碼！

🚀 下一步操作:
1. 訪問倉庫查看所有文件
2. 使用部署腳本進行生產部署
3. 開始你的量子財富之旅！
    `);
    
  } catch (error) {
    console.error(`❌ 上傳過程出錯: ${error.message}`);
    process.exit(1);
  }
}

main().catch(console.error);