from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url=os.getenv("DOUBAO_BASE_URL"),
    model=os.getenv("DOUBAO_MODEL"),
    temperature=0.1
)

response = llm.invoke("你好，豆包！")
print(response.content)