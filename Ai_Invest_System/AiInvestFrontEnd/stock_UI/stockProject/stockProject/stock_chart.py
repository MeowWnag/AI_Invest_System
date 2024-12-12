import os
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_chart(stock_code, max_days=14):
    # 初始化數據列表
    data = []

    # 從今天開始往回讀取文件
    for i in range(max_days):
        # 計算日期
        date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')

        # 構造 CSV 文件路徑
        csv_file_path =os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,'today_stock','stock_data',f'stocks_{date}.csv'))

        # 嘗試讀取 CSV 文件
        try:
            df = pd.read_csv(csv_file_path)

            # 根據股票代碼過濾
            row = df[df['Code'] == str(stock_code)]

            # 如果找到數據，提取日期和 TradeValue
            if not row.empty:
                trade_value = row.iloc[0]['TradeValue']
                data.append({'Date': date, 'TradeValue': trade_value})
        except FileNotFoundError:
            # 缺失文件時跳過
            print(f"File not found: {csv_file_path}")
        except Exception as e:
            print(f"Error reading {csv_file_path}: {e}")

    # 將數據轉為 DataFrame
    chart_data = pd.DataFrame(data)

    # 檢查是否有數據
    if not chart_data.empty:
        # 將日期排序，確保圖表按時間順序顯示
        chart_data = chart_data.sort_values(by='Date')

        print("Chart data:")
        print(chart_data)

        # 使用 Matplotlib 繪製圖表
        plt.figure(figsize=(10, 6))
        plt.plot(chart_data['Date'], chart_data['TradeValue'], marker='o', label=f"TradeValue for {stock_code}")
        plt.title(f"{stock_code} TradeValue Trend (Last {len(chart_data)} Days)", fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('TradeValue', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        print("No data available for the specified range.")

# 示例使用
generate_chart(stock_code='1101')
