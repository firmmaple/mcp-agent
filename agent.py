from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI # 导入 Gemini 模型
import os # 建议用于管理 API 密钥
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

client = MultiServerMCPClient(
    {
        # "weather": {
        #     "url": "http://localhost:3000/mcp/",
        #     "transport": "streamable_http",
        # }, 
        "a_share_data_provider": {
            "url": "http://mcp-server.danglingpointer.top:3000/mcp/",
            "transport": "streamable_http",
        }
    }
)

async def agent(state: AgentState) -> AgentState:
    try:
        tools = await client.get_tools()
        print("工具加载成功，可用工具数量:", len(tools))
        print("工具列表:", [tool.name for tool in tools])
    except Exception as e:
        print(f"获取工具失败: {e}")
        return
    
    # 1. 实例化 Gemini 模型
    # ChatGoogleGenerativeAI 会自动从环境变量中读取 GOOGLE_API_KEY
    try:
        # 确保 GOOGLE_API_KEY 已通过 .env 文件加载
        if not os.getenv("GOOGLE_API_KEY"):
            print("错误：GOOGLE_API_KEY 未在 .env 文件中或环境变量中设置。")
            print("请在 .env 文件中添加 GOOGLE_API_KEY='YOUR_KEY'")
            return

        llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
        print("Gemini 模型初始化成功。")
    except Exception as e:
        print(f"初始化 Gemini 模型失败: {e}")
        print("请确保您已安装 langchain-google-genai 并正确设置了 GOOGLE_API_KEY。")
        return
    
    # 2. 使用实例化的 Gemini 模型创建 agent executor
    try:
        agent_executor = create_react_agent(llm, tools)
        print("Agent Executor 创建成功。")
    except Exception as e:
        print(f"创建 Agent Executor 失败: {e}")
        return   
    
    # 3. 调用 agent (A股数据分析示例)
    try:
        response = await agent_executor.ainvoke({"messages": state["messages"]})
        print("\n=== Agent 分析结果 ===")
        print(response)
        # # 打印最后一条消息（通常是AI的最终回复）
        # if response and "messages" in response:
        #     last_message = response["messages"][-1]
        #     if hasattr(last_message, 'content'):
        #         print(last_message.content)
        #     else:
        #         print(last_message)
        # else:
        #     print("Agent 响应:", response)   
    except Exception as e:
        print(f"调用 agent 时出错: {e}")
        import traceback
        traceback.print_exc()
    return state

async def main():
    query = """我是专业的A股市场分析师，请根据我的问题智能选择合适的工具进行数据分析。
    
# 分析任务：请帮我分析贵州茅台(sh.600519)的投资价值

# 分析要求：
1. 先获取最新交易日期确定分析时点
2. 获取该股票的基本信息和最近表现
3. 分析其财务状况（盈利、成长、偿债能力）
4. 查看技术面表现（价格走势、成交量）
5. 综合评估投资价值并给出专业意见

请你自主选择合适的工具，按逻辑顺序进行分析，无需询问我每一步该做什么。"""
    initial_state = AgentState(messages=[HumanMessage(content=query)])
    await agent(initial_state)

if __name__ == "__main__":
    asyncio.run(main())