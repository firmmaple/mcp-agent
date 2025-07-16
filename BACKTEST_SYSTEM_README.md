# 简化的回测系统

## 系统架构

重新设计的回测系统采用清晰的数据流架构：

```
Multi-Agent Workflow → Summary Agent → Investment Agent → JSON决策 → 回测系统
```

### 核心组件

1. **Investment Agent** (`agents/investment_agent.py`)
   - 根据Summary Agent的综合分析结果生成JSON格式的投资决策
   - 输出标准化的投资方案，包含操作类型、目标价格、信心度等

2. **回测系统** (`backtest_system.py`)
   - 定期运行multi_agent_workflow（每天/每周）
   - 处理JSON投资决策
   - 执行虚拟交易
   - 追踪投资组合表现

3. **Multi-Agent Workflow** (`multi_agent_workflow.py`)
   - 协调所有Agent的工作
   - 提供统一的`run()`接口
   - 返回包含所有分析结果的字典

## JSON投资决策格式

Investment Agent生成的JSON决策包含以下字段：

```json
{
    "action": "BUY|SELL|HOLD",
    "confidence": 0.0-1.0,
    "target_price": 价格或null,
    "stop_loss": 价格或null,
    "position_size": 0.0-1.0,
    "holding_period": "short|medium|long",
    "risk_level": "low|medium|high",
    "reasons": ["理由1", "理由2", "理由3"]
}
```

## 使用方法

### 基本使用

```python
from backtest_system import BacktestSystem

# 创建回测系统
backtest = BacktestSystem(initial_capital=100000.0)

# 运行回测
results = await backtest.run_backtest(
    stock_code="sh.600519",
    company_name="贵州茅台",
    start_date="2024-01-01",
    end_date="2024-06-30",
    frequency="weekly"  # 每周运行一次workflow
)

# 查看结果
backtest.print_summary(results)
```

### 频率设置

- `"daily"` - 每天运行一次workflow
- `"weekly"` - 每周运行一次workflow
- `"monthly"` - 每月运行一次workflow

### 结果数据

回测结果包含：

- `total_return` - 总收益率
- `max_drawdown` - 最大回撤
- `sharpe_ratio` - 夏普比率
- `volatility` - 波动率
- `transactions` - 交易记录
- `daily_values` - 每日资产价值

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行示例：
```bash
python simple_backtest_example.py
```

## 系统特点

### 优势

1. **简化的架构** - 删除了多余的复杂功能
2. **标准化的数据流** - JSON格式的投资决策
3. **灵活的频率设置** - 支持每天、每周、每月运行
4. **清晰的接口** - 统一的`run()`方法
5. **自动化的决策执行** - 无需手动干预

### 工作流程

1. **定期触发** - 根据设置的频率运行workflow
2. **获取分析** - 运行完整的multi-agent分析
3. **生成决策** - Investment Agent输出JSON格式的决策
4. **执行交易** - 根据决策执行虚拟交易
5. **追踪表现** - 记录投资组合价值变化

## 注意事项

1. **数据源** - 使用baostock API获取历史数据
2. **交易限制** - 只在高信心度(>0.6)时买入
3. **风险控制** - 支持止损和仓位管理
4. **按手交易** - 股票交易按100股的倍数进行

## 扩展性

系统设计为可扩展的架构，可以轻松添加：

- 新的投资决策逻辑
- 更多的风险控制措施
- 不同的交易策略
- 多股票组合管理

---

*系统版本：2025.01* 