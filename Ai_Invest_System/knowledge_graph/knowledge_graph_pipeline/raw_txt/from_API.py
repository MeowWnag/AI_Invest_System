import os
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:6464"  # 替換為實際的 API 基礎 URL

def sanitize_filename(filename):
    """
    清理檔名中的非法字符。
    """
    return "".join(c for c in filename if c.isalnum() or c in " .-_").rstrip()

def save_news_to_txt(news_item):
    """
    將單條新聞儲存為 txt 檔案。
    :param news_item: 單條新聞內容
    """
    title = news_item.get('title', '無標題').strip()
    content = news_item.get('content', '無內容').strip()
    pub_date = news_item.get('date', '未知日期')

    filename = sanitize_filename(title) + ".txt"
    file_content = f"時間: {pub_date}\n\n內容:\n{content}"
    
    # 確保存放新聞的目錄存在
    os.makedirs("news", exist_ok=True)
    filepath = os.path.join("news", filename)
    
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(file_content)
    print(f"已儲存新聞至檔案: {filepath}")

def get_news(title, limit=100):
    """
    遍歷日期抓取包含指定標題的最近新聞，直到收集到目標數量。
    :param title: 新聞標題關鍵字
    :param limit: 需要抓取的新聞數量
    """
    collected_news = []
    date = datetime.today()  # 從今天開始
    while len(collected_news) < limit:
        format_date = date.strftime('%Y-%m-%d')
        endpoint = f"{BASE_URL}/news"
        params = {'date': format_date, 'title': title}
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            news_today = response.json()
            
            # 將符合條件的新聞加入結果中
            if news_today:
                collected_news.extend(news_today)

            print(f"抓取 {format_date} 的新聞，當前已收集 {len(collected_news)} 條")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP 錯誤: {http_err}")
        except Exception as err:
            print(f"其他錯誤: {err}")

        # 減少一天
        date -= timedelta(days=1)

        # 如果收集到的新聞已達到目標數量，截取到目標數量
        if len(collected_news) >= limit:
            collected_news = collected_news[:limit]
            break

    # 儲存新聞到檔案
    for news_item in collected_news:
        save_news_to_txt(news_item)

    # 打印收集到的新聞
    print(f"=== 收集到包含標題 '{title}' 的最近 {len(collected_news)} 條新聞 ===")
    print(json.dumps(collected_news, indent=4, ensure_ascii=False))
    return collected_news

# 使用函數抓取包含「台積電」標題的最近 100 條新聞
get_news("台積電", 100)