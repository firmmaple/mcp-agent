"""
增强版回测示例

展示如何使用改进后的系统：
1. 将投资组合状态传递给投资agent
2. 基于持仓情况做出更智能的决策
3. 支持部分买入/卖出操作
"""

import asyncio
from backtest_system import BacktestSystem


async def main():
    """运行增强版回测示例"""
    print("🚀 启动增强版回测系统示例")
    print("="*60)
    
    # 创建回测系统实例（关闭详细日志）
    backtest = BacktestSystem(initial_capital=100000.0, verbose=False)
    
    # 配置回测参数
    stock_code = "sh.600519"
    company_name = "贵州茅台"
    start_date = "2024-06-01"
    end_date = "2024-06-30"
    frequency = "weekly"  # 每周运行一次workflow
    
    print(f"📊 股票: {company_name} ({stock_code})")
    print(f"📅 期间: {start_date} 至 {end_date}")
    print(f"🔄 频率: {frequency}")
    print(f"💰 初始资金: {backtest.initial_capital:,.2f}")
    print("="*60)
    
    # 显示系统特性
    print("🎯 系统特性:")
    print("  • 投资组合状态实时传递给AI Agent")
    print("  • 基于持仓情况的智能决策")
    print("  • 支持部分买入/卖出操作")
    print("  • 动态止损和获利了结")
    print("  • 考虑资金使用率和风险控制")
    print("="*60)
    
    # 运行回测
    print("🤖 开始智能回测...")
    results = await backtest.run_backtest(
        stock_code=stock_code,
        company_name=company_name,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency
    )
    
    # 打印详细结果
    print("\n" + "="*60)
    print("📊 详细回测结果")
    print("="*60)
    
    # 基本指标
    print(f"💰 初始资金: {results['initial_capital']:,.2f} 元")
    print(f"💰 最终价值: {results['final_value']:,.2f} 元")
    print(f"📈 总收益: {results['total_profit']:,.2f} 元")
    print(f"📊 总收益率: {results['total_return']:.2%}")
    print(f"📉 最大回撤: {results['max_drawdown']:.2%}")
    print(f"📊 波动率: {results['volatility']:.4f}")
    print(f"📈 夏普比率: {results['sharpe_ratio']:.4f}")
    
    # 交易统计
    print(f"\n🔄 交易统计:")
    print(f"  • 总交易次数: {results['total_trades']}")
    print(f"  • 盈利交易: {results['winning_trades']}")
    if results['total_trades'] > 0:
        win_rate = results['winning_trades'] / results['total_trades'] * 100
        print(f"  • 胜率: {win_rate:.1f}%")
    
    # 显示交易记录
    if results['transactions']:
        print(f"\n📋 交易记录:")
        for i, trade in enumerate(results['transactions'], 1):
            action_icon = "🟢" if trade['action'] == 'BUY' else "🔴"
            print(f"  {i}. {action_icon} {trade['date']} {trade['action']} {trade['shares']}股 @ {trade['price']:.2f}元 (信心度: {trade['confidence']:.1%})")
    
    # 显示每日价值变化
    if results['daily_values']:
        print(f"\n📈 投资组合价值变化:")
        for value in results['daily_values']:
            change = value['portfolio_value'] - results['initial_capital']
            change_pct = (change / results['initial_capital']) * 100
            print(f"  {value['date']}: {value['portfolio_value']:,.2f}元 ({change:+,.2f}, {change_pct:+.1f}%)")
    
    # 保存结果
    filename = f"enhanced_backtest_results_{company_name}_{stock_code.replace('.', '_')}.json"
    backtest.save_results(results, filename)
    
    print(f"\n🎉 增强版回测完成！")
    print(f"📈 最终收益率: {results['total_return']:.2%}")
    print(f"📊 最大回撤: {results['max_drawdown']:.2%}")
    print(f"📁 结果已保存至: {filename}")


if __name__ == "__main__":
    asyncio.run(main()) 