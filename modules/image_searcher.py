import os
import pickle
import numpy as np
from PIL import Image
import requests
from io import BytesIO
from typing import List, Dict
from transformers import CLIPProcessor, CLIPModel
import torch
from config import KNOWLEDGE_BASES, RAG_CONFIG, HF_HOME
from modules.data_loader import DataLoader

# 京东反爬专用请求头
JD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.jd.com/",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

class ImageSearcher:
    """CLIP图片检索引擎（纯本地加载版，支持京东反爬）"""
    
    def __init__(self, knowledge_base_name: str):
        """
        初始化图片检索引擎
        :param knowledge_base_name: 知识库名称（英文键名，如"mobile_phones"）
        """
        self.kb_name = knowledge_base_name
        self.kb_config = KNOWLEDGE_BASES[knowledge_base_name]
        self.features_path = self.kb_config["image_features_path"]
        
        # 直接加载本地CLIP模型，不访问任何网络
        clip_model_path = os.path.join(HF_HOME, "clip-vit-base-patch32")
        print(f"加载本地CLIP模型：{clip_model_path}")
        
        self.model = CLIPModel.from_pretrained(
            clip_model_path,
            local_files_only=True  # 强制只使用本地文件
        )
        self.processor = CLIPProcessor.from_pretrained(
            clip_model_path,
            local_files_only=True  # 强制只使用本地文件
        )
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # 加载或预计算图片特征
        self.product_features = self._init_image_features()
    
    def _init_image_features(self) -> Dict[str, np.ndarray]:
        """初始化图片特征，如果不存在则预计算"""
        if os.path.exists(self.features_path):
            print(f"加载现有图片特征：{self.features_path}")
            with open(self.features_path, "rb") as f:
                return pickle.load(f)
        else:
            print(f"预计算图片特征：{self.features_path}")
            return self._precompute_features()
    
    def _download_image(self, url: str) -> Image.Image:
        """下载图片，自动绕过京东反爬"""
        try:
            response = requests.get(url, headers=JD_HEADERS, timeout=15)
            response.raise_for_status()  # 检查HTTP状态码
            return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            print(f"⚠️ 图片下载失败：{url}，错误：{str(e)}")
            # 返回一个1x1的占位图，避免程序崩溃
            return Image.new("RGB", (1, 1), color="white")
    
    def _precompute_features(self) -> Dict[str, np.ndarray]:
        """预计算所有商品图片的CLIP特征"""
        data_loader = DataLoader(self.kb_name)
        products = data_loader.get_all_products()
        
        features = {}
        for product in products:
            try:
                # 下载图片（已添加反爬）
                image = self._download_image(product["image_url"])
                
                # 提取特征
                inputs = self.processor(images=image, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                
                # 归一化
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                features[product["id"]] = image_features.cpu().numpy()[0]
                
                print(f"✅ 已计算：{product['name']}")
                
            except Exception as e:
                print(f"❌ 计算失败：{product['name']}，错误：{e}")
                continue
        
        # 保存特征
        with open(self.features_path, "wb") as f:
            pickle.dump(features, f)
        
        print(f"图片特征预计算完成，共{len(features)}个商品")
        return features
    
    def search(self, image: Image.Image, k: int = None) -> List[Dict]:
        """
        图片检索
        :param image: PIL Image对象
        :param k: 返回结果数量，默认使用配置值
        :return: 检索到的商品信息列表
        """
        if k is None:
            k = RAG_CONFIG["image_retrieval_k"]
        
        # 提取查询图片特征
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            query_features = self.model.get_image_features(**inputs)
        
        # 归一化
        query_features = query_features / query_features.norm(dim=-1, keepdim=True)
        query_features = query_features.cpu().numpy()[0]
        
        # 计算相似度
        similarities = {}
        for product_id, feature in self.product_features.items():
            similarity = np.dot(query_features, feature)
            similarities[product_id] = similarity
        
        # 按相似度排序
        sorted_ids = sorted(similarities.keys(), key=lambda x: similarities[x], reverse=True)[:k]
        
        # 获取商品信息
        data_loader = DataLoader(self.kb_name)
        results = []
        for product_id in sorted_ids:
            product = data_loader.get_product_by_id(product_id)
            if product:
                results.append(product)
        
        return results
    
    def search_by_text(self, text: str, k: int = None) -> List[Dict]:
        """
        文本到图片检索（可选功能）
        :param text: 查询文本
        :param k: 返回结果数量
        :return: 检索到的商品信息列表
        """
        if k is None:
            k = RAG_CONFIG["image_retrieval_k"]
        
        # 提取文本特征
        inputs = self.processor(text=text, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        
        # 归一化
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        text_features = text_features.cpu().numpy()[0]
        
        # 计算相似度
        similarities = {}
        for product_id, feature in self.product_features.items():
            similarity = np.dot(text_features, feature)
            similarities[product_id] = similarity
        
        # 按相似度排序
        sorted_ids = sorted(similarities.keys(), key=lambda x: similarities[x], reverse=True)[:k]
        
        # 获取商品信息
        data_loader = DataLoader(self.kb_name)
        results = []
        for product_id in sorted_ids:
            product = data_loader.get_product_by_id(product_id)
            if product:
                results.append(product)
        
        return results