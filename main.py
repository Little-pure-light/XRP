from app import app

if __name__ == "__main__":
    # 本地開發時才啟動 Flask
    # Railway 會用 Procfile 裡的 gunicorn 啟動，不需要這行
    app.run(debug=True)
