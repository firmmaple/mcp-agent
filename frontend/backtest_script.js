/**
 * 回测系统前端脚本
 * 处理用户交互、API调用、图表渲染等功能
 */

// 全局变量
let statusInterval = null;
let valueChart = null;
let returnsChart = null;
let currentResults = null;

// API 基础URL
const API_BASE = '/api';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

/**
 * 初始化页面
 */
async function initializePage() {
    console.log('🚀 初始化回测系统页面...');
    
    try {
        // 检查关键DOM元素
        const stockChipsContainer = document.getElementById('stockChips');
        if (!stockChipsContainer) {
            console.error('❌ 关键元素stockChips未找到，页面可能未正确加载');
            showToast('页面加载异常，请刷新重试', 'error');
            return;
        }
        console.log('✅ 关键DOM元素检查通过');
        
        // 设置默认日期
        setupDefaultDates();
        console.log('✅ 默认日期设置完成');
        
        // 立即显示一个临时的快速选择，确保用户能看到这个功能
        showTemporaryStockChips();
        
        // 先加载离线股票建议，确保用户能立即看到内容
        console.log('🔄 先加载离线股票列表作为备用...');
        loadOfflineStockSuggestions();
        
        // 然后尝试加载在线股票建议
        try {
            console.log('🔄 尝试加载在线股票建议...');
            await loadStockSuggestions();
        } catch (error) {
            console.error('❌ 在线加载失败，继续使用离线列表:', error);
            showToast('在线股票列表加载失败，使用离线列表', 'warning');
        }
        
        // 添加窗口大小变化监听器，确保图表响应式更新
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                console.log('📐 窗口大小变化，调整图表大小...');
                if (currentResults) {
                    // 先尝试调整现有图表大小
                    try {
                        if (valueChart) {
                            valueChart.resize();
                            console.log('✅ 资产价值图表大小已调整');
                        }
                        if (returnsChart) {
                            returnsChart.resize();
                            console.log('✅ 收益分布图表大小已调整');
                        }
                    } catch (error) {
                        console.warn('⚠️ 图表resize失败，重新渲染:', error);
                        // 如果resize失败，则重新渲染
                        if (valueChart) {
                            valueChart.destroy();
                            valueChart = null;
                        }
                        if (returnsChart) {
                            returnsChart.destroy();
                            returnsChart = null;
                        }
                        setTimeout(() => {
                            renderCharts(currentResults);
                        }, 100);
                    }
                }
            }, 300); // 300ms防抖
        });
        
        // 检查系统状态
        updateSystemStatus('系统就绪', 'success');
        console.log('✅ 页面初始化完成');
        
    } catch (error) {
        console.error('❌ 页面初始化失败:', error);
        showToast('页面初始化失败', 'error');
    }
}

/**
 * 显示临时的股票快选（确保用户能立即看到这个功能）
 */
function showTemporaryStockChips() {
    const chipsContainer = document.getElementById('stockChips');
    if (!chipsContainer) return;
    
    chipsContainer.innerHTML = '<div class="stock-chip" style="background: #e2e8f0; color: #666;">⏳ 正在加载股票建议...</div>';
    console.log('📝 显示临时加载提示');
}

/**
 * 添加重新加载股票建议的按钮
 */
function addReloadButton() {
    const chipsContainer = document.getElementById('stockChips');
    if (!chipsContainer) return;
    
    // 检查是否已经有重新加载按钮
    if (document.getElementById('reloadStocksBtn')) return;
    
    const reloadBtn = document.createElement('div');
    reloadBtn.id = 'reloadStocksBtn';
    reloadBtn.className = 'stock-chip reload-btn';
    reloadBtn.innerHTML = '🔄 重新加载';
    reloadBtn.title = '点击重新加载股票建议';
    
    reloadBtn.onclick = async () => {
        // 防止重复点击
        if (reloadBtn.innerHTML.includes('加载中')) return;
        
        reloadBtn.innerHTML = '⏳ 加载中...';
        reloadBtn.style.pointerEvents = 'none';
        
        try {
            await loadStockSuggestions();
            showToast('股票建议已更新', 'success');
        } catch (error) {
            console.error('重新加载失败:', error);
            reloadBtn.innerHTML = '🔄 重新加载';
            reloadBtn.style.pointerEvents = 'auto';
            showToast('重新加载失败', 'error');
        }
    };
    
    chipsContainer.appendChild(reloadBtn);
}

/**
 * 设置默认日期
 */
function setupDefaultDates() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 3); // 设为3个月前，快速模式
    
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    
    // 设置推荐的决策频率为每周
    document.getElementById('frequency').value = 'weekly';
    
    console.log('✅ 默认配置已设置为快速模式：3个月 + 每周决策');
}

/**
 * 加载股票建议
 */
