from app import app

# 首頁測試用路由
@app.route("/")
def index():
    return "✅ 系統已啟動，伺服器正常運行中！"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
