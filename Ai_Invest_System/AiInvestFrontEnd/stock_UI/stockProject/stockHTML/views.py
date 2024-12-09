import csv
import os
from django.shortcuts import render
from datetime import datetime
import traceback

today_file = datetime.now().strftime('%Y%m%d')
today = datetime.now().strftime('%Y/%m/%d')
# os.path.pardir 到上層目錄
path = os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,'today_stock','stock_data',f'stocks_{today_file}.csv'))


def stock_detail(request, stock_code):
    try:
        with open(path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Code'] == str(stock_code):
                    stock_data = {
                        "stock_name": row["Name"],
                        "stock_code": row["Code"],
                        "current_price": float(row["ClosingPrice"]),  # 修改：使用 ClosingPrice
                        "price_change": float(row["Change"]),
                        "opening_price": float(row["OpeningPrice"]),
                        "high_price": float(row["HighestPrice"]),
                        "low_price": float(row["LowestPrice"]),
                        "current_volume": float(row["TradeVolume"]),
                        "transaction": float(row["Transaction"])
                    }
                    print(f"找到股票資料: {stock_data}")
                    return render(request, 'stockHTML/stock_detail.html', stock_data)
            
            print(f"找不到股票代碼 {stock_code} 的資料")
            
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤: {str(e)}")
        print(f"詳細錯誤: {traceback.format_exc()}")
    
    # 如果找不到資料或發生錯誤，返回預設值
    return render(request, 'stockHTML/stock_detail.html', {
        "stock_name": "股票名稱",
        "stock_code": stock_code,
        "current_price": 0.00,
        "price_change": 0.00,
        # ... 其他預設值 ...
    })