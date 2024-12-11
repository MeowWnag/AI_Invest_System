import csv
import os
from django.shortcuts import render
from datetime import datetime
import stock_chart
import traceback

today_file = datetime.now().strftime('%Y%m%d')
today = datetime.now().strftime('%Y/%m/%d')
# os.path.pardir 到上層目錄
path = os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,'today_stock','stock_data',f'stocks_{today_file}.csv'))


def stock_detail(request, stock_code):
    # 預設股票數據
    stock_data = {
        "stock_name": "股票名稱",
        "stock_code": stock_code,
        "current_price": 0.00,
        "price_change": 0.00,
        "last_update": today,
        "previous_close": 0.00,
        "opening_price": 0.00,
        "high_price": 0.00,
        "low_price": 0.00,
        "current_volume": 0,
        "previous_volume": 0,
    }

    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader)
            for row in reader:
                if row['\ufeffCode'] == str(stock_code):
                    stock_data.update({
                        "stock_name": row['Name'],
                        "stock_code": row['Code'],
                        "current_price": float(row['ClosingPrice']),
                        "price_change": float(row['Change']),
                        "last_update": today,
                        "previous_close": float(row['ClosingPrice']) - float(row['Change']),
                        "opening_price": float(row['OpeningPrice']),
                        "high_price": float(row['HighestPrice']),
                        "low_price": float(row['LowestPrice']),
                        "current_volume": int(float(row['TradeVolume'])),
                        "previous_volume": int(float(row['Transaction'])),
                    })
                    break
    except FileNotFoundError:
        print(f"Error: CSV file not found at {path}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return render(request, 'stockHTML/stock_detail.html', stock_data)

def stock_detail(request, stock_code):
    chart_image = stock_chart.generate_chart()
    return render(request, 'stockHTML/stock_detail.html', {'chart_image': chart_image})
