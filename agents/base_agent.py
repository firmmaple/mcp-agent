"""
基础Agent类

提供所有Agent的基础功能和接口定义
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import datetime


class BaseAgent(ABC):
    """
    基础Agent抽象类
    
    所有专业分析Agent都应该继承这个类
    """
    
    def __init__(self, name: str, description: str):
        """
        初始化基础Agent
        
        Args:
            name: Agent名称
            description: Agent描述
        """
        self.name = name
        self.description = description
        self.llm = None
        self.tools = None
        self.websocket = None
        
    def set_llm(self, llm):
        """设置语言模型"""
        self.llm = llm
        
    def set_tools(self, tools):
        """设置工具集合"""
        self.tools = tools
        
    def set_websocket(self, websocket):
        """设置WebSocket连接用于日志发送"""
        self.websocket = websocket
    
    async def send_log(self, message: str, log_type: str = "info"):
        """发送日志消息"""
        if self.websocket:
            import json
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            await self.websocket.send_text(json.dumps({
                "message": f"[{self.name}] {message}",
                "type": log_type,
                "timestamp": timestamp
            }))
        else:
            print(f"[{self.name}] [{log_type.upper()}] {message}")
    
    def create_prompt(self, state: Dict[str, Any]) -> str:
        """
        创建分析提示词
        
        Args:
            state: 包含分析参数的状态字典
            
        Returns:
            生成的提示词字符串
        """
        return self.get_analysis_prompt(state)
    
    @abstractmethod
    def get_analysis_prompt(self, state: Dict[str, Any]) -> str:
        """
        获取专业分析的提示词
        
        子类必须实现这个方法来定义具体的分析任务
        
        Args:
            state: 包含分析参数的状态字典
            
        Returns:
            分析提示词
        """
        pass
    
    @abstractmethod
    def get_result_key(self) -> str:
        """
        获取结果在状态中的键名
        
        Returns:
            结果键名，如 "fundamental_analysis"
        """
        pass
    
    async def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行分析任务，显示优化的React中间过程
        
        Args:
            state: 包含分析参数的状态字典
            
        Returns:
            更新后的状态字典
        """
        await self.send_log(f"🚀 开始{self.description}...", "info")
        
        try:
            # 创建提示词
            prompt = self.create_prompt(state)
            
            # 创建agent executor
            agent_executor = create_react_agent(self.llm, self.tools)
            
            # 准备初始消息
            initial_messages = [HumanMessage(content=prompt)]
            config = {"configurable": {"thread_id": "1"}}
            
            # 初始化思考内容累积器
            thinking_buffer = ""
            
            def flush_thinking():
                """输出累积的思考内容"""
                nonlocal thinking_buffer
                if thinking_buffer.strip():
                    # 清理和格式化思考内容
                    cleaned_thinking = thinking_buffer.strip()
                    # 删除多余的换行，但保留段落结构
                    cleaned_thinking = '\n'.join(line.strip() for line in cleaned_thinking.split('\n') if line.strip())
                    
                    # 只显示有意义的思考内容，过滤掉重复的提示
                    if len(cleaned_thinking) > 20 and not cleaned_thinking.startswith("我需要"):
                        return cleaned_thinking
                    
                thinking_buffer = ""
                return None
            
            # 执行分析并显示优化的中间过程
            await self.send_log(f"⚡ 开始执行{self.description}，实时显示关键步骤", "info")
            
            # 使用流式执行来捕获中间步骤
            tool_count = 0
            reasoning_count = 0
            
            async for event in agent_executor.astream_events(
                {"messages": initial_messages}, 
                config=config,
                version="v1"
            ):
                # 处理不同类型的事件
                if event["event"] == "on_chat_model_start":
                    await self.send_log("🧠 模型开始分析思考...", "info")
                
                elif event["event"] == "on_chat_model_stream":
                    # 累积模型生成的思考内容
                    if "chunk" in event["data"]:
                        chunk = event["data"]["chunk"]
                        if hasattr(chunk, 'content') and chunk.content:
                            thinking_buffer += chunk.content
                
                elif event["event"] == "on_tool_start":
                    # 工具调用前，输出完整的思考过程
                    thinking_content = flush_thinking()
                    if thinking_content:
                        await self.send_log(f"💭 **思考过程** \n{thinking_content}", "info")
                    
                    tool_count += 1
                    tool_name = event["name"]
                    tool_input = event["data"].get("input", {})
                    
                    # 显示完整的工具参数
                    await self.send_log(f"🔧 **工具调用 #{tool_count} ** \n- 工具: `{tool_name}` \n- 参数: {tool_input}", "warning")
                    # await self.send_log(f"📝 **参数**: {tool_input}", "info")
                
                elif event["event"] == "on_tool_end":
                    tool_name = event["name"]
                    tool_output = event["data"].get("output", "")
                    
                    # 显示完整的工具输出
                    # await self.send_log(f"✅ **工具完成**: `{tool_name}`", "success")
                    # await self.send_log(f"📊 **完整结果**: {tool_output}", "info")
                
                elif event["event"] == "on_chain_start":
                    if "agent" in event["name"].lower():
                        reasoning_count += 1
                        await self.send_log(f"🔄 **推理循环 #{reasoning_count}** 开始", "info")
                
                elif event["event"] == "on_chain_end":
                    if "agent" in event["name"].lower():
                        # 推理循环结束时，输出最后的思考内容
                        thinking_content = flush_thinking()
                        if thinking_content:
                            await self.send_log(f"💭 **最终思考 #{reasoning_count}** \n{thinking_content}", "info")
                        await self.send_log(f"✨ **推理循环 #{reasoning_count}** 完成", "success")
            
            # 获取最终结果
            await self.send_log("📋 正在整理分析结果...", "info")
            final_response = await agent_executor.ainvoke({"messages": initial_messages})
            
            # 提取结果
            if final_response and "messages" in final_response:
                last_message = final_response["messages"][-1]
                result = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                result = str(final_response)
            
            # 存储结果
            result_key = self.get_result_key()
            state[result_key] = result
            
            # 显示分析摘要
            result_length = len(result)
            word_count = len(result.split())
            await self.send_log(f"📊 **分析完成**: 生成 {result_length} 字符，约 {word_count} 词", "success")
            
            # 显示完整结果
            await self.send_log(f"📄 **完整分析结果** \n{result}", "success")
            
            await self.send_log(f"🎉 **{self.description}** 执行完成！", "success")
            
        except Exception as e:
            await self.send_log(f"❌ **{self.description}失败**: {str(e)}", "error")
            result_key = self.get_result_key()
            state[result_key] = f"{self.description}执行失败: {e}"
        
        return state
    
    def get_common_context(self, state: Dict[str, Any]) -> str:
        """
        获取通用的上下文信息
        
        Args:
            state: 状态字典
            
        Returns:
            通用上下文字符串
        """
        return f"""
当前时间：{state.get('current_time_info', '')}
当前日期：{state.get('current_date', '')}
公司名称：{state.get('company_name', '')}
股票代码：{state.get('stock_code', '')}
""" 