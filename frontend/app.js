let ws = null;
let isExecuting = false;
let logCount = 0;
let isConnecting = false; // 防止重复连接
let reconnectAttempts = 0; // 重连尝试次数
let maxReconnectAttempts = 3; // 最大重连次数
let reconnectTimer = null; // 重连定时器

// 查询模板
const queryTemplates = {
    '茅台': `请分析贵州茅台(sh.600519)的投资价值

这是一个多Agent并行分析任务，将由以下三个专业Agent协作完成：
1. 基本面分析Agent - 分析财务状况、盈利能力、成长性等
2. 技术分析Agent - 分析价格趋势、技术指标、支撑阻力位等  
3. 估值分析Agent - 分析估值指标、与行业对比、投资价值等

最终将由汇总Agent整合三个专业分析，生成综合投资建议报告。`,
    
    '比亚迪': `请分析比亚迪(sz.002594)的投资价值

这是一个多Agent并行分析任务，将由以下三个专业Agent协作完成：
1. 基本面分析Agent - 分析财务状况、盈利能力、成长性等
2. 技术分析Agent - 分析价格趋势、技术指标、支撑阻力位等  
3. 估值分析Agent - 分析估值指标、与行业对比、投资价值等

最终将由汇总Agent整合三个专业分析，生成综合投资建议报告。`,
    
    '自定义': `请分析[公司名称]([股票代码])的投资价值

格式示例：
- 请分析贵州茅台(sh.600519)的投资价值
- 请分析比亚迪(sz.002594)的投资价值
- 请分析宁德时代(sz.300750)的投资价值

这是一个多Agent并行分析任务，将由基本面、技术面、估值分析三个专业Agent协作完成。`
};

function connect() {
    // 防止重复连接
    if (isConnecting) {
        console.log("正在连接中，跳过重复连接请求");
        return;
    }
    
    // 清除重连定时器
    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
    }
    
    // 直接连接到多Agent端点
    const wsUrl = "ws://localhost:8000/ws/multi";
    
    // 如果已有连接且状态正常，则不重新连接
    if (ws && ws.readyState === WebSocket.OPEN && ws.url.endsWith('/ws/multi')) {
        console.log("连接已存在且正常，无需重新连接");
        return;
    }
    
    // 关闭现有连接
    if (ws) {
        ws.onclose = null; // 移除close事件监听，防止触发重连
        ws.close();
        ws = null;
    }
    
    isConnecting = true;
    updateStatus("connecting", "连接中...");
    addLog("正在建立多Agent连接...", "info");
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function(event) {
        isConnecting = false;
        reconnectAttempts = 0; // 重置重连计数
        updateReconnectCount();
        updateStatus("connected", "已连接");
        addLog("多Agent系统连接已建立", "success");
    };
    
    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            addLog(data.message, data.type, data.timestamp);
            
            if (data.type === "execution_complete") {
                isExecuting = false;
                updateExecuteButton();
                updateStatus("connected", "已连接");
            }
        } catch (e) {
            addLog(event.data, "info");
        }
    };
    
    ws.onclose = function(event) {
        isConnecting = false;
        updateStatus("disconnected", "连接断开");
        
        // 只在非主动断开时尝试重连
        if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            updateReconnectCount();
            addLog(`多Agent连接断开，${3}秒后尝试第${reconnectAttempts}次重连...`, "warning");
            
            reconnectTimer = setTimeout(() => {
                if (reconnectAttempts <= maxReconnectAttempts) {
                    connect();
                }
            }, 3000);
        } else if (reconnectAttempts >= maxReconnectAttempts) {
            addLog("已达到最大重连次数，请点击手动连接按钮或刷新页面", "error");
        } else {
            addLog("多Agent连接已断开", "info");
        }
    };
    
    ws.onerror = function(error) {
        isConnecting = false;
        updateStatus("disconnected", "连接错误");
        addLog("多Agent连接错误", "error");
        console.error("WebSocket错误:", error);
    };
}

function updateStatus(status, text) {
    const statusElement = document.getElementById("status");
    statusElement.className = `status status-${status}`;
    statusElement.textContent = text;
}

function updateReconnectCount() {
    const reconnectCountElement = document.getElementById("reconnectCount");
    if (reconnectCountElement) {
        reconnectCountElement.textContent = reconnectAttempts;
    }
}

function manualConnect() {
    // 重置重连计数
    reconnectAttempts = 0;
    updateReconnectCount();
    
    // 清除重连定时器
    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
    }
    
    addLog("手动重连多Agent系统...", "info");
    connect();
}

