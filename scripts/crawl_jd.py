import requests
from bs4 import BeautifulSoup
import json
import time
import random

# 请求头，模拟浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def crawl_jd_ranklist(category_url, category_name, limit=10):
    """爬取京东排行榜商品"""
    products = []

    response = requests.get(category_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select(".gl-item")[:limit]

    for i, item in enumerate(items):
        try:
            # 基本信息
            name = item.select_one(".p-name em").text.strip()
            price = item.select_one(".p-price i").text.strip()
            image_url = "https:" + item.select_one(".p-img img")["src"]
            product_url = "https:" + item.select_one(".p-img a")["href"]

            # 提取品牌
            brand = name.split(" ")[0]

            # 模拟参数和评价（实际项目可以爬取详情页）
            parameters = f"品牌：{brand}\n名称：{name}\n价格：{price}元"
            description = f"{name}是{category_name}类别的热门产品，深受消费者喜爱。"
            reviews = [
                "质量很好，物流很快",
                "性价比很高，推荐购买",
                "使用体验不错，值得入手"
            ]

            product = {
                "id": f"{category_name}_{i + 1}",
                "name": name,
                "price": float(price),
                "brand": brand,
                "category": category_name,
                "parameters": parameters,
                "description": description,
                "reviews": reviews,
                "image_url": image_url,
                "product_url": product_url
            }

            products.append(product)
            print(f"✅ 已爬取：{name}")

            # 随机延时，避免被封
            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            print(f"❌ 爬取失败：{e}")
            continue

    return products


if __name__ == "__main__":
    # 手机排行榜
    print("正在爬取手机排行榜...")
    mobile_phones = crawl_jd_ranklist(
        "https://list.jd.com/list.html?cat=9987,653,655",
        "手机"
    )

    with open("data/mobile_phones.json", "w", encoding="utf-8") as f:
        json.dump(mobile_phones, f, ensure_ascii=False, indent=2)

    # 护肤品排行榜
    print("\n正在爬取护肤品排行榜...")
    skincare = crawl_jd_ranklist(
        "https://list.jd.com/list.html?cat=1316,1381,1389",
        "护肤品"
    )

    with open("data/skincare.json", "w", encoding="utf-8") as f:
        json.dump(skincare, f, ensure_ascii=False, indent=2)

    print("\n🎉 数据爬取完成！")
    print(f"手机：{len(mobile_phones)}款")
    print(f"护肤品：{len(skincare)}款")