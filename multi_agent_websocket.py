from multi_agent_workflow import MultiAgentWorkflow
from fastapi import WebSocket
import json
import datetime
import re

class MultiAgentWebSocketManager:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.workflow = MultiAgentWorkflow(websocket)
    
    async def send_log(self, message: str, log_type: str = "info"):
        """发送日志消息到前端"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        await self.websocket.send_text(json.dumps({
            "message": message,
            "type": log_type,
            "timestamp": timestamp
        }))
    
    def parse_query(self, query: str):
        """解析用户查询，提取公司名称和股票代码"""
        # 尝试提取股票代码（支持多种格式）
        code_patterns = [
            r'[（(]([a-zA-Z]{1,2}[\.\-]?\d{6})[）)]',  # (sh.600519) 或 (SH.600519)
            r'[（(](\d{6})[）)]',  # (600519)
            r'([a-zA-Z]{1,2}[\.\-]?\d{6})',  # sh.600519 或 SH.600519
            r'代码[：:]?\s*([a-zA-Z]{1,2}[\.\-]?\d{6})',  # 代码：sh.600519
            r'代码[：:]?\s*(\d{6})',  # 代码：600519
        ]
        
        stock_code = None
        for pattern in code_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                stock_code = match.group(1)
                break
        
        # 尝试提取公司名称
        company_patterns = [
            r'分析\s*([^（(]+?)[（(]',  # 分析贵州茅台(
            r'([^，,。.！!？?]+?)[（(]',  # 贵州茅台(
            r'请.*分析\s*([^，,。.！!？?\s]+)',  # 请分析贵州茅台
        ]
        
        company_name = None
        for pattern in company_patterns:
            match = re.search(pattern, query)
            if match:
                company_name = match.group(1).strip()
                break
        
        # 如果没有提取到，尝试一些默认值
        if not company_name and stock_code:
            if "600519" in stock_code:
                company_name = "贵州茅台"
            elif "000858" in stock_code:
                company_name = "五粮液"
            elif "002415" in stock_code:
                company_name = "海康威视"
        
        return company_name, stock_code
    
    async def execute_multi_agent_analysis(self, query: str):
        """执行多agent分析"""
        try:
            await self.send_log("开始解析查询内容...", "info")
            
            # 解析查询
            company_name, stock_code = self.parse_query(query)
            
            if not company_name or not stock_code:
                await self.send_log("无法从查询中提取公司名称或股票代码", "error")
                await self.send_log(f"提取到的公司名称: {company_name}", "info")
                await self.send_log(f"提取到的股票代码: {stock_code}", "info")
                await self.send_log("请确保查询格式如: '分析贵州茅台(sh.600519)的投资价值'", "warning")
                
                # 提供默认值
                if not company_name:
                    company_name = "目标公司"
                if not stock_code:
                    stock_code = "sh.600519"  # 默认茅台
                    await self.send_log(f"使用默认股票代码: {stock_code}", "warning")
            
            await self.send_log(f"解析结果 - 公司名称: {company_name}, 股票代码: {stock_code}", "success")
            
            # 运行多agent分析
            await self.send_log("启动多Agent分析系统...", "info")
            final_report = await self.workflow.run_analysis(company_name, stock_code)
            
            if final_report:
                await self.send_log("=== 综合分析报告 ===", "success")
                await self.send_log(f"📄 最终报告:\n{final_report}", "success")
                # # 分段发送长文本报告
                # if len(final_report) > 2000:
                #     parts = [final_report[i:i+2000] for i in range(0, len(final_report), 2000)]
                #     for i, part in enumerate(parts):
                #         await self.send_log(f"📄 报告 ({i+1}/{len(parts)}): {part}", "success")
                # else:
                #     await self.send_log(f"📄 最终报告: {final_report}", "success")
            else:
                await self.send_log("未能生成最终报告", "error")
            
            # 发送执行完成信号
            await self.send_log("执行完成", "execution_complete")
            
        except Exception as e:
            await self.send_log(f"执行过程中发生错误: {e}", "error")
            import traceback
            error_details = traceback.format_exc()
            await self.send_log(f"错误详情: {error_details}", "error")
            await self.send_log("执行完成", "execution_complete")

# 测试函数
async def test_parse_query():
    """测试查询解析功能"""
    manager = MultiAgentWebSocketManager(None)
    
    test_queries = [
        "分析贵州茅台(sh.600519)的投资价值",
        "请帮我分析贵州茅台（600519）",
        "分析五粮液(sz.000858)",
        "请分析海康威视 代码：002415",
        "分析茅台股票 sh.600519",
    ]
    
    for query in test_queries:
        company, code = manager.parse_query(query)
        print(f"查询: {query}")
        print(f"  公司: {company}, 代码: {code}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_parse_query()) 