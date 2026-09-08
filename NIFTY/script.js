const CONFIG = {
    API_BASE: 'http://localhost:5000/api',
    CHART_FONT_COLOR: '#94a3b8',
    CHART_GRID_COLOR: 'rgba(255, 255, 255, 0.05)',
    CHART_BG_COLOR: 'transparent',
};

// State
let globalData = null;
let currentMode = 'historical'; // 'historical' or 'realtime'
let activeTicker = '^NSEI';
let alertPrice = null;
let portfolio = JSON.parse(localStorage.getItem('stock_portfolio') || '[]');

// DOM Elements
const elements = {
    btnHistorical: document.getElementById('btn-historical'),
    btnRealtime: document.getElementById('btn-realtime'),
    realtimeControls: document.getElementById('realtime-controls'),
    tickerInput: document.getElementById('ticker-input'),
    btnFetchLive: document.getElementById('btn-fetch-live'),
    timeFilter: document.getElementById('time-filter'),
    predictDays: document.getElementById('predict-days'),
    btnPredict: document.getElementById('btn-predict'),
    btnDownload: document.getElementById('btn-download'),
    loadingIndicator: document.getElementById('loading-indicator'),
    
    // Alerts
    alertPriceInput: document.getElementById('alert-price'),
    btnSetAlert: document.getElementById('btn-set-alert'),

    // Portfolio
    portfolioQtyInput: document.getElementById('portfolio-qty'),
    btnBuyMock: document.getElementById('btn-buy-mock'),
    portfolioBody: document.getElementById('portfolio-body'),
    
    // Stats
    statCurrent: document.getElementById('stat-current'),
    statGrowth: document.getElementById('stat-growth'),
    statHighest: document.getElementById('stat-highest'),
    statTrend: document.getElementById('stat-trend'),
    statRec: document.getElementById('stat-rec'),
    statVol: document.getElementById('stat-vol'),
    statSentiment: document.getElementById('stat-sentiment'),
    statSentimentScore: document.getElementById('stat-sentiment-score'),
    
    // Toggles
    toggleMa50: document.getElementById('toggle-ma50'),
    toggleMa200: document.getElementById('toggle-ma200'),
    
    // Charts
    mainChart: 'main-chart',
    predictChart: 'predict-chart',
    rsiChart: 'rsi-chart',
    accuracyMetrics: document.getElementById('accuracy-metrics'),
    
    // Screener
    btnLoadScreener: document.getElementById('btn-load-screener'),
    screenerLoading: document.getElementById('screener-loading'),
    screenerBody: document.getElementById('screener-body')
};

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    fetchHistoricalData(); // default
    renderPortfolio();
});

function setupEventListeners() {
    elements.btnHistorical.addEventListener('click', () => {
        setMode('historical');
        activeTicker = '^NSEI';
        fetchHistoricalData();
    });
    
    elements.btnRealtime.addEventListener('click', () => {
        setMode('realtime');
        elements.realtimeControls.style.display = 'flex';
    });
    
    elements.btnFetchLive.addEventListener('click', () => {
        activeTicker = elements.tickerInput.value.trim().toUpperCase() || 'AAPL';
        fetchRealtimeData();
    });
    
    elements.timeFilter.addEventListener('change', () => {
        if (globalData) renderCharts(globalData);
    });
    
    elements.toggleMa50.addEventListener('change', () => { if(globalData) renderCharts(globalData); });
    elements.toggleMa200.addEventListener('change', () => { if(globalData) renderCharts(globalData); });
    
    elements.btnPredict.addEventListener('click', runPrediction);
    elements.btnDownload.addEventListener('click', downloadCSV);

    // Alerts
    elements.btnSetAlert.addEventListener('click', () => {
        const val = parseFloat(elements.alertPriceInput.value);
        if (val) {
            alertPrice = val;
            alert(`✅ Alert set! We will notify you when price hits ₹${val}`);
        }
    });

    // Portfolio Buy
    elements.btnBuyMock.addEventListener('click', () => {
        buyMockStock();
    });

    // Market Screener
    if (elements.btnLoadScreener) {
        elements.btnLoadScreener.addEventListener('click', fetchMarketOverview);
    }
}

function setMode(mode) {
    currentMode = mode;
    elements.btnHistorical.classList.toggle('active', mode === 'historical');
    elements.btnRealtime.classList.toggle('active', mode === 'realtime');
    elements.realtimeControls.style.display = mode === 'realtime' ? 'flex' : 'none';
}

