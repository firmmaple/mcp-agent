# 🤖 多Agent智能股票分析与回测系统

一个基于 **LangGraph** 和 **FastAPI** 的完整股票投资解决方案，集成了**实时分析**和**历史回测**两大核心功能。采用多Agent并行架构，提供专业级的基本面、技术面、估值分析，并支持完整的投资策略历史验证。

## 🌟 系统特色

### 📊 双核心模式
- **💡 实时分析模式**: 单次深度分析，3-5分钟生成专业投资报告
- **📈 智能回测模式**: 历史策略验证，自动化投资决策回测与性能评估

### 🤖 多Agent并行分析引擎  
- **📈 基本面分析Agent**: 财务状况、盈利能力、成长性深度分析
- **📉 技术分析Agent**: 价格趋势、技术指标、支撑阻力位分析  
- **💰 估值分析Agent**: 估值指标、行业对比、投资价值评估
- **📝 汇总分析Agent**: 整合专业分析，生成综合投资建议
- **💡 投资决策Agent**: 基于多维分析生成标准化JSON投资决策

### 🚀 核心优势
- 🤖 **智能多Agent系统**: 基于 LangGraph 的并行分析架构
- 📊 **全面A股数据**: MCP协议连接，35+专业数据分析工具  
- 💹 **三维度分析**: 基本面 + 技术面 + 估值分析并行执行
- 🔄 **实时通信**: WebSocket 实时进度监控和日志展示
- 📈 **可视化回测**: Chart.js 高清图表，实时进度跟踪
- 📄 **专业报告**: Markdown格式投资分析报告，支持一键导出
- 🎯 **智能解析**: 自动识别股票代码和公司名称
- ⚡ **性能优化**: 连接池+智能缓存，实现85%+ 速度提升
- 📱 **现代界面**: 响应式Web设计，完美支持移动设备

## 🏗️ 系统架构

### 🔄 完整工作流
```
实时分析模式:
用户查询 → 智能解析 → 并行Agent分析 → 汇总报告 → 可视化展示
                   ├── 基本面Agent (财务数据分析)
                   ├── 技术面Agent (技术指标分析) 
                   └── 估值Agent (估值对比分析)
                           ↓
                   汇总Agent → 综合投资报告

智能回测模式:  
配置参数 → 时间序列生成 → 循环执行多Agent分析 → JSON决策生成 → 虚拟交易执行 → 性能统计分析
```

### 🛠️ 技术架构
```
前端界面层 (HTML5 + CSS3 + JavaScript + Chart.js)
    ↓ WebSocket实时通信
API服务层 (FastAPI实时分析 + Flask回测服务)  
    ↓
多Agent工作流引擎 (multi_agent_workflow.py)
    ├── MCP连接池 (30秒超时 + 智能重试)
    ├── Gemini模型 (60秒超时 + 2次重试)
    └── 智能缓存系统 (价格缓存 + 分析缓存)
    ↓
数据层 (35个MCP专业工具 + 回测系统)
```

### 💻 技术栈
- **后端框架**: FastAPI + Flask + LangGraph + LangChain + asyncio
- **前端技术**: 原生 HTML/CSS/JavaScript + WebSocket + Chart.js 
- **AI模型**: Google Gemini 2.0 Flash (优化超时 + 重试机制)  
- **数据源**: MCP Server (35+ A股专业数据工具)
- **回测引擎**: 多频率决策支持 + 虚拟交易系统 + 综合性能统计

## 📦 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd mcp-agent

# 安装依赖  
pip install -r requirements.txt
```

### 2. 环境配置
创建 `.env` 文件：
```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### 3. 启动服务

#### 🚀 实时分析模式
```bash
python app.py
```
**访问地址**: http://localhost:8000/static/index.html

#### 📊 回测分析模式  
```bash
python start_backtest_system.py
# 或者
python backtest_api.py
```
**访问地址**: http://localhost:5000

## 💡 详细使用指南

### 🔍 实时分析模式

