# 产品安全仪表盘

<div class="cards">
  <div class="card"><div class="card-title">产品总数</div><div class="card-value" id="kpi-products">--</div></div>
  <div class="card"><div class="card-title">基线覆盖率</div><div class="card-value" id="kpi-coverage">--</div></div>
  <div class="card"><div class="card-title">高危未解</div><div class="card-value" id="kpi-high">--</div></div>
  <div class="card"><div class="card-title">临期豁免</div><div class="card-value" id="kpi-exempt">--</div></div>
</div>

## 趋势
<div class="charts">
  <div class="chart"><h3>基线覆盖率趋势</h3><div id="chart-coverage" class="chart-box"></div></div>
  <div class="chart"><h3>高危问题趋势</h3><div id="chart-highrisk" class="chart-box"></div></div>
</div>

## Top 风险产品
<table class="table"><thead><tr><th>产品</th><th>风险等级</th><th>未解高危</th><th>状态</th></tr></thead><tbody id="table-top-risk"></tbody></table>

<script>window.renderDashboard && window.renderDashboard();</script>