function setStatsLoading(isLoading) {
    const stats = [elements.statCurrent, elements.statGrowth, elements.statHighest, elements.statTrend, elements.statRec, elements.statVol, elements.statSentiment];
    stats.forEach(el => isLoading ? el.classList.add('loading') : el.classList.remove('loading'));
}

function formatPrice(val) {
    if(!val || isNaN(val)) return '--';
    return '₹' + parseFloat(val).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits:2});
}

function checkAlerts(currentPrice) {
    if (alertPrice !== null && globalData && globalData.dates) {
        // Simple logic: if price crosses threshold
        if (Math.abs(currentPrice - alertPrice) / currentPrice < 0.05) {    
            if(confirm(`🔔 ALERT: ${activeTicker} has reached ₹${currentPrice}. Close alert?`)) {
                alertPrice = null;
                elements.alertPriceInput.value = '';
            }
        }
    }
}

function updateStats(data) {
    elements.statCurrent.textContent = formatPrice(data.current_price);
    
    if (data.daily_growth !== undefined) {
        let growth = data.daily_growth;
        elements.statGrowth.textContent = (growth > 0 ? '+' : '') + growth.toFixed(2) + '%';
        elements.statGrowth.className = 'value ' + (growth > 0 ? 'buy-text' : growth < 0 ? 'sell-text' : 'hold-text');
    } else {
        elements.statGrowth.textContent = '--';
    }

    elements.statHighest.textContent = formatPrice(data.highest_price);
    
    elements.statTrend.textContent = data.trend || 'Sideways';
    
    const rec = data.recommendation || 'HOLD';
    elements.statRec.textContent = rec;
    elements.statRec.className = 'value ' + (rec === 'BUY' ? 'buy-text' : rec === 'SELL' ? 'sell-text' : 'hold-text');
    
    elements.statVol.textContent = data.volatility ? (data.volatility * 100).toFixed(2) + '%' : '--';

    checkAlerts(data.current_price);
    renderPortfolio(); // update live prices in portfolio
}

// 🧠 Sentiment Logic
async function fetchSentiment() {
    elements.statSentiment.classList.add('loading');
    try {
        const response = await fetch(`${CONFIG.API_BASE}/sentiment?ticker=${activeTicker}`);
        const data = await response.json();
        
        elements.statSentiment.textContent = data.sentiment;
        elements.statSentimentScore.textContent = `Score: ${data.score.toFixed(2)}`;
        
        if(data.score > 0) elements.statSentiment.style.color = 'var(--success)';
        else if(data.score < 0) elements.statSentiment.style.color = 'var(--danger)';
        else elements.statSentiment.style.color = 'var(--text-primary)';
        
    } catch (e) {
        elements.statSentiment.textContent = "Unavailable";
    } finally {
        elements.statSentiment.classList.remove('loading');
    }
}

function getFilteredData(data) {
    const filter = elements.timeFilter.value;
    let daysToKeep = data.dates.length;
    
    if (filter === '1mo') daysToKeep = 22;
    else if (filter === '6mo') daysToKeep = 130;
    else if (filter === '1y') daysToKeep = 252;
    else if (filter === '5y') daysToKeep = 1260;
    
    const startIndex = Math.max(0, data.dates.length - daysToKeep);
    const sliceArray = (arr) => arr && arr.length > 0 ? arr.slice(startIndex) : [];
    
    return {
        ...data,
        dates: sliceArray(data.dates),
        close: sliceArray(data.close),
        open: sliceArray(data.open),
        high: sliceArray(data.high),
        low: sliceArray(data.low),
        ma50: sliceArray(data.ma50),
        ma200: sliceArray(data.ma200),
        rsi: sliceArray(data.rsi)
    };
}

const defaultLayout = {
    paper_bgcolor: CONFIG.CHART_BG_COLOR,
    plot_bgcolor: CONFIG.CHART_BG_COLOR,
    font: { color: CONFIG.CHART_FONT_COLOR, family: 'Inter' },
    margin: { t: 20, r: 20, b: 40, l: 50 },
    xaxis: { gridcolor: CONFIG.CHART_GRID_COLOR },
    yaxis: { gridcolor: CONFIG.CHART_GRID_COLOR }
};

