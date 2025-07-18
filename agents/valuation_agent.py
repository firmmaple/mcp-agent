"""
估值分析Agent

专门负责股票估值分析，包括估值指标、相对估值、绝对估值等
"""

from typing import Any, Dict
from .base_agent import BaseAgent


class ValuationAgent(BaseAgent):
    """估值分析Agent"""
    
    def __init__(self, verbose: bool = True):
        super().__init__(
            name="估值分析Agent",
            description="估值分析",
            verbose=verbose
        )
    
    def get_result_key(self) -> str:
        """返回估值分析结果的键名"""
        return "valuation_analysis"
    
    def get_analysis_prompt(self, state: Dict[str, Any]) -> str:
        """生成估值分析的提示词"""
        context = self.get_common_context(state)
        
        return f"""请分析{state['company_name']}（股票代码：{state['stock_code']}）的估值情况。
{context}

请进行以下估值分析：

## 分析任务
1. **基本估值指标获取**
   - 获取公司基本信息（市值、股价、总股本等）
   - 获取当前主要估值指标（市盈率、市净率、市销率等）
   - 收集最新财务数据用于估值计算

2. **相对估值分析**
   - 市盈率（P/E）分析：动态、静态、预期PE
   - 市净率（P/B）分析：与净资产价值比较
   - 市销率（P/S）分析：与营收规模比较
   - PEG比率分析：考虑成长性的估值指标

3. **行业估值对比**
   - 获取同行业公司的估值指标
   - 与行业平均估值水平进行比较
   - 分析公司在行业中的估值位置
   - 评估估值溢价或折价的合理性

4. **历史估值分析**
   - 分析公司历史估值水平变化趋势
   - 识别历史估值的高点和低点
   - 判断当前估值在历史区间的位置
   - 分析估值波动的驱动因素

5. **股息估值分析**
   - 获取并分析股息数据和股息收益率
   - 计算股息贴现模型（DDM）估值
   - 分析股息支付的可持续性
   - 评估股息投资价值

6. **绝对估值方法**
   - DCF（现金流贴现）模型估值
   - 计算公司的内在价值
   - 敏感性分析（折现率、增长率变化影响）
   - 与市场价格对比分析

7. **综合估值判断**
   - 整合各种估值方法的结果
   - 给出目标价格区间
   - 评估投资价值和风险收益比
   - 提供估值相关的投资建议

## 分析要求
- 使用可用的工具获取实际数据进行分析，而不是基于假设
- 如果某些数据无法获取，请尝试使用不同的工具或参数组合
- 基于可用信息提供尽可能全面的估值分析
- 提供量化的估值结果和定性的价值判断
- 考虑估值方法的适用性和局限性

## 输出格式
请按照以下结构输出分析结果：

### 估值分析概述
[公司当前估值水平整体评估]

### 主要估值指标分析
[P/E、P/B、P/S、PEG等指标详细分析]

### 行业估值对比
[与同行业公司估值比较分析]

### 历史估值分析
[历史估值水平变化和当前位置分析]

### 股息价值分析
[股息收益率和股息投资价值分析]

### 内在价值评估
[DCF等绝对估值方法计算结果]

### 目标价格预测
[基于估值分析的合理价格区间]

### 估值风险因素
[影响估值的主要风险和不确定性]

### 投资价值结论
[基于估值分析的投资建议和策略]

请确保分析客观专业，提供具体的数值参考和价格目标。""" 