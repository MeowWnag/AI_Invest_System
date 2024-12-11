# Import the neo4j dependency
from neo4j import GraphDatabase
from py2neo import Graph, Node, Relationship
from hanlp_pos_zh import get_keywords
import threading

# 創建一個鎖
graph_lock = threading.RLock()

"""
driver = GraphDatabase.driver(
    "neo4j://localhost:7687", 
    auth=("mewcat", "910925as")
)
"""
graph = Graph("bolt://localhost:7687", auth=("neo4j", "910925as"), name="neo4j")
def create_document_node(title):
    with graph_lock:
    
        title_name = title
        title_props = {"title": title_name}
        title_node = Node(f"文章", **title_props)
        graph.create(title_node)

def create_sentence_node(document_title, sentence):
    with graph_lock:
        sentence_node_props = {"sentence": sentence, "document_title": document_title}
        sentence_node = Node("句子", **sentence_node_props)
        graph.create(sentence_node)

def create_doc_sentence_relation():
    with graph_lock:
        # 查詢所有Title和Sentence節點
        documents = graph.nodes.match("文章")
        sentences = graph.nodes.match("句子")

        # 遍歷節點並創建關係
        for document in documents:
            for sentence in sentences:
                if sentence["document_title"] == document["title"]:
                    rel = Relationship(document, "HAS_SENTENCE", sentence)
                    graph.create(rel)

def create_keyword_node(sentence_input):
    with graph_lock:
        keywords = get_keywords(sentence_input)
        sentences = graph.nodes.match("句子")
        for keyword in keywords:
            # 首先檢查關鍵字節點是否已存在
            existing_keyword_nodes = graph.nodes.match("關鍵字", keyword=keyword)
            if existing_keyword_nodes:
                # 如果已存在,則使用現有節點
                keyword_node = existing_keyword_nodes.first()
            else:
                # 否則創建新的關鍵字節點
                keyword_node_props = {"keyword": keyword}
                keyword_node = Node("關鍵字", **keyword_node_props)
                graph.create(keyword_node)
            
            for sentence in sentences:
                if sentence["sentence"] == sentence_input:
                    rel = Relationship(sentence, "HAS_KEYWORD", keyword_node)
                    graph.create(rel)
