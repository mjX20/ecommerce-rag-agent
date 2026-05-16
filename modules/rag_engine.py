import os
from typing import List, Dict
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import RAG_CONFIG, KNOWLEDGE_BASES
from modules.data_loader import DataLoader

class RAGEngine:
    """通用RAG检索引擎，支持多知识库"""
    
    def __init__(self, knowledge_base_name: str):
        """
        初始化RAG引擎
        :param knowledge_base_name: 知识库名称（英文键名，如"mobile_phones"）
        """
        self.kb_name = knowledge_base_name  # 保存英文键名，修复核心错误
        self.kb_config = KNOWLEDGE_BASES[knowledge_base_name]
        self.vector_db_path = self.kb_config["vector_db_path"]
        
        # 初始化嵌入模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name=RAG_CONFIG["embedding_model"],
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CONFIG["chunk_size"],
            chunk_overlap=RAG_CONFIG["chunk_overlap"]
        )
        
        # 加载或创建向量数据库
        self.vector_db = self._init_vector_db()
    
    def _init_vector_db(self) -> Chroma:
        """初始化向量数据库，如果不存在则创建"""
        if os.path.exists(self.vector_db_path):
            print(f"加载现有向量库：{self.vector_db_path}")
            return Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
        else:
            print(f"创建新向量库：{self.vector_db_path}")
            return self._build_vector_db()
    
    def _build_vector_db(self) -> Chroma:
        """从商品数据构建向量数据库"""
        # 修复核心错误：使用英文键名而不是中文名称
        data_loader = DataLoader(self.kb_name)
        products = data_loader.get_all_products()
        
        # 将商品转换为Document对象
        documents = []
        for product in products:
            text = data_loader.get_product_text(product)
            doc = Document(
                page_content=text,
                metadata={
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "brand": product["brand"],
                    "price": product["price"]
                }
            )
            documents.append(doc)
        
        # 分割文本
        splits = self.text_splitter.split_documents(documents)
        
        # 创建向量数据库
        vector_db = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.vector_db_path
        )
        
        print(f"向量库构建完成，共{len(splits)}个文档")
        return vector_db
    
    def search(self, query: str, k: int = None) -> List[Dict]:
        """
        文本检索
        :param query: 查询文本
        :param k: 返回结果数量，默认使用配置值
        :return: 检索到的商品信息列表
        """
        if k is None:
            k = RAG_CONFIG["text_retrieval_k"]
        
        # 检索文档
        docs = self.vector_db.similarity_search(query, k=k)
        
        # 提取商品信息
        data_loader = DataLoader(self.kb_name)
        results = []
        seen_ids = set()
        
        for doc in docs:
            product_id = doc.metadata["product_id"]
            if product_id not in seen_ids:
                product = data_loader.get_product_by_id(product_id)
                if product:
                    results.append(product)
                    seen_ids.add(product_id)
        
        return results
    
    def rebuild_vector_db(self):
        """重建向量数据库（当商品数据更新时调用）"""
        import shutil
        if os.path.exists(self.vector_db_path):
            shutil.rmtree(self.vector_db_path)
        self.vector_db = self._build_vector_db()
        print("向量库重建完成")