# 使用官方 Python 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統必要套件
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有程式碼
COPY . .

# Railway 會自動提供 PORT 環境變數
ENV PORT=5000

# 啟動指令，用 gunicorn 啟動 Flask
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "main:app"]
