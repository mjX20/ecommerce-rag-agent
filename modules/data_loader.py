import json
import pandas as pd
from typing import List, Dict
from config import KNOWLEDGE_BASES

class DataLoader:
    """通用数据加载器，支持JSON和Excel格式"""
    
    def __init__(self, knowledge_base_name: str):
        """
        初始化数据加载器
        :param knowledge_base_name: 知识库名称，对应config.py中的配置
        """
        self.kb_config = KNOWLEDGE_BASES[knowledge_base_name]
        self.data_path = self.kb_config["data_path"]
        self.products = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """从JSON文件加载商品数据"""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._clean_data(data)
        except FileNotFoundError:
            raise Exception(f"数据文件不存在：{self.data_path}")
        except json.JSONDecodeError:
            raise Exception(f"JSON格式错误：{self.data_path}")
    
    def _clean_data(self, data: List[Dict]) -> List[Dict]:
        """数据清洗与格式化"""
        cleaned_data = []
        for product in data:
            # 确保所有必要字段都存在
            cleaned_product = {
                "id": product.get("id", ""),
                "name": product.get("name", ""),
                "price": float(product.get("price", 0)),
                "brand": product.get("brand", ""),
                "category": product.get("category", ""),
                "parameters": product.get("parameters", ""),
                "description": product.get("description", ""),
                "reviews": product.get("reviews", []),
                "image_url": product.get("image_url", ""),
                "product_url": product.get("product_url", "")
            }
            cleaned_data.append(cleaned_product)
        return cleaned_data
    
    def get_all_products(self) -> List[Dict]:
        """获取所有商品"""
        return self.products
    
    def get_product_by_id(self, product_id: str) -> Dict:
        """根据ID获取商品"""
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None
    
    def get_product_text(self, product: Dict) -> str:
        """将商品信息转换为文本，用于RAG检索"""
        text = f"""
        商品名称：{product['name']}
        品牌：{product['brand']}
        价格：{product['price']}元
        类别：{product['category']}
        参数：{product['parameters']}
        描述：{product['description']}
        用户评价：{'；'.join(product['reviews'])}
        """
        return text.strip()
    
    @staticmethod
    def excel_to_json(excel_path: str, json_path: str):
        """
        将Excel文件转换为标准JSON格式
        Excel必须包含以下列：name, price, brand, category, parameters, description, image_url
        reviews列可选，多个评价用分号分隔
        """
        try:
            df = pd.read_excel(excel_path)
            
            # 转换为字典列表
            data = []
            for i, row in df.iterrows():
                product = {
                    "id": f"product_{i+1}",
                    "name": str(row.get("name", "")),
                    "price": float(row.get("price", 0)),
                    "brand": str(row.get("brand", "")),
                    "category": str(row.get("category", "")),
                    "parameters": str(row.get("parameters", "")),
                    "description": str(row.get("description", "")),
                    "reviews": str(row.get("reviews", "")).split("；") if pd.notna(row.get("reviews")) else [],
                    "image_url": str(row.get("image_url", "")),
                    "product_url": str(row.get("product_url", ""))
                }
                data.append(product)
            
            # 保存为JSON
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Excel转换完成：{json_path}")
            print(f"✅ 共转换{len(data)}款商品")
            return True
            
        except Exception as e:
            print(f"❌ Excel转换失败：{e}")
            return False