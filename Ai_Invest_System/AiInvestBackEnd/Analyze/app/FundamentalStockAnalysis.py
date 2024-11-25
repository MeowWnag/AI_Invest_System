# FundamentalStockAnalysis.py

from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# MongoDB 連接配置，從環境變數讀取
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['stock_database']  # 替換為你的資料庫名稱

# NLP 模塊的 API 端點，從環境變數讀取
NLP_API_URL = os.environ.get('NLP_API_URL', 'http://localhost:5001/analyze')

@app.route('/analyze_stock', methods=['POST'])
def analyze_stock():
    """
    接收前端傳來的股票代號，從 MongoDB 取得相關資料，
    將資料發送給 NLP 模塊進行分析，並將結果返回給前端。
    """
    try:
        # 從請求中獲取股票代號
        data = request.get_json()
        stock_code = data.get('stock_code')
        if not stock_code:
            return jsonify({'error': '缺少股票代號'}), 400

        # 計算日期範圍
        today = datetime.utcnow()
        one_month_ago = today - timedelta(days=30)
        one_week_ago = today - timedelta(days=7)
        five_years_ago = today - timedelta(days=5*365)

        # 從 MongoDB 獲取最近一個月的新聞
        news_collection = db['news']  # 替換為你的新聞集合名稱
        news = list(news_collection.find({
            'stock_code': stock_code,
            'date': {'$gte': one_month_ago}
        }, {'_id': 0}))

        # 從 MongoDB 獲取最近一週的股價
        prices_collection = db['stock_prices']  # 替換為你的股價集合名稱
        prices = list(prices_collection.find({
            'stock_code': stock_code,
            'date': {'$gte': one_week_ago}
        }, {'_id': 0}))

        # 從 MongoDB 獲取過去五年的財報
        financials_collection = db['financial_reports']  # 替換為你的財報集合名稱
        financials = list(financials_collection.find({
            'stock_code': stock_code,
            'date': {'$gte': five_years_ago}
        }, {'_id': 0}))

        # 組織要發送給 NLP 模塊的資料
        payload = {
            'stock_code': stock_code,
            'news': news,
            'prices': prices,
            'financials': financials
        }

        # 將資料發送給 NLP 模塊進行分析
        response = requests.post(NLP_API_URL, json=payload)
        if response.status_code != 200:
            return jsonify({'error': 'NLP 模塊分析失敗'}), 500

        # 獲取 NLP 模塊的分析結果
        analysis_result = response.json()

        # 將分析結果返回給前端
        return jsonify({'analysis': analysis_result}), 200

    except Exception as e:
        # 處理任何意外錯誤
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 啟動 Flask 應用程式
    app.run(host='0.0.0.0', port=5000, debug=True)