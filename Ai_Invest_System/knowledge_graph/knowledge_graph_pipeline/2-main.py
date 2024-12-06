from neo4j_export import create_document_node, create_sentence_node, create_doc_sentence_relation, create_keyword_node
from hanlp_pos_zh import get_keywords
import os
from py2neo import Graph
from neo4j import GraphDatabase
# 連接Neo4j數據庫
graph = Graph("bolt://localhost:7687", auth=("neo4j", "910925as"), name="neo4j")

def create_knowledge_graph():
    for root, dirs, files in os.walk("/home/mewcat/桌面/coding/python/amr parsing/knowledge_graph/knowledge_graph_pipeline/simple_sentences"):
        count = 0
        for file in files:
            file_path = os.path.join(root, file)
            count += 1
            print(count)
            with open(file_path, 'r', encoding='utf-8') as f:
                title = file
                create_document_node(title)
                lines = f.readlines()
                for line in lines:
                    #結合標題和句子
                    line = title + ': ' + line.replace('\n', '')
                    if not(line == ""):
                        create_sentence_node(title, line)
                create_doc_sentence_relation()
                
                for line in lines:
                    #結合標題和句子
                    line = title.replace('.txt', '') + ': ' + line.replace('\n', '')
                    if not(line == ""):
                        create_keyword_node(line)

def get_keywords_in_db(sentence_input):
        query = f"""
        MATCH (s:句子)-[:HAS_KEYWORD]->(k:關鍵字)
        WHERE s.sentence = '{sentence_input}'
        RETURN collect(k.keyword) AS keywords
        """

        # 执行查询并获取结果
        results = graph.run(query).data()
        return results[0]['keywords']
def get_RAG_sentences(user_input, depth: int = 3) -> list:
    searched_keywords = []
    def cypher_query(keywords : list) -> list:
        output = []
        for keyword in keywords:
            # 執行Cypher查詢
            query = f"""
            MATCH (s:句子)-[:HAS_KEYWORD]->(k:關鍵字)
            WHERE k.keyword = '{keyword}'
            RETURN s.sentence
            """

            # 執行查詢並獲取結果
            results = graph.run(query, parameters={"keyword": keyword}).data()

            # 輸出包含關鍵字的句子
            for record in results:
                sentence = record['s.sentence']
                document_query = f"""
                MATCH (d:文章)-[:HAS_SENTENCE]->(s:句子)
                WHERE s.sentence = '{sentence}'
                RETURN d.title
                """
                document_result = graph.run(query, parameters={"sentence": sentence}).data()
                #print(record['s.sentence'])
                output.append(f"{document_result[0]['d.title']}: "+ sentence)
        return output
    
    output = []
    keywords = get_keywords(user_input)
    for keyword in keywords:
        if keyword not in searched_keywords:
            searched_keywords.append(keyword)
    output.append(cypher_query(keywords))

    if depth > 1:
        for d in range(2, depth + 1):
            
            root_search_result = output[d - 2]
            further_depth = []
            for sentence in root_search_result:
                print(f"searched_keywords: {searched_keywords}")
                keywords = get_keywords_in_db(sentence)
                for keyword in keywords:
                    if keyword in searched_keywords:
                        keywords.remove(keyword)
                for keyword in keywords:
                    searched_keywords.append(keyword)
                results = cypher_query(keywords)
                for result in results:
                    further_depth.append(result)
            output.append(further_depth)
    
    # 去除重複
    for i in range(len(output)):
        output[i] = list(set(output[i])) 
    
    return output


user_input = '數學是甚麼?'
create_knowledge_graph()

"""
results = get_RAG_sentences(user_input, depth=1)
for result in results:
    print("-----")
    print(type(result))
    for sentence in result:
        print(sentence)
"""
