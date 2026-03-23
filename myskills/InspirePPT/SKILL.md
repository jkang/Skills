---
name: inspire_pptx
description: "任何涉及到 .pptx 文件的操作均请使用此技能（作为输入、输出或两者兼有）。包括：创建幻灯片演示文稿；读取、解析或提取任何 .pptx 文件的文本内容；编辑、修改或更新现有演示文稿；组合或拆分幻灯片；处理模板、版式、演讲备注或批注。只要用户提到“幻灯片”、“PPT”、“演示文稿”或提及 .pptx 文件名，请务必触发此技能。只要需要打开、创建或修改 .pptx 文件，都请使用它。"
license: Proprietary. 完整条款见 LICENSE.txt
---

# PPTX 技能 (InspirePPT)

## 两大标准子技能 (Subskills)

InspirePPT 是基于 Anthropic 的标准 PPTX 技能方法论构建的，包含核心的两大工作流。

**🚨 核心指令 (CRITICAL DIRECTIVE)**: **绝对禁止 (NEVER)** 自己编写自定义的 Python 或 Node.js 脚本（例如 `generate_ppt.py`）来解析 Markdown 或强行将文本注入到幻灯片中。必须像人类编辑一样，直接使用你的原生 Agent **文件编辑工具 (Edit Tool / `replace_file_content`)** 来自然地修改拆包后的 XML 文件。

### Subskill 1: 利用 Markdown 创建 Inspire PPT (新建模式)
**触发条件:** 当用户要求从文本、大纲或 Markdown 创建、生成、构建全新的演示文稿时。
**标准### 场景一：基于 Markdown 内容生成专家级 PPT (Create from Content)
**核心原则：设计先行 (Design-First)**
在直接操作 XML 之前，Agent 必须遵循以下 Pipeline：
1. **深度理解**：完整阅读 Markdown 内容，提取核心观点、技术细节和金句。
2. **结构化设计**：为每一页 PPT 设计：
   - **内容精华**：从原文提取并精炼的文本。
   - **布局选择**：根据内容复杂度（列表、网格、图表、大标题）从模板选择最匹配的 Slide ID。
   - **样式标注**：标注需要加粗、着色或特殊对齐的部分，对照 `SamplePPT` 标准。
3. **用户确认**：将上述完整设计表格通过 `notify_user` 发给用户确认。
4. **手术级执行**：确认后，使用 `add_slide.py` 克隆底版，通过 Agent 文本编辑工具精准注入。

**操作命令流：**
1. 解包模板：`python scripts/office/unpack.py assets/InspireTemplate.pptx unpacked/`
2. 循环克隆：`python scripts/add_slide.py unpacked/ slide[X].xml`
3. 注入内容：修改 `unpacked/ppt/slides/slide[N].xml`
4. 封装交付：`python scripts/office/pack.py unpacked/ NewPPT.pptx`
 克隆所需的版式，构建整套幻灯片的目录结构。
4. **Agent 编辑:** 使用你原生的 **编辑工具**，在解压出的 `slide*.xml` 的 `<a:t>` 标签内精准替换占位符文本。
5. 使用 `python scripts/clean.py unpacked/` 移除未使用的模板占位符和残留文件。
6. 编译最终的演示文稿: `python scripts/office/pack.py unpacked/ output.pptx --original assets/InspireTemplate.pptx`。
*(完整操作细节，请严格参考 [references/editing.md](references/editing.md))*

### Subskill 2: 将现有 PPT 转换为 Inspire 风格 (换皮模式)
**触发条件:** 当用户提供一个现有的幻灯片，并要求对其进行品牌重塑、重新设定样式或者转换为 Inspire 视觉风格时。
**标准样式迁移工作流:**
1. 提取目标演示文稿: `python scripts/office/unpack.py target.pptx unpacked/`
2. 运行 **全链路样式迁移 (Full Style Transfer) 脚本**:
   `python scripts/rebrand.py unpacked/ --style-json assets/pptstyle.json`
   *(该脚本会智能检测并替换Logo，将版权年份自动更新为当前年份，把旧有公司名称改为 "Inspire"，并通过注入品牌设计 Token，深度强行覆写 `theme*.xml` 中的 `<a:clrScheme>` 和字体排版)。*
3. 若需要，使用你的编辑工具进行任何微小的文案或排版手动调整。
4. 编译获得换皮后的演示文稿: `python scripts/office/pack.py unpacked/ rebranded.pptx --original target.pptx`。

---

## 快速参考 (Quick Reference)

| 任务 | 命令 / 指南 |
|------|-------|
| 读取/分析内容 | `python -m markitdown presentation.pptx` |
| 面向 Subskill 1 (新建) | 阅读 [references/editing.md](references/editing.md) |
| 面向 Subskill 2 (换皮) | `python scripts/rebrand.py unpacked/ --style-json assets/pptstyle.json` |
| 无模板硬编码创建 | 阅读 [references/pptxgenjs.md](references/pptxgenjs.md) |

---

## 读取内容 (Reading Content)

