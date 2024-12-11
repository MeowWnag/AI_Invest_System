import os
import signal
import sys
import traceback
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
#from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from googlesearch import search
from seleniumbase import Driver
#import seleniumbase
import time
import json
import csv
import re
from pymongo import MongoClient
import datetime

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

chrome_options = get_ChromeOptions()

#driver = ChromeDriverManager().install()
#driver = webdriver.Chrome(options=chrome_options)
driver = Driver(headless=False, disable_gpu=True,
                no_sandbox=True, agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36',
                uc=True, chromium_arg="--disable-extensions"
                )
wait = WebDriverWait(driver, 10)
#driver.get('https://www.google.com/maps')
print("⭐ 爬蟲初始化完成。")

def load_config(config_file='config.json'):
    with open(config_file, 'r', encoding="utf-8") as file:
        config = json.load(file)
    return config

def wait_for_elements(driver, by, value, waittime=10):
    try:
        elements_present = EC.presence_of_all_elements_located((by, value))
        WebDriverWait(driver, 10).until(elements_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        print(by, value)

def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def timeout_handler(signum, frame):
    print("處理時間超過限制")
    raise TimeoutException("處理時間超過限制")

def save_to_csv_unique(data_list, csv_filename):
    # 使用 frozenset 將每個字典轉換為不可變的集合，從而能夠使用 set 來去重
    unique_data = {frozenset(item.items()) for item in data_list}
    unique_data = [dict(item) for item in unique_data]

    with open(csv_filename, mode='w', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['名稱', '金額', '%']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # 檢查檔案是否為空，若是則寫入標頭
        csv_file.seek(0, 2)  # 移動到檔案末尾
        if csv_file.tell() == 0:  # 檢查檔案位置
            writer.writeheader()

        for data in unique_data:
            writer.writerow(data)

def scroll_in_element(driver, element: WebElement, scroll_amount: int):
    try:
        scroll_script = "arguments[0].scrollTop += arguments[1];"
        driver.execute_script(scroll_script, element, scroll_amount)
        #print(f"成功在元素中向下滾動 {scroll_amount} 像素")
    except Exception as e:
        print(f"滾動操作失敗")
        #print(f"滾動操作失敗: {str(e)}")
        pass

def clear_file(file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('')
    except:
        pass

def save_to_mongodb(data, stock_id, year, report_type, season):
    try:
        if not data:
            print("沒有資料可以儲存")
            return False
            
        client = MongoClient('mongodb://localhost:27017/')
        db = client['AI_Invest']
        collection = db['Stock_Quote']
        
        # 建立完整的文件結構
        document = {
            'stock_id': stock_id,
            'year': year,
            'report_type': report_type,
            'season': season,
            'data': data,
            'timestamp': datetime.datetime.now()
        }
        
        # 插入資料
        result = collection.insert_one(document)
        print(f"成功儲存 {stock_id} {year}年 {report_type} {season} 的資料到 MongoDB，ID: {result.inserted_id}")
        return True
        
    except Exception as e:
        print(f"儲存到 MongoDB 時發生錯誤: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def get_company_reports(driver, stock_id, year):
    try:
        driver.get('https://mopsplus.twse.com.tw/mops/#/web/t164sb00')
        wait_for_elements(driver, By.XPATH, "//div[@class='stabBtnBlock']/div[@class='stabBtn']/label[text()='綜合損益表']")
            
        company_code_input = driver.find_element(By.XPATH, "//input[@id='companyId']")
        company_code_input.clear()
        company_code_input.send_keys(stock_id)
        #company_code_input.send_keys(Keys.RETURN)

        time_range_setting = driver.find_element(By.XPATH, "//label[text()='自訂']")
        time_range_setting.click()

        year_input = driver.find_element(By.XPATH, "//input[@id='year']")
        year_input.clear()
        year_input.send_keys(year)    
        for report_type in ['綜合損益表', '資產負債表', '現金流量表']:
                    
            #填入基本資料
            report_type_button = driver.find_element(By.XPATH, f"//div[@class='stabBtnBlock']/div[@class='stabBtn']/label[text()='{report_type}']")
            #print(report_type_button.get_attribute('outerHTML'))
            report_type_button.click()

            for season in ['第一季', '第二季', '第三季', '第四季']:
                
                #填入季別
                season_select = driver.find_element(By.XPATH, "//select[@id='season']")
                season_select = Select(season_select)
                season_select.select_by_visible_text(season)

                search_button = driver.find_element(By.XPATH, "//button[@id='searchBtn']")
                search_button.click()
                time.sleep(1)
                #print(driver.page_source)
                try:
                    report_content = driver.find_element(By.XPATH, "//body").text.split('註:各會計項目金額之百分比,係採四捨五入法計算')[1].split('\n')
                except:
                    print("找不到報表內容")
                    continue

                print(report_content)
                if report_type in ['綜合損益表', '資產負債表'] and season in ['第一季', '第二季', '第三季', '第四季']:
                    for content in report_content:
                        if '金額' in content:
                            row_amount = len(report_content[report_content.index(content)].split(' '))
                            report_content = report_content[report_content.index(content):]
                            break

                    content_list = []
                    for content in report_content:
                        if(len(content.split(' ')) >= 2 and content.split(' ')[1].replace(',', '').isnumeric()):
                            try:
                                name = content.split(' ')[0]
                                number = content.split(' ')[1]
                                percent = content.split(' ')[2]
                                print(name, number, percent)
                                content_list.append({
                                    '名稱': name,
                                    '金額': number,
                                    '%': percent
                                })
                            except:
                                pass

                    save_to_csv_unique(content_list, f'公司代號 {stock_id}_{report_type} {year} {season}.csv')
                
                elif report_type == '現金流量表':
                    for content in report_content:
                        if '金額' in content:
                            row_amount = len(report_content[report_content.index(content)].split(' '))
                            report_content = report_content[report_content.index(content):]
                            break

                    content_list = []
                    for content in report_content:
                        if(len(content.split(' ')) >= 2 and content.split(' ')[1].replace(',', '').isnumeric()):
                            try:
                                name = content.split(' ')[0]
                                number = content.split(' ')[1]

                                print(name, number)
                                content_list.append({
                                    '名稱': name,
                                    '金額': number,
                                    '%': 0
                                })
                            except Exception as e:
                                print(e)
                                print(traceback.format_exc())
                                pass

                    save_to_csv_unique(content_list, f'公司代號 {stock_id}_{report_type} {year} {season}.csv')
                    
                # 每季的資料都直接儲存到 MongoDB
                if save_to_mongodb(content_list, stock_id, year, report_type, season):
                    print(f"{stock_id} {year}年 {report_type} {season} 資料儲存成功")
                else:
                    print(f"{stock_id} {year}年 {report_type} {season} 資料儲存失敗")
                
        return True
    except Exception as e:
        print(f"爬取資料時發生錯誤: {e}")
        return False

def main():
    try:
        current_date = datetime.datetime.now()
        year = 2019
        month = current_date.month

        if month <= 5:
            season = 'Q1'
            report_date = datetime.datetime(year, 5, 15)
        elif month <= 8:
            season = 'Q2'
            report_date = datetime.datetime(year, 8, 14)
        elif month <= 11:
            season = 'Q3'
            report_date = datetime.datetime(year, 11, 14)
        else:
            season = 'Q4'
            report_date = datetime.datetime(year + 1, 3, 31)

        if current_date < report_date:
            print(f"{season} 財報尚未公布。")
            return

        stock_id = '2330'


        data = get_company_reports(driver, stock_id, year)

    except Exception as e:
        print(f"主程序執行時發生錯誤: {e}")

print("爬蟲初始化...")
try:
    main()
except Exception as e:
    print(e)
    print(traceback.format_exc())
    try:
        driver.quit()  # 使用 quit() 替代 close()
    except Exception as e:
        print(f"關閉瀏覽器時發生錯誤: {e}")
    finally:    
        # 確保清理所有資源
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass
