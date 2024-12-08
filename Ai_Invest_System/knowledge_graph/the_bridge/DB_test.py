from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def test_mongodb_connection(uri="mongodb://localhost:27017/", db_name="admin"):
    try:
        # 建立 MongoDB 客戶端
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # 設定超時為5秒

        # 嘗試獲取服務器資訊以測試連接
        server_info = client.server_info()  # 這行會觸發連接

        print("成功連接到 MongoDB。服務器版本:", server_info["version"])
        return True
    except ConnectionFailure as e:
        print("無法連接到 MongoDB:", e)
        return False
    except Exception as e:
        print("發生錯誤:", e)
        return False
    finally:
        client.close()

if __name__ == "__main__":
    test_mongodb_connection()