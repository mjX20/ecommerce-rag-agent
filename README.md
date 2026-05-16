\# 多模态电商智能导购Agent通用框架

🚀 \*\*字节跳动2026 AI全栈挑战赛MVP项目\*\* | 已部署上线，点击即可体验



\## ✨ 核心特色

\- \*\*通用可插拔\*\*：数据与代码100%分离，替换JSON文件5分钟拥有专属导购

\- \*\*多模态检索\*\*：支持文本、图片、图文混合查询

\- \*\*多Agent协作\*\*：检索、推荐、对比三个专业Agent协同工作

\- \*\*零代码部署\*\*：一键部署至Streamlit Cloud，获得公开访问链接



\## 🛠️ 技术栈

| 模块 | 技术选型 |

|------|----------|

| 界面与部署 | Streamlit 1.35 |

| RAG框架 | LangChain 0.2 |

| 向量数据库 | Chroma 0.5 |

| 文本嵌入 | all-MiniLM-L6-v2 |

| 多模态模型 | CLIP-vit-base-p32 |

| 大语言模型 | 豆包API 4.0 |



\## 🚀 快速开始

\### 本地运行

```bash

\# 1. 克隆仓库

git clone https://github.com/你的用户名/ecommerce-rag-agent-framework.git

cd ecommerce-rag-agent-framework



\# 2. 安装依赖

pip install -r requirements.txt



\# 3. 配置环境变量

cp .env.example .env

\# 编辑.env文件，填入你的豆包API密钥



\# 4. 运行应用

streamlit run main.py

