from modules.data_loader import DataLoader
from modules.rag_engine import RAGEngine
from modules.image_searcher import ImageSearcher
from PIL import Image
import requests
from io import BytesIO

# 京东反爬专用请求头
JD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.jd.com/",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8"
}

print("="*50)
print("第二天任务测试")
print("="*50)

# 1. 测试数据加载器
print("\n1. 测试数据加载器...")
data_loader = DataLoader("mobile_phones")
products = data_loader.get_all_products()
print(f"✅ 成功加载{len(products)}款手机")
print(f"第一款手机：{products[0]['name']}，价格：{products[0]['price']}元")

# 2. 测试文本RAG引擎
print("\n2. 测试文本RAG引擎...")
rag_engine = RAGEngine("mobile_phones")
query = "推荐一款3000元左右的拍照手机"
results = rag_engine.search(query)
print(f"查询：{query}")
print(f"检索到{len(results)}款商品：")
for i, product in enumerate(results):
    print(f"  {i+1}. {product['name']} - {product['price']}元")

# 3. 测试图片检索引擎
print("\n3. 测试图片检索引擎...")
image_searcher = ImageSearcher("mobile_phones")

# 用第一款商品的图片测试（已添加反爬）
test_image_url = products[0]["image_url"]
print(f"测试图片：{test_image_url}")
response = requests.get(test_image_url, headers=JD_HEADERS, timeout=15)
test_image = Image.open(BytesIO(response.content)).convert("RGB")

results = image_searcher.search(test_image)
print(f"\n用{products[0]['name']}的图片进行检索")
print(f"检索到{len(results)}款商品：")
for i, product in enumerate(results):
    print(f"  {i+1}. {product['name']} - {product['price']}元")

print("\n🎉 第二天所有模块测试通过！")