#### 功能特点
- **⚡ 快速分析**: 3-5分钟完成完整的多维度分析
- **📊 实时监控**: WebSocket实时显示分析进度和关键步骤
- **📄 专业报告**: 生成完整的投资分析报告
- **🎯 智能识别**: 自动解析公司名称和股票代码

#### 访问地址
- **🌐 分析界面**: http://localhost:8000/static/index.html
- **📋 API文档**: http://localhost:8000/docs  
- **🔌 WebSocket**: ws://localhost:8000/ws/multi

#### 查询格式
**标准格式**: `请分析[公司名称]([股票代码])的投资价值`

**实例查询**:
```
请分析贵州茅台(sh.600519)的投资价值
请分析比亚迪(sz.002594)的投资价值  
请分析宁德时代(sz.300750)的投资价值
请分析海康威视(sz.002415)的投资价值
```

**支持的股票代码格式**:
- `sh.600519` (上海证券交易所主板)
- `sz.000858` (深圳证券交易所主板)  
- `sz.300750` (创业板)

### 📈 智能回测模式

#### ⚡ 性能优化配置表

| 模式 | 时间范围 | 决策频率 | 决策点数量 | 预计耗时 | 适用场景 | 推荐度 |
|------|----------|----------|------------|----------|----------|---------|
| ⚡ **超快速** | 3个月 | 每月决策 | 3个点 | 2-3分钟 | 快速体验测试 | ⭐⭐⭐⭐⭐ |  
| 🚀 **快速** | 3个月 | 每周决策 | 12个点 | 5-8分钟 | 日常策略验证 | ⭐⭐⭐⭐⭐ |
| 📊 **标准** | 6个月 | 每周决策 | 24个点 | 10-15分钟 | 详细策略分析 | ⭐⭐⭐⭐ |
| 📈 **深度** | 12个月 | 每周决策 | 48个点 | 20-30分钟 | 长期策略研究 | ⭐⭐⭐ |
| ⚠️ **详细** | 3个月 | 每日决策 | 90个点 | 30-45分钟 | 高频策略研究 | ⭐⭐ |

#### 🎯 回测操作流程

**第一步：配置回测参数**
1. **选择股票**: 
   - 手动输入公司名称和股票代码
   - 或使用快速选择按钮（贵州茅台、比亚迪、宁德时代等）
2. **设置时间范围**: 
   - 💡 **首次使用建议**: 3个月时间范围
   - 选择回测开始日期和结束日期
3. **配置策略参数**: 
   - 设置初始资金(≥10,000元)
   - 💡 **推荐选择**: "每周决策"获得速度与精度的最佳平衡
   - ⚠️ **避免选择**: "每日决策"会显著增加耗时

**第二步：启动回测分析**  
1. 点击 "🚀 开始回测" 按钮
2. 系统自动显示预计总耗时
3. 实时进度条显示当前分析状态和剩余时间
4. 可随时点击 "⏹️ 停止回测" 中断操作

**第三步：分析结果展示**
- **📊 关键指标卡片**: 总收益率、最大回撤、夏普比率、交易胜率
- **📈 可视化图表**: 资产价值走势图、收益分布直方图  
- **📋 详细交易记录**: 包含价格、数量、信心度的完整买卖记录
- **💾 一键导出**: 支持JSON格式结果下载

#### 💻 编程接口使用

```python
from backtest_system import BacktestSystem

# 创建回测系统实例
backtest = BacktestSystem(initial_capital=100000.0)

# 执行回测分析
results = await backtest.run_backtest(
    stock_code="sh.600519",        # 股票代码
    company_name="贵州茅台",        # 公司名称
    start_date="2024-01-01",       # 开始日期
    end_date="2024-06-30",         # 结束日期
    frequency="weekly"             # 决策频率: daily/weekly/monthly
)

# 结果分析
print(f"总收益率: {results['total_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")  
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
print(f"交易胜率: {results['win_rate']:.1%}")
```

## 📊 投资决策标准格式

系统生成的标准化JSON投资决策格式：