async function loadStockSuggestions() {
    try {
        console.log('🔍 开始加载股票建议...');
        
        const response = await fetch(`${API_BASE}/stocks/suggest`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} - ${response.statusText}`);
        }
        
        const suggestions = await response.json();
        console.log('📊 获取到股票建议:', suggestions);
        
        renderStockChips(suggestions);
        console.log(`✅ 成功加载了 ${suggestions.length} 个股票建议`);
        
    } catch (error) {
        console.error('❌ 加载股票建议失败:', error);
        
        // 提供离线模式的备用股票列表
        console.log('🔄 使用离线股票列表作为备用...');
        loadOfflineStockSuggestions();
        
        showToast('网络加载失败，使用离线股票列表', 'warning');
    }
}

/**
 * 加载离线股票建议（备用方案）
 */
function loadOfflineStockSuggestions() {
    const offlineSuggestions = [
        {"name": "贵州茅台", "code": "sh.600519", "type": "白酒"},
        {"name": "比亚迪", "code": "sz.002594", "type": "新能源汽车"},
        {"name": "海康威视", "code": "sz.002415", "type": "安防"},
        {"name": "宁德时代", "code": "sz.300750", "type": "新能源"},
        {"name": "五粮液", "code": "sh.000858", "type": "白酒"},
        {"name": "中国平安", "code": "sh.601318", "type": "保险"},
        {"name": "招商银行", "code": "sh.600036", "type": "银行"},
        {"name": "万科A", "code": "sz.000002", "type": "房地产"}
    ];
    
    renderStockChips(offlineSuggestions);
    console.log(`✅ 离线模式加载了 ${offlineSuggestions.length} 个股票建议`);
}

/**
 * 渲染股票选择按钮
 */
function renderStockChips(suggestions) {
    const chipsContainer = document.getElementById('stockChips');
    if (!chipsContainer) {
        console.error('❌ 找不到stockChips容器元素');
        return;
    }
    
    console.log(`📊 开始渲染 ${suggestions.length} 个股票选择按钮`);
    chipsContainer.innerHTML = '';
    
    // 添加股票选择按钮
    suggestions.forEach((stock, index) => {
        const chip = document.createElement('div');
        chip.className = 'stock-chip';
        chip.textContent = `${stock.name} (${stock.code})`;
        chip.setAttribute('data-name', stock.name);
        chip.setAttribute('data-code', stock.code);
        chip.onclick = () => selectStock(stock.name, stock.code, chip);
        chipsContainer.appendChild(chip);
        
        console.log(`  ✓ 添加股票按钮 ${index + 1}: ${stock.name} (${stock.code})`);
    });
    
    // 总是添加重新加载按钮
    addReloadButton();
    
    console.log(`✅ 股票选择按钮渲染完成，共 ${suggestions.length} 个股票 + 1 个重新加载按钮`);
}

/**
 * 选择股票
 */
function selectStock(name, code, chipElement) {
    console.log(`🎯 选择股票: ${name} (${code})`);
    
    // 清除其他选中状态
    document.querySelectorAll('.stock-chip').forEach(chip => {
        chip.classList.remove('active');
    });
    
    // 设置当前选中
    chipElement.classList.add('active');
    
    // 填充表单
    document.getElementById('companyName').value = name;
    document.getElementById('stockCode').value = code;
    
    console.log(`✅ 股票选择完成: ${name} (${code})`);
    showToast(`已选择 ${name} (${code})`, 'success');
}

/**
 * 开始回测
 */
async function startBacktest() {
    // 验证表单
    if (!validateForm()) {
        return;
    }
    
    // 收集参数
    const params = collectFormData();
    
    // 计算预计耗时
    const estimatedTime = calculateEstimatedTime(params);
    
    try {
        // 禁用开始按钮，启用停止按钮
        updateButtonStates(true);
        
        // 显示进度区域
        showProgressSection();
        
        // 隐藏结果区域
        hideResultsSection();
        
        // 显示预计时间
        showToast(`预计耗时: ${estimatedTime.text}，请耐心等待...`, 'info');
        updateProgress(5, `预计耗时 ${estimatedTime.text}，正在启动回测...`);
        
        // 发起回测请求
        const response = await fetch(`${API_BASE}/backtest/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ 回测启动成功:', result);
        
        showToast('回测已启动，正在运行...', 'success');
        updateSystemStatus('回测运行中', 'running');
        
        // 开始监控进度
        startProgressMonitoring(estimatedTime.minutes);
        
    } catch (error) {
        console.error('❌ 启动回测失败:', error);
        showToast(`启动回测失败: ${error.message}`, 'error');
        updateButtonStates(false);
        hideProgressSection();
        updateSystemStatus('启动失败', 'error');
    }
}

/**
 * 计算预计耗时
 */
function calculateEstimatedTime(params) {
    const startDate = new Date(params.start_date);
    const endDate = new Date(params.end_date);
    const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
    
    // 估算决策点数量
    let decisionPoints;
    switch (params.frequency) {
        case 'daily':
            decisionPoints = daysDiff;
            break;
        case 'weekly':
            decisionPoints = Math.ceil(daysDiff / 7);
            break;
        case 'monthly':
            decisionPoints = Math.ceil(daysDiff / 30);
            break;
        default:
            decisionPoints = Math.ceil(daysDiff / 7);
    }
    
    // 每个决策点预计耗时（分钟）
    const timePerDecision = {
        'daily': 0.5,    // 每日决策约30秒
        'weekly': 0.4,   // 每周决策约25秒
        'monthly': 0.3   // 每月决策约20秒
    };
    
    const estimatedMinutes = decisionPoints * (timePerDecision[params.frequency] || 0.4);
    
    let timeText;
    if (estimatedMinutes < 1) {
        timeText = "不到1分钟";
    } else if (estimatedMinutes < 60) {
        timeText = `约${Math.ceil(estimatedMinutes)}分钟`;
    } else {
        const hours = Math.floor(estimatedMinutes / 60);
        const minutes = Math.ceil(estimatedMinutes % 60);
        timeText = `约${hours}小时${minutes}分钟`;
    }
    
    return {
        minutes: estimatedMinutes,
        text: timeText,
        decisionPoints: decisionPoints
    };
}

/**
 * 停止回测
 */
