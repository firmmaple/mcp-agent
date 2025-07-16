"""
简化的回测系统

定期运行multi_agent_workflow获取JSON投资决策，并执行交易追踪表现
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import baostock as bs
import json
import os
from multi_agent_workflow import MultiAgentWorkflow


class BacktestSystem:
    """简化的回测系统"""
    
    def __init__(self, initial_capital: float = 100000.0, verbose: bool = True):
        """
        初始化回测系统
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # 股票代码 -> 持仓数量
        self.transactions = []  # 交易记录
        self.daily_values = []  # 每日资产价值
        self.workflow = MultiAgentWorkflow(verbose=False)
        
        # 添加缓存机制
        self.price_cache = {}  # 缓存股票价格数据
        self.analysis_cache = {}  # 缓存分析结果
        
        # 初始化baostock
        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"登录baostock失败: {lg.error_msg}")
    
    def __del__(self):
        """析构函数，登出baostock"""
        try:
            bs.logout()
        except:
            pass
    
    def get_stock_price(self, stock_code: str, date: str) -> Optional[float]:
        """
        获取指定日期的股票价格（带缓存）
        
        Args:
            stock_code: 股票代码
            date: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            股票价格，如果获取失败返回None
        """
        # 检查缓存
        cache_key = f"{stock_code}_{date}"
        if cache_key in self.price_cache:
            print(f"💾 使用缓存价格: {date} = {self.price_cache[cache_key]:.2f}")
            return self.price_cache[cache_key]
        
        try:
            # 确保baostock已登录
            lg = bs.login()
            if lg.error_code != '0':
                print(f"重新登录baostock失败: {lg.error_msg}")
                return None
            
            print(f"📡 获取股票价格: {stock_code} @ {date}")
            
            # 获取前后几天的数据，确保能获取到价格
            start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d')
            end_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=5)).strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                stock_code,
                "date,close",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"
            )
            
            data_list = []
            if rs and rs.error_code == '0':
                while rs.next():
                    data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            # 找到最接近目标日期的价格
            target_date = datetime.strptime(date, '%Y-%m-%d')
            closest_price = None
            min_diff = float('inf')
            
            for row in data_list:
                row_date = datetime.strptime(row[0], '%Y-%m-%d')
                diff = abs((row_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    closest_price = float(row[1])
            
            # 缓存结果
            if closest_price:
                self.price_cache[cache_key] = closest_price
                print(f"✅ 价格获取成功: {closest_price:.2f}")
            
            return closest_price
            
        except Exception as e:
            print(f"获取股票价格失败: {e}")
            return None
    
    def get_historical_prices(self, stock_code: str, end_date: str, days: int = 30) -> List[float]:
        """
        获取历史价格数据（带缓存优化）
        
        Args:
            stock_code: 股票代码
            end_date: 结束日期
            days: 历史天数
            
        Returns:
            价格列表
        """
        cache_key = f"hist_{stock_code}_{end_date}_{days}"
        if cache_key in self.price_cache:
            print(f"💾 使用缓存历史数据: {len(self.price_cache[cache_key])} 个价格点")
            return self.price_cache[cache_key]
        
        try:
            print(f"📡 获取历史价格数据: {stock_code} 最近 {days} 天")
            
            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=days+10)).strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                stock_code,
                "date,close",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"
            )
            
            prices = []
            if rs and rs.error_code == '0':
                while rs.next():
                    try:
                        close_price = float(rs.get_row_data()[1])
                        prices.append(close_price)
                    except (ValueError, IndexError):
                        continue
            
            # 只保留最近的天数
            if len(prices) > days:
                prices = prices[-days:]
            
            # 缓存结果
            self.price_cache[cache_key] = prices
            print(f"✅ 历史数据获取成功: {len(prices)} 个价格点")
            return prices
            
        except Exception as e:
            print(f"获取历史价格失败: {e}")
            return []
    
    def get_portfolio_state(self, stock_code: str, current_price: float) -> Dict[str, Any]:
        """
        获取当前投资组合状态
        
        Args:
            stock_code: 股票代码
            current_price: 当前价格
            
        Returns:
            投资组合状态字典
        """
        current_shares = self.positions.get(stock_code, 0)
        stock_value = current_shares * current_price
        total_value = self.current_capital + stock_value
        
        # 计算成本信息
        avg_cost = 0.0
        total_cost = 0.0
        if current_shares > 0:
            buy_transactions = [t for t in self.transactions if t['stock_code'] == stock_code and t['action'] == 'BUY']
            if buy_transactions:
                total_cost = sum(t['amount'] for t in buy_transactions)
                avg_cost = total_cost / current_shares
        
        # 计算盈亏
        unrealized_pnl = (current_price - avg_cost) * current_shares if current_shares > 0 else 0.0
        unrealized_pnl_percent = (unrealized_pnl / total_cost) * 100 if total_cost > 0 else 0.0
        
        # 计算资金使用率
        capital_usage = (total_value - self.current_capital) / self.initial_capital if self.initial_capital > 0 else 0.0
        
        return {
            "current_shares": current_shares,
            "cash": self.current_capital,
            "stock_value": stock_value,
            "total_value": total_value,
            "initial_capital": self.initial_capital,
            "avg_cost": avg_cost,
            "total_cost": total_cost,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_percent": unrealized_pnl_percent,
            "capital_usage": capital_usage,
            "available_cash_ratio": self.current_capital / self.initial_capital,
            "stock_ratio": stock_value / total_value if total_value > 0 else 0.0,
            "total_trades": len(self.transactions),
            "recent_transactions": self.transactions[-5:] if self.transactions else []
        }
    
    async def get_investment_decision(self, stock_code: str, company_name: str, date: str, current_price: float) -> Dict[str, Any]:
        """
        运行multi_agent_workflow获取投资决策
        
        Args:
            stock_code: 股票代码
            company_name: 公司名称
            date: 分析日期
            current_price: 当前价格
            
        Returns:
            JSON格式的投资决策
        """
        try:
            # 检查缓存
            cache_key = f"decision_{stock_code}_{date}"
            if cache_key in self.analysis_cache:
                print(f"💾 使用缓存投资决策: {date} - {company_name} ({stock_code})")
                return self.analysis_cache[cache_key]

            # 获取历史价格数据
            historical_prices = self.get_historical_prices(stock_code, date, days=30)
            
            # 获取当前投资组合状态
            portfolio_state = self.get_portfolio_state(stock_code, current_price)
            
            # 准备workflow输入
            input_data = {
                "stock_code": stock_code,
                "company_name": company_name,
                "current_date": date,
                "current_time_info": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "current_price": current_price,
                "historical_prices": historical_prices,
                "portfolio_state": portfolio_state
            }
            
            print(f"📊 {date} - 开始分析 {company_name} ({stock_code})")
            print(f"💰 当前状态: 价格{current_price:.2f} | 持股{portfolio_state['current_shares']}股 | 现金{portfolio_state['cash']:.2f} | 总值{portfolio_state['total_value']:.2f}")
            
            # 运行workflow
            result = await self.workflow.run(input_data)
            
            # 获取投资决策
            decision = result.get('investment_decision', {})
            
            print(f"💡 投资决策: {decision.get('action', 'HOLD')} | 信心度: {decision.get('confidence', 0):.2f} | 仓位: {decision.get('position_size', 0):.1%}")
            
            # 缓存结果
            self.analysis_cache[cache_key] = decision
            return decision
            
        except Exception as e:
            print(f"获取投资决策失败: {e}")
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "target_price": None,
                "stop_loss": None,
                "position_size": 0.0,
                "holding_period": "medium",
                "risk_level": "medium",
                "reasons": [f"分析失败: {e}"]
            }
    
    def execute_decision(self, stock_code: str, decision: Dict[str, Any], current_price: float, date: str):
        """
        [简化版]执行投资决策 (完全忽略100股限制，允许小数股)
        
        Args:
            stock_code: 股票代码
            decision: 投资决策
            current_price: 当前价格
            date: 交易日期
        """
        action = decision.get('action', 'HOLD')
        position_size = decision.get('position_size', 0.0) # 0.0 to 1.0
        confidence = decision.get('confidence', 0.0)
        current_position = self.positions.get(stock_code, 0)

        # 1. 处理买入信号
        if action == "BUY" and confidence > 0.5:
            if self.current_capital > 1: # 确保有钱可投 (设置一个很小的阈值)
                # 决定投资多少钱
                amount_to_invest = self.current_capital * position_size
                
                # 计算能买多少股 (可以是小数)
                shares_to_buy = amount_to_invest / current_price
                
                # 更新账户
                self.current_capital -= amount_to_invest
                self.positions[stock_code] = current_position + shares_to_buy
                
                # 记录交易
                self.transactions.append({
                    'date': date, 'stock_code': stock_code, 'action': 'BUY',
                    'shares': shares_to_buy, 'price': current_price, 'amount': amount_to_invest,
                    'confidence': confidence
                })
                print(f"✅ 买入 {shares_to_buy:.2f} 股 (小数)，价格 {current_price:.2f}，成本 {amount_to_invest:.2f}")
            else:
                print("❌ 现金不足，无法执行任何买入操作。")

        # 2. 处理卖出信号
        elif action == "SELL" and current_position > 0:
            # 如果position_size有效，则按比例卖出，否则全部卖出
            if position_size > 0 and position_size < 1:
                shares_to_sell = current_position * position_size
            else:
                shares_to_sell = current_position # 默认全部卖出
                
            revenue = shares_to_sell * current_price
            
            # 更新账户
            self.current_capital += revenue
            self.positions[stock_code] = current_position - shares_to_sell
            
            # 记录交易
            self.transactions.append({
                'date': date, 'stock_code': stock_code, 'action': 'SELL',
                'shares': shares_to_sell, 'price': current_price, 'amount': revenue,
                'confidence': confidence
            })
            print(f"✅ 卖出 {shares_to_sell:.2f} 股 (小数)，价格 {current_price:.2f}，收入 {revenue:.2f}")

        # 3. 处理持有信号
        else: # action == "HOLD"
            print(f"📊 保持持有 {current_position:.2f} 股，当前价格 {current_price:.2f}")

        # 显示决策理由
        reasons = decision.get('reasons', [])
        if reasons:
            print(f"💭 决策理由: {'; '.join(reasons)}")
    
    def calculate_portfolio_value(self, date: str) -> float:
        """
        计算投资组合总价值
        
        Args:
            date: 计算日期
            
        Returns:
            投资组合总价值
        """
        total_value = self.current_capital
        
        for stock_code, shares in self.positions.items():
            if shares > 0:
                price = self.get_stock_price(stock_code, date)
                if price:
                    total_value += shares * price
        
        return total_value
    
    async def run_backtest(self, stock_code: str, company_name: str, 
                          start_date: str, end_date: str, 
                          frequency: str = "weekly", 
                          progress_callback=None) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            stock_code: 股票代码
            company_name: 公司名称
            start_date: 开始日期
            end_date: 结束日期
            frequency: 决策频率 ("daily" 或 "weekly" 或 "monthly")
            progress_callback: 进度回调函数
            
        Returns:
            回测结果
        """
        print(f"🚀 开始回测: {company_name} ({stock_code})")
        print(f"📅 回测期间: {start_date} - {end_date}")
        print(f"🔄 决策频率: {frequency}")
        print(f"💰 初始资金: {self.initial_capital:,.2f}")
        print("-" * 50)
        
        # 生成决策日期列表
        decision_dates = self.generate_decision_dates(start_date, end_date, frequency)
        total_dates = len(decision_dates)
        
        print(f"📊 将进行 {total_dates} 次决策分析")
        
        if progress_callback:
            progress_callback(10, f"回测初始化完成，共需分析 {total_dates} 个决策点")
        
        # 预计每个决策点的耗时（秒）
        estimated_time_per_decision = {
            "daily": 30,    # 每日决策约30秒
            "weekly": 25,   # 每周决策约25秒
            "monthly": 20   # 每月决策约20秒
        }
        
        estimated_total_minutes = (total_dates * estimated_time_per_decision.get(frequency, 25)) / 60
        print(f"⏱️ 预计总耗时: {estimated_total_minutes:.1f} 分钟")
        
        if progress_callback:
            progress_callback(15, f"预计耗时 {estimated_total_minutes:.1f} 分钟，正在开始分析...")
        
        for i, date in enumerate(decision_dates):
            # 计算进度
            progress = 15 + int((i / total_dates) * 70)  # 15-85%的进度用于分析
            
            if progress_callback:
                progress_callback(progress, f"正在分析第 {i+1}/{total_dates} 个决策点: {date}")
            
            print(f"\n📈 [{i+1}/{total_dates}] 决策点: {date}")
            
            # 获取当前价格
            current_price = self.get_stock_price(stock_code, date)
            if not current_price:
                print(f"⚠️ {date} - 无法获取价格，跳过")
                continue
            
            # 获取投资决策
            decision = await self.get_investment_decision(stock_code, company_name, date, current_price)
            
            # 执行决策
            self.execute_decision(stock_code, decision, current_price, date)
            
            # 记录每日价值
            portfolio_value = self.calculate_portfolio_value(date)
            self.daily_values.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': self.current_capital,
                'stock_value': portfolio_value - self.current_capital
            })
            
            print(f"📈 投资组合价值: {portfolio_value:,.2f} | 现金: {self.current_capital:,.2f}")
            print("-" * 30)
        
        if progress_callback:
            progress_callback(90, "正在计算回测结果...")
        
        # 计算回测结果
        results = self.calculate_performance()
        
        if progress_callback:
            progress_callback(100, "回测完成！")
        
        return results
    
    def generate_decision_dates(self, start_date: str, end_date: str, frequency: str) -> List[str]:
        """
        生成决策日期列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率
            
        Returns:
            日期列表
        """
        dates = []
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            if frequency == "daily":
                current += timedelta(days=1)
            elif frequency == "weekly":
                current += timedelta(days=7)
            else:
                current += timedelta(days=30)  # monthly
        
        return dates
    
    def calculate_performance(self) -> Dict[str, Any]:
        """
        计算回测表现
        
        Returns:
            表现指标
        """
        if not self.daily_values:
            return {"error": "没有数据"}
        
        try:
            # 计算总收益
            final_value = self.daily_values[-1]['portfolio_value']
            total_return = (final_value - self.initial_capital) / self.initial_capital
            
            # 计算收益率序列
            values = [d['portfolio_value'] for d in self.daily_values]
            returns = np.diff(values) / values[:-1] if len(values) > 1 else np.array([])
            
        except Exception as e:
            return {"error": f"计算收益时出错: {e}"}
        
        # 计算交易统计
        buy_trades = [t for t in self.transactions if t['action'] == 'BUY']
        sell_trades = [t for t in self.transactions if t['action'] == 'SELL']
        
        # 计算盈利交易数量和胜率
        profitable_trades = 0
        total_completed_trades = 0
        
        if buy_trades and sell_trades:
            # 将买卖交易配对计算盈亏
            for sell_trade in sell_trades:
                # 找到对应的买入交易（简化为价格比较）
                corresponding_buys = [b for b in buy_trades if b['date'] <= sell_trade['date']]
                if corresponding_buys:
                    avg_buy_price = sum(b['price'] for b in corresponding_buys) / len(corresponding_buys)
                    if sell_trade['price'] > avg_buy_price:
                        profitable_trades += 1
                    total_completed_trades += 1
        
        # 计算胜率 - 只有完成买卖对的交易才计算胜率
        win_rate = (profitable_trades / total_completed_trades) if total_completed_trades > 0 else 0.0
        
        # 计算各种指标
        performance = {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_profit': final_value - self.initial_capital,
            'max_value': max(values) if values else self.initial_capital,
            'min_value': min(values) if values else self.initial_capital,
            'volatility': float(np.std(returns)) if len(returns) > 1 else 0.0,
            'sharpe_ratio': float(np.mean(returns) / np.std(returns)) if len(returns) > 1 and np.std(returns) > 0 else 0.0,
            'max_drawdown': self.calculate_max_drawdown(values),
            'total_trades': len(self.transactions),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'profitable_trades': profitable_trades,
            'win_rate': win_rate,
            'winning_trades': profitable_trades,  # 保持兼容性
            'daily_values': self.daily_values,
            'transactions': self.transactions
        }
        
        return performance
    
    def calculate_max_drawdown(self, values: List[float]) -> float:
        """计算最大回撤"""
        if len(values) < 2:
            return 0.0
        
        peak = values[0]
        max_drawdown = 0.0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def save_results(self, results: Dict[str, Any], filename: str):
        """
        保存回测结果
        
        Args:
            results: 回测结果
            filename: 文件名
        """
        # 保存JSON结果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"📁 结果已保存至: {filename}")
    
    def print_summary(self, results: Dict[str, Any]):
        """
        打印回测摘要
        
        Args:
            results: 回测结果
        """
        print("\n" + "="*50)
        print("📊 回测结果摘要")
        print("="*50)
        print(f"💰 初始资金: {results['initial_capital']:,.2f}")
        print(f"💰 最终价值: {results['final_value']:,.2f}")
        print(f"📈 总收益: {results['total_profit']:,.2f}")
        print(f"📊 总收益率: {results['total_return']:.2%}")
        print(f"📉 最大回撤: {results['max_drawdown']:.2%}")
        print(f"📊 波动率: {results['volatility']:.4f}")
        print(f"📈 夏普比率: {results['sharpe_ratio']:.4f}")
        print(f"🔄 总交易次数: {results['total_trades']}")
        print(f"✅ 盈利交易: {results['winning_trades']}")
        print("="*50)


async def main():
    """示例使用"""
    # 创建回测系统
    backtest = BacktestSystem(initial_capital=100000.0)
    
    # 运行回测
    results = await backtest.run_backtest(
        stock_code="sh.600519",
        company_name="贵州茅台",
        start_date="2024-06-01",
        end_date="2024-06-30",
        frequency="weekly"
    )
    
    # 打印结果
    backtest.print_summary(results)
    
    # 保存结果
    backtest.save_results(results, "backtest_results.json")


if __name__ == "__main__":
    asyncio.run(main()) 