```json
{
    "action": "BUY|SELL|HOLD",           // 操作类型
    "confidence": 0.85,                   // 信心度 (0.0-1.0)
    "target_price": 1800.0,             // 目标价格
    "stop_loss": 1600.0,                // 止损价格  
    "position_size": 0.3,               // 建议仓位 (0.0-1.0)
    "holding_period": "medium",          // 持有期限: short/medium/long
    "risk_level": "medium",              // 风险等级: low/medium/high
    "reasons": [                         // 决策依据
        "基本面强劲，ROE持续增长",
        "技术面突破关键阻力位", 
        "估值合理，PE低于行业平均"
    ]
}
```

## 📈 分析报告示例

系统生成的专业投资分析报告结构：

```markdown
# 贵州茅台(sh.600519) 投资分析报告

## 📊 执行摘要
基于多Agent并行分析，贵州茅台当前展现出优异的投资价值...
[AI生成的核心投资观点和策略建议]

## 📈 基本面分析要点
**财务健康度**: 优秀 | **盈利能力**: 强劲 | **成长性**: 稳定
- ROE连续5年超过20%，盈利能力行业领先
- 营收和净利润保持稳定增长趋势
- 现金流充沛，财务结构健康

## 📉 技术分析要点  
**趋势**: 上升 | **动量**: 强劲 | **支撑/阻力**: 1650/1850
- 股价成功突破20日均线，技术面转强
- MACD指标出现金叉信号，市场情绪转好
- RSI指标显示轻微超买，需关注回调风险

## 💰 估值分析要点
**估值水平**: 合理 | **PE**: 28.5倍 | **PB**: 5.2倍  
- 当前PE低于历史平均30倍，估值具有吸引力
- 相比同行业龙头企业估值具有明显优势
- PEG比率显示估值与成长性匹配度良好

## ⚖️ 综合投资评级
**投资建议**: 买入 | **目标价格**: 1800-1900元 | **风险级别**: 中等

## 🎯 投资亮点 & ⚠️ 主要风险
[AI提供详细的投资亮点分析和风险警示]

## 🚀 操作策略建议
[具体的进场时机、持仓管理、止盈止损策略]
```

## 🛠️ MCP数据工具总览 (35个专业工具)

本系统集成了35个专业的A股数据分析工具，覆盖全方位的投资分析需求：

### 📊 行情数据与基础信息 (2个工具)
- **get_historical_k_data**: 历史K线数据 (支持日/周/月/分钟级别)
- **get_stock_basic_info**: 股票基本信息 (行业分类、市值等)

### 📈 基本面数据分析 (10个工具)
- **get_profit_data**: 季度盈利能力数据 (ROE、ROA、净利率等)  
- **get_operation_data**: 季度运营能力数据 (各类周转率指标)
- **get_growth_data**: 季度成长能力数据 (营收增长率、利润增长率)
- **get_balance_data**: 资产负债表数据 (资产结构、负债情况)
- **get_cash_flow_data**: 现金流量数据 (经营、投资、筹资现金流)
- **get_dupont_data**: 杜邦分析数据 (ROE分解分析)
- **get_dividend_data**: 历年分红信息 (分红率、派息记录)
- **get_performance_express_report**: 业绩快报 (季度业绩预览)
- **get_forecast_report**: 业绩预告 (管理层业绩指引)

### 📉 技术分析工具 (3个工具)
- **get_technical_indicators**: 全面技术指标计算 (MACD、RSI、KDJ、BOLL、WR等)
- **get_moving_averages**: 多周期移动平均线 (5/10/20/50/120/250日)
- **calculate_risk_metrics**: 风险指标计算 (贝塔、夏普比率、最大回撤、波动率)

### 💰 估值分析工具 (4个工具)  
- **get_valuation_metrics**: 估值指标与历史趋势 (PE、PB、PS及历史分位数)
- **calculate_peg_ratio**: PEG比率计算 (市盈率相对盈利增长比率)
- **calculate_dcf_valuation**: DCF现金流贴现估值模型
- **compare_industry_valuation**: 同行业估值比较分析