async function stopBacktest() {
    try {
        const response = await fetch(`${API_BASE}/backtest/stop`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        showToast('回测已停止', 'warning');
        updateSystemStatus('回测已停止', 'warning');
        
        // 停止进度监控
        stopProgressMonitoring();
        
        // 更新按钮状态
        updateButtonStates(false);
        
    } catch (error) {
        console.error('❌ 停止回测失败:', error);
        showToast(`停止回测失败: ${error.message}`, 'error');
    }
}

/**
 * 重置表单
 */
function resetForm() {
    document.getElementById('companyName').value = '贵州茅台';
    document.getElementById('stockCode').value = 'sh.600519';
    document.getElementById('initialCapital').value = '100000';
    document.getElementById('frequency').value = 'weekly';
    
    // 重置日期
    setupDefaultDates();
    
    // 清除股票选择
    document.querySelectorAll('.stock-chip').forEach(chip => {
        chip.classList.remove('active');
    });
    
    // 隐藏进度和结果
    hideProgressSection();
    hideResultsSection();
    
    showToast('参数已重置', 'success');
}

/**
 * 验证表单
 */
function validateForm() {
    const companyName = document.getElementById('companyName').value.trim();
    const stockCode = document.getElementById('stockCode').value.trim();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const initialCapital = parseFloat(document.getElementById('initialCapital').value);
    
    if (!companyName) {
        showToast('请输入公司名称', 'warning');
        return false;
    }
    
    if (!stockCode) {
        showToast('请输入股票代码', 'warning');
        return false;
    }
    
    if (!startDate || !endDate) {
        showToast('请选择回测时间范围', 'warning');
        return false;
    }
    
    if (new Date(startDate) >= new Date(endDate)) {
        showToast('开始日期必须早于结束日期', 'warning');
        return false;
    }
    
    if (isNaN(initialCapital) || initialCapital < 10000) {
        showToast('初始资金必须大于等于10,000元', 'warning');
        return false;
    }
    
    return true;
}

/**
 * 收集表单数据
 */
function collectFormData() {
    return {
        company_name: document.getElementById('companyName').value.trim(),
        stock_code: document.getElementById('stockCode').value.trim(),
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        initial_capital: parseFloat(document.getElementById('initialCapital').value),
        frequency: document.getElementById('frequency').value
    };
}

/**
 * 更新按钮状态
 */
function updateButtonStates(isRunning) {
    const startBtn = document.getElementById('startBacktestBtn');
    const stopBtn = document.getElementById('stopBacktestBtn');
    
    if (isRunning) {
        startBtn.disabled = true;
        startBtn.querySelector('.btn-text').textContent = '回测运行中...';
        stopBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        startBtn.querySelector('.btn-text').textContent = '开始回测';
        stopBtn.disabled = true;
    }
}

/**
 * 显示进度区域
 */
function showProgressSection() {
    document.getElementById('progressSection').style.display = 'block';
    updateProgress(0, '正在初始化...');
}

/**
 * 隐藏进度区域
 */
function hideProgressSection() {
    document.getElementById('progressSection').style.display = 'none';
}

/**
 * 显示结果区域
 */
function showResultsSection() {
    document.getElementById('resultsSection').style.display = 'block';
}

/**
 * 隐藏结果区域
 */
function hideResultsSection() {
    document.getElementById('resultsSection').style.display = 'none';
}

/**
 * 更新进度
 */
function updateProgress(percentage, message) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressMessage = document.getElementById('progressMessage');
    
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
    progressMessage.textContent = message;
}

/**
 * 开始进度监控
 */
