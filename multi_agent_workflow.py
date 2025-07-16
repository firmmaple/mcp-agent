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
        
        # 优化MCP客户端配置 - 使用测试验证的工作配置
        self.client = MultiServerMCPClient({
            "a_share_data_provider": {
                "url": "http://localhost:3000/mcp/",
                "transport": "streamable_http"
            }
        })
        self.tools = None
        self.llm = None
        self._initialized = False  # 追踪初始化状态
        
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
    
    async def initialize_tools_and_model(self):
        """初始化工具和模型（带缓存和优化的连接管理）"""
        if self._initialized:
            await self.send_log("使用已初始化的连接", "info")
            return True
            
        try:
            # 获取工具
            await self.send_log("正在连接 MCP 服务器...", "info")
            
            # 优化的连接逻辑：减少重试次数，增加每次重试间隔
            max_retries = 2
            base_delay = 3
            
            for attempt in range(max_retries):
                try:
                    # 确保每次尝试都是独立的
                    await self.send_log(f"尝试连接 MCP 服务器 ({attempt + 1}/{max_retries})", "info")
                    
                    # 设置适中的超时时间，确保MCP连接稳定
                    self.tools = await asyncio.wait_for(
                        self.client.get_tools(), 
                        timeout=30.0  # 增加超时时间
                    )
                    
                    await self.send_log(f"✅ MCP连接成功！可用工具数量: {len(self.tools)}", "success")
                    break
                    
                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        delay = base_delay * (attempt + 1)
                        await self.send_log(f"MCP连接超时，{delay}秒后重试... ({attempt + 1}/{max_retries})", "warning")
                        await asyncio.sleep(delay)
                    else:
                        raise Exception("MCP服务器连接超时，请检查服务器状态")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "session" in error_msg.lower() or "missing session id" in error_msg.lower():
                        # 会话相关错误，稍等后重试
                        if attempt < max_retries - 1:
                            delay = base_delay * (attempt + 1)
                            await self.send_log(f"MCP会话错误，{delay}秒后重试... ({attempt + 1}/{max_retries})", "warning")
                            await asyncio.sleep(delay)
                        else:
                            raise Exception("MCP服务器会话管理错误，请重启MCP服务器")
                    else:
                        if attempt < max_retries - 1:
                            delay = base_delay * (attempt + 1)
                            await self.send_log(f"MCP连接失败，{delay}秒后重试... ({attempt + 1}/{max_retries}): {error_msg}", "warning")
                            await asyncio.sleep(delay)
                        else:
                            raise Exception(f"MCP连接失败: {error_msg}")
            
            # 初始化 Gemini 模型
            await self.send_log("正在初始化 Gemini 模型...", "info")
            if not os.getenv("GOOGLE_API_KEY"):
                raise Exception("GOOGLE_API_KEY 未设置")
            
            self.llm = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                timeout=60,  # 设置模型调用超时
                max_retries=2,  # 设置模型重试次数
                temperature=0.1  # 降低随机性
            )
            
            await self.send_log("✅ 系统初始化完成", "success")
            
            # 为所有agent设置LLM、工具和WebSocket
            for agent in [self.fundamental_agent, self.technical_agent, 
                         self.valuation_agent, self.summary_agent, self.investment_agent]:
                agent.set_llm(self.llm)
                agent.set_tools(self.tools)
                agent.set_websocket(self.websocket)
            
            await self.send_log("Gemini 模型和Agent配置完成", "success")
            self._initialized = True
            return True
            
        except Exception as e:
            await self.send_log(f"❌ 初始化失败: {e}", "error")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self.client, 'close'):
                await self.client.close()
            await self.send_log("MCP连接已清理", "info")
        except Exception as e:
            await self.send_log(f"清理资源时出错: {e}", "warning")
    
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
        await self.send_log("💰 开始生成投资决策...", "info")
        
        try:
            # 使用投资agent进行分析
            result_state = await self.investment_agent.analyze(state)
            
            await self.send_log("✅ 投资决策生成完成", "success")
            return result_state
            
        except Exception as e:
            await self.send_log(f"❌ 投资决策生成失败: {e}", "error")
            state["investment_decision"] = {
                "action": "HOLD",
                "confidence": 0.0,
                "target_price": None,
                "stop_loss": None,
                "position_size": 0.0,
                "holding_period": "medium",
                "risk_level": "medium",
                "reasons": [f"投资决策生成失败: {e}"]
            }
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
        """
        执行完整的分析流程
        
        Args:
            company_name: 公司名称
            stock_code: 股票代码
            
        Returns:
            分析结果字典
        """
        await self.send_log(f"🎯 开始完整分析: {company_name} ({stock_code})", "info")
        
        # 准备初始状态
        initial_state = {
            "company_name": company_name,
            "stock_code": stock_code,
            "current_time_info": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "current_price": 0.0,
            "historical_prices": [],
            "portfolio_state": {},
            "fundamental_analysis": "",
            "technical_analysis": "",
            "valuation_analysis": "",
            "summary_analysis": "",
            "investment_decision": "",
            "final_report": "",
            "messages": []
        }
        
        try:
            # 初始化工具和模型
            await self.send_log("📡 正在初始化分析系统...", "info")
            if not await self.initialize_tools_and_model():
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
            await self.send_log("🔧 构建分析工作流...", "info")
            app = self.create_workflow()
            
            # 运行工作流
            await self.send_log("🚀 开始执行分析工作流（无超时限制）...", "info")
            result = await app.ainvoke(initial_state)
            
            await self.send_log("🎉 所有分析完成！", "success")
            
            # 返回完整的状态结果
            return result
            
        except Exception as e:
            error_msg = f"分析过程中发生错误: {e}"
            await self.send_log(f"❌ {error_msg}", "error")
            return {
                "error": error_msg,
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
        finally:
            # 清理资源（可选，避免频繁清理影响性能）
            # await self.cleanup()
            pass
    
    async def run(self, input_data: dict):
        """
        简化的运行接口，用于回测系统调用
        
        Args:
            input_data: 包含分析所需数据的字典
            
        Returns:
            包含投资决策的结果字典
        """
        try:
            company_name = input_data.get("company_name", "未知公司")
            stock_code = input_data.get("stock_code", "unknown")
            
            await self.send_log(f"📊 开始单次分析: {company_name} ({stock_code})", "info")
            
            # 准备状态
            state = {
                "company_name": company_name,
                "stock_code": stock_code,
                "current_time_info": input_data.get("current_time_info", ""),
                "current_date": input_data.get("current_date", ""),
                "current_price": input_data.get("current_price", 0.0),
                "historical_prices": input_data.get("historical_prices", []),
                "portfolio_state": input_data.get("portfolio_state", {}),
                "fundamental_analysis": "",
                "technical_analysis": "",
                "valuation_analysis": "",
                "summary_analysis": "",
                "investment_decision": "",
                "final_report": "",
                "messages": []
            }
            
            # 确保已初始化
            if not await self.initialize_tools_and_model():
                raise Exception("系统初始化失败")
            
            # 创建简化的工作流（只到投资决策）
            app = self.create_investment_workflow()
            
            await self.send_log(f"🚀 开始单次分析（无超时限制）", "info")
            
            result = await app.ainvoke(state)
            
            # 提取投资决策
            investment_decision = result.get('investment_decision', {})
            
            # 如果是字符串，尝试解析
            if isinstance(investment_decision, str):
                try:
                    import json
                    investment_decision = json.loads(investment_decision)
                except:
                    # 解析失败时提供默认决策
                    investment_decision = {
                        "action": "HOLD",
                        "confidence": 0.5,
                        "target_price": None,
                        "stop_loss": None,
                        "position_size": 0.0,
                        "holding_period": "medium",
                        "risk_level": "medium",
                        "reasons": ["决策解析失败"]
                    }
            
            await self.send_log(f"✅ 投资决策生成完成: {investment_decision.get('action', 'HOLD')}", "success")
            
            return {
                "investment_decision": investment_decision,
                "fundamental_analysis": result.get('fundamental_analysis', ''),
                "technical_analysis": result.get('technical_analysis', ''),
                "valuation_analysis": result.get('valuation_analysis', ''),
                "summary_analysis": result.get('summary_analysis', '')
            }
            
        except Exception as e:
            await self.send_log(f"❌ 单次分析失败: {e}", "error")
            return {
                "investment_decision": {
                    "action": "HOLD",
                    "confidence": 0.5,
                    "target_price": None,
                    "stop_loss": None,
                    "position_size": 0.0,
                    "holding_period": "medium",
                    "risk_level": "medium",
                    "reasons": [f"分析失败: {str(e)}"]
                }
            }
    
    def create_investment_workflow(self):
        """创建简化的投资决策工作流（用于回测）"""
        # 创建状态图
        workflow = StateGraph(MultiAgentState)
        
        # 添加节点
        workflow.add_node("router", self.router_node)
        workflow.add_node("parallel_analysis", self.parallel_analysis)
        workflow.add_node("investment_node", self.investment_agent_node)
        
        # 设置入口点
        workflow.set_entry_point("router")
        
        # 添加边
        workflow.add_edge("router", "parallel_analysis")
        workflow.add_edge("parallel_analysis", "investment_node")
        workflow.add_edge("investment_node", END)
        
        # 编译工作流
        return workflow.compile()

# 测试函数
async def test_multi_agent():
    """测试多agent工作流"""
    workflow = MultiAgentWorkflow()
    result = await workflow.run_analysis("贵州茅台", "sh.600519")
    print("最终报告:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_multi_agent()) 
