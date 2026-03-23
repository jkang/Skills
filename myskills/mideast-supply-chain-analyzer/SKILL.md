---
name: mideast-supply-chain-analyzer
description: 自动抓取中东地区地缘政治新闻动态，分析其对航运供应链的潜在影响，生成 Excel 风险报表和 HTML 可视化看板。当用户提到"中东局势"、"地缘政治风险"、"供应链风险分析"、"航运风险"、"红海危机"、"霍尔木兹海峡"、"苏伊士运河"、"胡塞武装"、"油价波动"、"航线中断"、"运费飙升"、"海运保险"、"也门局势"、"伊朗制裁"，或要求分析地缘事件对物流、航运、贸易的影响时，使用此技能。即使用户没有明确说"供应链"，只要提到中东新闻对商业或贸易的影响分析，也应触发。
---

# 中东局势供应链风险分析器

自动抓取中东地区地缘政治新闻，通过 AI 分析评估其对航运供应链的影响，输出结构化的 Excel 风险报表和交互式 HTML 可视化看板。

## 技能概述

**目标用户**: 供应链管理人员、航运风控分析师、采购经理、物流规划师

**核心价值**: 将散乱的中东地区新闻自动转化为结构化的供应链风险评估，帮助决策者快速掌握地缘政治风险态势。

**输出物**:
- `risk_report.xlsx` — 格式化的 Excel 风险报表（4个Sheet）
- `dashboard.html` — 单文件交互式可视化看板（ECharts）
- `raw_data.json` — 原始数据存档（新闻 + 评分 + 分析）

**依赖**:
- 新闻抓取: agent-reach 技能（Exa web search、Twitter/X、Reddit）
- Excel 生成: `pip install openpyxl`
- 可视化: ECharts CDN（HTML 内联）

---

## 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 | 示例 |
|------|------|------|--------|------|------|
| `region` | String | 否 | "中东" | 聚焦地区 | "红海"、"波斯湾"、"苏伊士运河" |
| `industry` | String | 否 | "航运" | 目标行业 | "航运"、"能源"、"大宗商品" |
| `time_range` | String | 否 | "最近7天" | 时间范围 | "最近3天"、"本月"、"2024年1月" |
| `focus_topic` | String | 否 | 无 | 特定关注议题 | "胡塞武装袭击"、"伊朗制裁" |
| `sources` | List | 否 | ["exa"] | 新闻来源 | ["exa","twitter","reddit"] |
| `depth` | String | 否 | "standard" | 分析深度 | "quick" / "standard" / "deep" |

当用户请求模糊时（如"帮我看看中东最近怎么样"），按以下逻辑补全参数：
- 没有指定 region → 默认"中东"（覆盖红海、波斯湾、亚丁湾全区域）
- 没有指定 industry → 默认"航运"
- 没有指定 time_range → 默认"最近7天"
- 没有指定 sources → 默认 ["exa"]，如果用户提到 Twitter/X 或实时消息则加入 "twitter"

---

## 工作流

### Step 1: 多源新闻抓取

**目标**: 从多个来源收集中东地区与供应链相关的新闻，形成结构化的新闻列表。

#### 1.1 搜索策略

根据用户参数构建搜索查询。组合关键词模板：

**中文搜索**:
```
"{region} {focus_topic} 航运 供应链 最新动态"
"{region} 局势 对航运影响"
"中东 {focus_topic} 航线中断 运费"
```

**英文搜索**:
```
"Middle East {region} shipping supply chain disruption latest"
"{region} geopolitical risk maritime trade impact"
"Middle East {focus_topic} freight shipping route"
```

#### 1.2 新闻来源调用

**Exa Web Search（主要来源，始终使用）**:
```
使用 agent-reach 的 Exa web search 能力:
  中文搜索: numResults=10
  英文搜索: numResults=10
```

**Twitter/X（补充来源，当 sources 包含 "twitter" 时使用）**:
```
使用 agent-reach 的 Twitter 搜索能力:
  搜索关键词: "Middle East shipping {region} disruption"
  数量: 10条
```

**Reddit（补充来源，当 sources 包含 "reddit" 时使用）**:
```
使用 agent-reach 的 Exa 搜索:
  搜索: site:reddit.com "Middle East supply chain {region}"
  数量: 5条
```

#### 1.3 结果标准化

将所有来源的搜索结果统一为以下 JSON 格式：