### 🏛️ 市场与行业数据 (5个工具)
- **get_stock_industry**: 行业分类数据  
- **get_sz50_stocks**: 上证50成分股列表
- **get_hs300_stocks**: 沪深300成分股列表
- **get_zz500_stocks**: 中证500成分股列表
- **get_all_stock**: 全市场股票清单及交易状态

### 🌐 宏观经济数据 (8个工具)
- **get_deposit_rate_data**: 存款基准利率历史数据
- **get_loan_rate_data**: 贷款基准利率历史数据  
- **get_required_reserve_ratio_data**: 存款准备金率变化
- **get_money_supply_data_month/year**: 货币供应量数据(M0/M1/M2)
- **get_shibor_data**: 上海银行间同业拆放利率

### 🔧 辅助分析工具 (3个工具)
- **get_latest_trading_date**: 获取最近交易日
- **get_market_analysis_timeframe**: 分析时间范围建议
- **get_stock_analysis**: 综合数据驱动分析报告

> 📋 **详细API文档**: 每个工具的完整参数说明和使用示例请参考 [DOCUMENTS.md](DOCUMENTS.md)

## ⚡ 性能优化成果

### 🚀 核心优化技术 (实现85%+ 速度提升)
- **🔄 MCP连接池技术** (50%提升): 复用连接避免重复建立，减少网络开销
- **💾 智能缓存系统** (30%提升): 价格数据缓存+分析结果缓存，避免重复计算
- **⚡ 简化工作流程** (15%提升): 针对回测优化的专用决策流程
- **⚙️ 默认参数优化** (5%提升): 预设最优的时间范围和频率配置

### 📊 实际性能表现
- **⚡ 超快模式** (3个月/月决策): 3决策点，2-3分钟 (优化前: 15-20分钟)
- **🚀 快速模式** (3个月/周决策): 12决策点，5-8分钟 (优化前: 45-60分钟)  
- **📊 标准模式** (6个月/周决策): 24决策点，10-15分钟 (优化前: 90-120分钟)

### 🔧 分层超时控制策略
- **✅ 基础设施超时** (保留): MCP连接30秒，Gemini API 60秒，确保快速故障发现
- **❌ 应用层超时** (移除): 分析工作流无超时限制，避免复杂任务被误终止
- **✅ 前端交互超时** (保留): WebSocket重连3秒间隔，图表加载10秒等待

## 📁 项目结构

```
mcp-agent/
├── 🚀 核心服务层
│   ├── app.py                        # 实时分析FastAPI服务器
│   ├── backtest_api.py              # 回测系统Flask服务器
│   ├── start_backtest_system.py     # 一键启动脚本
│   └── multi_agent_websocket.py     # WebSocket通信管理器
│
├── 🤖 多Agent引擎层
│   ├── multi_agent_workflow.py      # 核心工作流引擎
│   ├── backtest_system.py          # 智能回测系统
│   └── agents/                      # Agent模块目录
│       ├── base_agent.py           # 基础Agent抽象类
│       ├── fundamental_agent.py    # 基本面分析Agent
│       ├── technical_agent.py      # 技术分析Agent
│       ├── valuation_agent.py      # 估值分析Agent
│       ├── summary_agent.py        # 汇总分析Agent
│       └── investment_agent.py     # 投资决策Agent
│
├── 🎨 前端界面层  
│   └── frontend/
│       ├── index.html              # 实时分析主页面
│       ├── backtest.html          # 回测分析页面
│       ├── app.js                 # 实时分析JavaScript逻辑
│       ├── backtest_script.js     # 回测功能JavaScript逻辑
│       ├── style.css             # 通用样式文件
│       └── backtest_style.css    # 回测专用样式
│
├── 📋 配置文档层
│   ├── requirements.txt            # Python依赖包清单
│   ├── .env                       # 环境变量配置文件
│   ├── README.md                  # 项目主文档 (本文件)
│   └── DOCUMENTS.md              # MCP工具详细API文档
│
└── 📊 示例数据层
    ├── backtest_results_*.json    # 回测结果示例文件
    └── 投资分析报告_*.txt        # 分析报告示例文件
```

