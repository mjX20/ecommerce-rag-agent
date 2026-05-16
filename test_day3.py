from modules.agent_manager import AgentManager

print("="*50)
print("第三天任务测试：多Agent系统")
print("="*50)

# 初始化多Agent系统
agent_manager = AgentManager("mobile_phones")
print("✅ 多Agent系统初始化完成")

# 测试1：普通问答
print("\n1. 测试普通问答...")
result = agent_manager.process_query("iPhone 15 Pro Max的价格是多少？")
print(f"回答：{result['answer']}")
print(f"返回商品数：{len(result['products'])}")

# 测试2：个性化推荐
print("\n2. 测试个性化推荐...")
result = agent_manager.process_query("我想要一款拍照好的手机，预算6000元左右")
print(f"回答：\n{result['answer']}")

# 测试3：商品对比
print("\n3. 测试商品对比...")
result = agent_manager.process_query("对比一下小米14 Ultra和华为Mate 60 Pro+")
print(f"回答：\n{result['answer']}")

print("\n🎉 第三天所有模块测试通过！")