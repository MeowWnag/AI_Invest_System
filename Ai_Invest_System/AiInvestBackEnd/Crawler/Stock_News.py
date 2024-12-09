# 抓yahoo股票下方的新聞
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
#import pymongo
from pymongo import MongoClient

stock_dict = {
 '半導體業': ['2330'], 
}

def Ad_block(files):
    # 過濾出包含 <div class='CF'> 的項目
    news = []#只存herf
    turn = True
    for i in files:
        try:
            # 檢查是否包含子元素 <div class='CF'>
            i.find_element(By.CSS_SELECTOR, "div[class = 'Cf']")
            turn = True
        except Exception:
            # 若未找到 <div class='CF'>，跳過該項目
            turn = False
            continue
        if turn:  # 確認找到後加入過濾結果
            a_tag = i.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")
            news.append(href)  # 儲存新聞連結
    #news = news[:10]
    print(news)
    print(len(news))
    return news

# 設定輸出字元編碼
sys.stdout.reconfigure(encoding="UTF-8")

# 防止瀏覽器自動關閉
def get_ChromeOptions(): 
    options = Options()
    options.add_argument('--start_maximized')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-gpu')
    
    options.add_argument('--headless') 
    options.add_argument("--dns-prefetch-disable")
    #options.add_argument('--heanless=new')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")
    #options.add_argument("--incognito")
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-dev-shm-usage")
    #options.add_experimental_option('prefs', {'intl.accept_languages': 'zh-TW'})
    #options.add_argument("--user-data-dir={}".format(os.path.abspath("profile1")))
    return options

driver = webdriver.Chrome(options=get_ChromeOptions())

url = "https://tw.stock.yahoo.com/"
driver.get(url)

# 建立 MongoDB 連接
client = MongoClient("mongodb://localhost:27017/")
db = client["AI_Invest"]
collection = db["Stock_News"]

for category, stocks in stock_dict.items():
        print(category,stocks)
        for stock in stocks:
            print("股票代碼: ",stock)
            stock_number = stock

            # 等待搜索框加載並輸入關鍵字
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ssb-search-input"))
            )
            
            url = f"https://tw.stock.yahoo.com/quote/{stock_number}.TW"
            driver.get(url)

            # 等待搜索結果加載
            time.sleep(3)

            for i in range(2000):
                # 使用 JavaScript 滾動到頁面底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.3)

            # 找到所有的新聞項目
            all_news = driver.find_elements(By.CSS_SELECTOR, "li[class*='js-stream-content Pos(r)']")
            news = Ad_block(all_news)
            print(f"共有 news{len(news)} 則新聞")

            # 保存結果到 MongoDB
            for count in range(len(news)):
                try:
                    # 進入新聞詳細頁面
                    driver.get(news[count])

                    title = driver.find_element(By.CLASS_NAME, "caas-title-wrapper")
                    title_name = driver.find_element(By.TAG_NAME, "h1")
                    print("新聞標題：", title_name.text)
                    print("新聞連結：", news[count])

                    # 等待新聞內容加載
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='caas-body'] p"))
                    )
                    
                    # 新聞來源
                    try:
                        author_div = driver.find_element(By.CLASS_NAME, "caas-attr-item-author")
                        span_tag = author_div.find_element(By.TAG_NAME, "span")
                        print("新聞來源：", span_tag.text)
                        author = span_tag.text
                    except Exception as e:
                        print(f"未爬取到新聞來源: {e}")
                        author = None

                    # 新聞發布時間
                    try:
                        time_div = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "caas-attr-time-style"))
                        )
                        time_tag = time_div.find_element(By.TAG_NAME, "time")
                        print(f"新聞發布時間: {time_tag.text}")
                        publish_time = time_tag.text
                    except Exception as e:
                        print(f"未爬取到新聞發布時間: {e}")
                        publish_time = None

                    # 抓取新聞內容
                    print("新聞文章：")
                    paragraphs = driver.find_elements(By.CSS_SELECTOR, "div[class*='caas-body'] p")
                    content = "\n".join([p.text for p in paragraphs])
                    print(content)

                    # 準備要插入的文檔
                    news_document = {
                        "Stock_Id": stock_number,
                        "title": title_name.text,
                        "link": news[count],
                        "author": author,
                        "publish_time": publish_time,
                        "content": content
                    }

                    # 插入到 MongoDB
                    collection.insert_one(news_document)
                    print("新聞已儲存到 MongoDB")
                    print("=" * 40)

                except Exception as e:
                    print("處理過程中發生錯誤：", e)

    

# 結束並關閉瀏覽器
driver.quit()