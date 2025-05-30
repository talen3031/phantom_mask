
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 進容器
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案所有檔案進容器
COPY . .

# 預設執行 Flask 主程式(包括etl.py)
CMD ["sh", "-c", "python etl.py && python app.py"]

