# MCP Server 工具列表

---

### **行情数据 & 基础信息 (Market Data & Basic Info)**

---

#### **get_historical_k_data**
获取中国A股股票的历史K线（开盘价、最高价、最低价、收盘价、成交量）数据。

* **参数:**
    * `code` (string, 必需): 股票代码 (例如, 'sh.600000', 'sz.000001')。
    * `start_date` (string, 必需): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 必需): 结束日期 'YYYY-MM-DD'。
    * `frequency` (string, 可选): 数据频率。'd'(日), 'w'(周), 'm'(月), '5', '15', '30', '60'(分钟)。默认为 'd'。
    * `adjust_flag` (string, 可选): 复权类型。'1'(后复权), '2'(前复权), '3'(不复权)。默认为 '3'。
* **返回:**
    * 包含K线数据的Markdown表格。

---

#### **get_stock_basic_info**
获取给定中国A股股票的基本信息。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `fields` (list[string], 可选): 指定需要返回的字段 (例如, 'code_name', 'industry')。
* **返回:**
    * 包含股票基本信息的Markdown表格。

---

### **基本面数据 (Fundamental Data)**

---

#### **get_dividend_data**
获取指定股票和年份的分红信息。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 查询年份 (例如, '2023')。
    * `year_type` (string, 可选): 年份类型。'report'(预案公告年份), 'operate'(除权除息年份)。默认为 'report'。
* **返回:**
    * 包含分红数据的Markdown表格。

---

#### **get_profit_data**
获取股票的季度盈利能力数据。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 4位数字年份。
    * `quarter` (integer, 必需): 季度 (1, 2, 3, or 4)。
* **返回:**
    * 包含盈利能力数据的Markdown表格。

---

#### **get_operation_data**
获取股票的季度运营能力数据。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 4位数字年份。
    * `quarter` (integer, 必需): 季度 (1, 2, 3, or 4)。
* **返回:**
    * 包含运营能力数据的Markdown表格。

---

#### **get_growth_data**
获取股票的季度成长能力数据。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 4位数字年份。
    * `quarter` (integer, 必需): 季度 (1, 2, 3, or 4)。
* **返回:**
    * 包含成长能力数据的Markdown表格。

---

#### **get_balance_data**
获取股票的季度偿债能力数据（资产负债表）。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 4位数字年份。
    * `quarter` (integer, 必需): 季度 (1, 2, 3, or 4)。
* **返回:**
    * 包含资产负债表数据的Markdown表格。

---

#### **get_cash_flow_data**
获取股票的季度现金流量数据。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 4位数字年份。
    * `quarter` (integer, 必需): 季度 (1, 2, 3, or 4)。
* **返回:**
    * 包含现金流量数据的Markdown表格。

---

#### **get_dupont_data**
获取股票的季度杜邦分析数据。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 4位数字年份。
    * `quarter` (integer, 必需): 季度 (1, 2, 3, or 4)。
* **返回:**
    * 包含杜邦分析数据的Markdown表格。

---

#### **get_performance_express_report**
获取股票在指定日期范围内的业绩快报。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `start_date` (string, 必需): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 必需): 结束日期 'YYYY-MM-DD'。
* **返回:**
    * 包含业绩快报数据的Markdown表格。

---

#### **get_forecast_report**
获取股票在指定日期范围内的业绩预告。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `start_date` (string, 必需): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 必需): 结束日期 'YYYY-MM-DD'。
* **返回:**
    * 包含业绩预告数据的Markdown表格。

---

### **市场与行业 (Market & Industry)**

---

#### **get_stock_industry**
获取指定股票或所有股票的行业分类。

* **参数:**
    * `code` (string, 可选): 股票代码。如果为空，则获取所有股票。
    * `date` (string, 可选): 日期 'YYYY-MM-DD'。如果为空，使用最新数据。
* **返回:**
    * 包含行业分类数据的Markdown表格。

---

#### **get_sz50_stocks**
获取上证50指数在指定日期的成分股。

