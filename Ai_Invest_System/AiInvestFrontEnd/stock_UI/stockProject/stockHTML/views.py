import csv
import os
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse
import traceback

# 檔案路徑設置
today_file = datetime.now().strftime('%Y%m%d')
today = datetime.now().strftime('%Y/%m/%d')
path = os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,'today_stock','stock_data',f'stocks_{today_file}.csv'))
pic_path = os.path.abspath(os.path.join(os.getcwd(),'picture'))


def stock_detail(request, stock_code):
    stock_data = {
        "stock_name": "股票名稱",
        "stock_code": stock_code,
        "current_price": 0.00,
        "price_change": 0.00,
        "opening_price": 0.00,
        "high_price": 0.00,
        "low_price": 0.00,
        "current_volume": 0.00,
        "transaction": 0.00,
        "last_update": today,
    }
    # 預設股票數據
    try:
        with open(path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Code'] == str(stock_code):
                    stock_data.update ({
                        "stock_name": row["Name"],
                        "stock_code": row["Code"],
                        "current_price": float(row["ClosingPrice"]),  # 修改：使用 ClosingPrice
                        "price_change": float(row["Change"]),
                        "opening_price": float(row["OpeningPrice"]),
                        "high_price": float(row["HighestPrice"]),
                        "low_price": float(row["LowestPrice"]),
                        "current_volume": float(row["TradeVolume"]),
                        "transaction": float(row["Transaction"]),
                        "last_update" : today,
                    })
                    # print(f"找到股票資料: {stock_data}")
                    break
                    
            
            # print(f"找不到股票代碼 {stock_code} 的資料")
            
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤: {str(e)}")
        print(f"詳細錯誤: {traceback.format_exc()}")
         # 如果找不到資料或發生錯誤，返回預設值

    try:
        
        # 最近 14 天交易數據
        end_date = datetime.now()
        date_list = [(end_date - timedelta(days=i)).strftime("%Y%m%d") for i in range(14)]
        # print(date_list)
        closingPrices = []
        dates = []

        # 遍歷日期並讀取對應 CSV 文件
        for date in date_list:
            file_name = f"stocks_{date}.csv"
            file_path = os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,'today_stock','stock_data', file_name))
            if os.path.exists(file_path):
                # print(f"路徑存在{file_path}")
                with open(file_path, mode='r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['Code'] == str(stock_code):
                            closingPrices.append(float(row["ClosingPrice"]))
                            dates.append(date)
                            # print(f"找到{file_name},{ClosingPrice},{dates}")
                            break
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤: {str(e)}")
        print(f"詳細錯誤: {traceback.format_exc()}")
        
    # 處理 AJAX 請求
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"dates": dates[::-1], "values": closingPrices[::-1]})

    # 返回頁面渲染
    stock_data["chart_data"] = {"dates": dates[::-1], "values": closingPrices[::-1]}
    return render(request, 'stockHTML/stock_detail.html', stock_data)

#登入   
def login(request):
    return render(request, 'stockHTML/stock_start.html')



def today_stock(request):
    # 初始頁面只顯示前10筆資料
    return render(request, 'stockHTML/today_stock.html')
#建立today_stock_table
def get_today_stock_data(request, page=1):
    # 每頁顯示10筆資料
    PAGE_SIZE = 10
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = page * PAGE_SIZE
    stocks = []
    # 預設股票數據
    try:
        with open(path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            all_rows = list(reader)
            for row in all_rows[start_idx:end_idx]:
                stocks.append ({
                    "stock_name": row["Name"],
                    "stock_code": row["Code"],
                    "current_price": float(row["ClosingPrice"]),  # 修改：使用 ClosingPrice
                    "price_change": float(row["Change"]),
                    "opening_price": float(row["OpeningPrice"]),
                    "high_price": float(row["HighestPrice"]),
                    "low_price": float(row["LowestPrice"]),
                    "current_volume": float(row["TradeVolume"]),
                    "transaction": float(row["Transaction"]),
                    "tradeValue" : float(row["TradeValue"]),
                    "last_update" : today,
                    "stock_color" : "danger" if float(row["Change"]) > 0 else "success"
                })
                

            
    except Exception as e:
        print(f"讀取 CSV 文件時發生錯誤: {e}")
        # 如果出錯，返回空數據
    # 傳遞數據給模板
    #反傳給 AJAX 
    return JsonResponse({"stocks": stocks})

def search_stocks(request):
    search_term = request.GET.get('search', '')  # 獲取搜尋條件
    stocks = []

    try:
        # 打開CSV文件並讀取資料
        with open(path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                stock_name = row["Name"]
                stock_code = row["Code"]
                # 如果名稱或代碼匹配搜尋條件
                if search_term.upper() in stock_name.upper() or search_term.upper() in stock_code.upper():
                    stock_data = {
                        "stock_name": stock_name,
                        "stock_code": stock_code,
                        "current_price": float(row["ClosingPrice"]),  # 修改：使用 ClosingPrice
                        "price_change": float(row["Change"]),
                        "opening_price": float(row["OpeningPrice"]),
                        "high_price": float(row["HighestPrice"]),
                        "low_price": float(row["LowestPrice"]),
                        "current_volume": float(row["TradeVolume"]),
                        "transaction": float(row["Transaction"]),
                        "tradeValue" : float(row["TradeValue"]),
                        "last_update" : today,
                        "stock_color" : "danger" if float(row["Change"]) > 0 else "success"
                    }
                    stocks.append(stock_data)
                    if len(stocks) >= 10:  # 限制為前10筆資料
                        break
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤: {e}")
        return JsonResponse({"error": "資料讀取錯誤"}, status=500)

    # 返回符合條件的股票資料
    return JsonResponse({"stocks": stocks})
