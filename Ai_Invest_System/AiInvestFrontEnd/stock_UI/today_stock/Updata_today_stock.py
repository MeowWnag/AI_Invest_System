import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

today_time = datetime.today().strftime('%Y%m%d')
data_path = "today_stock/stock_data"
# 讀取 CSV 檔案
csv_file = f'{data_path}/stocks_{today_time}.csv' 
df = pd.read_csv(csv_file)
print(f"CSV file path: {csv_file}")

# 讀取現有的 HTML 模板文件
stock_table = 'C:today_stock/today_stock.html'
with open(stock_table, 'r', encoding='utf-8') as file:
    template_content = BeautifulSoup(file, "html.parser")

div = template_content.find("div", class_="stock_table")
print(f"HTML template path: {stock_table}")


# 創建 HTML 表格標題
html_table = '''
    <table class="table table-bordered text-center" id="main_table">
        <thead class="thead_light" style = "position: sticky; top: 10%;background-color:white">
            <tr>
                <th scope="col">加入我的最愛</th>
                <th scope="col">股票名稱/代碼</th>
                <th scope="col">成交金額</th>
                <th scope="col">漲跌</th>
                <th scope="col">開盤</th>
                <th scope="col">昨收</th>
                <th scope="col">最高</th>
                <th scope="col">最低</th>
                <th scope="col">成交量(張)</th>
                <th scope="col">時間</th>
            </tr>
        </thead>
        <tbody>
'''
  
# 遍歷 CSV 資料行並將其轉換為 HTML 表格行
for index, row in df.iterrows():
    html_table += f'''
    <tr>
        <td><input type="checkbox"></td>
        <td>{row['Name']}<br>{row['Code']}.TW</td>
        <td>{row['TradeValue']}</td>
        <td class="{"text-danger" if row['Change'] > 0 else "text-success"}">{row['Change']}</td>
        <td>{row['OpeningPrice']}</td>
        <td>{row['ClosingPrice']}</td>
        <td>{row['HighestPrice']}</td>
        <td>{row['LowestPrice']}</td>
        <td>{row['TradeVolume']}</td>
        <td> {today_time} </td>
    </tr>
    '''

# 完成 HTML 表格結尾
html_table += '''
            </tbody>
        </table>
    </div>
</body>
</html>
'''

if div:
    div.clear()
    div.append(BeautifulSoup(html_table, "html.parser"))
else:
    print("Error: <div class='stock_table'> not found.")




# 儲存更新後的 HTML 到新文件
output_html_file = "today_stock/today_stock.html"
    
# 寫回 HTML 文件
with open("today_stock/today_stock.html", "w", encoding="utf-8") as file:
    file.write(str(template_content))
    
print(f"HTML file has been saved as {output_html_file}")
