"""
投资决策Agent

基于综合分析报告和市场数据生成具体的投资决策
"""

from typing import Any, Dict
from .base_agent import BaseAgent
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import json
import re


class InvestmentAgent(BaseAgent):
    """投资决策Agent"""
    
    def __init__(self, verbose: bool = True):
        super().__init__(
            name="投资决策Agent",
            description="智能投资决策生成",
            verbose=verbose
        )
    
    def get_result_key(self) -> str:
        """返回投资决策结果的键名"""
        return "investment_decision"
    
    async def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行投资决策任务，生成JSON格式的投资决策
        
        Args:
            state: 包含分析参数的状态字典
            
        Returns:
            更新后的状态字典
        """
        await self.send_log(f"🚀 开始{self.description}...", "info")
        
        try:
            # 创建提示词
            prompt = self.create_prompt(state)
            
            await self.send_log(f"📝 正在基于综合分析和市场数据生成投资决策...", "info")
            
            # 创建一个不带工具的agent executor
            agent_executor = create_react_agent(self.llm, [])
            
            # 准备初始消息
            initial_messages = [HumanMessage(content=prompt)]
            config = {"configurable": {"thread_id": "1"}}
            
            # 获取AI响应
            final_response = await agent_executor.ainvoke({"messages": initial_messages})
            
            # 提取结果
            if final_response and "messages" in final_response:
                last_message = final_response["messages"][-1]
                if hasattr(last_message, 'content'):
                    result = last_message.content
                else:
                    result = str(last_message)
            else:
                result = str(final_response)
            
            # 解析JSON投资决策
            decision_json = self.extract_json_decision(result, state)
            
            # 存储结果
            result_key = self.get_result_key()
            state[result_key] = decision_json
            
            # 显示决策统计信息
            await self.send_log(f"📊 **投资决策完成**: {decision_json.get('action', 'N/A')} | 目标价格: {decision_json.get('target_price', 'N/A')} | 信心度: {decision_json.get('confidence', 'N/A')}", "success")
            
            await self.send_log(f"🎉 **{self.description}** 执行完成！", "success")
            
        except Exception as e:
            await self.send_log(f"❌ **{self.description}失败**: {str(e)}", "error")
            result_key = self.get_result_key()
            state[result_key] = self.get_default_decision()
        
        return state
    
    def extract_json_decision(self, response_text: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        从AI响应中提取JSON投资决策
        
        Args:
            response_text: AI的响应文本
            state: 状态信息，包含价格等数据
            
        Returns:
            JSON格式的投资决策
        """
        try:
            # 尝试直接解析JSON
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                decision = json.loads(json_str)
                return self.validate_decision(decision, state)
            
            # 如果没有找到JSON，尝试从文本中提取信息
            return self.parse_text_to_json(response_text, state)
            
        except Exception as e:
            print(f"提取JSON决策时发生错误: {e}")
            return self.get_default_decision()
    
    def parse_text_to_json(self, text: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        从文本中解析投资决策信息并转换为JSON
        
        Args:
            text: 包含决策信息的文本
            state: 状态信息
            
        Returns:
            JSON格式的投资决策
        """
        decision = self.get_default_decision()
        
        # 提取投资动作
        if re.search(r'买入|BUY|建仓|增持', text, re.IGNORECASE):
            decision["action"] = "BUY"
        elif re.search(r'卖出|SELL|减仓|清仓', text, re.IGNORECASE):
            decision["action"] = "SELL"
        else:
            decision["action"] = "HOLD"
        
        # 提取目标价格
        price_match = re.search(r'目标价格?[：:]\s*([0-9]+\.?[0-9]*)', text)
        if price_match:
            decision["target_price"] = float(price_match.group(1))
        
        # 提取止损价格
        stop_loss_match = re.search(r'止损价?[：:]\s*([0-9]+\.?[0-9]*)', text)
        if stop_loss_match:
            decision["stop_loss"] = float(stop_loss_match.group(1))
        
        # 提取仓位
        position_match = re.search(r'仓位[：:]\s*([0-9]+\.?[0-9]*)%', text)
        if position_match:
            decision["position_size"] = float(position_match.group(1)) / 100.0
        
        # 提取信心度
        confidence_match = re.search(r'信心度[：:]\s*([0-9]+\.?[0-9]*)', text)
        if confidence_match:
            decision["confidence"] = float(confidence_match.group(1)) / 10.0
        
        return self.validate_decision(decision, state)
    
    def validate_decision(self, decision: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证并修正投资决策数据
        
        Args:
            decision: 投资决策字典
            state: 状态信息
            
        Returns:
            验证后的投资决策
        """
        # 确保必要的字段存在
        default_decision = self.get_default_decision()
        for key, default_value in default_decision.items():
            if key not in decision:
                decision[key] = default_value
        
        # 验证数据范围
        if decision["confidence"] > 1.0:
            decision["confidence"] = decision["confidence"] / 10.0
        decision["confidence"] = max(0.0, min(1.0, decision["confidence"]))
        
        if decision["position_size"] > 1.0:
            decision["position_size"] = decision["position_size"] / 100.0
        decision["position_size"] = max(0.0, min(1.0, decision["position_size"]))
        
        # 验证动作
        if decision["action"] not in ["BUY", "SELL", "HOLD"]:
            decision["action"] = "HOLD"
        
        # 获取当前价格信息
        current_price = state.get('current_price', None)
        if current_price:
            decision["current_price"] = current_price
            
            # 如果没有目标价格，设置合理的目标价格
            if not decision["target_price"]:
                if decision["action"] == "BUY":
                    decision["target_price"] = current_price * 1.1  # 10%涨幅目标
                elif decision["action"] == "SELL":
                    decision["target_price"] = current_price * 0.9  # 10%跌幅目标
            
            # 如果没有止损价格，设置合理的止损价格
            if not decision["stop_loss"]:
                if decision["action"] == "BUY":
                    decision["stop_loss"] = current_price * 0.95  # 5%止损
                elif decision["action"] == "SELL":
                    decision["stop_loss"] = current_price * 1.05  # 5%止损
        
        # 智能决策调整 - 基于投资组合状态
        portfolio_state = state.get('portfolio_state', {})
        current_shares = portfolio_state.get('current_shares', 0)
        cash_ratio = portfolio_state.get('available_cash_ratio', 1.0)
        unrealized_pnl_percent = portfolio_state.get('unrealized_pnl_percent', 0.0)
        
        # 如果当前没有持股且信心度较高，应该买入
        if current_shares == 0 and decision["confidence"] > 0.6:
            decision["action"] = "BUY"
            decision["position_size"] = min(0.4, decision["confidence"] * 0.6)  # 根据信心度调整仓位
            decision["reasons"].append("当前空仓，基于高信心度买入")
        
        # 如果当前持股且浮动盈亏不佳，考虑止损
        elif current_shares > 0 and unrealized_pnl_percent < -5:
            if decision["confidence"] < 0.4:
                decision["action"] = "SELL"
                decision["position_size"] = 0.5  # 部分止损
                decision["reasons"].append("浮动亏损过大，止损减仓")
        
        # 如果当前持股且盈利较好，考虑部分获利了结
        elif current_shares > 0 and unrealized_pnl_percent > 15:
            if decision["confidence"] < 0.7:
                decision["action"] = "SELL"
                decision["position_size"] = 0.3  # 部分获利
                decision["reasons"].append("浮动盈利较好，部分获利了结")
        
        # 如果现金比例过高且分析积极，积极买入
        elif cash_ratio > 0.8 and decision["confidence"] > 0.7:
            decision["action"] = "BUY"
            decision["position_size"] = min(0.5, decision["confidence"] * 0.7)
            decision["reasons"].append("现金比例过高，积极买入")
        
        return decision
    
    def get_default_decision(self) -> Dict[str, Any]:
        """
        获取默认的投资决策
        
        Returns:
            默认投资决策
        """
        return {
            "action": "HOLD",
            "confidence": 0.5,
            "target_price": None,
            "stop_loss": None,
            "position_size": 0.0,
            "holding_period": "medium",
            "risk_level": "medium",
            "reasons": ["数据不足，保持观望"],
            "current_price": None
        }
    
    def get_analysis_prompt(self, state: Dict[str, Any]) -> str:
        """生成投资决策的提示词"""
        context = self.get_common_context(state)
        
        # 获取综合分析结果
        summary_analysis = state.get('summary_analysis', '综合分析暂未完成')
        
        # 获取市场数据
        current_price = state.get('current_price', '未知')
        historical_prices = state.get('historical_prices', [])
        portfolio_state = state.get('portfolio_state', {})
        
        # 构建价格趋势信息
        price_trend = ""
        if historical_prices and len(historical_prices) > 1:
            recent_change = ((historical_prices[-1] - historical_prices[0]) / historical_prices[0]) * 100
            if recent_change > 2:
                price_trend = f"价格上涨趋势 (+{recent_change:.1f}%)"
            elif recent_change < -2:
                price_trend = f"价格下跌趋势 ({recent_change:.1f}%)"
            else:
                price_trend = f"价格相对稳定 ({recent_change:.1f}%)"
        
        # 构建投资组合状态信息
        portfolio_info = ""
        if portfolio_state:
            portfolio_info = f"""
- **当前持股**: {portfolio_state.get('current_shares', 0)}股
- **持股价值**: {portfolio_state.get('stock_value', 0):.2f}元
- **现金余额**: {portfolio_state.get('cash', 0):.2f}元
- **总资产**: {portfolio_state.get('total_value', 0):.2f}元
- **初始资金**: {portfolio_state.get('initial_capital', 0):.2f}元
- **平均成本**: {portfolio_state.get('avg_cost', 0):.2f}元/股
- **浮动盈亏**: {portfolio_state.get('unrealized_pnl', 0):.2f}元 ({portfolio_state.get('unrealized_pnl_percent', 0):.1f}%)
- **资金使用率**: {portfolio_state.get('capital_usage', 0):.1%}
- **现金比例**: {portfolio_state.get('available_cash_ratio', 0):.1%}
- **持股比例**: {portfolio_state.get('stock_ratio', 0):.1%}
- **历史交易次数**: {portfolio_state.get('total_trades', 0)}次"""
        
        return f"""基于以下综合分析报告、市场数据和投资组合状态，为{state['company_name']}（股票代码：{state['stock_code']}）生成具体的投资决策。

{context}

## 市场数据信息：
- **当前价格**: {current_price}元
- **价格趋势**: {price_trend}
- **历史价格**: {historical_prices}

## 投资组合状态：
{portfolio_info}

## 综合分析报告：
{summary_analysis}

## 投资决策要求

请基于上述分析报告和市场数据，生成一个具体的投资决策。请特别注意：

1. **积极的投资态度** - 不要总是选择HOLD，要根据分析结果做出积极的决策
2. **具体的仓位管理** - 明确买入或卖出的具体比例
3. **合理的价格目标** - 基于当前价格设定合理的目标价和止损价
4. **清晰的决策理由** - 说明为什么要做出这个决策

## 决策指导原则：

**基于投资组合状态的决策逻辑：**
- 如果当前持股为0且分析积极（信心度>0.6），应该考虑买入
- 如果当前持股>0且浮动盈亏<-5%，应该考虑止损卖出
- 如果当前持股>0且浮动盈亏>10%，应该考虑部分获利了结
- 如果现金比例>80%且分析积极，应该积极买入
- 如果持股比例>70%且分析转向负面，应该考虑减仓

**具体决策标准：**
- 买入：当前持股少 + 分析积极 + 现金充足
- 卖出：当前持股多 + 分析负面 或 止损条件触发
- 持有：当前仓位合理 + 分析中性
- 仓位大小应该与信心度和当前持仓状态成正比

## 输出格式
请直接输出JSON格式的投资决策：

```json
{{
    "action": "BUY|SELL|HOLD",
    "confidence": 0.0-1.0,
    "target_price": 具体价格,
    "stop_loss": 具体价格,
    "position_size": 0.0-1.0,
    "holding_period": "short|medium|long",
    "risk_level": "low|medium|high",
    "reasons": ["具体理由1", "具体理由2", "具体理由3"]
}}
```

注意：
1. 要根据综合分析的结果做出积极的决策
2. 所有价格都应该是具体的数值
3. 信心度要反映分析的确定性
4. 理由要具体且有说服力
""" 