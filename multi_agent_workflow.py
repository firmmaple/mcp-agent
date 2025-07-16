from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
import asyncio
import datetime
from fastapi import WebSocket
import json

# 导入新创建的agent类
from agents import FundamentalAgent, TechnicalAgent, ValuationAgent, SummaryAgent, InvestmentAgent

load_dotenv()

class MultiAgentState(TypedDict):
    company_name: str
    stock_code: str
    current_time_info: str
    current_date: str
    current_price: float
    historical_prices: list
    portfolio_state: dict
    fundamental_analysis: str
    technical_analysis: str
    valuation_analysis: str
    summary_analysis: str
    investment_decision: str
    final_report: str
    messages: Annotated[list[BaseMessage], add_messages]

class MultiAgentWorkflow:
    def __init__(self, websocket: WebSocket = None, verbose: bool = True):
        self.websocket = websocket
        self.verbose = verbose
        self.client = MultiServerMCPClient({
            "a_share_data_provider": {
                # "url": "http://165.22.115.184:3000/mcp/",
                "url": "http://localhost:3000/mcp/",
                "transport": "streamable_http",
            }
        })
        self.tools = None
        self.llm = None
        
        # 初始化agent实例，传入verbose参数
        self.fundamental_agent = FundamentalAgent(verbose=self.verbose)
        self.technical_agent = TechnicalAgent(verbose=self.verbose)
        self.valuation_agent = ValuationAgent(verbose=self.verbose)
        self.summary_agent = SummaryAgent(verbose=self.verbose)
        self.investment_agent = InvestmentAgent(verbose=self.verbose)
        
    async def send_log(self, message: str, log_type: str = "info"):
        """发送日志消息到前端"""
        if self.websocket:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            await self.websocket.send_text(json.dumps({
                "message": message,
                "type": log_type,
                "timestamp": timestamp
            }))
        else:
            print(f"[{log_type.upper()}] {message}")
    
    async def initialize(self):
        """初始化工具和模型"""
        try:
            # 获取工具
            await self.send_log("正在连接 MCP 服务器...", "info")
            self.tools = await self.client.get_tools()
            await self.send_log(f"工具加载成功，可用工具数量: {len(self.tools)}", "success")
            
            # 初始化 Gemini 模型
            await self.send_log("正在初始化 Gemini 模型...", "info")
            if not os.getenv("GOOGLE_API_KEY"):
                raise Exception("GOOGLE_API_KEY 未设置")
            
            self.llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
            await self.send_log("Gemini 模型初始化成功", "success")
            
            # 为所有agent设置LLM、工具和WebSocket
            for agent in [self.fundamental_agent, self.technical_agent, 
                         self.valuation_agent, self.summary_agent, self.investment_agent]:
                agent.set_llm(self.llm)
                agent.set_tools(self.tools)
                agent.set_websocket(self.websocket)
            
            return True
            
        except Exception as e:
            await self.send_log(f"初始化失败: {e}", "error")
            return False
    
    async def router_node(self, state: MultiAgentState) -> MultiAgentState:
        """路由节点，用于启动并行分析"""
        await self.send_log("🚀 启动并行分析流程...", "info")
        return state
    
    async def parallel_analysis(self, state: MultiAgentState) -> MultiAgentState:
        """并行执行三个分析agent"""
        await self.send_log("⚡ 开始并行执行三个专业分析...", "info")
        
        # 并行执行三个分析
        tasks = [
            self.fundamental_agent.analyze(state),
            self.technical_agent.analyze(state),
            self.valuation_agent.analyze(state)
        ]
        
        # 等待所有分析完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果并更新状态
        agent_names = ["基本面分析", "技术分析", "估值分析"]
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                await self.send_log(f"❌ {agent_names[i]}失败: {result}", "error")
                # 结果已经在agent的analyze方法中处理过了
            else:
                # 结果已经在agent的analyze方法中更新到state中
                await self.send_log(f"✅ {agent_names[i]}完成", "success")
        
        return state
    
    async def summary_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """汇总分析节点"""
        await self.send_log("📝 开始生成综合分析报告...", "info")
        
        try:
            # 使用汇总agent进行分析
            result_state = await self.summary_agent.analyze(state)
            
            await self.send_log("✅ 综合分析报告生成完成", "success")
            return result_state
            
        except Exception as e:
            await self.send_log(f"❌ 综合分析报告生成失败: {e}", "error")
            state["summary_analysis"] = f"综合分析报告生成失败: {e}"
            return state
    
    async def investment_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """投资决策节点"""
        await self.send_log("💰 开始生成投资决策指令...", "info")
        
        try:
            # 使用投资决策agent进行分析
            result_state = await self.investment_agent.analyze(state)
            
            # 将投资决策结果整合到最终报告
            summary_analysis = result_state.get("summary_analysis", "")
            investment_decision = result_state.get("investment_decision", {})
            
            # 获取投资决策的原始文本
            investment_text = ""
            if isinstance(investment_decision, dict):
                investment_text = investment_decision.get("raw_decision", "")
            else:
                investment_text = str(investment_decision)
            
            # 组合最终报告
            final_report = f"{summary_analysis}\n\n---\n\n{investment_text}"
            result_state["final_report"] = final_report
            
            await self.send_log("✅ 投资决策指令生成完成", "success")
            return result_state
            
        except Exception as e:
            await self.send_log(f"❌ 投资决策指令生成失败: {e}", "error")
            state["investment_decision"] = f"投资决策指令生成失败: {e}"
            # 如果投资决策失败，使用summary作为最终报告
            state["final_report"] = state.get("summary_analysis", "分析失败")
            return state
    
    def create_workflow(self):
        """创建工作流图"""
        workflow = StateGraph(MultiAgentState)
        
        # 添加节点
        workflow.add_node("router", self.router_node)
        workflow.add_node("parallel_analysis", self.parallel_analysis)
        workflow.add_node("summary", self.summary_agent_node)
        workflow.add_node("investment", self.investment_agent_node)
        
        # 设置入口点
        workflow.set_entry_point("router")
        
        # 设置边
        workflow.add_edge("router", "parallel_analysis")
        workflow.add_edge("parallel_analysis", "summary")
        workflow.add_edge("summary", "investment")
        workflow.add_edge("investment", END)
        
        return workflow.compile()
    
    async def run_analysis(self, company_name: str, stock_code: str):
        """运行完整的分析流程"""
        # 初始化
        if not await self.initialize():
            return None
        
        # 准备状态
        current_time = datetime.datetime.now()
        initial_state = MultiAgentState(
            company_name=company_name,
            stock_code=stock_code,
            current_time_info=current_time.strftime("%Y年%m月%d日 %H:%M:%S"),
            current_date=current_time.strftime("%Y-%m-%d"),
            current_price=0.0,
            historical_prices=[],
            portfolio_state={},
            fundamental_analysis="",
            technical_analysis="",
            valuation_analysis="",
            summary_analysis="",
            investment_decision="",
            final_report="",
            messages=[]
        )
        
        await self.send_log(f"🚀 开始分析 {company_name}({stock_code})", "info")
        
        # 创建并运行工作流
        app = self.create_workflow()
        
        try:
            # 运行工作流
            result = await app.ainvoke(initial_state)
            
            await self.send_log("🎉 所有分析完成！", "success")
            
            # 返回最终报告
            return result.get("final_report", "分析完成，但未能生成最终报告")
            
        except Exception as e:
            await self.send_log(f"❌ 工作流执行失败: {e}", "error")
            return f"分析过程中发生错误: {e}"
    
    async def run(self, input_data: dict) -> dict:
        """
        运行工作流的简化接口
        
        Args:
            input_data: 包含stock_code, company_name等的输入数据
            
        Returns:
            包含所有分析结果的字典
        """
        # 准备状态
        current_time = datetime.datetime.now()
        initial_state = MultiAgentState(
            company_name=input_data.get("company_name", ""),
            stock_code=input_data.get("stock_code", ""),
            current_time_info=input_data.get("current_time_info", current_time.strftime("%Y年%m月%d日 %H:%M:%S")),
            current_date=input_data.get("current_date", current_time.strftime("%Y-%m-%d")),
            current_price=input_data.get("current_price", 0.0),
            historical_prices=input_data.get("historical_prices", []),
            portfolio_state=input_data.get("portfolio_state", {}),
            fundamental_analysis="",
            technical_analysis="",
            valuation_analysis="",
            summary_analysis="",
            investment_decision="",
            final_report="",
            messages=[]
        )
        
        await self.send_log(f"🚀 开始分析 {input_data.get('company_name', '')}({input_data.get('stock_code', '')})", "info")
        
        # 初始化工具和模型
        if not await self.initialize():
            return {
                "error": "初始化失败",
                "investment_decision": {
                    "action": "HOLD",
                    "confidence": 0.0,
                    "target_price": None,
                    "stop_loss": None,
                    "position_size": 0.0,
                    "holding_period": "medium",
                    "risk_level": "medium",
                    "reasons": ["初始化失败"]
                }
            }
        
        # 创建并运行工作流
        app = self.create_workflow()
        
        try:
            # 运行工作流
            result = await app.ainvoke(initial_state)
            
            await self.send_log("🎉 所有分析完成！", "success")
            
            # 返回完整的状态结果
            return result
            
        except Exception as e:
            await self.send_log(f"❌ 工作流执行失败: {e}", "error")
            return {
                "error": f"分析过程中发生错误: {e}",
                "investment_decision": {
                    "action": "HOLD",
                    "confidence": 0.0,
                    "target_price": None,
                    "stop_loss": None,
                    "position_size": 0.0,
                    "holding_period": "medium",
                    "risk_level": "medium",
                    "reasons": [f"分析失败: {str(e)}"]
                }
            }

# 测试函数
async def test_multi_agent():
    """测试多agent工作流"""
    workflow = MultiAgentWorkflow()
    result = await workflow.run_analysis("贵州茅台", "sh.600519")
    print("最终报告:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_multi_agent()) 
