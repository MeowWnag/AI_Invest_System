import requests
import time


def chunk_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

# 定义 API 的 URL
url = "http://localhost:8062/chat"
title = '千禧年大獎難題'

content = """千禧年大獎難題（英語：Millennium Prize Problems）是七條由美國的克雷數學研究所（Clay Mathematics Institute，CMI）於2000年5月24日公佈的數學難題[1]，解題總獎金700萬美元。根據克雷數學研究所制定的規則，這系列挑戰不限時間，題解必須發表在知名的國際期刊，並經過各方驗證，只要通過兩年驗證期和專家小組審核，每解破一題可獲獎金100萬美元[2]:153-155。

這些難題旨在呼應1900年德國數學家大衛·希爾伯特在巴黎提出的23個歷史性數學難題[2]:xv，經過一百年，約17條難題至少已局部解答。而千禧年大獎難題的破解，極有可能為密碼學、航天、通訊等領域帶來突破性進展。

迄今為止，在七條問題中，龐加萊猜想是唯一已解決的，2003年，俄羅斯數學家格里戈里·佩雷爾曼證明了它的正確性。而其它六道難題仍有待研究者探索。

緣起與公佈
2000年5月24日，克雷數學研究所在巴黎的法蘭西公學院召開了巴黎千年會議（Paris Millennium Event）[3][4]。百多年前的1900年，德國數學家大衛·希爾伯特宣佈了著名的希爾伯特的23個問題，地點正是在巴黎舉行的第二屆國際數學家大會。在二十世紀，對此系列問題的研究極大地推動了數學的發展[5]。出此考慮，克雷數學研究所決定邀請世界上有影響力的數學家參會，並在會上宣佈二十一世紀須解決的七大數學難題[3]。宣佈這些問題前，當天會議首先播放了1930年希爾伯特退休時演講的錄音，包括他的名言：「我們必須知道，我們必將知道[4]。」隨後，美國數學家約翰·泰特登台，依如下順序宣佈了七條問題中的三條：黎曼猜想、貝赫和斯維訥通-戴爾猜想和P/NP問題，並逐一簡單介紹。之後是英國數學家麥可·阿蒂亞演講，介紹剩下四題，分別是龐加萊猜想、霍奇猜想、楊-米爾斯存在性與質量間隙和納維-斯托克斯存在性與光滑性[3][註 1]。

這七大難題是由克雷數學研究所的科學顧問委員會（Scientific Advisory Board）在諮詢其他頂尖數學家後共同選出[6][7]。小組有五位國際數學專家，領導者是美國數學家、哈佛大學教授亞瑟·賈菲[8]，此外還包括解決了費馬大定理的安德魯·懷爾斯、法國數學家阿蘭·科納、數學物理學家愛德華·威滕，以及上述提及過的約翰·泰特和麥可·阿蒂亞[7]。他們旨在記錄當今數學家面對最難的問題，引起大眾對數學研究的注意，強調為難題尋找答案的重要性[7]。問題甄選完成後，克雷數學研究所董事會撥款七百萬美元，為每條問題設立一百萬美元獎金，並寫出授獎規則[6]。

"""

chunks = chunk_list(content.split('。'), 10)

for chunk in chunks:
    chunk_str = ''
    for sentence in chunk:
        chunk_str += sentence + '。'
    
    print(chunk_str)
    # 定义要发送的消息
    payload = {
        "message": f"""請全程用繁體中文回覆我。
                    最短句子為一個表達知識的最小句子單位，要能獨立表達一個知識，
                    句子中不可以有代詞，不可以有例如「這些」、「這個」、「你我他」、「當時」等等。
                    如果知識有時間順序，則將同段時間的知識組合成最短句子，不要將其分開。
                    如果知識只在特定時間、地點是正確的，要說明出特定時間、地點。
                    最短句子的詞語要越少越好，所有的最短句子能完整的表達整個文章的知識。
                    以下是一篇文章，請將此文章轉換成多個能表達此文章主旨的最短句子將這些句子並以換行的方式輸出，且不要有其他修飾符號、數字、標記或者其他無關資訊，不要使用markdown語法。
                    
                    這是文章的主旨:
                    {title}

                    這是此段文章的內容:
                    {chunk_str}
                    
                    """,
        "tempature": 0.5,
        "max_tokens": 512,
        "top_p": 0.8,
        "repeat_penalty": 1.2
    }

    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }

    # 记录开始时间
    start_time = time.time()

    # 发送 POST 请求到 API
    response = requests.post(url, json=payload, headers=headers)

    # 记录结束时间并计算响应时间
    end_time = time.time()
    response_time = end_time - start_time

    # 打印结果
    if response.status_code == 200:
        print("API 回應成功")
        print("回覆內容:", response.json()['choices'][0]['message']['content'])
        print(f"回應時間: {response_time:.2f} 秒")
    else:
        print("API 回應錯誤")
        print("錯誤訊息:", response.status_code, response.text)
        print(f"回應時間: {response_time:.2f} 秒")