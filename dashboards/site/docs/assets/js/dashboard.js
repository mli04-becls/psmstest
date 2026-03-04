// ====== dashboard.js (增强版) ======

async function loadJSON(path) {
  // 加上时间戳避免缓存 & 明确不使用缓存
  const url = `${path}?t=${Date.now()}`;
  const resp = await fetch(url, { cache: 'no-store' });
  if (!resp.ok) throw new Error(`加载失败: ${url} ${resp.status}`);
  return resp.json();
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function renderCoverageChart(data) {
  const el = document.getElementById('chart-coverage');
  if (!el) return;
  const chart = echarts.init(el);
  chart.setOption({
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
    series: [{ type: 'line', data: data.values, smooth: true, areaStyle: {} }],
    tooltip: { trigger: 'axis' }
  });
}

function renderHighRiskChart(data) {
  const el = document.getElementById('chart-highrisk');
  if (!el) return;
  const chart = echarts.init(el);
  chart.setOption({
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: data.values, itemStyle: { color: '#ef4444' } }],
    tooltip: { trigger: 'axis' }
  });
}

function renderTopRiskTable(items) {
  const tbody = document.getElementById('table-top-risk');
  if (!tbody) return;
  tbody.innerHTML = (items || []).map(it => `
    <tr>
      <td>${it.product}</td>
      <td><span style="color:${it.risk_color||'#ef4444'};font-weight:600">${it.risk}</span></td>
      <td>${it.open_high}</td>
      <td>${it.status||''}</td>
    </tr>
  `).join('');
}

async function renderDashboard() {
  try {
    const [summary, cov, high, top] = await Promise.all([
      loadJSON('data/summary.json'),
      loadJSON('data/coverage_trend.json'),
      loadJSON('data/high_risk_trend.json'),
      loadJSON('data/top_risk_products.json'),
    ]);

    setText('kpi-products', summary.total_products ?? '--');
    setText('kpi-coverage', (summary.baseline_coverage ?? 0) + '%');
    setText('kpi-high', summary.open_high_risk ?? '--');
    setText('kpi-exempt', summary.expiring_exemptions ?? '--');

    renderCoverageChart(cov);
    renderHighRiskChart(high);
    renderTopRiskTable(top.items || []);
  } catch (e) {
    console.error('Dashboard 渲染失败：', e);
  }
}

// 导出到全局（可手动在控制台调用）
window.renderDashboard = renderDashboard;

// -------- 关键：兼容 MkDocs Material 的 SPA 导航 --------
// 情况 A：Material 提供的 document$（单页导航刷新时触发）
if (typeof window.document$ !== 'undefined') {
  window.document$.subscribe(() => {
    // 页面内容已更新，重新渲染
    renderDashboard();
  });
} else {
  // 情况 B：普通页面（本地或未启用 instant navigation）
  window.addEventListener('DOMContentLoaded', renderDashboard);
}