* **参数:**
    * `date` (string, 可选): 日期 'YYYY-MM-DD'。如果为空，使用最新数据。
* **返回:**
    * 包含上证50成分股的Markdown表格。

---

#### **get_hs300_stocks**
获取沪深300指数在指定日期的成分股。

* **参数:**
    * `date` (string, 可选): 日期 'YYYY-MM-DD'。如果为空，使用最新数据。
* **返回:**
    * 包含沪深300成分股的Markdown表格。

---

#### **get_zz500_stocks**
获取中证500指数在指定日期的成分股。

* **参数:**
    * `date` (string, 可选): 日期 'YYYY-MM-DD'。如果为空，使用最新数据。
* **返回:**
    * 包含中证500成分股的Markdown表格。

---

#### **get_all_stock**
获取指定日期的所有股票（A股和指数）及其交易状态。

* **参数:**
    * `date` (string, 可选): 日期 'YYYY-MM-DD'。如果为空，使用当前日期。
* **返回:**
    * 包含股票列表和交易状态的Markdown表格。

---

### **宏观经济 (Macro Economy)**

---

#### **get_deposit_rate_data**
获取指定日期范围内的存款基准利率。

* **参数:**
    * `start_date` (string, 可选): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 可选): 结束日期 'YYYY-MM-DD'。
* **返回:**
    * 包含存款利率数据的Markdown表格。

---

#### **get_loan_rate_data**
获取指定日期范围内的贷款基准利率。

* **参数:**
    * `start_date` (string, 可选): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 可选): 结束日期 'YYYY-MM-DD'。
* **返回:**
    * 包含贷款利率数据的Markdown表格。

---

#### **get_required_reserve_ratio_data**
获取指定日期范围内的存款准备金率。

* **参数:**
    * `start_date` (string, 可选): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 可选): 结束日期 'YYYY-MM-DD'。
* **返回:**
    * 包含存款准备金率数据的Markdown表格。

---

#### **get_money_supply_data_month**
获取月度货币供应量数据 (M0, M1, M2)。

* **参数:**
    * `start_date` (string, 可选): 开始月份 'YYYY-MM'。
    * `end_date` (string, 可选): 结束月份 'YYYY-MM'。
* **返回:**
    * 包含月度货币供应数据的Markdown表格。

---

#### **get_money_supply_data_year**
获取年度货币供应量数据 (M0, M1, M2)。

* **参数:**
    * `start_date` (string, 可选): 开始年份 'YYYY'。
    * `end_date` (string, 可选): 结束年份 'YYYY'。
* **返回:**
    * 包含年度货币供应数据的Markdown表格。

---

#### **get_shibor_data**
获取指定日期范围内的上海银行间同业拆放利率 (SHIBOR)。

* **参数:**
    * `start_date` (string, 可选): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 可选): 结束日期 'YYYY-MM-DD'。
* **返回:**
    * 包含SHIBOR数据的Markdown表格。

---

### **技术分析 (Technical Analysis)**

---

#### **get_technical_indicators**
计算股票的技术指标，包括MACD、RSI、KDJ、布林带、威廉指标、随机震荡器等。

* **参数:**
    * `code` (string, 必需): 股票代码 (例如, 'sh.600000', 'sz.000001')。
    * `start_date` (string, 必需): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 必需): 结束日期 'YYYY-MM-DD'。
    * `indicators` (list[string], 可选): 指标列表，可选值包括 ['MACD', 'RSI', 'KDJ', 'BOLL', 'WR', 'STOCH', 'CCI', 'ATR']。如果为空，则计算所有支持的指标。
* **返回:**
    * 包含技术指标数据的Markdown表格。

---

#### **get_moving_averages**
计算多种周期的移动平均线（5、10、20、50、120、250日），包括SMA、EMA、WMA等类型。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `start_date` (string, 必需): 开始日期 'YYYY-MM-DD'。
    * `end_date` (string, 必需): 结束日期 'YYYY-MM-DD'。
    * `periods` (list[integer], 可选): 移动平均线周期列表，如[5, 10, 20, 50]。默认使用常用周期[5, 10, 20, 50, 120, 250]。