```json
{
  "title": "新闻标题",
  "url": "https://...",
  "source": "exa|twitter|reddit",
  "published_date": "2024-01-15",
  "snippet": "新闻摘要（200字以内）",
  "language": "zh|en",
  "raw_content": "完整内容（如有）"
}
```

#### 1.4 去重与排序

- URL 完全相同的条目去重
- 标题高度相似（>80%重叠词）的条目合并，保留最详细的版本
- 按 `published_date` 降序排列（最新在前）
- 英文新闻的 snippet 翻译为中文摘要

**Step 1 输出**: `news_items[]` 数组（通常 15-30 条新闻）

---

### Step 2: 风险事件提取与评分

**目标**: 从新闻中提取结构化的风险事件，并计算综合风险评分。

#### 2.1 事件提取

逐条分析 `news_items`，提取以下结构化字段。一条新闻可能包含多个事件，也可能多条新闻描述同一个事件——需要合并同一事件的多源报道。

参照 `references/risk_categories.json` 中的事件类型代码和严重度评估标准。

每个事件的结构：

```json
{
  "event_id": "evt_001",
  "title": "事件简明标题",
  "event_type": "SHP",
  "event_type_name": "航运中断",
  "countries": ["也门", "沙特"],
  "affected_routes": ["红海-苏伊士运河航线"],
  "affected_ports": ["亚丁港"],
  "severity": 4,
  "probability": 4,
  "time_sensitivity": "紧急",
  "supply_chain_impact": "直接",
  "summary": "事件摘要（含关键数据和影响范围描述）",
  "source_urls": ["https://...", "https://..."],
  "source_count": 3
}
```

**评分标准（参考 references/risk_categories.json）**:
- `severity`（1-5）: 事件本身的严重程度，参考 event_types 中的 base_severity 和 severity_scale
- `probability`（1-5）: 事件持续或升级的概率
- `time_sensitivity`: 紧急（正在发生）/ 短期（1-7天）/ 中期（1-4周）/ 长期（>1月）
- `supply_chain_impact`: 直接（航线中断）/ 间接（成本传导）/ 潜在（可能演变）

#### 2.2 风险评分计算

将提取的事件列表传入评分引擎：

```bash
echo '<events_json>' | python scripts/risk_scorer.py
```

或保存为临时文件后调用：

```bash
python scripts/risk_scorer.py /tmp/events.json
```

脚本读取事件数据，参照 `references/supply_chain_map.json` 中的航线重要性权重，计算综合评分。

**评分公式**:
```
综合评分 = 严重度 × 0.35 + 概率 × 0.25 + 紧急度 × 0.20 + 航线权重 × 0.20
         + 多源验证加成（3源+0.5, 5源+1.0）
```

**风险等级**:
- >= 4.0: 高危（红色）— 立即启动应急预案
- 3.0-3.9: 中等（橙色）— 密切监控，准备备选方案
- < 3.0: 低（绿色）— 常规关注，定期复查

**Step 2 输出**: `scored_events[]` 数组 + 整体风险统计

---

### Step 3: 供应链影响分析 + Excel 报表

**目标**: 基于评分结果，分析供应链影响路径，生成格式化的 Excel 报表。

#### 3.1 影响路径分析

参照 `references/supply_chain_map.json`，为每个受影响的航线/港口生成影响评估：

```json
{
  "node_name": "红海-苏伊士运河航线",
  "node_type": "航线",
  "impact_level": "严重",
  "impact_path": "胡塞武装袭击 → 商船绕行好望角 → 运力下降15% → 运费上涨50-200%",
  "current_status": "多家航运公司已暂停红海通行",
  "alternative": "好望角绕行（+10天, +15-25%成本）",
  "extra_cost": "约50-80万美元/航次",
  "recovery_time": "取决于地缘局势，预计数月"
}
```

同时生成应对建议列表：

```json
{
  "risk_level": "高危",
  "action": "启动替代航线预案",
  "detail": "将红海航线货物转至好望角航线，与船公司协商运费锁定协议",
  "priority": "紧急",
  "department": "物流部/采购部",
  "timeframe": "立即执行",
  "estimated_cost": "运输成本增加15-25%"
}
```

#### 3.2 生成 Excel 报表

将所有数据组装为 JSON，调用生成脚本：

```bash
python scripts/generate_excel.py --input /tmp/report_data.json --output reports/{date}_{region}/risk_report.xlsx
```

输入 JSON 结构：
```json
{
  "news_items": [...],
  "scored_events": [...],
  "impact_analysis": [...],
  "recommendations": [...]
}
```

