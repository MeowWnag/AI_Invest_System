import os
import requests
import time
import argparse
import logging

def chunk_list(lst, n):
    """將列表分割成每塊包含 n 個元素的子列表"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def setup_logging():
    """設定日誌記錄"""
    logging.basicConfig(
        filename='process_articles.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def process_file(file_path, api_url, output_dir, max_retries=3):
    """處理單個文件，將其轉換為最簡句子並保存"""
    title = os.path.splitext(os.path.basename(file_path))[0]
    
    # 讀取文件內容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查文件內容是否為空
    if not content.strip():
        logging.info(f"文件內容為空，跳過文件: {file_path}")
        print(f"文件內容為空，跳過文件: {file_path}")
        return
    
    sentences = content.split('。')
    chunks = chunk_list(sentences, 10)
    simplified_sentences = []
    
    for chunk in chunks:
        chunk_str = '。'.join(chunk) + '。' if chunk else ''
        
        payload = {
            "message": f"""請全程用繁體中文回覆我。
最短句子為一個表達知識的最小句子單位，要能獨立表達一個知識，
句子中不可以有代詞，不可以有例如「這些」、「這個」、「你我他」、「當時」等等。
如果知識有時間順序，則將同段時間的知識組合成最短句子，不要將其分開。
如果知識只在特定時間、地點是正確的，要說明出特定時間、地點。
最短句子的詞語要越少越好，所有的最短句子能完整的表達整個文章的知識。
以下是一篇文章，請將此文章轉換成多個能表達此文章主旨的最短句子將這些句子並以換行的方式輸出，且不要有其他修飾符號、數字、標記或者其他無關資訊，不要使用markdown語法。
不要有1. 2. 3.這種列表的數字或其他列表的方式。

這是文章的主旨:
{title}

這是此段文章的內容:
{chunk_str}
""",
            "temperature": 0.5,
            "max_tokens": 512,
            "top_p": 0.8,
            "repeat_penalty": 1.2
        }

        headers = {
            "Content-Type": "application/json"
        }

        retries = 0
        while retries < max_retries:
            start_time = time.time()
            try:
                response = requests.post(api_url, json=payload, headers=headers)
                end_time = time.time()
                response_time = end_time - start_time

                if response.status_code == 200:
                    logging.info(f"API 回應成功 (耗時: {response_time:.2f} 秒) for chunk in {title}")
                    response_content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
                    print('最簡句子:\n')
                    print(response_content)
                    simplified_sentences.append(response_content.strip())
                    break
                else:
                    logging.error(f"API 回應錯誤: {response.status_code}, {response.text} (耗時: {response_time:.2f} 秒) for chunk in {title}")
            except Exception as e:
                logging.error(f"請求時發生錯誤: {e} for chunk in {title}")
            
            retries += 1
            logging.info(f"重試 {retries}/{max_retries} for chunk in {title}")
            time.sleep(2)  # 增加重試間隔

        if retries == max_retries:
            logging.error(f"最大重試次數達到，跳過此塊: {title}")
            continue

        #time.sleep(1)  # 避免過於頻繁的請求

    if not simplified_sentences:
        logging.info(f"沒有收到任何簡化句子，跳過保存文件: {file_path}")
        print(f"沒有收到任何簡化句子，跳過保存文件: {file_path}")
        return

    final_content = '\n'.join(simplified_sentences)
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, f"{title}.txt")

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logging.info(f"已保存簡化後的內容到: {output_file_path}")
    print(f"已保存簡化後的內容到: {output_file_path}")

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="將維基百科條目轉換為最簡句子並保存到指定的資料夾。")
    parser.add_argument('-i', '--input', type=str, default='/home/mewcat/桌面/coding/python/amr parsing/wikiextractor/extracted/AA/output_files', help="輸入資料夾的路徑，包含原始的 .txt 檔案。")
    parser.add_argument('-o', '--output', type=str, default='/home/mewcat/桌面/coding/python/amr parsing/knowledge_graph/knowledge_graph_pipeline/simple_sentences', help="輸出資料夾的路徑，用於保存簡化後的 .txt 檔案。")
    parser.add_argument('-u', '--url', type=str, default="http://localhost:8062/chat", help="API 的 URL，默認為 http://localhost:8062/chat")
    
    args = parser.parse_args()
    
    api_url = args.url
    input_dir = args.input
    output_dir = args.output

    if not os.path.isdir(input_dir):
        logging.error(f"輸入資料夾不存在: {input_dir}")
        print(f"輸入資料夾不存在: {input_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_dir, filename)
            logging.info(f"開始處理文件: {file_path}")
            print(f"處理文件: {file_path}")
            process_file(file_path, api_url, output_dir)

if __name__ == "__main__":
    main()