function startProgressMonitoring(estimatedMinutes = 5) {
    if (statusInterval) {
        clearInterval(statusInterval);
    }
    
    const startTime = Date.now();
    
    statusInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/backtest/status`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const status = await response.json();
            
            // 计算剩余时间
            const elapsedMinutes = (Date.now() - startTime) / 60000;
            const progressPercent = status.progress || 0;
            let timeMessage = status.message;
            
            if (progressPercent > 10 && progressPercent < 90) {
                const remainingPercent = (100 - progressPercent) / 100;
                const estimatedRemainingMinutes = (estimatedMinutes * remainingPercent);
                
                if (estimatedRemainingMinutes > 1) {
                    timeMessage += ` (预计剩余${Math.ceil(estimatedRemainingMinutes)}分钟)`;
                } else {
                    timeMessage += ` (即将完成)`;
                }
            }
            
            updateProgress(progressPercent, timeMessage);
            
            // 检查是否完成
            if (!status.is_running && status.progress === 100) {
                stopProgressMonitoring();
                updateButtonStates(false);
                updateSystemStatus('回测完成', 'success');
                await loadResults();
            } else if (!status.is_running && status.progress === 0) {
                // 回测失败或被停止
                stopProgressMonitoring();
                updateButtonStates(false);
                hideProgressSection();
                updateSystemStatus('回测失败', 'error');
                showToast(status.message, 'error');
            }
            
        } catch (error) {
            console.error('❌ 获取状态失败:', error);
        }
    }, 2000); // 每2秒检查一次
}

/**
 * 停止进度监控
 */
function stopProgressMonitoring() {
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
}

/**
 * 加载回测结果
 */
async function loadResults() {
    try {
        const response = await fetch(`${API_BASE}/backtest/results`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const results = await response.json();
        currentResults = results;
        
        console.log('✅ 回测结果加载成功:', results);
        
        // 显示结果
        displayResults(results);
        showResultsSection();
        hideProgressSection();
        
        showToast('回测完成！', 'success');
        
    } catch (error) {
        console.error('❌ 加载结果失败:', error);
        showToast(`加载结果失败: ${error.message}`, 'error');
    }
}

/**
 * 显示回测结果
 */
function displayResults(results) {
    try {
        // 更新关键指标
        updateMetrics(results);
        
        // 渲染图表
        renderCharts(results);
        
        // 显示交易记录
        displayTransactions(results.transactions || []);
        
    } catch (error) {
        console.error('❌ 显示结果失败:', error);
        showToast('显示结果时出现错误', 'error');
    }
}

/**
 * 更新关键指标
 */
function updateMetrics(results) {
    console.log('📊 更新指标数据:', results); // 调试信息
    
    // 总收益
    const totalProfit = results.total_profit || 0;
    const totalReturn = results.total_return || 0;
    document.getElementById('totalProfit').textContent = `¥${totalProfit.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    
    const returnElement = document.getElementById('totalReturn');
    returnElement.textContent = `${(totalReturn * 100).toFixed(2)}%`;
    returnElement.className = `metric-change ${totalReturn >= 0 ? 'positive' : 'negative'}`;
    
    // 最大回撤
    const maxDrawdown = results.max_drawdown || 0;
    const maxDrawdownElement = document.getElementById('maxDrawdown');
    maxDrawdownElement.textContent = `${(maxDrawdown * 100).toFixed(2)}%`;
    
    // 夏普比率
    const sharpeRatio = results.sharpe_ratio || 0;
    const sharpeElement = document.getElementById('sharpeRatio');
    sharpeElement.textContent = sharpeRatio.toFixed(3);
    
    // 添加指标说明
    const dailyValuesCount = results.daily_values ? results.daily_values.length : 0;
    
    // 为最大回撤添加说明
    const maxDrawdownCard = document.querySelector('.metric-card:nth-child(2) .metric-sub');
    if (maxDrawdownCard) {
        if (maxDrawdown === 0 && dailyValuesCount <= 2) {
            maxDrawdownCard.textContent = '数据点少，无回撤';
        } else if (maxDrawdown === 0) {
            maxDrawdownCard.textContent = '期间无回撤，表现稳定';
        } else {
            maxDrawdownCard.textContent = '风险控制指标';
        }
    }
    
    // 为夏普比率添加说明
    const sharpeCard = document.querySelector('.metric-card:nth-child(3) .metric-sub');
    if (sharpeCard) {
        if (sharpeRatio === 0 && dailyValuesCount <= 2) {
            sharpeCard.textContent = '数据不足，无法计算';
        } else if (sharpeRatio === 0) {
            sharpeCard.textContent = '收益波动较小';
        } else if (sharpeRatio > 1) {
            sharpeCard.textContent = '风险调整收益优秀';
        } else if (sharpeRatio > 0.5) {
            sharpeCard.textContent = '风险调整收益良好';
        } else {
            sharpeCard.textContent = '风险调整收益一般';
        }
    }
    
    // 交易次数和胜率
    const totalTrades = results.total_trades || 0;
    const sellTrades = results.sell_trades || 0;
    const winRate = results.win_rate || 0;
    
    // 更新交易次数显示
    const tradesElement = document.querySelector('.metric-card:nth-child(4) .metric-value');
    if (tradesElement) {
        tradesElement.textContent = totalTrades;
    }
    
    // 更新胜率显示 - 根据是否有卖出交易来显示不同的信息
    const winRateElement = document.querySelector('.metric-card:nth-child(4) .metric-sub');
    if (winRateElement) {
        if (sellTrades === 0) {
            winRateElement.textContent = `胜率: 暂无卖出`;
        } else {
            winRateElement.textContent = `胜率: ${(winRate * 100).toFixed(1)}%`;
        }
    }
    
    console.log(`📈 指标更新完成: 收益${(totalReturn*100).toFixed(2)}%, 回撤${(maxDrawdown*100).toFixed(2)}%, 夏普${sharpeRatio.toFixed(3)}, 胜率${(winRate*100).toFixed(1)}%`);
}

/**
 * 渲染图表
 */
async function renderCharts(results) {
    console.log('🎨 开始渲染图表，检查Chart.js状态...');
    
    try {
        // 等待Chart.js加载完成
        await waitForChartJS();
        
        console.log('✅ Chart.js已确认加载，开始渲染图表');
        renderChartsInternal(results);
        
    } catch (error) {
        console.error('❌ Chart.js加载失败，使用备用方案:', error);
        renderFallbackCharts(results);
    }
}

/**
 * 等待Chart.js加载完成
 */
function waitForChartJS(timeout = 10000) {
    return new Promise((resolve, reject) => {
        console.log('⏳ 等待Chart.js加载...');
        
        // 如果已经加载，直接返回
        if (typeof Chart !== 'undefined') {
            console.log('✅ Chart.js已经可用');
            resolve();
            return;
        }
        
        // 检查全局状态
        if (window.chartJSReady === true) {
            console.log('✅ Chart.js全局状态已就绪');
            resolve();
            return;
        }
        
        if (window.chartJSReady === false) {
            console.log('❌ Chart.js全局状态显示加载失败');
            reject(new Error(window.chartJSError || 'Chart.js加载失败'));
            return;
        }
        
        let attempts = 0;
        const maxAttempts = timeout / 200; // 每200ms检查一次
        
        const checkInterval = setInterval(() => {
            attempts++;
            console.log(`🔍 检查Chart.js状态 (${attempts}/${maxAttempts})`);
            
            if (typeof Chart !== 'undefined') {
                console.log('✅ Chart.js检查成功');
                clearInterval(checkInterval);
                resolve();
                return;
            }
            
            if (window.chartJSReady === true) {
                console.log('✅ Chart.js全局状态变为就绪');
                clearInterval(checkInterval);
                resolve();
                return;
            }
            
            if (window.chartJSReady === false || attempts >= maxAttempts) {
                console.log('❌ Chart.js等待超时或失败');
                clearInterval(checkInterval);
                reject(new Error(window.chartJSError || 'Chart.js等待超时'));
                return;
            }
        }, 200);
    });
}

/**
 * 渲染备用图表
 */
function renderFallbackCharts(results) {
    console.log('🔄 渲染备用图表方案...');
    
    try {
        const valueCanvas = document.getElementById('valueChart');
        const returnsCanvas = document.getElementById('returnsChart');
        
        if (valueCanvas) {
            const ctx = valueCanvas.getContext('2d');
            drawSimpleLineChart(ctx, results.daily_values || [], '资产价值走势');
            console.log('✅ 资产价值备用图表绘制成功');
        }
        
        if (returnsCanvas) {
            const ctx = returnsCanvas.getContext('2d');
            drawReturnsChart(ctx, results);
            console.log('✅ 收益分布备用图表绘制成功');
        }
        
        // 在页面上显示提示信息
        showToast('图表使用简化模式显示（Chart.js未加载）', 'warning');
        
    } catch (error) {
        console.error('❌ 备用图表绘制失败:', error);
        showChartPlaceholder();
    }
}

/**
 * 内部图表渲染函数
 */
function renderChartsInternal(results) {
    try {
        renderValueChart(results);
        renderReturnsChart(results);
    } catch (error) {
        console.error('❌ 图表渲染内部错误:', error);
        showChartPlaceholder();
    }
}

/**
 * 显示图表占位符
 */
function showChartPlaceholder() {
    const valueCanvas = document.getElementById('valueChart');
    const returnsCanvas = document.getElementById('returnsChart');
    
    if (valueCanvas) {
        showSimpleChart(valueCanvas.getContext('2d'), '图表功能暂时不可用');
    }
    
    if (returnsCanvas) {
        showSimpleChart(returnsCanvas.getContext('2d'), '图表功能暂时不可用');
    }
}

/**
 * 显示简单的文本图表
 */
function showSimpleChart(ctx, message) {
    // 设置高DPI支持
    const dimensions = setupHighDPICanvas(ctx.canvas);
    const width = dimensions.width;
    const height = dimensions.height;
    
    // 清空画布
    ctx.clearRect(0, 0, width, height);
    
    // 设置背景渐变
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, '#f8fafc');
    gradient.addColorStop(1, '#f1f5f9');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    
    // 绘制圆角边框
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(5, 5, width - 10, height - 10, 8);
    ctx.stroke();
    
    // 绘制图标
    ctx.font = '32px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText('📊', width/2, height/2 - 30);
    
    // 绘制主要文本
    ctx.fillStyle = '#64748b';
    ctx.font = 'bold 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(message, width/2, height/2 + 10);
    
    // 绘制提示文本
    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.fillText('刷新页面或检查数据', width/2, height/2 + 35);
}

