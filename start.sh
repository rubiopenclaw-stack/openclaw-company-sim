#!/bin/bash
# OpenClaw 公司模擬器啟動腳本

cd "$(dirname "$0")"

echo "🏢 啟動 OpenClaw 公司模擬器..."
echo ""

# 啟動應用
echo "🚀 啟動中..."
python3 -m streamlit run app.py --server.port 8501 --server.headless true