**4个 Sheet 规格**:

| Sheet | 内容 | 关键格式 |
|-------|------|----------|
| 新闻汇总 | 所有收集的新闻 | URL 超链接、时间排序 |
| 风险评分矩阵 | 评分后的事件 | 条件着色（红/橙/绿）、COUNTIF 汇总 |
| 供应链影响评估 | 影响节点分析 | 影响程度着色、替代方案 |
| 应对建议 | 行动方案 | 优先级着色、时间框架 |

**Step 3 输出**: `risk_report.xlsx` 文件

---

### Step 4: HTML 可视化看板

**目标**: 生成单文件交互式 HTML 可视化看板。

参照 `references/visualization_spec.md` 中的完整设计规范，生成看板。

#### 4.1 看板结构

6个核心组件：

1. **Header**: 报告标题 + 生成时间 + 综合风险指数仪表盘（gauge）
2. **KPI 卡片条**: 4个KPI（事件总数 / 高危事件数 / 受影响航线数 / 综合风险指数）
3. **风险事件时间线**: scatter 图，x=日期，y=风险评分，大小=严重度，颜色=风险等级
4. **中东风险地理分布**: scatter 模拟地理位置，标注关键节点和受影响航线
5. **风险类型分布**: 饼图/环形图，展示各风险类型（军事冲突/航运中断/制裁等）占比
6. **供应链影响矩阵**: scatter 四象限图，x=影响程度，y=发生概率，标注风险事件
7. **Top 5 高风险事件**: 详情卡片列表 + AI 综合分析摘要
8. **Footer**: 数据来源 + 免责声明

#### 4.2 技术要求

- **单文件原则**: CSS 写在 `<style>`，JS 写在 `<script>`，仅 ECharts 通过 CDN 加载
- **数据嵌入**: `var rawData = {...}` 嵌入在 `<script>` 块底部
- **ECharts CDN**: `https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js`
- **字体**: `'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif`
- **布局**: CSS Grid，2列桌面端，1列移动端（断点 768px）

#### 4.3 必须遵守的 ECharts 规则

这些规则来自实际踩坑经验，每一条都能避免看板渲染失败：

1. **初始化时机**: 所有 ECharts 初始化必须在 `window.addEventListener('load', ...)` 内执行
2. **JS 兼容性**: 使用 `var` 和 `function(){}`，禁止 `const`/`let`/箭头函数
3. **错误隔离**: 每个图表初始化包裹在独立的 `try-catch` 中
4. **markLine type**: 只有 `'average'`/`'min'`/`'max'`，`'median'` 不存在
5. **markLine symbol**: 必须用数组 `['none','none']`
6. **scatter symbolSize**: 回调接收扁平数组 `function(val) { return val[2] * 8; }`
7. **resize**: 统一监听 `window.resize`，调用所有图表实例的 `.resize()`
8. **CDN 降级**: 检测 `typeof echarts === 'undefined'`，显示友好提示

**Step 4 输出**: `dashboard.html` 文件

---

## 输出与交付

所有输出文件保存至：
```
reports/{YYYY-MM-DD}_{region}/
├── risk_report.xlsx     # Excel 风险报表（4个Sheet）
├── dashboard.html       # 交互式可视化看板
└── raw_data.json        # 原始数据存档
```

交付时向用户说明：
1. Excel 报表可直接在 Excel/WPS 中打开，支持筛选和排序
2. HTML 看板可在浏览器中打开，支持鼠标悬停查看详情
3. raw_data.json 包含完整的原始数据，便于后续自定义分析

---

## 约束条件

- **来源可追溯**: 所有结论必须有新闻来源 URL 支撑，不得臆测或编造数据
- **评分标准统一**: 风险评分严格遵循 `references/risk_categories.json` 中的评分体系
- **时效性标注**: 每条新闻标注发布时间，超过30天的新闻单独标记为"历史参考"
- **单文件HTML**: 可视化看板必须是单文件，可离线打开（仅 ECharts CDN 除外）
- **中文输出**: 所有报表和看板内容均为中文，英文新闻需翻译摘要
- **免责声明**: HTML 看板底部必须包含免责声明，说明本报告基于 AI 分析仅供参考
- **数据量控制**: 新闻条数控制在 15-30 条范围内（quick 模式 10 条，deep 模式 40 条）
- **不过度解读**: 对于影响程度不确定的事件，标注为"潜在"而非"直接"影响