/**
 * 设置Canvas高DPI支持，确保图表清晰
 */
function setupHighDPICanvas(canvas) {
    const ctx = canvas.getContext('2d');
    const devicePixelRatio = window.devicePixelRatio || 1;
    
    // 获取Canvas的显示尺寸
    const rect = canvas.getBoundingClientRect();
    const displayWidth = rect.width;
    const displayHeight = rect.height;
    
    // 设置Canvas的实际尺寸（考虑设备像素比）
    canvas.width = displayWidth * devicePixelRatio;
    canvas.height = displayHeight * devicePixelRatio;
    
    // 设置Canvas的显示尺寸
    canvas.style.width = displayWidth + 'px';
    canvas.style.height = displayHeight + 'px';
    
    // 缩放上下文以匹配设备像素比
    ctx.scale(devicePixelRatio, devicePixelRatio);
    
    console.log(`📏 Canvas高DPI设置完成: 显示尺寸 ${displayWidth}x${displayHeight}, 实际尺寸 ${canvas.width}x${canvas.height}, 像素比 ${devicePixelRatio}`);
    
    return { width: displayWidth, height: displayHeight, ratio: devicePixelRatio };
}

/**
 * 使用Canvas原生API绘制简单折线图（备用方案）
 */
function drawSimpleLineChart(ctx, data, title = '数据走势') {
    if (!data || data.length === 0) {
        showSimpleChart(ctx, '暂无数据');
        return;
    }
    
    // 设置高DPI支持
    const dimensions = setupHighDPICanvas(ctx.canvas);
    const width = dimensions.width;
    const height = dimensions.height;
    const padding = 40;
    
    // 清空画布
    ctx.clearRect(0, 0, width, height);
    
    // 设置背景
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    
    // 绘制标题
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 18px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(title, width / 2, 30);
    
    // 计算数据范围
    const values = data.map(d => d.portfolio_value || d.value || 0);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const valueRange = maxValue - minValue || 1;
    
    // 绘制坐标轴
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    
    // Y轴
    ctx.beginPath();
    ctx.moveTo(padding, padding + 20);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();
    
    // X轴
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // 绘制网格线
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 0.5;
    
    // 水平网格线
    for (let i = 1; i <= 4; i++) {
        const y = (height - padding) - (i / 5) * (height - 2 * padding - 20);
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // 绘制数据线
    if (values.length > 1) {
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        for (let i = 0; i < values.length; i++) {
            const x = padding + (i / (values.length - 1)) * (width - 2 * padding);
            const y = (height - padding) - ((values[i] - minValue) / valueRange) * (height - 2 * padding - 20);
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
        
        // 绘制数据点
        ctx.fillStyle = '#667eea';
        for (let i = 0; i < values.length; i++) {
            const x = padding + (i / (values.length - 1)) * (width - 2 * padding);
            const y = (height - padding) - ((values[i] - minValue) / valueRange) * (height - 2 * padding - 20);
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
            
            // 添加白色边框
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    }
    
    // 绘制Y轴标签
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i <= 4; i++) {
        const value = minValue + (maxValue - minValue) * (i / 4);
        const y = (height - padding) - (i / 4) * (height - 2 * padding - 20);
        ctx.fillText('¥' + Math.round(value).toLocaleString(), padding - 8, y);
    }
    
    // 绘制X轴标签（日期）
    ctx.textAlign = 'center';
    if (data.length > 0) {
        const startDate = new Date(data[0].date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
        const endDate = new Date(data[data.length - 1].date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
        
        ctx.fillText(startDate, padding, height - padding + 20);
        ctx.fillText(endDate, width - padding, height - padding + 20);
        
        if (data.length > 2) {
            const midIndex = Math.floor(data.length / 2);
            const midDate = new Date(data[midIndex].date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
            ctx.fillText(midDate, width / 2, height - padding + 20);
        }
    }
    
    // 绘制优化后的提示信息
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('高清图表 - 原生Canvas渲染', width / 2, height - 8);
}

/**
 * 渲染资产价值图表
 */
function renderValueChart(results) {
    console.log('📈 开始渲染资产价值图表...');
    
    const canvas = document.getElementById('valueChart');
    if (!canvas) {
        console.error('❌ 找不到valueChart画布元素');
        return;
    }
    
    // 确保Canvas有合适的尺寸
    const rect = canvas.getBoundingClientRect();
    console.log(`📏 Canvas尺寸: ${rect.width}x${rect.height}`);
    
    if (rect.width === 0 || rect.height === 0) {
        console.warn('⚠️ Canvas尺寸为0，设置默认尺寸');
        canvas.style.width = '100%';
        canvas.style.height = '300px';
    }
    
    const ctx = canvas.getContext('2d');
    
    // 销毁现有图表
    if (valueChart) {
        console.log('🗑️ 销毁现有图表');
        valueChart.destroy();
        valueChart = null;
    }
    
    const dailyValues = results.daily_values || [];
    console.log('📊 日值数据条数:', dailyValues.length);
    
    if (dailyValues.length === 0) {
        console.warn('⚠️ 没有日值数据可显示');
        showSimpleChart(ctx, '暂无数据');
        return;
    }
    
    console.log('📊 样本数据:', dailyValues[0]);
    
    const labels = dailyValues.map(d => new Date(d.date).toLocaleDateString('zh-CN'));
    const portfolioValues = dailyValues.map(d => d.portfolio_value);
    const cashValues = dailyValues.map(d => d.cash);
    const stockValues = dailyValues.map(d => d.stock_value);
    
    console.log('📈 图表数据准备:', {
        labels: labels.length,
        portfolioValues: portfolioValues.length,
        cashValues: cashValues.length,
        stockValues: stockValues.length
    });
    
    try {
        console.log('🎨 开始创建Chart实例...');
        console.log('📋 图表数据:', { labels: labels.length, portfolioValues: portfolioValues.length });
        
        // 检查Chart构造函数
        if (typeof Chart !== 'function') {
            throw new Error('Chart不是一个函数');
        }
        
        const chartConfig = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '总资产',
                        data: portfolioValues,
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: '现金',
                        data: cashValues,
                        borderColor: 'rgb(34, 197, 94)',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    },
                    {
                        label: '股票价值',
                        data: stockValues,
                        borderColor: 'rgb(239, 68, 68)',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                devicePixelRatio: window.devicePixelRatio || 1,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                layout: {
                    padding: {
                        left: 10,
                        right: 10,
                        top: 10,
                        bottom: 10
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: '资产价值走势',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '价值 (¥)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return '¥' + value.toLocaleString('zh-CN');
                            },
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '日期',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            maxTicksLimit: 8
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        };
        
        console.log('📊 Chart配置准备完成');
        valueChart = new Chart(ctx, chartConfig);
        console.log('✅ 资产价值图表渲染成功, Chart实例:', valueChart);
        
        // 强制图表立即调整到容器大小
        setTimeout(() => {
            if (valueChart) {
                valueChart.resize();
                console.log('📐 资产价值图表已强制调整大小');
            }
        }, 100);
        
    } catch (error) {
        console.error('❌ 资产价值图表渲染失败:', error);
        console.error('❌ 错误详情:', error.stack);
        
        // 使用备用绘制方案
        console.log('🔄 尝试使用备用绘制方案...');
        try {
            drawSimpleLineChart(ctx, dailyValues, '资产价值走势');
            console.log('✅ 备用图表绘制成功');
        } catch (fallbackError) {
            console.error('❌ 备用图表也失败:', fallbackError);
            showSimpleChart(ctx, '图表创建失败');
        }
    }
}

/**
 * 渲染收益分布图
 */
function renderReturnsChart(results) {
    console.log('📊 开始渲染收益分布图表...', results);
    
    const canvas = document.getElementById('returnsChart');
    if (!canvas) {
        console.error('❌ 找不到returnsChart画布元素');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // 销毁现有图表
    if (returnsChart) {
        returnsChart.destroy();
    }
    
    const dailyValues = results.daily_values || [];
    console.log('📊 用于收益计算的日值数据:', dailyValues);
    
    if (dailyValues.length < 2) {
        console.warn('⚠️ 数据点不足，无法计算收益分布');
        showSimpleChart(ctx, '数据不足，无法显示收益分布');
        return;
    }
    
    // 计算日收益率
    const returns = [];
    for (let i = 1; i < dailyValues.length; i++) {
        const prevValue = dailyValues[i-1].portfolio_value;
        const currentValue = dailyValues[i].portfolio_value;
        if (prevValue > 0) {
            const dailyReturn = (currentValue - prevValue) / prevValue;
            returns.push(dailyReturn);
        }
    }
    
    console.log('📈 计算的收益率数据:', returns);
    
    if (returns.length === 0) {
        console.warn('⚠️ 无法计算有效的收益率数据');
        showSimpleChart(ctx, '无法计算收益率数据');
        return;
    }
    
    // 创建收益率分布区间
    const bins = 10;
    const minReturn = Math.min(...returns);
    const maxReturn = Math.max(...returns);
    const binWidth = (maxReturn - minReturn) / bins;
    
    const binCounts = new Array(bins).fill(0);
    const binLabels = [];
    
    for (let i = 0; i < bins; i++) {
        const binStart = minReturn + i * binWidth;
        const binEnd = binStart + binWidth;
        binLabels.push(`${(binStart * 100).toFixed(1)}%`);
        
        returns.forEach(ret => {
            if (ret >= binStart && (i === bins - 1 ? ret <= binEnd : ret < binEnd)) {
                binCounts[i]++;
            }
        });
    }
    
    console.log('📊 收益分布数据:', { binLabels, binCounts });
    
    try {
        returnsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: binLabels,
                datasets: [{
                    label: '频次',
                    data: binCounts,
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgb(102, 126, 234)',
                    borderWidth: 2,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                devicePixelRatio: window.devicePixelRatio || 1,
                layout: {
                    padding: {
                        left: 10,
                        right: 10,
                        top: 10,
                        bottom: 10
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: '日收益率分布',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '频次',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            stepSize: 1,
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '日收益率',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            font: {
                                size: 10
                            },
                            maxRotation: 45,
                            minRotation: 0
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
        console.log('✅ 收益分布图表渲染成功');
        
        // 强制图表立即调整到容器大小
        setTimeout(() => {
            if (returnsChart) {
                returnsChart.resize();
                console.log('📐 收益分布图表已强制调整大小');
            }
        }, 100);
        
    } catch (error) {
        console.error('❌ 收益分布图表渲染失败:', error);
        
        // 使用简单提示作为备用方案
        try {
            showSimpleChart(ctx, '收益分布图表');
            console.log('✅ 收益分布备用显示成功');
        } catch (fallbackError) {
            console.error('❌ 收益分布备用方案也失败:', fallbackError);
        }
    }
}

/**
 * 使用Canvas绘制收益分布图（备用方案）
 */
function drawReturnsChart(ctx, results) {
    const dailyValues = results.daily_values || [];
    
    if (dailyValues.length < 2) {
        showSimpleChart(ctx, '数据不足，无法显示收益分布');
        return;
    }
    
    // 计算日收益率
    const returns = [];
    for (let i = 1; i < dailyValues.length; i++) {
        const prevValue = dailyValues[i-1].portfolio_value;
        const currentValue = dailyValues[i].portfolio_value;
        if (prevValue > 0) {
            const dailyReturn = (currentValue - prevValue) / prevValue;
            returns.push(dailyReturn);
        }
    }
    
    if (returns.length === 0) {
        showSimpleChart(ctx, '无收益数据');
        return;
    }
    
    // 绘制简单的收益分布图
    drawSimpleBarChart(ctx, returns, '收益分布');
}

/**
 * 绘制简单的柱状图
 */
function drawSimpleBarChart(ctx, data, title = '数据分布') {
    // 设置高DPI支持
    const dimensions = setupHighDPICanvas(ctx.canvas);
    const width = dimensions.width;
    const height = dimensions.height;
    const padding = 40;
    
    // 清空画布
    ctx.clearRect(0, 0, width, height);
    
    // 设置背景
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    
    // 绘制标题
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 18px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(title, width / 2, 30);
    
    // 创建收益率分布区间
    const bins = 8;
    const minReturn = Math.min(...data);
    const maxReturn = Math.max(...data);
    const binWidth = (maxReturn - minReturn) / bins;
    
    const binCounts = new Array(bins).fill(0);
    
    // 统计各区间频次
    for (let i = 0; i < bins; i++) {
        const binStart = minReturn + i * binWidth;
        const binEnd = binStart + binWidth;
        
        data.forEach(ret => {
            if (ret >= binStart && (i === bins - 1 ? ret <= binEnd : ret < binEnd)) {
                binCounts[i]++;
            }
        });
    }
    
    const maxCount = Math.max(...binCounts);
    if (maxCount === 0) {
        showSimpleChart(ctx, '无有效数据');
        return;
    }
    
    // 绘制坐标轴
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    
    // Y轴
    ctx.beginPath();
    ctx.moveTo(padding, padding + 20);
    ctx.lineTo(padding, height - padding - 20);
    ctx.stroke();
    
    // X轴
    ctx.beginPath();
    ctx.moveTo(padding, height - padding - 20);
    ctx.lineTo(width - padding, height - padding - 20);
    ctx.stroke();
    
    // 绘制网格线
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 0.5;
    
    for (let i = 1; i <= 4; i++) {
        const y = (height - padding - 20) - (i / 5) * (height - 2 * padding - 40);
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // 绘制柱状图
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding - 40;
    const barWidth = chartWidth / bins;
    
    // 渐变色效果
    const gradient = ctx.createLinearGradient(0, padding + 20, 0, height - padding - 20);
    gradient.addColorStop(0, 'rgba(102, 126, 234, 0.9)');
    gradient.addColorStop(1, 'rgba(102, 126, 234, 0.6)');
    
    for (let i = 0; i < bins; i++) {
        if (binCounts[i] > 0) {
            const barHeight = (binCounts[i] / maxCount) * chartHeight;
            const x = padding + i * barWidth;
            const y = height - padding - 20 - barHeight;
            
            // 绘制柱子
            ctx.fillStyle = gradient;
            ctx.fillRect(x + 4, y, barWidth - 8, barHeight);
            
            // 绘制柱子边框
            ctx.strokeStyle = 'rgba(102, 126, 234, 1)';
            ctx.lineWidth = 1;
            ctx.strokeRect(x + 4, y, barWidth - 8, barHeight);
            
            // 绘制数值标签
            if (barHeight > 20) {
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(binCounts[i].toString(), x + barWidth/2, y + barHeight/2);
            } else {
                ctx.fillStyle = '#666666';
                ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';
                ctx.fillText(binCounts[i].toString(), x + barWidth/2, y - 5);
            }
        }
    }
    
    // 绘制Y轴标签（频次）
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i <= 4; i++) {
        const value = Math.round((maxCount * i) / 4);
        const y = (height - padding - 20) - (i / 4) * chartHeight;
        ctx.fillText(value.toString(), padding - 8, y);
    }
    
    // 绘制X轴标签（收益率范围）
    ctx.fillStyle = '#6b7280';
    ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    
    for (let i = 0; i < bins; i++) {
        const binStart = minReturn + i * binWidth;
        const x = padding + i * barWidth + barWidth/2;
        ctx.fillText(`${(binStart * 100).toFixed(1)}%`, x, height - padding - 15);
    }
    
    // 添加Y轴标题
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('频次', 0, 0);
    ctx.restore();
    
    // 添加X轴标题
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('日收益率 (%)', width / 2, height - 5);
    
    // 绘制优化后的提示信息
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText('高清图表 - 原生Canvas渲染', width - 10, 20);
}

/**
 * 显示交易记录
 */
function displayTransactions(transactions) {
    const tbody = document.querySelector('#transactionsTable tbody');
    tbody.innerHTML = '';
    
    if (!transactions || transactions.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell(0);
        cell.colSpan = 6;
        cell.textContent = '暂无交易记录';
        cell.style.textAlign = 'center';
        cell.style.color = '#666';
        return;
    }
    
    transactions.forEach(transaction => {
        const row = tbody.insertRow();
        
        // 日期
        const dateCell = row.insertCell(0);
        dateCell.textContent = new Date(transaction.date).toLocaleDateString('zh-CN');
        
        // 操作
        const actionCell = row.insertCell(1);
        actionCell.textContent = transaction.action;
        actionCell.className = `action-${transaction.action.toLowerCase()}`;
        
        // 股数
        const sharesCell = row.insertCell(2);
        sharesCell.textContent = transaction.shares.toFixed(2);
        
        // 价格
        const priceCell = row.insertCell(3);
        priceCell.textContent = `¥${transaction.price.toFixed(2)}`;
        
        // 金额
        const amountCell = row.insertCell(4);
        amountCell.textContent = `¥${transaction.amount.toLocaleString('zh-CN', {minimumFractionDigits: 2})}`;
        
        // 信心度
        const confidenceCell = row.insertCell(5);
        confidenceCell.textContent = `${(transaction.confidence * 100).toFixed(1)}%`;
    });
}

/**
 * 下载结果
 */
async function downloadResults() {
    if (!currentResults) {
        showToast('暂无可下载的结果', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/backtest/download`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        // 获取文件名
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'backtest_results.json';
        if (contentDisposition) {
            const matches = contentDisposition.match(/filename="?([^"]+)"?/);
            if (matches) filename = matches[1];
        }
        
        // 下载文件
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('结果已下载', 'success');
        
    } catch (error) {
        console.error('❌ 下载失败:', error);
        showToast(`下载失败: ${error.message}`, 'error');
    }
}

/**
 * 更新系统状态
 */
function updateSystemStatus(message, type = 'success') {
    const statusElement = document.getElementById('systemStatus');
    statusElement.textContent = message;
    statusElement.className = `status-indicator ${type}`;
}

/**
 * 显示提示消息
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : 
                 type === 'error' ? '❌' : 
                 type === 'warning' ? '⚠️' : 'ℹ️';
    
    toast.innerHTML = `
        <span style="font-size: 1.2rem;">${icon}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
    
    console.log(`📢 [${type.toUpperCase()}] ${message}`);
}

/**
 * 测试函数 - 手动强制加载股票建议（调试用）
 */
function testLoadStocks() {
    console.log('🧪 手动测试加载股票建议...');
    loadOfflineStockSuggestions();
    showToast('手动加载股票建议完成', 'success');
}

// 将测试函数暴露到全局，方便在浏览器控制台调用
window.testLoadStocks = testLoadStocks; 