function renderCharts(rawData) {
    const data = getFilteredData(rawData);
    let traces = [];
    
    if (data.open && data.open.length > 0) {
        traces.push({
            x: data.dates, close: data.close, high: data.high, low: data.low, open: data.open,
            type: 'candlestick', name: 'Price Action',
            increasing: {line: {color: '#10b981'}}, decreasing: {line: {color: '#ef4444'}}
        });
    } else {
        traces.push({ x: data.dates, y: data.close, type: 'scatter', mode: 'lines', name: 'Close Price', line: {color: '#3b82f6', width: 2} });
    }

    if (elements.toggleMa50.checked && data.ma50) traces.push({ x: data.dates, y: data.ma50, type: 'scatter', mode: 'lines', name: 'MA50', line: {color: '#f59e0b', width: 1.5, dash: 'dot'} });
    if (elements.toggleMa200.checked && data.ma200) traces.push({ x: data.dates, y: data.ma200, type: 'scatter', mode: 'lines', name: 'MA200', line: {color: '#ec4899', width: 2} });

    Plotly.newPlot(elements.mainChart, traces, { ...defaultLayout, xaxis: { ...defaultLayout.xaxis, rangeslider: {visible: false} } }, {responsive: true});

    if (data.rsi && data.rsi.length > 0) {
        let rsiTrace = { x: data.dates, y: data.rsi, type: 'scatter', mode: 'lines', line: {color: '#a855f7'} };
        let layoutRsi = {
            ...defaultLayout, margin: { t: 10, r: 20, b: 30, l: 50 },
            yaxis: { title: 'RSI', range: [0, 100], gridcolor: CONFIG.CHART_GRID_COLOR },
            shapes: [
                { type: 'line', y0: 70, y1: 70, x0: data.dates[0], x1: data.dates[data.dates.length-1], line: { color: 'rgba(239, 68, 68, 0.5)', dash: 'dot' } },
                { type: 'line', y0: 30, y1: 30, x0: data.dates[0], x1: data.dates[data.dates.length-1], line: { color: 'rgba(16, 185, 129, 0.5)', dash: 'dot' } }
            ]
        };
        Plotly.newPlot(elements.rsiChart, [rsiTrace], layoutRsi, {responsive: true});
    }
}

async function fetchHistoricalData() {
    setStatsLoading(true);
    try {
        const response = await fetch(`${CONFIG.API_BASE}/data`);
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        globalData = data;
        updateStats(data);
        renderCharts(data);
        fetchSentiment();
    } catch (err) {
        console.error(err);
        alert("Failed to load historical data.");
    } finally {
        setStatsLoading(false);
    }
}

async function fetchRealtimeData() {
    if (!activeTicker) return;
    setStatsLoading(true);
    elements.btnFetchLive.textContent = "Fetching...";
    try {
        const response = await fetch(`${CONFIG.API_BASE}/realtime?ticker=${activeTicker}`);
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        globalData = data;
        updateStats(data);
        renderCharts(data);
        fetchSentiment();
    } catch (err) {
        console.error(err);
        alert(`Failed to fetch live data for ${activeTicker}`);
    } finally {
        setStatsLoading(false);
        elements.btnFetchLive.textContent = "Fetch Data";
    }
}

// Portfolio Logic
function buyMockStock() {
    const qty = parseInt(elements.portfolioQtyInput.value);
    if (!qty || !globalData || !globalData.current_price) return alert("Enter valid quantity while viewing a stock.");
    
    portfolio.push({
        id: Date.now(),
        ticker: activeTicker,
        qty: qty,
        avgPrice: globalData.current_price
    });
    
    localStorage.setItem('stock_portfolio', JSON.stringify(portfolio));
    elements.portfolioQtyInput.value = '';
    renderPortfolio();
}

function removeStockFromPortfolio(id) {
    portfolio = portfolio.filter(p => p.id !== id);
    localStorage.setItem('stock_portfolio', JSON.stringify(portfolio));
    renderPortfolio();
}

function renderPortfolio() {
    elements.portfolioBody.innerHTML = '';
    if(portfolio.length === 0) {
        elements.portfolioBody.innerHTML = '<tr><td colspan="5" style="padding:10px;text-align:center;color:#666;">No stocks in portfolio</td></tr>';
        return;
    }
    
    let currentTickerPrice = (globalData && globalData.current_price) ? globalData.current_price : null;

    portfolio.forEach(item => {
        let currentP = item.ticker === activeTicker ? currentTickerPrice : item.avgPrice; // Assume unchanged if not active
        let pnl = (currentP - item.avgPrice) * item.qty;
        let pnlText = pnl >= 0 ? `<span class="buy-text">+₹${pnl.toFixed(2)}</span>` : `<span class="sell-text">-₹${Math.abs(pnl).toFixed(2)}</span>`;
        
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
        tr.innerHTML = `
            <td style="padding: 10px 0;"><strong>${item.ticker}</strong></td>
            <td>${item.qty}</td>
            <td>₹${item.avgPrice.toFixed(2)}</td>
            <td>₹${currentP.toFixed(2)} <small style="color:#666">(estimated)</small></td>
            <td>${pnlText} <button onclick="removeStockFromPortfolio(${item.id})" style="background:none;border:none;color:var(--danger);cursor:pointer;margin-left:10px;">✖</button></td>
        `;
        elements.portfolioBody.appendChild(tr);
    });
}

