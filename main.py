import streamlit as st
from PIL import Image
from config import APP_NAME, APP_VERSION, KNOWLEDGE_BASES
from modules.agent_manager import AgentManager

# 页面配置
st.set_page_config(
    page_title=f"{APP_NAME} v{APP_VERSION}",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_kb" not in st.session_state:
    st.session_state.current_kb = list(KNOWLEDGE_BASES.keys())[0]
if "agent_manager" not in st.session_state:
    st.session_state.agent_manager = AgentManager.get_instance(st.session_state.current_kb)
if "recommended_products" not in st.session_state:
    st.session_state.recommended_products = []

# 标题
st.title(f"🛒 {APP_NAME}")
st.caption(f"基于RAG的多模态通用导购框架 | 字节跳动2026 AI全栈挑战赛")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统设置")
    
    # 知识库切换
    selected_kb = st.selectbox(
        "选择商品知识库",
        options=list(KNOWLEDGE_BASES.keys()),
        format_func=lambda x: KNOWLEDGE_BASES[x]["name"],
        index=list(KNOWLEDGE_BASES.keys()).index(st.session_state.current_kb)
    )
    
    # 切换知识库时重新加载Agent
    if selected_kb != st.session_state.current_kb:
        st.session_state.current_kb = selected_kb
        st.session_state.agent_manager = AgentManager.get_instance(selected_kb)
        st.session_state.chat_history = []
        st.session_state.recommended_products = []
        st.rerun()
    
    st.info(f"当前知识库：{KNOWLEDGE_BASES[selected_kb]['description']}")
    
    st.divider()
    st.subheader("📖 使用说明")
    st.markdown("""
    1. 选择左侧知识库切换商品品类
    2. 在对话框输入你的需求
    3. 支持上传图片进行以图搜图
    4. 支持多轮对话和商品对比
    """)
    
    st.divider()
    st.subheader("💡 示例问题")
    example_questions = [
        "推荐一款3000元左右的拍照手机",
        "对比一下小米14和华为Mate 60",
        "iPhone 15 Pro Max的价格是多少？",
        "哪款手机的续航最好？"
    ]
    
    for q in example_questions:
        if st.button(q, use_container_width=True):
            st.session_state.user_input = q
            st.rerun()
    
    st.divider()
    st.caption(f"版本 v{APP_VERSION}")

# 主界面：三栏布局
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 对话窗口")
    
    # 显示对话历史
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 图片上传
    uploaded_image = st.file_uploader("上传图片进行以图搜图", type=["jpg", "jpeg", "png"])
    
    # 用户输入
    user_input = st.chat_input("输入你的问题...")
    
    # 处理用户输入
    if user_input or uploaded_image:
        # 添加用户消息到历史
        with st.chat_message("user"):
            if uploaded_image:
                st.image(uploaded_image, caption="上传的图片", width=200)
            if user_input:
                st.markdown(user_input)
        
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input or "以图搜图",
            "image": uploaded_image
        })
        
        # 处理查询
        with st.chat_message("assistant"):
            with st.spinner("正在思考中..."):
                image = None
                if uploaded_image:
                    image = Image.open(uploaded_image).convert("RGB")
                
                # 调用多Agent系统
                result = st.session_state.agent_manager.process_query(
                    query=user_input or "",
                    image=image,
                    chat_history=st.session_state.chat_history
                )
                
                # 显示回答
                st.markdown(result["answer"])
                
                # 更新推荐商品
                st.session_state.recommended_products = result["products"]
        
        # 添加助手消息到历史
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"]
        })
        
        st.rerun()
    
    # 清空对话按钮
    if st.button("清空对话历史", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.recommended_products = []
        st.rerun()

with col2:
    st.subheader("🛍️ 推荐商品")
    
    if st.session_state.recommended_products:
        for product in st.session_state.recommended_products:
            with st.container():
                st.image(product["image_url"], use_column_width=True)
                st.markdown(f"**{product['name']}**")
                st.markdown(f"💰 {product['price']}元")
                st.markdown(f"🏷️ {product['brand']}")
                st.divider()
    else:
        st.info("输入问题后，这里会显示推荐的商品")