## 🔧 高级配置选项

### 环境变量完整配置
```env
# 🔑 必需配置
GOOGLE_API_KEY=your_google_api_key_here

# ⚙️ 可选配置  
GEMINI_MODEL=gemini-2.0-flash              # AI模型版本
MCP_SERVER_URL=http://localhost:3000/mcp/  # MCP服务器地址
BACKTEST_CACHE_SIZE=1000                   # 缓存容量限制
```

### MCP服务器连接配置
```python
# multi_agent_workflow.py 中的连接配置
"a_share_data_provider": {
    "url": "http://localhost:3000/mcp/",   # MCP服务器地址
    "transport": "streamable_http"         # 传输协议
}
```

### 性能调优关键参数
```python
# 超时控制参数
MCP_TIMEOUT = 30.0          # MCP连接超时时间 (秒)
GEMINI_TIMEOUT = 60         # Gemini API调用超时 (秒)  
MAX_RETRIES = 2             # 连接失败最大重试次数
BASE_DELAY = 3              # 重试基础延迟时间 (秒)

# 缓存优化参数
PRICE_CACHE_LIMIT = 1000    # 价格数据缓存条目上限
ANALYSIS_CACHE_LIMIT = 500  # 分析结果缓存条目上限
```

## 🚀 快速体验演示

### 一分钟体验回测功能
```bash
# 启动回测系统 (Web界面)
python start_backtest_system.py

# 或直接运行命令行回测
python backtest_system.py --stock_code sh.600519 --mode super_fast --period 3M
```

### 测试实时分析功能
```bash  
# 启动实时分析服务
python app.py

# 浏览器访问测试
# 地址: http://localhost:8000/static/index.html
# 测试查询: 请分析贵州茅台(sh.600519)的投资价值
```

## 📞 技术支持与故障排除

### 🔧 常见问题解决方案
1. **MCP连接失败**: 
   - 检查网络连接状态
   - 验证MCP服务器运行状态
   - 确认防火墙设置

2. **Gemini API调用错误**: 
   - 验证API密钥有效性
   - 检查API调用配额限制
   - 确认网络连接正常

3. **回测执行速度缓慢**: 
   - 使用推荐的快速模式配置
   - 避免选择每日决策频率
   - 检查缓存系统运行状态

4. **前端界面无法访问**: 
   - 确认对应服务器正常启动
   - 检查端口8000/5000是否被占用
   - 验证防火墙端口开放状态

### ⚡ 性能优化建议
- 🚀 **首次使用**: 强烈建议选择"超快速模式" (3个月/每月) 快速体验
- 📊 **日常分析**: 推荐使用"快速模式" (3个月/每周)，平衡分析深度与执行速度
- 🔧 **避免高频决策**: 除非进行高频策略研究，否则避免每日决策频率
- 💾 **定期清理缓存**: 定期清理缓存文件，避免占用过多内存资源

### 👨‍💻 开发者扩展指南
- 📝 **添加新Agent**: 继承BaseAgent抽象类，实现analyze方法接口
- 🔧 **扩展MCP工具**: 参考DOCUMENTS.md查看完整API规范
- 📈 **自定义投资策略**: 修改investment_agent.py中的决策生成逻辑
- 🎨 **界面个性化定制**: 编辑frontend/目录下的HTML/CSS/JS源文件

---

**📊 数据驱动智能投资，让AI成为您的投资分析师** | **Version 4.0** | **🤖 多Agent + 📈 回测 = 完整投资解决方案**

## 贡献指南

欢迎提交 Issue 或 Pull Request 来帮助改进项目。贡献前请先查看现有 Issue 和文档。

## 许可证

本项目采用 MIT 许可证 - 详情请查看 LICENSE 文件

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,15,20,24&section=footer&height=100&animation=fadeIn" />
</div>

