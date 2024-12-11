import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

def generate_chart():
    # 示例數據
    data = {'Date': ['2024-12-06', '2024-12-07', '2024-12-08'], 'Price': [33.6, 34.0, 33.8]}
    df = pd.DataFrame(data)

    # 生成圖表
    plt.figure(figsize=(6, 4))
    plt.plot(df['Date'], df['Price'], marker='o')
    plt.title('走勢圖')
    plt.xlabel('日期')
    plt.ylabel('價格')

    # 將圖表保存為字節流並轉換為 base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return image_base64
