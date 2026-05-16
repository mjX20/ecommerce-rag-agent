import os
from dotenv import load_dotenv

# ==================== 模型下载配置（必须放在最开头，所有导入之前） ====================
# 1. 强制所有Hugging Face库使用国内镜像源（终极方案）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com/"
os.environ["HUGGINGFACE_HUB_ENDPOINT"] = "https://hf-mirror.com/"
os.environ["HF_HUB_URL"] = "https://hf-mirror.com/"

# 2. 统一使用HF_HOME作为唯一缓存目录（新版标准）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
HF_HOME = os.path.join(MODELS_DIR, "huggingface")

os.environ["HF_HOME"] = HF_HOME
os.environ["TRANSFORMERS_CACHE"] = HF_HOME  # 兼容旧版
os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.path.join(MODELS_DIR, "sentence_transformers")
os.environ["TORCH_HOME"] = os.path.join(MODELS_DIR, "torch")

# 3. 自动创建所有目录
os.makedirs(HF_HOME, exist_ok=True)
os.makedirs(os.path.join(MODELS_DIR, "sentence_transformers"), exist_ok=True)
os.makedirs(os.path.join(MODELS_DIR, "torch"), exist_ok=True)

# 4. 禁用所有不必要的警告和遥测
os.environ["TRANSFORMERS_OFFLINE"] = "0"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "0"

print(f"✅ 模型缓存根目录：{MODELS_DIR}")
print(f"✅ 已启用国内镜像源：{os.environ['HF_ENDPOINT']}")

# 加载环境变量
load_dotenv()

# ==================== 全局配置 ====================
APP_NAME = "多模态电商智能导购Agent"
APP_VERSION = "1.0.0"

# ==================== 知识库配置 ====================
ACTIVE_KNOWLEDGE_BASE = "mobile_phones"

KNOWLEDGE_BASES = {
    "mobile_phones": {
        "name": "热门手机",
        "description": "京东2026年5月热门手机排行榜前10名",
        "data_path": "data/mobile_phones.json",
        "vector_db_path": "vector_db/mobile_phones",
        "image_features_path": "data/mobile_phones_image_features.pkl"
    },
    "skincare": {
        "name": "护肤产品",
        "description": "京东2026年5月热门护肤品排行榜前10名",
        "data_path": "data/skincare.json",
        "vector_db_path": "vector_db/skincare",
        "image_features_path": "data/skincare_image_features.pkl"
    }
}

# ==================== RAG配置 ====================
RAG_CONFIG = {
    "embedding_model": "all-MiniLM-L6-v2",
    "text_retrieval_k": 3,
    "image_retrieval_k": 3,
    "chunk_size": 512,
    "chunk_overlap": 50
}

# ==================== 大模型配置 ====================
LLM_CONFIG = {
    "api_key": os.getenv("DOUBAO_API_KEY"),
    "base_url": os.getenv("DOUBAO_BASE_URL"),
    "model": os.getenv("DOUBAO_MODEL"),
    "temperature": 0.1,
    "max_tokens": 2048
}

# ==================== 多Agent配置 ====================
AGENT_CONFIG = {
    "retrieval_agent_name": "信息检索专家",
    "recommendation_agent_name": "个性化推荐专家",
    "comparison_agent_name": "商品对比专家"
}

# 导出所有全局变量，让其他模块可以导入
__all__ = [
    "HF_HOME",
    "APP_NAME",
    "APP_VERSION",
    "ACTIVE_KNOWLEDGE_BASE",
    "KNOWLEDGE_BASES",
    "RAG_CONFIG",
    "LLM_CONFIG",
    "AGENT_CONFIG"
]