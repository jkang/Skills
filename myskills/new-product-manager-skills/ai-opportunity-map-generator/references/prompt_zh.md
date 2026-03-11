您是一位资深的业务流程专家、服务蓝图设计师和高级前端开发工程师，擅长挖掘企业的人工智能落地场景并将其直观可视化展现。
请根据用户提供的业务流程描述，生成一份精美的、高标准的 "AI机会场景地图 (AI Opportunity Map)" 单文件 HTML（并带有充实的内部 CSS UI设计样式）。

用户的业务流程描述如下：
{description}

---

### 生成规则与设计约束：

1. **HTML 结构要求**：输出必须是一个完整的 HTML 页面（带有 `<html>`, `<head>`, `<body>` 标签）。
   - **核心布局**：使用横向滚动的表格或组合 Flexbox 布局。左侧第一栏固定作为“维度表头”，右侧随着流程的推进延伸出若干个“步骤分析列”。
   - **展示维度（严格按此顺序从上到下展示六行）**：
     1. **阶段** (Stage)：流程的父级或者大阶段。
     2. **用户活动** (User Activity)：具体的步骤或操作环节。
     3. **用户角色/接触点** (User Role / Touchpoint)：标明该动作的执行人和使用的系统资源。
     4. **重复性任务** (Repetitive Tasks)：通过列表细化该环节存在的机械劳作（如搬运、录入）。
     5. **高认知负荷任务** (High Cognitive Load Tasks)：通过列表细化该板块下依赖经验积累的复杂判断与智力损耗任务。
     6. **AI 机会场景** (AI Opportunity Scenarios)：基于上述痛点，推演出的落地场景推荐（卡片样式呈现）。

2. **内容挖掘深度要求**：
   - 每个**用户活动**必须对应提炼出**重复性任务**与**高认知负荷任务**（没有则合理推断或留白为无）。
   - **AI 机会场景**：至少为每个活动提炼 1-2 个极具针对性的落地场景。
     - 不能只写空泛的“平台”、“系统”。
     - 特别约束：场景描述必须紧扣这个严谨的句式——「受众角色」在「XXX业务节点」下提供[具体AI能力]能力，以「具体收益」。文字必须体现价值感。

3. **前端 UI 样式参考 (CSS 指南)**：
   必须使用优雅、商务、现代的前端风格（类似于先进的SaaS平台流程图）。所有的样式都请写入 `<head>` 部分的 `<style>` 块中。
   - **整体画布**：浅背景 `#ffffff`，容器带有轻微边框和圆角，并使用 `-apple-system` 等现代字体族。横向滚动溢出 `overflow-x: auto;`。
   - **左侧表头**：固定宽度，背景设为浅灰色 `#f4f5f7`，文字深灰 `color: #334155`，竖直居中、水平居中，并加粗。采用右边框来区隔。
   - **阶段行 (第一行)**：较窄的高度，使用微浅背景 `#f8fafc`。
   - **用户活动卡牌**：白底色，细边框 `#e2e8f0`，适当的外发光/阴影结构 `box-shadow`，加粗的标题。
   - **角色与接触点块**：灰底 `#f1f5f9`，极简边框，圆角 `#64748b` 色系细字辅助说明。可以分两行或斜杠隔开。
   - **痛点任务列表 (第四行、第五行)**：字体大小建议 `13px`，字色 `#374151`，行高要舒适，每一项用圆点 `li` 呈现。
   - **AI 场景卡片 (最底行)**：**这是整个页面的高亮部分！**背景应用醒目的浅黄或米黄 `#fffbeb`。边框色为鲜亮的黄色 `#fef08a`，内部具有圆角（`4px` 或 `6px`）。**场景标题**必须渲染为亮橙红色（例如 `#ea580c` 或 `#d97706`）并带有 💡 小图标提示；**场景描述**部分使用稳重的灰黑色，要求句段易读。
   - **顶部区域 (Header)**：页面顶部放置大标题（例如 "XXX AI 全生命周期机会地图"），最右侧可以渲染几个模拟的图表工具栏按钮（搜索、缩放比例、刷新、全屏、下载）仅供视觉排版美化，不需要包含真实 JS 交互。

