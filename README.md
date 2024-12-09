# AI_Invest_System
這是在2024年由**國立高雄師範大學**的 </br> **軟體工程與管理學系**的 **王奕晨**、**張芮綾**、**彭子彧** 發表的畢業專題
### 專題簡介
當前金融市場每天產生大量的財務報告、行業數據和新聞資訊，這些數據為投資者提供了無數的潛在機會。</br>
然而，投資者面臨以下幾個主要挑戰：數據量龐大且碎片化、專業壁壘、時間與效率的壓力。</br>
所以，為了解決這些問題，我們想製作整合「**股票基本面資訊**」、「**財經資訊**」與「**公開財務報表**」三者資訊的私人助理，以幫助投資者更快的應對市場資訊。 </br>
### 專題亮點
- #### 自創的GraphRAG
  由[張芮綾](https://github.com/samttoo22-MewCat)開發的自創GraphRAG，使用**neo4j**、**llama 3 Taiwan 70B**和**HanLP**建構出知識圖譜。</br>
  有別於一般的向量資料庫RAG，圖譜資料庫可以精準分解文章，在RAG上會更加精準與廣泛。
- #### 微調模型
  使用股票基本面投資相關知識，透過LoRA技術微調訓練Breeze 7B Instruct模型，最後用於初步的股票基本面資訊與新聞分析。
- #### 不需額外購買API服務
  所有分析都沒有使用到其他API服務，可以**完全本地運作**，不用擔心資料外洩與長期訂閱造成的金錢損失。
- #### 即時資訊統合
  使用網路爬蟲即時抓取相關資訊，隨時更新最新資訊。
### 系統架構
- #### 圖譜資料處理模組
    詳見路徑Ai_Invest_System/knowledge_graph/knowledge_graph_pipeline/</br>
    其由「**標題**」—「**最簡句子**」—「**關鍵字**」的結構組成。</br>
    「**最簡句子**」的意義在此為「**構成一個知識的最小單位**」</br>
    首先我們使用資料夾中的 1-simple_sentences.py 去使用 llama 3 Taiwan 70B 去分解原始文章為「最簡句子」</br>
    接著使用 2.main.py 去使用 HanLP 去從最簡句子中分解出人事時地物等有關的關鍵字，我們也將維基百科製作成字典提供給 HanLP，為求更精準的分解。 </br>
    最後其會將兩個結果結合成為我們的知識圖譜，其中「關鍵字」可以被不同的「最簡句子」共用，這個設計是為了讓RAG可以跨檔案搜尋。</br></br>
    這是將一篇維基百科條目依照上述方式轉換為知識圖譜的樣子。</br>
    <img src="https://github.com/user-attachments/assets/1b4c0767-8d6e-494f-a9a8-ac8553ab4dd5" width=50% height=50%></br>
    這是一百篇維基百科條目的知識圖譜的樣子。</br>
    <img src="https://github.com/user-attachments/assets/0f2f55b1-71d2-4ede-bfc0-ca6b4a6b25b1" width=50% height=50%></br>

- #### 數據蒐集模組
    負責蒐集外部來源的財務數據和公司相關資訊，並將整理後的數據存入MongoDB資料庫，為後續處理提供基礎資料來源。
- #### 統合模組
    將圖譜資料庫的資訊與微調模型輸出的資訊提供給llama 3 Taiwan 70B，最後整合出給使用者的建議。
- #### 使用者介面模組
    將分析結果以易於理解的方式呈現在前端介面中，方便使用者互動操作。