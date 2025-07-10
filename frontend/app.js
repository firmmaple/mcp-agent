let ws = null;
let isExecuting = false;
let logCount = 0;
let isConnecting = false; // 防止重复连接
let reconnectAttempts = 0; // 重连尝试次数
let maxReconnectAttempts = 3; // 最大重连次数
let reconnectTimer = null; // 重连定时器
let finalReport = null; // 存储最终报告

// 查询模板
const queryTemplates = {
    '茅台': {
        companyName: '贵州茅台',
        stockCode: 'sh.600519'
    },
    '比亚迪': {
        companyName: '比亚迪',
        stockCode: 'sz.002594'
    },
    '海康威视': {
        companyName: '海康威视',
        stockCode: 'sz.002415'
    },
    '宁德时代': {
        companyName: '宁德时代',
        stockCode: 'sz.300750'
    }
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
    if (statusElement) {
        statusElement.className = `status status-${status}`;
        statusElement.textContent = text;
    }
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

// 检查表格分隔行的函数
function isTableSeparatorLine(line) {
    if (!line.startsWith('|') || !line.endsWith('|')) {
        return false;
    }
    
    // 移除首尾的 |
    const content = line.slice(1, -1);
    const cells = content.split('|');
    
    // 检查每个单元格是否只包含空格、破折号和冒号
    return cells.every(cell => {
        const trimmed = cell.trim();
        return trimmed.match(/^:?-+:?$/) || trimmed.match(/^[\s\-:]+$/);
    });
}

// 全局Markdown渲染函数
function renderMarkdown(text) {
        // 检查输入有效性
        if (!text || typeof text !== 'string') {
            console.warn("renderMarkdown 收到无效输入:", text);
            return '';
        }
        
        if (text.trim().length === 0) {
            console.warn("renderMarkdown 收到空字符串");
            return '';
        }
        
        console.log("renderMarkdown 处理文本，长度:", text.length);
        
        // 预处理表格数据
        function preprocessTables(text) {
            // 确保表格前后有空行
            text = text.replace(/([^\n])\n(\|[^\n]+\|)/g, '$1\n\n$2');
            text = text.replace(/(\|[^\n]+\|)\n([^\n|])/g, '$1\n\n$2');
            return text;
        }
        
        // 基本markdown格式fallback渲染
        function renderFallbackMarkdown(text) {
            let result = text;
            
            // 首先处理字面上的\n字符（转换为真正的换行符）
            result = result.replace(/\\n/g, '\n');
            
            // 特殊检查：如果是单独的表格行，优先处理
            const trimmedText = result.trim();
            if (trimmedText.startsWith('|') && trimmedText.endsWith('|') && !trimmedText.includes('\n')) {
                if (isTableSeparatorLine(trimmedText)) {
                    // 如果是分隔行，直接返回空字符串（不显示）
                    return '';
                }
                
                // 单独的表格行，直接返回表格渲染结果
                return renderTableFallback(result);
            }
            
            // 处理表格
            if (result.includes('|')) {
                result = renderTableFallback(result);
            }
            
            // 处理标题（必须在其他格式之前处理，按照从多到少的顺序处理，避免冲突）
            result = result.replace(/^#{6}\s*(.+)$/gm, '<h6 style="color: #a78bfa; font-size: 14px; margin: 8px 0 5px 0; font-weight: normal;">$1</h6>');
            result = result.replace(/^#{5}\s*(.+)$/gm, '<h5 style="color: #a78bfa; font-size: 16px; margin: 10px 0 6px 0; font-weight: bold;">$1</h5>');
            result = result.replace(/^#{4}\s*(.+)$/gm, '<h4 style="color: #a78bfa; font-size: 18px; margin: 12px 0 8px 0; font-weight: bold;">$1</h4>');
            result = result.replace(/^#{3}\s*(.+)$/gm, '<h3 style="color: #a78bfa; font-size: 20px; margin: 15px 0 10px 0; font-weight: bold;">$1</h3>');
            result = result.replace(/^#{2}\s*(.+)$/gm, '<h2 style="color: #a78bfa; font-size: 22px; margin: 20px 0 12px 0; font-weight: bold;">$1</h2>');
            result = result.replace(/^#{1}\s*(.+)$/gm, '<h1 style="color: #a78bfa; font-size: 24px; margin: 25px 0 15px 0; font-weight: bold;">$1</h1>');
            
            // 处理粗体 **text**
            result = result.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>');
            
            // 处理斜体 *text* (避免处理单独的星号，确保内容不为空)
            result = result.replace(/\*([^\*\n]+?)\*/g, function(match, content) {
                // 确保内容不为空且不全是空格
                if (content && content.trim().length > 0) {
                    return '<em>' + content + '</em>';
                }
                return match; // 如果内容为空，保持原样
            });
            
            // 处理代码 `code`
            result = result.replace(/`([^`]+?)`/g, '<code style="background: rgba(37, 99, 235, 0.3); padding: 2px 6px; border-radius: 3px; color: #ffffff; border: 1px solid rgba(37, 99, 235, 0.5); font-family: \'Courier New\', monospace; font-weight: 500;">$1</code>');
            
            // 处理链接 [text](url)
            result = result.replace(/\[([^\]]+?)\]\(([^)]+?)\)/g, '<a href="$2" style="color: #007bff; text-decoration: underline;">$1</a>');
            
            // 处理列表项
            result = result.replace(/^[-*+]\s+(.+)$/gm, '<li style="margin: 3px 0;">$1</li>');
            result = result.replace(/^(\d+)\.\s+(.+)$/gm, '<li style="margin: 3px 0;">$2</li>');
            
            // 将连续的li包装在ul中
            result = result.replace(/(<li[^>]*>.*?<\/li>(?:\s*<li[^>]*>.*?<\/li>)*)/gs, '<ul style="margin: 8px 0; padding-left: 20px;">$1</ul>');
            
            // 清理剩余的单独星号（前后有空格或在行边界的孤立星号）
            result = result.replace(/(^|\s)\*(\s|$)/g, '$1$2');
            
            // 处理换行符（将真正的换行符转换为<br>）
            result = result.replace(/\n/g, '<br>');
            
            // 清理多余的连续<br>标签
            result = result.replace(/(<br\s*\/?>){3,}/g, '<br><br>');
            
            return result;
        }
        
        // 简单的表格渲染fallback
        function renderTableFallback(text) {
            // 特殊处理：如果文本只是单独的表格行，暂时跳过单独渲染，等待完整表格
            const trimmedText = text.trim();
            if (trimmedText.startsWith('|') && trimmedText.endsWith('|') && trimmedText.split('\n').length === 1) {
                // 检查是否是分隔行
                if (isTableSeparatorLine(trimmedText)) {
                    // 如果是分隔行，直接返回空字符串（不显示）
                    return '';
                }
                
                // 单独的表格行，先不处理，保持原格式让它和其他行一起组成完整表格
                return text;
            }
            
            const lines = text.split('\n');
            let inTable = false;
            let tableHtml = '';
            let result = '';
            let headerProcessed = false;
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].trim();
                
                if (line.startsWith('|') && line.endsWith('|')) {
                    if (!inTable) {
                        inTable = true;
                        headerProcessed = false;
                        tableHtml = '<table style="border-collapse: collapse; width: 100%; margin: 15px 0; border: 1px solid #ddd;">';
                    }
                    
                    // 检查是否是分隔行（如 |---|---| 或 |:--|--:| 等）
                    if (isTableSeparatorLine(line)) {
                        headerProcessed = true;
                        continue; // 跳过分隔行，不输出到页面
                    }
                    
                    const cells = line.split('|').slice(1, -1); // 移除首尾的空元素
                    const isHeader = !headerProcessed; // 第一个非分隔行是表头
                    
                    tableHtml += '<tr>';
                    cells.forEach(cell => {
                        const cellContent = cell.trim();
                        const tag = isHeader ? 'th' : 'td';
                        const style = isHeader ? 
                            'border: 1px solid #374151; padding: 12px 8px; background: rgba(59, 130, 246, 0.2); font-weight: bold; text-align: center; color: white;' :
                            'border: 1px solid #374151; padding: 10px 8px; text-align: left; color: white;';
                        tableHtml += `<${tag} style="${style}">${cellContent}</${tag}>`;
                    });
                    tableHtml += '</tr>';
                    
                    if (isHeader) {
                        headerProcessed = true;
                    }
                } else {
                    if (inTable) {
                        tableHtml += '</table>';
                        result += tableHtml + '\n';
                        tableHtml = '';
                        inTable = false;
                        headerProcessed = false;
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
        
        // 检测是否包含完整的表格结构
        function hasCompleteTable(text) {
            const lines = text.split('\n');
            let hasHeader = false;
            let hasSeparator = false;
            let hasDataRow = false;
            
            for (let line of lines) {
                line = line.trim();
                if (line.startsWith('|') && line.endsWith('|')) {
                    if (isTableSeparatorLine(line)) {
                        hasSeparator = true;
                    } else if (!hasHeader) {
                        hasHeader = true;
                    } else {
                        hasDataRow = true;
                    }
                }
            }
            
            return hasHeader && hasSeparator && hasDataRow;
        }
        
        // 强化检测：如果包含特定格式标记，优先使用fallback确保一致性
        const hasMarkdownFeatures = (
            text.includes('|') && (text.match(/\|.*\|/) || text.trim().startsWith('|')) ||
            text.includes('\\n') ||  // 包含字面上的\n字符
            text.match(/^#{1,6}\s/m) ||  // 包含标题
            text.includes('**') ||  // 包含粗体
            text.includes('`') ||   // 包含代码
            text.match(/^\s*[-*+]\s/m) || // 包含列表
            text.match(/^\s*\d+\.\s/m)    // 包含有序列表
        );
        
        if (hasMarkdownFeatures) {
            console.log('检测到markdown格式内容，使用fallback渲染确保一致性');
            return renderFallbackMarkdown(text);
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
                    tables: true,         // 明确启用表格支持
                    smartypants: false,   // 禁用智能标点转换
                    xhtml: false          // 不使用XHTML输出
                });
                
                const rendered = marked.parse(preprocessedText);
                
                // 检查渲染结果：如果包含表格但仍有未处理的 | 符号，说明marked.js没有完全处理
                if (text.includes('|') && hasCompleteTable(text)) {
                    // 检查渲染后是否还有未处理的表格行
                    if (rendered.includes('|') && rendered.match(/\|[^<>]*\|/)) {
                        console.warn('marked.js未完全处理表格，使用fallback渲染');
                        return renderFallbackMarkdown(text);
                    }
                }
                
                // 调试：检查渲染结果
                if (rendered.includes('<table')) {
                    console.log('表格渲染成功');
                } else if (text.includes('|') && text.match(/\|.*\|/)) {
                    console.warn('包含表格数据但未渲染成功，使用fallback');
                    return renderFallbackMarkdown(text);
                }
                
                return rendered;
            } catch (e) {
                // 如果Markdown解析失败，使用fallback渲染
                console.error('Markdown parsing failed:', e);
                return renderFallbackMarkdown(text);
            }
        } else {
            console.warn('marked.js library not available, using fallback');
            // 如果marked库不可用，使用fallback渲染（包括基本markdown格式）
            return renderFallbackMarkdown(text);
        }
}

function addLog(message, type = "info", timestamp = null) {
    const logsContainer = document.getElementById("logs");
    if (!logsContainer) return;
    
    const logEntry = document.createElement("div");
    logEntry.className = `log-entry log-${type}`;
    
    const time = timestamp || new Date().toLocaleTimeString();
    
    // 检查是否是最终报告 - 只处理真正包含内容的报告
    if (message.includes("📄 最终报告")) {
        console.log("检测到最终报告消息，原始消息长度:", message.length);
        
        // 提取报告内容 - 改进的匹配规则，支持多种格式
        let reportMatch = null;
        
        // 模式1: 📄 最终报告:\n{content}
        reportMatch = message.match(/📄 最终报告:\s*\n([\s\S]*)/);
        if (!reportMatch) {
            // 模式2: 📄 最终报告:{content}
            reportMatch = message.match(/📄 最终报告:\s*([\s\S]*)/);
        }
        if (!reportMatch) {
            // 模式3: 📄 最终报告：{content} (中文冒号)
            reportMatch = message.match(/📄 最终报告：\s*([\s\S]*)/);
        }
        if (!reportMatch) {
            // 模式4: 更宽松的匹配
            reportMatch = message.match(/📄\s*最终报告[：:]\s*([\s\S]*)/);
        }
        
        if (reportMatch && reportMatch[1].trim().length > 10) {
            finalReport = reportMatch[1].trim();
            console.log("✅ 成功提取最终报告，长度:", finalReport.length);
            console.log("报告内容预览:", finalReport.substring(0, 200) + "...");
            
            // 启用下载按钮
            const downloadTxtBtn = document.getElementById("downloadTxtBtn");
            if (downloadTxtBtn) {
                downloadTxtBtn.disabled = false;
            }
            
            addLog("📄 最终报告已准备就绪，可以下载", "success");
        } else if (reportMatch) {
            console.log("⚠️ 检测到最终报告标题，但内容太短，跳过");
        }
    }
    
    const renderedMessage = renderMarkdown(message);
    
    // 调试：记录渲染信息
    if (message.length > 500) { // 对于长消息进行调试记录
        console.log('长消息渲染调试:');
        console.log('原始长度:', message.length);
        console.log('渲染后长度:', renderedMessage.length);
        console.log('原始内容前200字符:', message.substring(0, 200));
        console.log('渲染后内容前200字符:', renderedMessage.substring(0, 200));
    }
    
    logEntry.innerHTML = `
        <div class="timestamp">${time}</div>
        <div class="log-message">${renderedMessage}</div>
    `;
    
    logsContainer.appendChild(logEntry);
    
    // 更新日志计数
    logCount++;
    const logCountElement = document.getElementById("logCount");
    if (logCountElement) {
        logCountElement.textContent = logCount;
    }
    
    // 自动滚动
    const autoScrollElement = document.getElementById("autoScroll");
    if (autoScrollElement && autoScrollElement.checked) {
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
    
    const companyNameElement = document.getElementById("companyName");
    const stockCodeElement = document.getElementById("stockCode");
    
    if (!companyNameElement || !stockCodeElement) {
        addLog("页面元素未正确加载，请刷新页面", "error");
        return;
    }
    
    const companyName = companyNameElement.value.trim();
    const stockCode = stockCodeElement.value.trim();
    
    if (!companyName || !stockCode) {
        addLog("请输入公司名称和股票代码", "error");
        return;
    }
    
    // 重置最终报告和下载按钮状态
    finalReport = null;
    const downloadTxtBtn = document.getElementById("downloadTxtBtn");
    if (downloadTxtBtn) {
        downloadTxtBtn.disabled = true;
    }
    
    isExecuting = true;
    updateExecuteButton();
    updateStatus("running", "执行中");
    
    const messageType = 'execute_multi_agent';
    
    addLog(`开始执行多Agent并行分析: ${companyName} (${stockCode})`, "info");
    ws.send(JSON.stringify({
        type: messageType,
        company_name: companyName,
        stock_code: stockCode
    }));
}

function updateExecuteButton() {
    const btn = document.getElementById("executeBtn");
    if (!btn) return;
    
    const btnText = btn.querySelector('.btn-text');
    if (!btnText) return;
    
    btn.disabled = isExecuting;
    
    if (isExecuting) {
        btnText.textContent = "多Agent分析中...";
    } else {
        btnText.textContent = "开始多Agent分析";
    }
}

// TXT格式下载函数
function downloadReportAsTxt() {
    console.log("downloadReportAsTxt 被调用");
    console.log("finalReport 状态:", finalReport ? `有内容，长度: ${finalReport.length}` : "为空");
    
    if (!finalReport) {
        addLog("❌ 暂无可下载的报告，请先完成分析", "warning");
        return;
    }
    
    if (finalReport.trim().length === 0) {
        addLog("❌ 报告内容为空", "warning");
        return;
    }
    
    const companyNameElement = document.getElementById("companyName");
    const stockCodeElement = document.getElementById("stockCode");
    
    if (!companyNameElement || !stockCodeElement) {
        addLog("页面元素未正确加载", "error");
        return;
    }
    
    const companyName = companyNameElement.value.trim();
    const stockCode = stockCodeElement.value.trim();
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    
    // 创建报告内容
    const reportContent = `${companyName} (${stockCode}) 投资分析报告
生成时间: ${new Date().toLocaleString()}
==========================================

${finalReport}

==========================================
报告由多Agent股票分析系统生成
包含基本面分析、技术分析、估值分析三个维度的专业分析`;
    
    // 创建并下载文件
    const blob = new Blob([reportContent], { type: 'text/plain; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `投资分析报告_${companyName}_${stockCode}_${timestamp}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
    addLog("投资分析报告已下载 (TXT格式)", "success");
}

function clearLogs() {
    const logsElement = document.getElementById("logs");
    if (logsElement) {
        logsElement.innerHTML = "";
    }
    
    logCount = 0;
    const logCountElement = document.getElementById("logCount");
    if (logCountElement) {
        logCountElement.textContent = logCount;
    }
    
    addLog("日志已清空", "info");
}

function exportLogs() {
    const logsElement = document.getElementById("logs");
    if (!logsElement) {
        addLog("无法获取日志内容", "error");
        return;
    }
    
    const logs = logsElement.innerText;
    const blob = new Blob([logs], { type: 'text/plain; charset=utf-8' });
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
    const template = queryTemplates[templateType];
    if (!template) {
        addLog(`未找到${templateType}模板`, "error");
        return;
    }
    
    const companyNameElement = document.getElementById("companyName");
    const stockCodeElement = document.getElementById("stockCode");
    
    if (!companyNameElement || !stockCodeElement) {
        addLog("页面元素未正确加载", "error");
        return;
    }
    
    companyNameElement.value = template.companyName;
    stockCodeElement.value = template.stockCode;
    addLog(`已加载${templateType}分析模板`, "info");
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