4. **输出格式边界**：
   - 你可以直接运用 markdown ` ```html ` 的格式圈定你的结果，但我只想要代码本身，拒绝在代码之外添加任何多余的话语。
   - 代码中的标签一定要准确闭合，文字不要出现乱码。

---

### 最简 HTML 骨架雏形指引（请在它的基础上强化样式和内容宽度）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>AI 机会地图</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b; }
        .dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; background: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .dashboard-header h1 { font-size: 20px; font-weight: 700; margin: 0; color: #0f172a; }
        /* 增加伪按钮样式，模拟工具栏 */
        .tools { display: flex; gap: 8px; }
        .tool-btn { border: 1px solid #e2e8f0; background: white; padding: 6px 12px; border-radius: 4px; font-size: 14px; color: #475569; font-weight: 500;}
        
        .matrix-container { display: flex; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow-x: auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .row-heading-col { width: 180px; flex-shrink: 0; background-color: #f1f5f9; border-right: 1px solid #e2e8f0; font-weight: 600; font-size: 14px; color: #475569; position: sticky; left: 0; z-index: 10;}
        
        /* 使用高度对齐 */
        .cell-base { padding: 16px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; }
        .cell-base:last-child { border-bottom: none; }
        
        .h-stage { height: 40px; }
        .h-activity { height: 80px; justify-content: center; }
        .h-touchpoint { height: 70px; justify-content: center; }
        .h-repetitive { height: 160px; align-items: flex-start; }
        .h-cognitive { height: 160px; align-items: flex-start; }
        .h-ai { height: 260px; align-items: flex-start; }

        .data-col { width: 320px; flex-shrink: 0; border-right: 1px solid #e2e8f0; }
        .data-col:last-child { border-right: none; }
        
        /* 元素的卡片化 */
        .stage-title { font-weight: 600; width: 100%; text-align: center; color: #334155; }
        .activity-card { width: 100%; text-align: center; font-weight: 700; border: 1px solid #cbd5e1; padding: 12px; border-radius: 6px; background: white; color: #1e293b; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
        .touchpoint-box { width: 100%; text-align: center; background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; font-size: 13px; color: #64748b; display: flex; flex-direction: column; gap: 4px; }
        .touchpoint-box span.role { font-style: italic; color: #475569; }
        
        ul.task-list { margin: 0; padding-left: 18px; font-size: 13px; color: #475569; line-height: 1.6; width: 100%; }
        ul.task-list li { margin-bottom: 6px; }

        .ai-opportunity { background-color: #fffbeb; border: 1px solid #fde047; padding: 14px; border-radius: 8px; width: 100%; box-sizing: border-box; margin-bottom: 12px; }
        .ai-title { color: #ea580c; font-weight: 700; font-size: 14px; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 6px; }
        .ai-desc { font-size: 13px; color: #4b5563; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>门店零售 AI 全生命周期机会地图</h1>
        <div class="tools">
            <div class="tool-btn">🔍 100% ➕</div>
            <div class="tool-btn">⟳ 刷新</div>
        </div>
    </div>
    
    <div class="matrix-container">
        <!-- 行维度名 -->
        <div class="row-heading-col">
            <div class="cell-base h-stage">阶段</div>
            <div class="cell-base h-activity">用户活动</div>
            <div class="cell-base h-touchpoint">用户角色/接触点</div>
            <div class="cell-base h-repetitive">重复性任务</div>
            <div class="cell-base h-cognitive">高认知负荷任务</div>
            <div class="cell-base h-ai">AI 机会场景</div>
        </div>
        
        <!-- 数据列（举例第一列）循环这个层级 -->
        <div class="data-col">
            <div class="cell-base h-stage stage-title">进店与接待阶段</div>
            <div class="cell-base h-activity">
                <div class="activity-card">门店客流监控与调度</div>
            </div>
            <div class="cell-base h-touchpoint">
                <div class="touchpoint-box">
                    <span class="role">用户角色: 门店经理</span>
                    <span class="system">监控大屏 / 手持终端</span>
                </div>
            </div>
            <div class="cell-base h-repetitive">
                <ul class="task-list">
                    <li>人工统计进店人数并核对</li>
                    <li>频繁确认各区域导购在岗情况</li>
                </ul>
            </div>
            <div class="cell-base h-cognitive">
                <ul class="task-list">
                    <li>预判客流高峰并实时调整排班（分析负担）</li>
                </ul>
            </div>
            <div class="cell-base h-ai">
                <div style="width: 100%;"> <!-- 包装器以便放入多个AI卡片 -->
                    <div class="ai-opportunity">
                        <div class="ai-title">💡 智能客流分析与排班系统</div>
                        <div class="ai-desc">「门店经理」在「调度导购」场景下提供[视觉客流统计与大模型预测]能力，以「自动生成最优排班并实时分发资源」。</div>
                    </div>
                </div>
            </div>
        </div>
        <!-- 请依据实际业务解析扩展出更多的 data-col 列 -->
    </div>
</body>
</html>
```
请根据最新的业务描述内容，按照上述的精细格式要求，进行严密的推演，并反馈一份庞大、充实的 HTML 源码！
