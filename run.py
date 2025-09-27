"""
銀恆 XRP 套利交易系統 - 主啟動檔案
避免循環導入問題的啟動方式
"""
import os
import sys

# 確保能找到所有模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        # 延遲導入以避免循環依賴
        from app import app, db
        
        # 確保數據庫表存在
        with app.app_context():
            db.create_all()
            print("✅ 數據庫初始化完成")
        
        print("🚀 銀恆交易控制中心啟動中...")
        print("📡 Web介面地址: http://127.0.0.1:5000")
        print("⚡ 按 Ctrl+C 停止服務")
        
        # 啟動Flask服務器
        from flask import jsonify

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("🔧 正在嘗試修復...")
        
        # 嘗試修復循環導入
        try:
            import models
            import routes
            from app import app, db
            
            with app.app_context():
                db.create_all()
            
            from flask import jsonify

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

app.run(host='0.0.0.0', port=5000, debug=True)
        except Exception as fix_error:
            print(f"❌ 修復失敗: {fix_error}")
            print("請檢查代碼結構")
    
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)