```bash
# 文本内容提取
python -m markitdown presentation.pptx

# 视觉效果总览
python scripts/thumbnail.py presentation.pptx

# 查看原始 XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## 编辑工作流 (Editing Workflow)

**阅读 [references/editing.md](references/editing.md) 获取完整详情。**

1. 使用 `thumbnail.py` 分析模板
2. Unpack（解包） → 克隆幻灯片版式 → 依靠编辑工具编辑内容 → Rebrand（品牌替换） → Clean（清理残留） → Pack（打包）

---

## 从零创建 (Creating from Scratch)

**阅读 [references/pptxgenjs.md](references/pptxgenjs.md) 获取完整详情。**

仅当完全没有任何模板或可供参考的演示文稿时使用。

---

## 设计系统 (`pptstyle.json`)

**强制要求 (MANDATORY)**: 您必须严格且唯一地使用 `assets/pptstyle.json` 中定义的设计标量 (Design Tokens) 作为所有排版决策的真实来源。**严禁自行发明或随意使用十六进制色值、字体家族或字号。**

### 1. 规则手册: `pptstyle.json`
在生成或修改任何幻灯片之前，请先解析 `assets/pptstyle.json`。
- **色彩**: 必须使用 `color_system.brand_primary` (如 `#1B2B47` Starry Blues, `#4A9FD8` Creative Blue) 和 `color_system.functional`。
- **排版**: 必须应用 `typography.hierarchy` 中规定的确切字体和尺寸 (例如，`h1` 必须使用 `MiSans SemiBold` 28pt)。
- **布局**: 请遵循 `layout_grid` 设定的边距距离 (例如，上下 48px，左右 60px)。
- **组件**: 卡片、徽章以及标注框的绘制参数必须与 `components` 字段中的定义分毫不差。

### 2. 视觉组件库: `SamplePPT.pptx`
当需要了解复杂的排版长什么样时：
- 使用 `python scripts/thumbnail.py assets/SamplePPT.pptx` 或 `markitdown` 参阅示例文件。

### 3. 母版画布: `InspireTemplate.pptx`
在通过 XML 路线编辑时 (`references/editing.md` 工作流)：
- 请始终使用 `assets/InspireTemplate.pptx` 作为您解包的基础模板。
- 找到对应的幻灯片结构，克隆它，并替换掉它的假数据。

### 视觉排版铁律 (Visual Layout Rules)
**每一页幻灯片都必须包含视觉元素** —— 图像、图表、图标或形状。纯文字的幻灯片是不合格的。
- **可选排版**: 双列 (左文右图)、图标+文本横排、2x2 四宫格、半出血图像。
- **留白**: 请严格按照 JSON 中定义的留白间距，避免内容压边。

### 绝对避免（常见错误）

- **不要重复相同的版式** —— 交替使用分栏、卡片、图文
- **不要将正文居中** —— 保持段落和列表左对齐；只居中标题
- **大小对比不能缩水** —— 标题需要 36pt 以上才能从 14-16pt 的正文中脱颖而出
- **不要滥用蓝色** —— 挑选适合该子话题的具体颜色
- **不要创建纯文本幻灯片** —— 避开干巴巴的“大标题+几个子要点”，一定要加上对应的 Icon 或图形
- **绝对不要使用低对比度元素** —— 若在浅色背景，字必须极深；若在深色背景，字必须极浅。

---

## 质量检测 QA (Required)

**默认假定结果是有问题的。你的任务是把它们找出来。**

你的第一次生成或修改的结果几乎不可能是完美的。把 QA (审查) 看作是一场 Bug 狩猎，而不是走过场。如果在第一眼没找到任何瑕疵，说明你找得不够仔细。

### 内容 QA (Content)

```bash
python -m markitdown output.pptx
```

检查是否漏写内容、出现错别字、顺序颠倒。
如使用了模板库，强制搜索是否残留了假内容（如 "lorem", "ipsum" 等占位符）：
```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```
如果 Grep 弹出了结果，证明修改不到位。解决它们再向上汇报。

### 视觉 QA (Visual)

**⚠️ 强烈建议通过 Subagents 进行多模态图像识别**，因为当局者迷，大模型本身很容易脑补自己代码写出来的是完美的布局。
首先，将幻灯片切片为多张图片（参考下方“切图命令”），然后在 Prompt 中挂载图像，对 Agent 说：

> 仔细检查这些幻灯片，找出所有的排版错误：
> - 文本溢出了边界，还是和背景形状重叠了？
> - 并列的元素（卡片、栏目）是不是没对齐？大小不一致？
> - 页面边缘的留白是不是过于局促（小于 0.5英寸）？
> - 字体是不是用了浅灰色配白色底，导致完全看不清（低对比度）？
> - 是不是残留了乱码或占位符？

### QA 循环闭环

1. 生成幻灯片 → 导出为图片集 → 视觉审查
2. **列出发现的 Bug 列表**
3. 使用工具逐一修复这些 Bug
4. **重新验证受波及的 XML 幻灯片**（注意：修复 A 可能导致 B 偏移）
5. 直到没有任何布局 Bug 时方可停止。

---

## 将 PPT 转换为图片供 Agent 视觉审查

方便你将幻灯片渲染成单张图片，以便多模态分析：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

这将会产出 `slide-01.jpg`, `slide-02.jpg` 等文件。

---

## 环境依赖 (Dependencies)

- `pip install "markitdown[pptx]"` - 强力文本提取分析
- `pip install Pillow` - 头图拼接与 Logo 解析缩放
- `npm install -g pptxgenjs` - 从零绘制脚本生成专属库
- LibreOffice (`soffice`) - PPT 转 PDF 引擎
- Poppler (`pdftoppm`) - PDF 转高分辨率图片引擎
