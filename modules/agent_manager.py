import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from config import LLM_CONFIG, AGENT_CONFIG
from modules.rag_engine import RAGEngine
from modules.image_searcher import ImageSearcher

# 全局缓存：避免重复加载模型和向量库
_AGENT_CACHE = {}

class AgentManager:
    """多Agent管理器，负责协调三个专业Agent的工作"""
    
    @staticmethod
    def get_instance(knowledge_base_name: str):
        """获取指定知识库的AgentManager实例（带缓存）"""
        if knowledge_base_name not in _AGENT_CACHE:
            _AGENT_CACHE[knowledge_base_name] = AgentManager(knowledge_base_name)
        return _AGENT_CACHE[knowledge_base_name]
    
    def __init__(self, knowledge_base_name: str):
        """
        初始化多Agent系统（不要直接调用，使用get_instance()）
        :param knowledge_base_name: 当前激活的知识库名称
        """
        self.kb_name = knowledge_base_name
        
        # 初始化大语言模型
        self.llm = ChatOpenAI(
            api_key=LLM_CONFIG["api_key"],
            base_url=LLM_CONFIG["base_url"],
            model=LLM_CONFIG["model"],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=LLM_CONFIG["max_tokens"]
        )
        
        # 初始化检索引擎
        self.rag_engine = RAGEngine(knowledge_base_name)
        self.image_searcher = ImageSearcher(knowledge_base_name)
        
        # 初始化三个专业Agent
        self.retrieval_agent = RetrievalAgent(self.llm, self.rag_engine, self.image_searcher)
        self.recommendation_agent = RecommendationAgent(self.llm)
        self.comparison_agent = ComparisonAgent(self.llm)
    
    def process_query(self, query: str, image=None, chat_history: List = None) -> Dict:
        """
        处理用户查询，自动分配任务给合适的Agent
        :param query: 用户文本查询
        :param image: 用户上传的图片（PIL Image对象，可选）
        :param chat_history: 对话历史（可选）
        :return: 处理结果，包含回答和推荐商品
        """
        if chat_history is None:
            chat_history = []
        
        # 第一步：信息检索Agent获取相关商品
        retrieval_result = self.retrieval_agent.retrieve(query, image)
        
        if not retrieval_result["products"]:
            return {
                "answer": "抱歉，我没有找到相关的商品信息。请尝试换个关键词搜索。",
                "products": []
            }
        
        # 第二步：判断用户意图，分配给对应Agent
        intent = self._classify_intent(query)
        
        if intent == "comparison":
            # 商品对比意图
            result = self.comparison_agent.compare(retrieval_result["products"], query)
        elif intent == "recommendation":
            # 个性化推荐意图
            result = self.recommendation_agent.recommend(retrieval_result["products"], query, chat_history)
        else:
            # 普通问答意图
            result = self._answer_general_query(retrieval_result["products"], query)
        
        return result
    
    def _classify_intent(self, query: str) -> str:
        """分类用户查询意图"""
        prompt = f"""
        请分析以下用户查询的意图，只能返回以下三个选项中的一个：
        - comparison：用户想要对比多个商品
        - recommendation：用户想要获得个性化推荐
        - general：普通问答，询问商品信息
        
        用户查询：{query}
        
        意图：
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        intent = response.content.strip().lower()
        
        if "comparison" in intent:
            return "comparison"
        elif "recommendation" in intent:
            return "recommendation"
        else:
            return "general"
    
    def _answer_general_query(self, products: List[Dict], query: str) -> Dict:
        """回答普通商品信息查询"""
        products_text = "\n\n".join([
            f"【商品{i+1}】\n{self._get_product_summary(product)}"
            for i, product in enumerate(products)
        ])
        
        prompt = f"""
        你是一个专业的电商导购助手，请根据以下商品信息回答用户的问题。
        要求：
        1. 只使用提供的商品信息，绝对不要编造内容
        2. 回答清晰、简洁、有条理
        3. 突出商品的核心卖点和优势
        4. 如果信息不足，直接说明
        
        商品信息：
        {products_text}
        
        用户问题：{query}
        
        回答：
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "answer": response.content,
            "products": products
        }
    
    def _get_product_summary(self, product: Dict) -> str:
        """获取商品摘要"""
        return f"""
        名称：{product['name']}
        价格：{product['price']}元
        品牌：{product['brand']}
        参数：{product['parameters']}
        描述：{product['description']}
        用户评价：{'；'.join(product['reviews'])}
        """