function addLog(message, type = "info", timestamp = null) {
    const logsContainer = document.getElementById("logs");
    const logEntry = document.createElement("div");
    logEntry.className = `log-entry log-${type}`;
    
    const time = timestamp || new Date().toLocaleTimeString();
    
    // 使用marked.js进行真正的Markdown渲染
    function renderMarkdown(text) {
        // 预处理表格数据
        function preprocessTables(text) {
            // 确保表格前后有空行
            text = text.replace(/([^\n])\n(\|[^\n]+\|)/g, '$1\n\n$2');
            text = text.replace(/(\|[^\n]+\|)\n([^\n|])/g, '$1\n\n$2');
            return text;
        }
        
        // 简单的表格渲染fallback
        function renderTableFallback(text) {
            const lines = text.split('\n');
            let inTable = false;
            let tableHtml = '';
            let result = '';
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].trim();
                
                if (line.startsWith('|') && line.endsWith('|')) {
                    if (!inTable) {
                        inTable = true;
                        tableHtml = '<table class="markdown-table">';
                    }
                    
                    // 检查是否是分隔行
                    if (line.match(/^\|[\s\-:]+\|$/)) {
                        continue; // 跳过分隔行
                    }
                    
                    const cells = line.split('|').slice(1, -1); // 移除首尾的空元素
                    const isHeader = i === 0 || (lines[i-1] && !lines[i-1].startsWith('|'));
                    
                    tableHtml += '<tr>';
                    cells.forEach(cell => {
                        const cellContent = cell.trim();
                        const tag = isHeader ? 'th' : 'td';
                        tableHtml += `<${tag}>${cellContent}</${tag}>`;
                    });
                    tableHtml += '</tr>';
                } else {
                    if (inTable) {
                        tableHtml += '</table>';
                        result += tableHtml + '\n';
                        tableHtml = '';
                        inTable = false;
                    }
                    result += line + '\n';
                }
            }
            
            if (inTable) {
                tableHtml += '</table>';
                result += tableHtml;
            }
            
            return result;
        }
        
        // 检查是否有marked库可用
        if (typeof marked !== 'undefined') {
            try {
                // 预处理表格
                const preprocessedText = preprocessTables(text);
                
                // 配置marked选项
                marked.setOptions({
                    breaks: true,          // 支持换行
                    gfm: true,            // GitHub风格的Markdown（包含表格支持）
                    headerIds: false,     // 不生成header ID
                    mangle: false,        // 不混淆邮箱
                    sanitize: false,      // 不sanitize HTML
                    tables: true          // 明确启用表格支持
                });
                
                // 调试：检查是否包含表格
                if (text.includes('|') && text.includes('\n')) {
                    console.log('检测到可能的表格数据:', text.substring(0, 200));
                }
                
                const rendered = marked.parse(preprocessedText);
                
                // 调试：检查渲染结果
                if (rendered.includes('<table')) {
                    console.log('表格渲染成功');
                } else if (text.includes('|')) {
                    console.warn('包含表格数据但未渲染成功，使用fallback');
                    return renderTableFallback(text).replace(/\n/g, '<br>');
                }
                
                return rendered;
            } catch (e) {
                // 如果Markdown解析失败，尝试fallback表格渲染
                console.error('Markdown parsing failed:', e);
                if (text.includes('|')) {
                    return renderTableFallback(text).replace(/\n/g, '<br>');
                }
                return text.replace(/\n/g, '<br>');
            }
        } else {
            console.warn('marked.js library not available, using fallback');
            // 如果marked库不可用，使用fallback表格渲染
            if (text.includes('|')) {
                return renderTableFallback(text).replace(/\n/g, '<br>');
            }
            return text.replace(/\n/g, '<br>');
        }
    }
    
    const renderedMessage = renderMarkdown(message);
    
    logEntry.innerHTML = `
        <div class="timestamp">${time}</div>
        <div class="log-message">${renderedMessage}</div>
    `;
    
    logsContainer.appendChild(logEntry);
    
    // 更新日志计数
    logCount++;
    document.getElementById("logCount").textContent = logCount;
    
    // 自动滚动
    if (document.getElementById("autoScroll").checked) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

function executeAgent() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        addLog("WebSocket 未连接，请等待连接建立", "error");
        return;
    }
    
    if (isExecuting) {
        addLog("Agent 正在执行中，请等待完成", "warning");
        return;
    }
    
    const query = document.getElementById("queryInput").value.trim();
    if (!query) {
        addLog("请输入查询内容", "error");
        return;
    }
    
    isExecuting = true;
    updateExecuteButton();
    updateStatus("running", "执行中");
    
    const messageType = 'execute_multi_agent';
    
    addLog(`开始执行多Agent并行分析...`, "info");
    ws.send(JSON.stringify({
        type: messageType,
        query: query
    }));
}

function updateExecuteButton() {
    const btn = document.getElementById("executeBtn");
    const btnText = btn.querySelector('.btn-text');
    
    btn.disabled = isExecuting;
    
    if (isExecuting) {
        btnText.textContent = "多Agent分析中...";
    } else {
        btnText.textContent = "开始多Agent分析";
    }
}

function clearLogs() {
    document.getElementById("logs").innerHTML = "";
    logCount = 0;
    document.getElementById("logCount").textContent = logCount;
    addLog("日志已清空", "info");
}

function exportLogs() {
    const logs = document.getElementById("logs").innerText;
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
    addLog("日志已导出", "success");
}

function loadTemplate(templateType) {
    const queryInput = document.getElementById("queryInput");
    if (queryTemplates[templateType]) {
        queryInput.value = queryTemplates[templateType];
        addLog(`已加载${templateType}分析模板`, "info");
    }
}

// 页面卸载时清理连接
window.addEventListener('beforeunload', function() {
    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
    }
    if (ws) {
        ws.onclose = null; // 移除close事件监听
        ws.close();
    }
});

// 页面加载时的初始化
window.onload = function() {
    // 初始化按钮状态
    updateExecuteButton();
    
    // 连接WebSocket
    connect();
}; 