* **返回:**
    * 包含各种移动平均线数据的Markdown表格，包含均线分析。

---

#### **calculate_risk_metrics**
计算风险指标，包括贝塔值、夏普比率、最大回撤、波动率、下行风险等，与基准指数比较。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `benchmark_code` (string, 可选): 基准指数代码。默认'sh.000300'(沪深300)，可选'sh.000016'(上证50)。
    * `period` (string, 可选): 分析周期。'1Y'(1年), '6M'(6个月), '3M'(3个月), '2Y'(2年)。默认为'1Y'。
* **返回:**
    * 包含风险指标的详细分析报告，包括收益率、风险指标和风险调整收益指标。

---

### **估值分析 (Valuation Analysis)**

---

#### **get_valuation_metrics**
获取股票的估值指标数据，包括市盈率(P/E)、市净率(P/B)、市销率(P/S)等的实时数据和历史趋势。

* **参数:**
    * `code` (string, 必需): 股票代码 (例如, 'sh.600000', 'sz.000001')。
    * `start_date` (string, 可选): 开始日期 'YYYY-MM-DD'。默认为最近1年。
    * `end_date` (string, 可选): 结束日期 'YYYY-MM-DD'。默认为当前日期。
* **返回:**
    * 包含各种估值指标的Markdown表格和趋势分析，包括当前估值、历史均值、分位数等。

---

#### **calculate_peg_ratio**
计算PEG比率（市盈率相对盈利增长比率），PEG = PE / 净利润增长率。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `year` (string, 必需): 4位数字年份，如'2024'。
    * `quarter` (integer, 必需): 季度 (1, 2, 3, or 4)。
* **返回:**
    * 包含PEG比率计算和分析的详细报告，包括估值水平判断。

---

#### **calculate_dcf_valuation**
计算DCF（现金流贴现）估值，基于历史现金流数据进行未来现金流预测和贴现。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `years_back` (integer, 可选): 用于分析的历史年份数。默认5年。
    * `discount_rate` (float, 可选): 折现率/WACC。默认10% (0.10)。
    * `terminal_growth_rate` (float, 可选): 永续增长率。默认2.5% (0.025)。
* **返回:**
    * 包含DCF估值计算过程和结果的详细报告，包括企业价值、关键假设等。

---

#### **compare_industry_valuation**
进行同行业估值比较分析，对比目标股票与同行业其他公司的估值水平。

* **参数:**
    * `code` (string, 必需): 目标股票代码。
    * `date` (string, 可选): 比较基准日期 'YYYY-MM-DD'。默认为最新交易日。
* **返回:**
    * 包含同行业估值比较的详细分析报告，包括行业统计、排名分位、估值水平评价。

---

### **辅助工具 (Utility Tools)**

---

#### **get_latest_trading_date**
获取最近的交易日期。

* **参数:**
    * 无
* **返回:**
    * 最近的交易日期字符串 'YYYY-MM-DD'。

---

#### **get_market_analysis_timeframe**
获取适合市场分析的时间范围。

* **参数:**
    * `period` (string, 可选): 时间范围类型。'recent'(最近1-2月), 'quarter'(最近一季度), 'half_year'(最近半年), 'year'(最近一年)。默认为 'recent'。
* **返回:**
    * 描述分析时间范围的字符串。

---

#### **get_stock_analysis**
提供基于数据的股票分析报告（非投资建议）。

* **参数:**
    * `code` (string, 必需): 股票代码。
    * `analysis_type` (string, 可选): 分析类型。'fundamental'(基本面), 'technical'(技术面), 'comprehensive'(综合)。默认为 'fundamental'。
* **返回:**
    * 包含关键指标、历史表现和行业比较的数据驱动分析报告。