// Prediction Logic
async function runPrediction() {
    const days = elements.predictDays.value;
    elements.btnPredict.style.display = 'none';
    elements.loadingIndicator.style.display = 'block';
    elements.accuracyMetrics.innerHTML = '<i>Training LSTM Model (This may take a minute so sit back)...</i>';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/predict?days=${days}`);
        const result = await response.json();
        
        if (result.error) throw new Error(result.error);
        elements.accuracyMetrics.innerHTML = `<span><strong>RMSE:</strong> ${result.rmse.toFixed(2)}</span><span><strong>MAE:</strong> ${result.mae.toFixed(2)}</span>`;
        renderPredictionChart(result.predictions, parseInt(days));
    } catch (err) {
        elements.accuracyMetrics.innerHTML = '<span style="color:red">Prediction failed. Check console.</span>';
    } finally {
        elements.btnPredict.style.display = 'flex';
        elements.loadingIndicator.style.display = 'none';
    }
}

function renderPredictionChart(predictions, days) {
    if (!globalData || !predictions || predictions.length === 0) return;
    const lastDateStr = globalData.dates[globalData.dates.length - 1];
    let lastDate = new Date(lastDateStr);
    
    let predDates = [];
    for(let i=1; i<=days; i++) {
        let nDate = new Date(lastDate);
        nDate.setDate(nDate.getDate() + i);
        predDates.push(nDate.toISOString().split('T')[0]);
    }
    
    const histSliceLen = Math.min(30, globalData.dates.length);
    const histDates = globalData.dates.slice(-histSliceLen);
    const histClose = globalData.close.slice(-histSliceLen);
    
    let traces = [
        { x: histDates, y: histClose, name: 'Historical Price', mode: 'lines+markers', line: {color: '#3b82f6'} },
        { x: predDates, y: predictions, name: 'AI Prediction', mode: 'lines+markers', line: {color: '#a855f7', dash: 'dot'} },
        { x: [histDates[histDates.length-1], predDates[0]], y: [histClose[histClose.length-1], predictions[0]], showlegend: false, mode: 'lines', line: {color: '#a855f7', dash: 'dot'} }
    ];
    Plotly.newPlot(elements.predictChart, traces, { ...defaultLayout, margin: {t:20, b:30, l:50, r:20} }, {responsive: true});
}

function downloadCSV() {
    if (!globalData || !globalData.close) return alert("No data available to download");
    let csvContent = "data:text/csv;charset=utf-8,Date,Close\n";
    globalData.dates.forEach((date, i) => csvContent += `${date},${globalData.close[i]}\n`);
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.href = encodedUri;
    link.download = `stock_data_${activeTicker}.csv`;
    link.click();
}

async function fetchMarketOverview() {
    elements.screenerLoading.style.display = 'block';
    elements.btnLoadScreener.disabled = true;
    elements.screenerBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#666;">Scanning global market data... This takes about 10-15 seconds.</td></tr>';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/market_overview`);
        const result = await response.json();
        
        if (result.error) throw new Error(result.error);
        if (!result.data || result.data.length === 0) throw new Error("No data returned");
        
        elements.screenerBody.innerHTML = '';
        
        result.data.forEach(item => {
            let growth = item.estimated_growth;
            let growthText = growth >= 0 ? `<span class="buy-text">+${growth.toFixed(2)}%</span>` : `<span class="sell-text">${growth.toFixed(2)}%</span>`;
            
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            tr.innerHTML = `
                <td style="padding: 10px 0;"><strong>${item.ticker}</strong><br><small style="color:#666;">${item.symbol}</small></td>
                <td>₹${item.open.toFixed(2)}</td>
                <td>₹${item.predicted_close.toFixed(2)}</td>
                <td>${growthText}</td>
            `;
            elements.screenerBody.appendChild(tr);
        });
        
    } catch (err) {
        elements.screenerBody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--danger)">Failed to load market overview: ${err.message}</td></tr>`;
    } finally {
        elements.screenerLoading.style.display = 'none';
        elements.btnLoadScreener.disabled = false;
    }
}
