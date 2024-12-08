import traceback
from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from datetime import datetime
import os
from bson import ObjectId

app = FastAPI(title="Stock Data API", version="1.0")

# MongoDB 設定
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGODB_URI)

# 選擇單一資料庫 "AI_invest"
db = client['AI_Invest']

# 選擇不同的集合
db_news = db['Stock_News']
db_info = db['Stock_info']
db_quotes = db['Stock_Quote']

# Pydantic 模型
class News(BaseModel):
    id: str = Field(alias="_id")
    title: str
    link: str
    author: str
    publish_time: str
    content: str

class StockInfo(BaseModel):
    id: str = Field(alias="_id")
    Stock_prices: datetime
    open_price: float
    company_name: str
    high_price: float
    low_price: float
    volume: int
    stock_code: str
    close_price: Optional[float] = None

class QuoteData(BaseModel):
    名稱: str
    金額: str
    percent: Union[str, int] = Field(alias="%")

    @validator('percent', pre=True)
    def convert_percent(cls, v):
        if isinstance(v, int):
            return f"{v}%"
        return v

class StockQuotes(BaseModel):
    id: str = Field(alias="_id")
    stock_id: str
    year: int
    report_type: str
    season: str
    data: List[QuoteData]

# Helper 函數
def convert_object_id(data):
    """遞歸地將 MongoDB 結果中的 ObjectId 轉換為字符串"""
    if isinstance(data, list):
        return [convert_object_id(item) for item in data]
    if isinstance(data, dict):
        return {key: str(value) if isinstance(value, ObjectId) else convert_object_id(value) for key, value in data.items()}
    return data

# API 端點
@app.get("/news", response_model=List[News])
async def get_news(
    date: Optional[str] = Query(None, description='發布日期，格式為 "YYYY年MM月DD日"（例如 "2024年11月22日"）'),
    title: Optional[str] = Query(None, description='標題關鍵字，用於模糊搜尋')
):
    query = {}
    if date and date.strip():
        query['publish_time'] = date
    if title and title.strip():
        query['title'] = {'$regex': title, '$options': 'i'}
    try:
        cursor = db_news.find(query)
        results = await cursor.to_list(length=100)  # 限制最多返回100條
        if not results:
            raise HTTPException(status_code=404, detail="沒有找到符合條件的 Stock_News 資料。")
        return convert_object_id(results)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")

def handle_missing_fields(data, default_value=0.0):
    """填補缺失字段的值為默認值"""
    if isinstance(data, list):
        return [handle_missing_fields(item, default_value) for item in data]
    if isinstance(data, dict):
        for field in ['open_price', 'high_price', 'low_price']:
            if field not in data or data[field] is None:
                data[field] = default_value
        return data
    return data

@app.get("/info", response_model=List[StockInfo])
async def get_info(
    stock_code: Optional[str] = Query(None, description='股票代碼（例如 "2330"）'),
    company_name: Optional[str] = Query(None, description='公司名稱，用於模糊搜尋'),
    start_date: Optional[str] = Query(None, description='開始日期，格式為 "YYYY-MM-DD"'),
    end_date: Optional[str] = Query(None, description='結束日期，格式為 "YYYY-MM-DD"')
):
    query = {}
    if stock_code and stock_code.strip():
        query['stock_code'] = stock_code
    if company_name and company_name.strip():
        query['company_name'] = {'$regex': company_name, '$options': 'i'}
    if start_date or end_date:
        query['Stock_prices'] = {}
        if start_date and start_date.strip():
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                query['Stock_prices']['$gte'] = start
            except ValueError:
                raise HTTPException(status_code=400, detail="開始日期格式錯誤，應為 YYYY-MM-DD")
        if end_date and end_date.strip():
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                query['Stock_prices']['$lte'] = end
            except ValueError:
                raise HTTPException(status_code=400, detail="結束日期格式錯誤，應為 YYYY-MM-DD")
    try:
        cursor = db_info.find(query)
        results = await cursor.to_list(length=100)
        if not results:
            raise HTTPException(status_code=404, detail="沒有找到符合條件的 Stock_info 資料。")
        # 填補缺失字段
        results = convert_object_id(results)
        results = handle_missing_fields(results)
        return results
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")

@app.get("/quotes", response_model=List[StockQuotes])
async def get_quotes(
    stock_id: Optional[str] = Query(None, description='股票 ID（例如 "2330"）'),
    year: Optional[int] = Query(None, description='年份（例如 2024）'),
    report_type: Optional[str] = Query(None, description='報告類型（例如 "綜合損益表"）'),
    season: Optional[str] = Query(None, description='季度（例如 "第二季"）')
):
    query = {}
    if stock_id and stock_id.strip():
        query['stock_id'] = stock_id
    if year is not None:
        query['year'] = year
    if report_type and report_type.strip():
        query['report_type'] = {'$regex': report_type, '$options': 'i'}
    if season and season.strip():
        query['season'] = {'$regex': season, '$options': 'i'}
    try:
        cursor = db_quotes.find(query)
        results = await cursor.to_list(length=100)
        if not results:
            raise HTTPException(status_code=404, detail="沒有找到符合條件的 Stock_Quotes 資料。")
        return convert_object_id(results)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="內部伺服器錯誤")