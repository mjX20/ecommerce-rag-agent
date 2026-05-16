---
title: 多模态电商智能导购Agent
emoji: 🛒
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.35.0"
python_version: "3.10"
app_file: main.py
pinned: false
---

# 多模态电商智能导购Agent
基于RAG的多模态通用电商导购框架，支持文本问答、个性化推荐、商品对比和以图搜图。

## 功能特性
- ✅ 多模态检索：支持文本和图片混合查询
- ✅ 多Agent协作：检索Agent、推荐Agent、对比Agent协同工作
- ✅ 可插拔知识库：一键切换不同商品品类
- ✅ 零代码部署：商家只需上传Excel表格即可生成专属导购
- ✅ 24小时在线：自动回答所有商品咨询，提高转化率

## 技术架构
- 前端：Streamlit
- 大模型：字节跳动豆包API
- 向量数据库：ChromaDB
- 嵌入模型：all-MiniLM-L6-v2
- 图片检索：CLIP ViT-B/32

## 使用方法
1. 选择左侧知识库切换商品品类
2. 在对话框输入你的需求
3. 支持上传图片进行以图搜图
4. 支持多轮对话和商品对比
