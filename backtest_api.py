"""
回测系统 Web API 服务器

提供回测系统的HTTP API接口，支持前端调用
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import json
import os
import threading
from datetime import datetime
from backtest_system import BacktestSystem
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend', static_url_path='/static')
CORS(app)  # 允许跨域请求

# 全局变量存储回测实例
current_backtest = None
backtest_results = None
backtest_status = {"is_running": False, "progress": 0, "message": ""}

@app.route('/')
def index():
    """返回主页"""
    return send_from_directory('frontend', 'backtest.html')

@app.route('/frontend/<path:filename>')
def frontend_files(filename):
    """提供前端静态文件"""
    return send_from_directory('frontend', filename)

@app.route('/api/stocks/suggest', methods=['GET'])
def suggest_stocks():
    """获取股票建议列表"""
    suggestions = [
        {"name": "贵州茅台", "code": "sh.600519", "type": "白酒"},
        {"name": "比亚迪", "code": "sz.002594", "type": "新能源汽车"},
        {"name": "海康威视", "code": "sz.002415", "type": "安防"},
        {"name": "宁德时代", "code": "sz.300750", "type": "新能源"},
        {"name": "五粮液", "code": "sh.000858", "type": "白酒"},
        {"name": "中国平安", "code": "sh.601318", "type": "保险"},
        {"name": "招商银行", "code": "sh.600036", "type": "银行"},
        {"name": "万科A", "code": "sz.000002", "type": "房地产"},
        {"name": "格力电器", "code": "sz.000651", "type": "家电"},
        {"name": "美的集团", "code": "sz.000333", "type": "家电"}
    ]
    return jsonify(suggestions)

@app.route('/api/backtest/start', methods=['POST'])
def start_backtest():
    """启动回测"""
    global current_backtest, backtest_status, backtest_results
    
    try:
        data = request.get_json()
        
        # 验证参数
        required_fields = ['stock_code', 'company_name', 'start_date', 'end_date', 'initial_capital', 'frequency']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需参数: {field}'}), 400
        
        # 检查是否已有回测在运行
        if backtest_status["is_running"]:
            return jsonify({'error': '已有回测在运行中，请等待完成'}), 400
        
        # 更新状态
        backtest_status.update({
            "is_running": True,
            "progress": 0,
            "message": "正在初始化回测系统..."
        })
        
        # 清空之前的结果
        backtest_results = None
        
        # 在新线程中运行回测
        def run_backtest():
            global current_backtest, backtest_results, backtest_status
            
            try:
                # 创建回测实例
                current_backtest = BacktestSystem(
                    initial_capital=float(data['initial_capital']),
                    verbose=True
                )
                
                backtest_status.update({
                    "progress": 10,
                    "message": "回测系统初始化完成，开始运行回测..."
                })
                
                # 定义进度回调函数
                def progress_callback(progress, message):
                    backtest_status.update({
                        "progress": progress,
                        "message": message
                    })
                    logger.info(f"进度更新: {progress}% - {message}")
                
                # 运行回测
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                backtest_status.update({
                    "progress": 15,
                    "message": f"正在初始化回测 {data['company_name']} ({data['stock_code']})..."
                })
                
                results = loop.run_until_complete(current_backtest.run_backtest(
                    stock_code=data['stock_code'],
                    company_name=data['company_name'],
                    start_date=data['start_date'],
                    end_date=data['end_date'],
                    frequency=data['frequency'],
                    progress_callback=progress_callback
                ))
                
                backtest_status.update({
                    "progress": 95,
                    "message": "正在处理回测结果..."
                })
                
                # 处理结果以便JSON序列化
                processed_results = process_results_for_json(results)
                backtest_results = processed_results
                
                backtest_status.update({
                    "is_running": False,
                    "progress": 100,
                    "message": "回测完成！"
                })
                
                logger.info("回测完成")
                
            except Exception as e:
                logger.error(f"回测错误: {e}")
                backtest_status.update({
                    "is_running": False,
                    "progress": 0,
                    "message": f"回测失败: {str(e)}"
                })
            finally:
                if loop:
                    loop.close()
        
        # 启动回测线程
        thread = threading.Thread(target=run_backtest)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': '回测已启动',
            'status': backtest_status
        })
        
    except Exception as e:
        logger.error(f"启动回测失败: {e}")
        backtest_status.update({
            "is_running": False,
            "progress": 0,
            "message": f"启动失败: {str(e)}"
        })
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest/status', methods=['GET'])
def get_backtest_status():
    """获取回测状态"""
    return jsonify(backtest_status)

@app.route('/api/backtest/results', methods=['GET'])
def get_backtest_results():
    """获取回测结果"""
    global backtest_results
    
    if backtest_results is None:
        return jsonify({'error': '暂无回测结果'}), 404
    
    return jsonify(backtest_results)

@app.route('/api/backtest/stop', methods=['POST'])
def stop_backtest():
    """停止回测"""
    global backtest_status
    
    if not backtest_status["is_running"]:
        return jsonify({'error': '没有正在运行的回测'}), 400
    
    # 这里可以添加停止逻辑
    backtest_status.update({
        "is_running": False,
        "progress": 0,
        "message": "回测已停止"
    })
    
    return jsonify({'message': '回测已停止'})

@app.route('/api/backtest/download', methods=['GET'])
def download_results():
    """下载回测结果"""
    global backtest_results
    
    if backtest_results is None:
        return jsonify({'error': '暂无回测结果'}), 404
    
    try:
        # 生成文件名
        filename = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 保存结果到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backtest_results, f, ensure_ascii=False, indent=2, default=str)
        
        return send_from_directory('.', filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"下载结果失败: {e}")
        return jsonify({'error': str(e)}), 500

def process_results_for_json(results):
    """处理回测结果以便JSON序列化"""
    def convert_to_serializable(obj):
        if hasattr(obj, 'isoformat'):  # datetime对象
            return obj.isoformat()
        elif hasattr(obj, 'item'):  # numpy对象
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy数组
            return obj.tolist()
        else:
            return str(obj)
    
    def process_dict(d):
        if isinstance(d, dict):
            return {k: process_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [process_dict(item) for item in d]
        else:
            try:
                # 尝试JSON序列化
                json.dumps(d)
                return d
            except (TypeError, ValueError):
                return convert_to_serializable(d)
    
    return process_dict(results)

if __name__ == '__main__':
    print("🚀 启动回测系统Web服务器...")
    print("📱 前端地址: http://localhost:5000")
    print("🔧 API地址: http://localhost:5000/api")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) 