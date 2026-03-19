# InspirePPTSkills

将任意 PPT 文档转换为 **Inspire 设计规范** 风格的工具，严格保留原文内容。

## Inspire 视觉设计系统

| 元素 | 规范 |
|---|---|
| 主品牌色 | 星空蓝 `#1B2B47` — 封面/章节页背景、标题 |
| 强调色 | 创想蓝 `#4A9FD8` — 序号、数字、重点词 |
| 内容页背景 | 白色 `#FFFFFF` |
| 正文色 | `#1B2B47`（深蓝灰，非纯黑） |
| 次要文字 | `#64748B` |
| 封面/章节页 | 星空蓝→创想蓝 渐变背景，白色文字 |
| 中文字体 | 思源黑体 / 微软雅黑（回退） |

## 参考 PDF 的页面结构

基于 **AI商业落地实战：从场景选择到落地应用.pdf**（55页），该 PPT 的完整页面类型分布：

| 页面类型 | 示例 | 特征 |
|---|---|---|
| `cover` 封面 | P1 | 深蓝渐变背景，大标题居中 |
| `agenda` 议程 | P2 | "AGENDA 议程" 标题，5个章节列表 |
| `section` 章节封面 | P5 P13 P21 P32 P40 P48 P53 | `PART XX` 格式，短文本，深蓝渐变 |
| `interactive` 互动页 | P4 P17 P20 P25 P31 P38 P46 P51 | 🎯 图标开头，"互动环节/实操引导" |
| `case_study` 案例页 | P26-P30 P35-P37 | 英文标签 "CASE STUDY"，白色背景 |
| `content` 内容页 | P6-P12 P14-P16… | 英文标签+中文标题，白色背景 |
| `ending` 结尾页 | P55 | "感谢聆听"，深蓝渐变背景 |

## 页面处理策略 (v5.0 Source-Host Strategy)

| 页面类型 | 处理方式 |
|---|---|
| `cover` / `agenda` / `section` / `ending` | **直接替换结构**：清空目标页原有形状，通过XML深度拷贝（Deepcopy） `InspireTemplate.pptx` 的 `<p:bg>` 和 `<p:spTree>`，再由程序注入源文本。此法保留完美渐变背景，无需依赖容易破坏图片关系的版式应用机制。 |
| `content` / `interactive` / `case_study` | **原位样式清洗（Style Washing）**：源PPT作为Host容器（完美保留所有原生图片、图表的关系链）。强制全局替换 `theme1.xml` 植入 Inspire 色板，再将非标准文本刷为微软雅黑及标准主色 `#1B2B47`，所有纯色填充块强制转为创想蓝 `#4A9FD8` 或标准背景色。 |

## InspireTemplate.pptx 幻灯片索引映射（固定）

```
index 1  (Slide 2)  → Cover 封面
index 4  (Slide 5)  → Agenda/CONTENTS 目录
index 5  (Slide 6)  → Section Divider 章节封面（无图）
index 6  (Slide 7)  → Section Divider with Image
index 10 (Slide 11) → Ending 结尾页
```

## 分类识别规则

```python
# 封面:  index == 0
# 议程:  index <= 3 AND 含 agenda/议程/目录
# 章节:  含 "PART \d+" 且文本 < 400 字符
# 互动:  含 🎯 或 "互动环节" 或 "实操引导"
# 结尾:  最后一张 AND 文本 < 400 字符
# 其他:  content
```

## 使用方法

```bash
python scripts/style_transfer.py <target.pptx>
# 可选：--template InspireTemplate.pptx --style pptstyle.json
```

输出：`<原文件名>_inspired.pptx`

## 文件说明

| 文件 | 说明 |
|---|---|
| `InspireTemplate.pptx` | 11张幻灯片，各页型模板 |
| `pptstyle.json` | 完整设计系统（颜色/字体/间距/组件） |
| `AI商业落地实战：…pdf` | **55页参考示例** — 效果标准 |
| `scripts/style_transfer.py` | 核心引擎 v5.0 (Source-Host ZIP 融合架构) |
