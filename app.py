from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import List
import uvicorn
from multi_agent_websocket import MultiAgentWebSocketManager

# 创建 FastAPI 应用
app = FastAPI(
    title="多Agent股票分析系统 API",
    description="基于LangGraph的多Agent并行股票分析系统，支持基本面、技术面、估值分析",
    version="3.0.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# WebSocket 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"客户端 <{websocket.client.host}:{websocket.client.port}> 已连接. 当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"客户端 <{websocket.client.host}:{websocket.client.port}> 已断开.  当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"发送消息失败: {e}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"广播消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@app.get("/")
async def read_root():
    return {
        "message": "多Agent股票分析系统 API",
        "version": "3.0.0",
        "features": [
            "多Agent并行分析（基本面+技术面+估值分析）",
            "实时WebSocket通信",
            "综合投资报告生成",
            "完整数据展示",
            "真实Markdown渲染"
        ],
        "endpoints": {
            "websocket": "/ws/multi",
            "frontend": "/static/index.html",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/connections")
async def get_connections():
    return {
        "active_connections": len(manager.active_connections),
        "connections": [
            {
                "id": id(conn),
                "state": conn.client_state.name if hasattr(conn, 'client_state') else "unknown"
            }
            for conn in manager.active_connections
        ]
    }

@app.websocket("/ws/multi")
async def multi_agent_websocket_endpoint(websocket: WebSocket):
    """多Agent分析的WebSocket端点"""
    await manager.connect(websocket)
    multi_agent_manager = MultiAgentWebSocketManager(websocket)
    
    try:
        while True:
            # 等待客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                print(f"[多Agent] 收到消息: {message.get('type', 'unknown')}")
                
                if message["type"] == "execute_multi_agent":
                    query = message["query"]
                    print(f"[多Agent] 开始执行查询: {query[:50]}...")
                    await multi_agent_manager.execute_multi_agent_analysis(query)
                    
                elif message["type"] == "ping":
                    # 心跳检测
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }))
                    
            except json.JSONDecodeError as e:
                print(f"[多Agent] JSON 解析错误: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "无效的 JSON 格式"
                }))
            except Exception as e:
                print(f"[多Agent] 处理消息时出错: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"处理消息时出错: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[多Agent] 客户端主动断开连接")
    except Exception as e:
        print(f"[多Agent] WebSocket 错误: {e}")
        manager.disconnect(websocket)

# 启动配置
if __name__ == "__main__":
    print("🚀 启动多Agent股票分析系统...")
    print("📍 API 文档: http://localhost:8000/docs")
    print("🌐 前端页面: http://localhost:8000/static/index.html")
    print("🔌 多Agent WebSocket: ws://localhost:8000/ws/multi")
    print("🤖 支持功能：基本面分析 + 技术面分析 + 估值分析 + 综合报告")
    
    uvicorn.run(
        "app:app",  # 使用导入字符串格式
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True  # 现在可以正常使用重载功能
    ) 