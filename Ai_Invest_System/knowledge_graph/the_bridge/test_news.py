import requests
import json

# 定義 API 的基本 URL
BASE_URL = "http://localhost:6464"

def test_get_news(date=None, title=None):
    """
    測試 /news 端點
    """
    endpoint = f"{BASE_URL}/news"
    params = {}
    if date:
        params['date'] = date
    if title:
        params['title'] = title
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        news = response.json()
        print("=== /news 端點回應 ===")
        print(json.dumps(news, indent=4, ensure_ascii=False))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤: {http_err} - {response.text}")
    except Exception as err:
        print(f"其他錯誤: {err}")

def test_get_info(stock_code=None, company_name=None, start_date=None, end_date=None):
    """
    測試 /info 端點
    """
    endpoint = f"{BASE_URL}/info"
    params = {}
    if stock_code:
        params['stock_code'] = stock_code
    if company_name:
        params['company_name'] = company_name
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        info = response.json()
        print("=== /info 端點回應 ===")
        print(json.dumps(info, indent=4, ensure_ascii=False))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤: {http_err} - {response.text}")
    except Exception as err:
        print(f"其他錯誤: {err}")

def test_get_quotes(stock_id=None, year=None, report_type=None, season=None):
    """
    測試 /quotes 端點
    """
    endpoint = f"{BASE_URL}/quotes"
    params = {}
    if stock_id:
        params['stock_id'] = stock_id
    if year:
        params['year'] = year
    if report_type:
        params['report_type'] = report_type
    if season:
        params['season'] = season
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        quotes = response.json()
        print("=== /quotes 端點回應 ===")
        print(json.dumps(quotes, indent=4, ensure_ascii=False))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤: {http_err} - {response.text}")
    except Exception as err:
        print(f"其他錯誤: {err}")

def test_get_random_info():
    endpoint = f"{BASE_URL}/random_info"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        info = response.json()
        print("=== /random_info 端點回應 ===")
        print(json.dumps(info, indent=4, ensure_ascii=False))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤: {http_err} - {response.text}")
    except Exception as err:
        print(f"其他錯誤: {err}")
        
def test_get_random_quotes():
    endpoint = f"{BASE_URL}/random_quotes"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        quotes = response.json()
        print("=== /random_quotes 端點回應 ===")
        print(json.dumps(quotes, indent=4, ensure_ascii=False))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤: {http_err} - {response.text}")
    except Exception as err:
        print(f"其他錯誤: {err}")
        
def test_get_random_news():
    endpoint = f"{BASE_URL}/random_news"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        news = response.json()
        print("=== /random_news 端點回應 ===")
        print(json.dumps(news, indent=4, ensure_ascii=False))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤: {http_err} - {response.text}")
    except Exception as err:
        print(f"其他錯誤: {err}")

def main():
    # 測試 /news 端點
    print("測試 /news 端點")
    #test_get_news(date="", title="科技")
    print("\n--------------------------------\n")
    
    # 測試 /info 端點
    print("測試 /info 端點")
    #test_get_info(stock_code="2330", company_name="台積電", start_date="2024-01-01", end_date="2024-12-31")
    print("\n--------------------------------\n")
    
    # 測試 /quotes 端點
    print("測試 /quotes 端點")
    test_get_quotes(stock_id="2330", year=2023, report_type="現金流量表", season="第三季")
    print("\n--------------------------------\n")
    
    # 測試 /random_info 端點
    print("測試 /random_info 端點")
    #test_get_random_info()
    print("\n--------------------------------\n")
    
    # 測試 /random_quotes 端點
    print("測試 /random_quotes 端點")
    #test_get_random_quotes()
    print("\n--------------------------------\n")
    
    # 測試 /random_news 端點
    print("測試 /random_news 端點")
    #test_get_random_news()
    print("\n--------------------------------\n")

if __name__ == "__main__":
    main()