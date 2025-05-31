# 多Agent股票分析系统

一个基于 LangGraph 和 FastAPI 的智能股票分析系统，采用多Agent并行分析架构，提供基本面、技术面、估值分析和综合投资报告生成。

## 🌟 主要特性

### 多Agent并行分析
- **基本面分析Agent**: 分析财务状况、盈利能力、成长性等
- **技术分析Agent**: 分析价格趋势、技术指标、支撑阻力位等
- **估值分析Agent**: 分析估值指标、与行业对比、投资价值等
- **汇总分析Agent**: 整合三个专业分析，生成综合投资建议报告

### 核心功能
- 🤖 基于 LangGraph 的智能多Agent系统
- 📊 实时股票数据分析（A股市场）
- 💹 三维度并行分析：基本面、技术面、估值分析
- 🔄 实时WebSocket通信
- 📈 可视化执行过程监控
- 📄 专业级投资报告生成
- 🎯 智能查询解析和股票模板系统
- 📝 完整数据展示（无截断）
- 🎨 真实Markdown渲染

## 🏗️ 系统架构

### 多Agent工作流
```
用户查询 → 查询解析 → 并行执行三个专业Agent
                    ├── 基本面分析Agent (财务数据、盈利能力等)
                    ├── 技术分析Agent (价格趋势、技术指标等) 
                    └── 估值分析Agent (估值指标、行业对比等)
                           ↓
                    汇总Agent → 综合投资报告
```

### 技术栈
- **后端**: FastAPI + LangGraph + LangChain
- **前端**: 原生 HTML/CSS/JavaScript + WebSocket + marked.js
- **AI模型**: Google Gemini (通过 langchain-google-genai)
- **数据源**: MCP (Model Context Protocol) 服务器

## 📦 安装和设置

### 1. 克隆项目
```bash
git clone <repository-url>
cd <project-name>
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 环境配置
创建 `.env` 文件并配置：
```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### 4. 启动服务
```bash
python app.py
```

## 🚀 使用指南

### 访问地址
- **前端界面**: http://localhost:8000/static/index.html
- **API文档**: http://localhost:8000/docs
- **多Agent WebSocket**: ws://localhost:8000/ws/multi

### 分析查询格式

**标准格式**: `请分析[公司名称]([股票代码])的投资价值`

**查询示例**:
```
请分析贵州茅台(sh.600519)的投资价值
请分析比亚迪(sz.002594)的投资价值
请分析宁德时代(sz.300750)的投资价值
```

### 支持的股票代码格式
- `sh.600519` (上海证券交易所)
- `sz.000858` (深圳证券交易所)
- `sz.300750` (创业板)

## 📁 项目结构

```
multi-agent-stock-analysis/
├── app.py                        # 主应用服务器
├── multi_agent_workflow.py       # 多Agent工作流核心
├── multi_agent_websocket.py      # 多Agent WebSocket管理器
├── test_multi_agent.py           # 测试脚本
├── requirements.txt              # Python依赖
├── .env                          # 环境变量配置
├── README.md                     # 项目文档
├── agents/                       # Agent模块目录
│   ├── base_agent.py            # 基础Agent抽象类
│   ├── fundamental_agent.py     # 基本面分析Agent
│   ├── technical_agent.py       # 技术分析Agent
│   ├── valuation_agent.py       # 估值分析Agent
│   └── summary_agent.py         # 汇总分析Agent
└── frontend/                     # 前端文件
    ├── index.html               # 主页面
    ├── app.js                   # JavaScript逻辑
    └── style.css                # 样式文件
```

## 📊 分析报告示例

多Agent系统会生成包含以下部分的综合投资报告：

```markdown
# 贵州茅台(sh.600519) 投资分析报告

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
```

## 🔧 配置选项

### 环境变量
- `GOOGLE_API_KEY`: Google Gemini API密钥 (必需)
- `GEMINI_MODEL`: 使用的Gemini模型版本 (默认: gemini-1.5-flash)

### MCP服务器配置
当前配置的MCP服务器提供A股数据：
```python
"a_share_data_provider": {
    "url": "http://mcp-server.danglingpointer.top:3000/mcp/",
    "transport": "streamable_http",
}
```