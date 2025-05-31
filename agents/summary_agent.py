"""
汇总分析Agent

专门负责整合三个专业Agent的分析结果，生成综合投资报告
"""

from typing import Any, Dict
from .base_agent import BaseAgent
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent


class SummaryAgent(BaseAgent):
    """汇总分析Agent"""
    
    def __init__(self):
        super().__init__(
            name="汇总分析Agent",
            description="综合分析汇总"
        )
    
    def get_result_key(self) -> str:
        """返回汇总分析结果的键名"""
        return "summary_analysis"
    
    async def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行汇总分析任务 - 优化的日志显示
        
        Args:
            state: 包含分析参数的状态字典
            
        Returns:
            更新后的状态字典
        """
        await self.send_log(f"🚀 开始{self.description}...", "info")
        
        try:
            # 创建提示词
            prompt = self.create_prompt(state)
            
            # 汇总agent不需要工具，直接使用LLM
            await self.send_log(f"📝 正在整合三个专业分析结果，生成综合报告...", "info")
            
            # 创建一个不带工具的agent executor用于汇总
            agent_executor = create_react_agent(self.llm, [])  # 空工具列表
            
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
            
            # 使用流式执行来显示思考过程
            async for event in agent_executor.astream_events(
                {"messages": initial_messages}, 
                config=config,
                version="v1"
            ):
                # 处理不同类型的事件
                if event["event"] == "on_chat_model_start":
                    await self.send_log("🧠 开始整合分析结果...", "info")
                
                elif event["event"] == "on_chat_model_stream":
                    # 累积模型生成的思考内容
                    if "chunk" in event["data"]:
                        chunk = event["data"]["chunk"]
                        if hasattr(chunk, 'content') and chunk.content:
                            thinking_buffer += chunk.content
                
                elif event["event"] == "on_chain_start":
                    if "agent" in event["name"].lower():
                        await self.send_log("🔄 **开始生成综合投资报告**", "info")
                
                elif event["event"] == "on_chain_end":
                    if "agent" in event["name"].lower():
                        # 报告生成结束时，输出完整的思考内容
                        thinking_content = flush_thinking()
                        if thinking_content:
                            await self.send_log(f"💭 **整合思考**: \n{thinking_content}", "info")
                        await self.send_log("✨ **综合报告生成完成**", "success")
            
            # 获取最终结果
            await self.send_log("📋 正在整理综合报告...", "info")
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
            
            # 显示报告统计信息
            result_length = len(result)
            word_count = len(result.split())
            lines_count = len(result.split('\n'))
            
            await self.send_log(f"📊 **综合报告完成**: {result_length} 字符，{word_count} 词，{lines_count} 行", "success")
            
            # 分析报告结构
            if "##" in result:
                section_count = result.count("##")
                await self.send_log(f"📑 **报告结构**: 包含 {section_count} 个主要章节", "info")
            
            await self.send_log(f"🎉 **{self.description}** 执行完成！", "success")
            
        except Exception as e:
            await self.send_log(f"❌ **{self.description}失败**: {str(e)}", "error")
            result_key = self.get_result_key()
            state[result_key] = f"{self.description}执行失败: {e}"
        
        return state
    
    def get_analysis_prompt(self, state: Dict[str, Any]) -> str:
        """生成汇总分析的提示词"""
        context = self.get_common_context(state)
        
        # 获取三个专业分析的结果
        fundamental_analysis = state.get('fundamental_analysis', '基本面分析暂未完成')
        technical_analysis = state.get('technical_analysis', '技术分析暂未完成')
        valuation_analysis = state.get('valuation_analysis', '估值分析暂未完成')
        
        return f"""请基于以下三个专业分析的结果，对{state['company_name']}（股票代码：{state['stock_code']}）进行综合分析并生成投资研究报告。
{context}

## 专业分析结果

### 基本面分析结果：
{fundamental_analysis}

### 技术分析结果：
{technical_analysis}

### 估值分析结果：
{valuation_analysis}

## 综合分析任务
请基于以上三个专业分析，进行以下综合分析：

1. **分析结果整合**
   - 总结三个维度分析的核心观点
   - 识别各分析之间的一致性和分歧点
   - 评估不同分析维度的重要性权重

2. **投资价值综合评估**
   - 结合基本面、技术面、估值面给出综合评价
   - 分析公司的投资亮点和风险点
   - 评估短期、中期、长期投资价值

3. **投资建议生成**
   - 基于综合分析给出明确的投资建议（买入/持有/卖出）
   - 提供投资逻辑和理由支撑
   - 设定合理的目标价格和时间期限

4. **风险收益分析**
   - 识别主要投资风险和机会
   - 评估风险收益比
   - 提供风险控制建议

5. **投资策略建议**
   - 针对不同类型投资者提供策略建议
   - 建议合适的投资时机和方式
   - 提供止损止盈参考位

## 输出要求
请生成一份专业的投资研究报告，格式如下：

# {state['company_name']}（{state['stock_code']}）投资分析报告

## 📊 执行摘要
[核心投资观点和建议，2-3段概述]

## 📈 基本面分析要点
[基本面分析核心结论，包括财务状况、盈利能力、成长性等]

## 📉 技术分析要点  
[技术分析核心结论，包括趋势、指标、操作建议等]

## 💰 估值分析要点
[估值分析核心结论，包括估值水平、目标价格等]

## ⚖️ 综合投资评级
**投资建议：** [买入/增持/持有/减持/卖出]
**目标价格：** [具体价格区间]
**投资期限：** [短期/中期/长期]
**风险级别：** [低/中/高]

## 🎯 投资亮点
[列出3-5个主要投资亮点]

## ⚠️ 主要风险
[列出3-5个主要风险因素]

## 🚀 操作策略
### 进场策略
[具体的买入时机和价位建议]

### 持仓管理
[持仓比例和仓位管理建议]

### 退出策略
[止盈止损设置和退出条件]

## 📅 关键节点关注
[需要重点关注的时间节点和事件]

## 🔍 后续跟踪要点
[需要持续跟踪的关键指标和信息]

---
*报告生成时间：{state.get('current_time_info', '')}*
*数据截止时间：{state.get('current_date', '')}*

请确保报告内容客观、专业、可操作，避免过于乐观或悲观的表述。""" 