class RetrievalAgent:
    """信息检索专家，负责从知识库中获取相关商品信息"""
    
    def __init__(self, llm, rag_engine, image_searcher):
        self.llm = llm
        self.rag_engine = rag_engine
        self.image_searcher = image_searcher
    
    def retrieve(self, query: str, image=None) -> Dict:
        """执行多模态检索"""
        products = []
        
        if image is not None:
            # 有图片时优先使用图片检索
            image_results = self.image_searcher.search(image)
            products.extend(image_results)
        
        # 文本检索
        text_results = self.rag_engine.search(query)
        products.extend(text_results)
        
        # 去重
        seen_ids = set()
        unique_products = []
        for product in products:
            if product["id"] not in seen_ids:
                unique_products.append(product)
                seen_ids.add(product["id"])
        
        return {
            "products": unique_products[:5],  # 最多返回5个商品
            "query": query
        }

class RecommendationAgent:
    """个性化推荐专家，负责根据用户需求推荐最合适的商品"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def recommend(self, products: List[Dict], query: str, chat_history: List) -> Dict:
        """生成个性化推荐"""
        products_text = "\n\n".join([
            f"【商品{i+1}】\n{self._get_product_summary(product)}"
            for i, product in enumerate(products)
        ])
        
        prompt = f"""
        你是一个专业的电商推荐专家，请根据以下商品信息和用户需求，给出个性化推荐。
        要求：
        1. 只使用提供的商品信息，绝对不要编造内容
        2. 分析用户的核心需求（预算、用途、偏好等）
        3. 推荐1-3款最合适的商品，并说明推荐理由
        4. 回答清晰、有条理，使用Markdown格式
        5. 最后给出一个明确的购买建议
        
        商品信息：
        {products_text}
        
        用户需求：{query}
        
        推荐：
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "answer": response.content,
            "products": products
        }
    
    def _get_product_summary(self, product: Dict) -> str:
        return f"""
        名称：{product['name']}
        价格：{product['price']}元
        品牌：{product['brand']}
        参数：{product['parameters']}
        描述：{product['description']}
        用户评价：{'；'.join(product['reviews'])}
        """

class ComparisonAgent:
    """商品对比专家，负责生成详细的商品对比表格和分析"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def compare(self, products: List[Dict], query: str) -> Dict:
        """生成商品对比分析"""
        # 生成Markdown对比表格
        table = self._generate_comparison_table(products)
        
        prompt = f"""
        你是一个专业的商品对比专家，请根据以下对比表格和用户需求，给出详细的对比分析。
        要求：
        1. 只使用表格中的信息，绝对不要编造内容
        2. 分析每款商品的优缺点
        3. 针对用户的需求，给出明确的购买建议
        4. 回答清晰、有条理，使用Markdown格式
        
        对比表格：
        {table}
        
        用户需求：{query}
        
        对比分析：
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "answer": table + "\n\n" + response.content,
            "products": products
        }
    
    def _generate_comparison_table(self, products: List[Dict]) -> str:
        """生成Markdown对比表格"""
        if len(products) < 2:
            return "需要至少2款商品才能进行对比。"
        
        # 表格头部
        headers = ["对比项"] + [product["name"] for product in products]
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        # 价格行
        table += "| 价格 | " + " | ".join([f"{product['price']}元" for product in products]) + " |\n"
        
        # 品牌行
        table += "| 品牌 | " + " | ".join([product["brand"] for product in products]) + " |\n"
        
        # 核心参数行
        table += "| 核心参数 | " + " | ".join([product["parameters"][:50] + "..." if len(product["parameters"]) > 50 else product["parameters"] for product in products]) + " |\n"
        
        # 用户评价行
        table += "| 用户评价 | " + " | ".join([product["reviews"][0] if product["reviews"] else "暂无评价" for product in products]) + " |\n"
        
        return table