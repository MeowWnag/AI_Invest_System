import os
import time
import logging
from datetime import datetime
from typing import List

import twstock  # 用於抓取台灣股票資料的套件
import pymongo  # 用於連接和操作 MongoDB 的套件
from apscheduler.schedulers.blocking import BlockingScheduler  # 用於排程工作的套件

# 日誌配置
logging.basicConfig(
    level=logging.INFO,  # 設定日誌等級為 INFO
    format='%(asctime)s - %(levelname)s: %(message)s',  # 日誌格式
    datefmt='%Y-%m-%d %H:%M:%S'  # 日期時間格式
)

class StockCrawler:
    def __init__(self, stock_codes: List[str], mongodb_uri: str):
        """
        初始化股票爬蟲

        :param stock_codes: 股票代碼列表
        :param mongodb_uri: MongoDB 連接 URI
        """
        self.stock_codes = stock_codes
        self.client = pymongo.MongoClient(mongodb_uri)  # 建立 MongoDB 連接
        self.db = self.client['AI_Invest']  # 選擇資料庫（已更改為 AI_Invest）
        self.collection = self.db['Stock_info']  # 選擇集合（表）

    def fetch_stock_info(self, stock_code: str):
        """
        抓取單一股票的即時資訊

        :param stock_code: 股票代碼
        :return: 股票資料字典或 None
        """
        try:
            stock = twstock.Stock(stock_code)  # 建立股票物件
            realtime = twstock.realtime.get(stock_code)  # 取得即時資訊

            if realtime['success'] is False:
                logging.error(f"無法取得 {stock_code} 即時資訊")
                return None

            # 組織股票資料
            stock_data = {
                "Stock_prices": datetime.now(),  # 抓取時間
                "stock_code": stock_code,  # 股票代碼
                "company_name": realtime['info']['name'],  # 公司名稱
                "open_price": float(realtime['realtime']['open']),  # 開盤價
                "high_price": float(realtime['realtime']['high']),  # 最高價
                "low_price": float(realtime['realtime']['low']),  # 最低價
                "close_price": float(realtime['realtime']['latest_trade_price']),  # 最新交易價
                "volume": int(realtime['realtime']['accumulate_trade_volume'])  # 累積交易量
            }

            return stock_data

        except Exception as e:
            logging.error(f"爬取 {stock_code} 失敗: {e}")
            return None

    def crawl_and_save(self):
        """
        爬取所有股票代碼的資訊並儲存到 MongoDB
        """
        logging.info("開始股票資訊爬蟲...")

        for stock_code in self.stock_codes:
            stock_info = self.fetch_stock_info(stock_code)

            if stock_info:
                self.collection.insert_one(stock_info)  # 插入資料到 MongoDB
                logging.info(f"成功爬取並儲存 {stock_code} 股票資訊")

    def close(self):
        """
        關閉 MongoDB 連接
        """
        self.client.close()

def main():
    """
    主函數，設定爬蟲參數和排程
    """
    stock_codes = ['2330']  # 股票代碼列表
    mongodb_uri = "mongodb://localhost:27017/"  # MongoDB 連接 URI

    crawler = StockCrawler(stock_codes, mongodb_uri)  # 初始化股票爬蟲

    scheduler = BlockingScheduler()  # 建立排程器
    scheduler.add_job(
        crawler.crawl_and_save,  # 要執行的函數
        'cron',  # 使用 cron 排程
        day_of_week='mon-fri',  # 每週一到週五
        hour='9-13',  # 上午9點到下午1點
        minute='0'  # 每小時的第0分鐘執行
    )

    try:
        logging.info("股票爬蟲排程已啟動...")
        scheduler.start()  # 啟動排程器
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        crawler.close()  # 關閉爬蟲並釋放資源

if __name__ == "__main__":
    main()