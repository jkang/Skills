# HTML 可视化看板设计规范

> mideast-supply-chain-analyzer 的 HTML 看板输出必须遵循本规范。

## 1. 文件结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>中东局势供应链风险看板 — {date}</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>/* 所有 CSS 内联 */</style>
</head>
<body>
  <header class="dashboard-header">...</header>
  <section class="kpi-strip">...</section>
  <section class="charts-grid">
    <div class="chart-card" id="timeline-card">...</div>
    <div class="chart-card" id="geo-card">...</div>
    <div class="chart-card" id="type-dist-card">...</div>
    <div class="chart-card" id="impact-matrix-card">...</div>
  </section>
  <section class="top-risks">...</section>
  <footer>...</footer>
  <script>
    var rawData = { /* 嵌入的 JSON 数据 */ };
    // ECharts 初始化代码
  </script>
</body>
</html>
```

**单文件原则**: 所有 CSS 写在 `<style>` 中，所有 JS 写在 `<script>` 中。仅允许通过 CDN 加载 ECharts。

---

## 2. 配色方案

### 2.1 基础色板

```css
:root {
  --color-bg: #F5F7FA;
  --color-card-bg: #FFFFFF;
  --color-primary: #1677FF;
  --color-text-primary: #1D2129;
  --color-text-secondary: #86909C;
  --color-border: #E5E6EB;
  --color-card-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
```

### 2.2 风险等级色系

| 等级 | 文字色 | 背景色 | 用途 |
|------|--------|--------|------|
| 高危 | `#FF4D4F` | `#FFF1F0` | 评分>=4.0 |
| 中等 | `#FAAD14` | `#FFFBE6` | 评分 3.0-3.9 |
| 低 | `#52C41A` | `#F6FFED` | 评分<3.0 |

### 2.3 ECharts 图表色系

```javascript
var CHART_COLORS = ['#1677FF', '#FF4D4F', '#FAAD14', '#52C41A', '#722ED1', '#13C2C2', '#FA541C', '#2F54EB'];
```

### 2.4 地图/地理标注色

- 地图底色: `#E8F0FE`
- 航线线条: `#1677FF`（正常）/ `#FF4D4F`（受影响）
- 港口标注: `#1677FF`（正常）/ `#FF4D4F`（高危）/ `#FAAD14`（中危）

---

## 3. 布局规范

### 3.1 整体布局（CSS Grid）

```css
body {
  margin: 0;
  padding: 24px;
  background: var(--color-bg);
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  color: var(--color-text-primary);
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 16px 0;
}

/* 响应式: <768px 单列 */
@media (max-width: 768px) {
  .charts-grid { grid-template-columns: 1fr; }
}
```

### 3.2 看板整体结构

```
┌──────────────────────────────────────────────────┐
│  dashboard-header: 标题 + 生成时间 + 综合风险指数   │
├──────────────────────────────────────────────────┤
│  kpi-strip: 4个KPI卡片横向排列                     │
│  [事件总数] [高危事件] [受影响航线] [综合风险指数]    │
├────────────────────┬─────────────────────────────┤
│  风险事件时间线      │  中东风险地理分布图            │
│  (scatter+line)     │  (scatter 模拟地理)           │
│  400px             │  400px                       │
├────────────────────┼─────────────────────────────┤
│  风险类型分布        │  供应链影响矩阵              │
│  (pie 饼图)         │  (scatter 四象限)            │
│  400px             │  400px                       │
├────────────────────┴─────────────────────────────┤
│  top-risks: Top 5 高风险事件详情卡片 + AI 分析摘要   │
├──────────────────────────────────────────────────┤
│  footer: 数据来源 + 生成时间 + 免责声明             │
└──────────────────────────────────────────────────┘
```

### 3.3 卡片样式

```css
.chart-card {
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--color-card-shadow);
}

.chart-card .card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.chart-container {
  width: 100%;
  height: 400px;
}
```

---

## 4. KPI 卡片模板

```html
<section class="kpi-strip">
  <div class="kpi-card">
    <div class="kpi-label">新闻事件总数</div>
    <div class="kpi-value">{total_events}</div>
  </div>
  <div class="kpi-card kpi-danger">
    <div class="kpi-label">高危事件</div>
    <div class="kpi-value">{high_risk_count}</div>
  </div>
  <div class="kpi-card kpi-warning">
    <div class="kpi-label">受影响航线</div>
    <div class="kpi-value">{affected_routes}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">综合风险指数</div>
    <div class="kpi-value" style="color:{risk_color}">{risk_index}</div>
    <div class="kpi-sublabel">{risk_level}</div>
  </div>
</section>
```

```css
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 16px 0;
}

.kpi-card {
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: var(--color-card-shadow);
}

.kpi-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-primary);
}

.kpi-danger .kpi-value { color: #FF4D4F; }
.kpi-warning .kpi-value { color: #FAAD14; }

.kpi-sublabel {
  font-size: 12px;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
}
```

---

## 5. ECharts 图表配置模板

### 5.1 风险事件时间线（scatter + markLine）

```javascript
function initTimeline(container, events) {
  var chart = echarts.init(container);
  var option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        return params.value[0] + '<br/>'
          + params.data.title + '<br/>'
          + '风险评分: ' + params.value[1] + '<br/>'
          + '类型: ' + params.data.typeName;
      }
    },
    xAxis: {
      type: 'time',
      name: '日期',
      axisLabel: { formatter: '{yyyy}-{MM}-{dd}' }
    },
    yAxis: {
      type: 'value',
      name: '风险评分',
      min: 0,
      max: 5,
      splitLine: { lineStyle: { type: 'dashed' } }
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100, bottom: '5%' }
    ],
    series: [{
      type: 'scatter',
      symbolSize: function(val) { return val[1] * 8 + 10; },
      data: '__INJECT_TIMELINE_DATA__',
      itemStyle: {
        color: function(params) {
          var score = params.value[1];
          if (score >= 4) return '#FF4D4F';
          if (score >= 3) return '#FAAD14';
          return '#52C41A';
        }
      },
      markLine: {
        silent: true,
        symbol: ['none', 'none'],
        lineStyle: { type: 'dashed' },
        data: [
          { yAxis: 4, label: { formatter: '高危线' }, lineStyle: { color: '#FF4D4F' } },
          { yAxis: 3, label: { formatter: '中危线' }, lineStyle: { color: '#FAAD14' } }
        ]
      }
    }]
  };
  chart.setOption(option);
  return chart;
}
```

### 5.2 中东风险地理分布图（scatter 模拟）

用 scatter 图模拟中东地图，用经纬度映射为 x/y 坐标：

```javascript
function initGeoRisk(container, locations) {
  var chart = echarts.init(container);
  var option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        return params.data.name + '<br/>风险等级: ' + params.data.riskLevel;
      }
    },
    xAxis: {
      type: 'value',
      name: '经度',
      min: 30, max: 65,
      show: false
    },
    yAxis: {
      type: 'value',
      name: '纬度',
      min: 10, max: 35,
      show: false
    },
    series: [
      {
        name: '关键节点',
        type: 'scatter',
        symbolSize: function(val) { return val[2] * 10 + 15; },
        data: '__INJECT_GEO_DATA__',
        itemStyle: {
          color: function(params) {
            var level = params.data.riskLevel;
            if (level === '高危') return '#FF4D4F';
            if (level === '中等') return '#FAAD14';
            return '#52C41A';
          }
        },
        label: {
          show: true,
          formatter: function(params) { return params.data.name; },
          position: 'right',
          fontSize: 11
        }
      },
      {
        name: '航线',
        type: 'lines',
        coordinateSystem: 'cartesian2d',
        polyline: false,
        lineStyle: { width: 2, opacity: 0.6, curveness: 0.2 },
        data: '__INJECT_ROUTE_LINES__'
      }
    ]
  };
  chart.setOption(option);
  return chart;
}
```

> 注意：如果 ECharts lines series 在 cartesian2d 上不可用，改用多条 markLine 或自定义 graphic 线段来表示航线。

### 5.3 风险类型分布（饼图）

```javascript
function initTypeDist(container, distribution) {
  var chart = echarts.init(container);
  var option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, type: 'scroll' },
    color: ['#FF4D4F', '#FA541C', '#FAAD14', '#52C41A', '#1677FF', '#722ED1', '#13C2C2', '#2F54EB'],
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 18, fontWeight: 'bold' }
      },
      labelLine: { show: false },
      data: '__INJECT_TYPE_DATA__'
    }]
  };
  chart.setOption(option);
  return chart;
}
```

### 5.4 供应链影响矩阵（scatter 四象限）

```javascript
function initImpactMatrix(container, events) {
  var chart = echarts.init(container);
  var option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        return params.data.title + '<br/>'
          + '影响程度: ' + params.value[0] + '<br/>'
          + '发生概率: ' + params.value[1] + '<br/>'
          + '风险等级: ' + params.data.riskLevel;
      }
    },
    xAxis: {
      type: 'value',
      name: '影响程度',
      min: 0, max: 5,
      splitLine: { lineStyle: { type: 'dashed' } }
    },
    yAxis: {
      type: 'value',
      name: '发生概率',
      min: 0, max: 5,
      splitLine: { lineStyle: { type: 'dashed' } }
    },
    series: [{
      type: 'scatter',
      symbolSize: function(val) { return val[2] * 8 + 12; },
      data: '__INJECT_MATRIX_DATA__',
      itemStyle: {
        color: function(params) {
          var score = params.value[0] * params.value[1] / 5;
          if (score >= 4) return '#FF4D4F';
          if (score >= 2.5) return '#FAAD14';
          return '#52C41A';
        }
      },
      label: {
        show: true,
        formatter: function(params) { return params.data.shortTitle; },
        position: 'top',
        fontSize: 10
      },
      markLine: {
        silent: true,
        symbol: ['none', 'none'],
        lineStyle: { type: 'dashed', color: '#C9CDD4' },
        data: [
          { xAxis: 2.5 },
          { yAxis: 2.5 }
        ]
      },
      markArea: {
        silent: true,
        data: [
          [{ xAxis: 2.5, yAxis: 2.5, itemStyle: { color: 'rgba(255,77,79,0.05)' } },
           { xAxis: 5, yAxis: 5 }],
          [{ xAxis: 0, yAxis: 0, itemStyle: { color: 'rgba(82,196,26,0.05)' } },
           { xAxis: 2.5, yAxis: 2.5 }]
        ]
      }
    }]
  };
  chart.setOption(option);
  return chart;
}
```

### 5.5 综合风险指数仪表盘（gauge，用于 header 区域，可选）

```javascript
function initGauge(container, riskIndex) {
  var chart = echarts.init(container);
  var option = {
    series: [{
      type: 'gauge',
      min: 0,
      max: 5,
      splitNumber: 5,
      axisLine: {
        lineStyle: {
          width: 20,
          color: [
            [0.6, '#52C41A'],
            [0.8, '#FAAD14'],
            [1, '#FF4D4F']
          ]
        }
      },
      pointer: { width: 5, length: '60%' },
      axisTick: { show: false },
      splitLine: { length: 15 },
      axisLabel: { fontSize: 12 },
      detail: {
        valueAnimation: true,
        formatter: '{value}',
        fontSize: 28,
        offsetCenter: [0, '70%']
      },
      data: [{ value: riskIndex }]
    }]
  };
  chart.setOption(option);
  return chart;
}
```

---

## 6. Top 5 高风险事件卡片

```html
<section class="top-risks">
  <h2>高风险事件详情</h2>
  <div class="risk-cards">
    <!-- 重复 N 次 -->
    <div class="risk-card risk-{level}">
      <div class="risk-card-header">
        <span class="risk-badge">{risk_level}</span>
        <span class="risk-score">评分: {score}</span>
        <span class="risk-date">{date}</span>
      </div>
      <h3 class="risk-title">{event_title}</h3>
      <p class="risk-summary">{ai_summary}</p>
      <div class="risk-tags">
        <span class="tag tag-type">{event_type}</span>
        <span class="tag tag-route">{affected_route}</span>
        <span class="tag tag-country">{country}</span>
      </div>
      <div class="risk-impact">
        <strong>供应链影响:</strong> {impact_description}
      </div>
      <div class="risk-source">
        来源: <a href="{url}" target="_blank">{source}</a>
      </div>
    </div>
  </div>
  <div class="ai-summary-box">
    <h3>AI 综合分析</h3>
    <p>{overall_ai_analysis}</p>
  </div>
</section>
```

```css
.top-risks {
  margin: 16px 0;
}

.risk-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.risk-card {
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: var(--color-card-shadow);
  border-left: 4px solid #C9CDD4;
}

.risk-card.risk-high { border-left-color: #FF4D4F; }
.risk-card.risk-medium { border-left-color: #FAAD14; }
.risk-card.risk-low { border-left-color: #52C41A; }

.risk-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.risk-high .risk-badge { background: #FFF1F0; color: #FF4D4F; }
.risk-medium .risk-badge { background: #FFFBE6; color: #FAAD14; }
.risk-low .risk-badge { background: #F6FFED; color: #52C41A; }

.risk-tags {
  margin: 8px 0;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-right: 6px;
  background: #F2F3F5;
  color: var(--color-text-secondary);
}

.ai-summary-box {
  background: #F0F5FF;
  border: 1px solid #ADC6FF;
  border-radius: 8px;
  padding: 16px 20px;
  margin-top: 16px;
}
```

---

## 7. 交互要求（必须遵循）

1. **Tooltip**: 每个图表都必须配置 tooltip
2. **DataZoom**: 时间线图表必须同时配置 `type: 'inside'` 和 `type: 'slider'`
3. **Legend**: 多系列图表必须有 `legend: { bottom: 0, type: 'scroll' }`
4. **Responsive**: 在 `window.load` 事件中添加 resize 监听

```javascript
window.addEventListener('load', function() {
  var charts = [];
  try { charts.push(initTimeline(...)); } catch(e) { console.error('时间线初始化失败', e); }
  try { charts.push(initGeoRisk(...)); } catch(e) { console.error('地理图初始化失败', e); }
  try { charts.push(initTypeDist(...)); } catch(e) { console.error('类型分布初始化失败', e); }
  try { charts.push(initImpactMatrix(...)); } catch(e) { console.error('影响矩阵初始化失败', e); }

  window.addEventListener('resize', function() {
    for (var i = 0; i < charts.length; i++) {
      if (charts[i]) charts[i].resize();
    }
  });
});
```

---

## 8. 常见 Pitfall（务必遵守）

这些是高频 ECharts 错误，每一条都源自实际踩坑经验：

### Pitfall 1: 初始化时机
- 图表初始化**必须**在 `window.addEventListener('load', ...)` 内执行，不能在脚本解析时直接执行。
- 必须检查 `typeof echarts === 'undefined'`，如果 CDN 加载失败则显示友好的降级提示。

### Pitfall 2: JavaScript 兼容性
- **禁止使用** `const`、`let` 和箭头函数 `=>`。
- 统一使用 `var` 和 `function(){}`，确保在旧版预览环境中不出错。
- 一个语法错误会**静默杀死**整个 `<script>` 块中后续的所有 JS 执行。

### Pitfall 3: markLine 的 type 值
- 只有三个合法值: `'average'`、`'min'`、`'max'`。
- `'median'` **不存在**，会抛出错误并破坏后续所有图表。
- 如需中位线，手动计算数值并使用 `{ yAxis: 3.5 }` 形式。

### Pitfall 4: markLine symbol 格式
- 必须用数组: `symbol: ['none', 'none']`
- 裸字符串 `symbol: 'none'` 会产生意外的箭头标记。

### Pitfall 5: scatter symbolSize 回调签名
- 回调接收的是扁平的 `value` 数组（如 `[x, y, size]`），不是数据对象。
- 错误: `function(d) { return d.value[2] * 4; }`
- 正确: `function(val) { return val[2] * 8 + 10; }`

### Pitfall 6: 错误隔离
- 任何一个图表函数中的未捕获异常会**静默终止**页面上后续所有 JS 执行。
- 因此每个图表初始化必须包裹在独立的 try-catch 中（参见第7节的初始化模式）。

---

## 9. Header 区域模板

```html
<header class="dashboard-header">
  <div class="header-left">
    <h1>中东局势供应链风险看板</h1>
    <p class="header-meta">
      报告生成时间: {datetime} | 数据范围: {time_range} | 聚焦地区: {region}
    </p>
  </div>
  <div class="header-right">
    <div class="gauge-mini" id="gauge-container" style="width:120px;height:120px;"></div>
  </div>
</header>
```

```css
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 20px 24px;
  box-shadow: var(--color-card-shadow);
  margin-bottom: 16px;
}

.dashboard-header h1 {
  font-size: 22px;
  margin: 0 0 8px;
}

.header-meta {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}
```

---

## 10. Footer 模板

```html
<footer class="dashboard-footer">
  <p>数据来源: Exa Web Search / Twitter / Reddit | 报告生成时间: {datetime}</p>
  <p class="disclaimer">免责声明: 本报告基于公开新闻来源的AI分析，仅供参考，不构成任何投资或决策建议。风险评分为模型估算值，实际风险可能与评估存在偏差。</p>
</footer>
```

```css
.dashboard-footer {
  text-align: center;
  padding: 16px;
  margin-top: 24px;
  font-size: 12px;
  color: var(--color-text-secondary);
  border-top: 1px solid var(--color-border);
}

.disclaimer {
  font-size: 11px;
  color: #C9CDD4;
  margin-top: 8px;
}
```
