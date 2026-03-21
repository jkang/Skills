# 打造属于你的 AI 辅助 PPT 制作利器：Inspire PPT Skill 深度解析

在这个 AI Agent 大行其道的时代，如何让 AI 不仅能帮你“写”文案，还能直接帮你“做”出甚至“改”出符合企业级规范的精美演示文稿？

今天，我想和大家分享一个最近打造的极客级工具——**Inspire PPT Skill**。它不仅是一个自动化修改 PPT 的脚本集合，更是一套赋予大模型深入操控 Microsoft Office 格式能力的完整框架。

---

## 💡 什么是 Inspire PPT Skill？它有什么用？

Inspire PPT Skill 是一套专为 AI Agent（以及开发者）设计的命令行工具和工作流集合，位于我们的 `.agents/skills` 体系中。

**它的核心目标是：** 在保证排版、样式和企业品牌规范（如 Inspire 品牌视觉）的前提下，实现对 `.pptx` 文件的**精准结构化读取、自动化品牌转换、以及细粒度的内容修改**。

日常工作中，你可能会遇到以下痛点：
1. **公司换 Logo/品牌升级了**，历史几百份 PPT 需要一页页改 Logo 和修改版权年份。
2. 拿到一份旧模板的演讲稿，需要**完全迁移到新的品牌配色和字体**。
3. 想让 AI 帮你生成 PPT，但直接用纯文本生成出来的排版总是惨不忍睹，且不符合公司的视觉规范。

Inspire PPT 就是为了解决这些问题而生的。

---

## 🛠️ Inspire PPT 究竟能做什么？

在这个 Skill 中，我们提供了全链路的自动化能力：

- **深度解析与洞察**：通过集成 `markitdown` 和 `thumbnail.py`，不仅能提取 PPT 中的纯文本内容，还能直接生成每一页的高清缩略图，让大语言模型（如 Gemini/Claude）能够“看到”幻灯片的真实长相，从而做出更精准的版式决策。
- **一键全方位品牌替换 (Rebranding)**：这是该 Skill 最亮眼的功能。它可以自动找出 PPT 里的旧 Logo 图片进行尺寸适配并无缝替换，遍历全文将“旧公司名”替换为“新品牌”，甚至自动追踪版权声明（如 `© 2025`）将其更新到当前年份。
- **无感样式转移 (Style Transfer)**：你不再需要手动点选颜色刷。提供一份 `pptstyle.json` 配置，它能自动解析 PPT 主题的底层 XML，将旧的色板（如各种深色调）全部替换为 Inspire 的“星空蓝”和“创想蓝”，并将全局字体批量替换为符合规范的无衬线字体（如 MiSans / Montserrat）。
- **安全的原子化编辑**：支持针对特定单页进行增删改，自动维护复杂的关联引用关系，保证修改后的文件用 Office 打开绝对不会报错。

---

## 🚀 如何使用 Inspire PPT？

无论是新建还是修改，Inspire PPT 都遵循一套严谨的 Pipeline。

### 场景一：一键自动换皮与修改现有 PPT
假设你有一份旧的演示文稿 `examples/旧版产品方案.pptx`，你想将其包装成全新的 Inspire 品牌：

1. **解包 (Unpack)**
   ```bash
   python scripts/office/unpack.py "examples/旧版产品方案.pptx" unpacked_dir/
   ```
   *这一步会将二进制的压缩包展开为可读的 XML 树，并进行排版美化，方便后续代码或 AI 阅读。*

2. **执行品牌重塑 (Rebrand & Style Transfer)**
   ```bash
   python scripts/rebrand.py unpacked_dir/ \
       --old-name "Thoughtworks" \
       --new-name "Inspire" \
       --year "2026" \
       --style-json templates/pptstyle.json
   ```
   *瞬间完成：检测异常宽度的图片替换为 Inspire Logo；将所有文字替换；更新底层 `theme1.xml` 应用新的色板和字体。*

3. **让 AI 进行细粒度内容编辑 (Edit Content)**
   你可以启动 Subagent 专门针对某几张幻灯片（如 `ppt/slides/slide3.xml`）的 `<a:t>` 文本节点进行修改。由于解包后每个 Slide 都是独立的文件，多 Agent 并发处理毫无压力。

4. **清理与打包 (Clean & Pack)**
   ```bash
   python scripts/clean.py unpacked_dir/
   python scripts/office/pack.py unpacked_dir/ "examples/新版产品方案-Inspire.pptx"
   ```
   *脚本会自动移除未使用的媒体文件、修复损坏的关联关系（Relationships），重新压缩成合法的标准 PPTX 格式。*

### 场景二：结合大模型从零生成 (Create from Scratch)
如果要全新生成，Skill 中也结合了 `pptxgenjs` 方案：
1. 编写一份符合期望大纲的 Markdown 内容。
2. 依据 `pptstyle.json` 中的模板规范，将其转换为结构化的 JSON 指令。
3. 通过 Node 脚本将 JSON 渲染出结构完美、带有炫彩底纹和正确字体的新 PPTX 文件。

---

## ⚙️ 深入源码：设计与实现过程揭秘

也许你会好奇，为什么不用现成的 `python-pptx` 库？

因为对于高度定制化的模板重构和 AI 交互，现有库在处理**主题色底层继承**、**智能图片替换**。我们选择了**直接硬核操作 Office Open XML (OOXML)** 规范。

### 目录结构图解
一个成熟的 AI Skill 不应该是一堆散乱脚本的堆砌。Inspire PPT Skill 拥有严谨的工程化架构：

```text
InspirePPT/
├── SKILL.md                 # Agent 的主入口，定义 Skill 能力边界、系统提示词和标准工作流。
├── editing.md               # 修改现有 PPT 时大模型应遵循的分步策略。
├── templates/               # 品牌视觉资源库
│   ├── pptstyle.json        # Design Tokens：定义品牌色板、排版规范的 Single Source of Truth。
│   ├── Inspire logo.png     # 标准品牌 Logo（适用于浅色背景）
│   └── Inspire logo white.png # 反白的品牌 Logo（适用于深色背景）
├── scripts/                 # 自动化工具链
│   ├── rebrand.py           # 品牌重塑脚本（Logo、文字替换及 Style Transfer 的核心大脑）。
│   ├── add_slide.py         # 用于在代码层面安全地克隆和追加新幻灯片。
│   ├── clean.py             # 智能清理废弃的素材与悬空节点。
│   └── office/              # 底层基建
│       ├── unpack.py        # 解压并格式化 XML。
│       ├── pack.py          # 带有 Auto-healing（自愈）能力的重打包脚本。
│       └── thumbnail.py     # 视觉截帧工具，赋予大模型读取版式的“眼睛”。
└── examples/                # 用于演示和端到端测试的样本。
```

### 1. 巧妙的图片感知 (Image Recognition Hook)
在 `rebrand.py` 中，如何在成百上千的配图中准确找到原公司的 Logo 图片进行替换？
我们并没有依赖复杂且不稳定的图片分类模型，而是利用了简单的启发式规则结合图像库 `Pillow`：
长宽比例大于 3:1，且高度小于 500px 的大概率是 Logo。接着，通过采样透明底色上的非透明像素平均亮度，判断该原生 Logo 适合用深色还是白色的 Inspire Logo 替换，甚至还能精准保持原始图片的宽高关系，防止排版错乱。

### 2. Style Transfer 的奥义：重写 `theme.xml`
PPT 的页面颜色并不是写死在单个文本上的，而是通过 `<a:schemeClr val="accent2"/>` 这样的指针来引用主题色。
我们在设计 Skill 时，引入了 `templates/pptstyle.json`，将设计系统（Design System）与代码解耦。
脚本会解析 `<a:clrScheme>`，强制将其中的核心调色板映射为：
- `dk1` -> 主字体色
- `accent1`、`accent2` -> Inspire 星空蓝、创想蓝

**关键代码实现摘录：**
```python
def replace_theme_styles(unpacked_dir: Path, style_json_path: Path) -> list[str]:
    # 1. 解析设计师提供的 style token
    with open(style_json_path, "r") as f: style = json.load(f)
    
    # 2. 映射 JSON 色值到 OOXML 主题槽位 (去除 HEX # 号)
    colors_map = {
        "dk1": style["color_system"]["functional"]["text_primary"]["hex"].replace("#", ""),
        "lt1": "FFFFFF", 
        "accent1": style["color_system"]["brand_primary"]["starry_blues"]["hex"].replace("#", ""),
        "accent2": style["color_system"]["brand_primary"]["creative_blue"]["hex"].replace("#", ""),
        # ...省略其他映射
    }

    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    for theme_file in (unpacked_dir / "ppt" / "theme").glob("theme*.xml"):
        tree = ET.parse(theme_file)
        
        # 3. 拦截并修改底层颜色模式
        clr_scheme = tree.find(".//a:clrScheme", ns)
        if clr_scheme is not None:
            clr_scheme.set("name", "Inspire Theme") # 宣示新主权
            for slot, hex_val in colors_map.items():
                slot_el = clr_scheme.find(f"a:{slot}", ns)
                if slot_el is not None:
                    # 强行刷新 srgbClr 颜色标签
                    srgb = slot_el.find("a:srgbClr", ns)
                    if srgb is not None: srgb.set("val", hex_val)
                    
                    # 如遇 sysClr 系统色绑架，直接将其转化为绝对 sRGB 色
                    sys_clr = slot_el.find("a:sysClr", ns)
                    if sys_clr is not None:
                        slot_el.remove(sys_clr)
                        new_srgb = ET.SubElement(slot_el, "{...}srgbClr")
                        new_srgb.set("val", hex_val)
        
        tree.write(theme_file, encoding="utf-8", xml_declaration=True)
```
这样，即便原来的文档用了各式各样的色块，只要他们遵循了主题色，运行完脚本瞬间就能实现“一键换装”，视觉冲击力极强。

### 3. `pack.py` 的自愈能力
直接修改 XML 极容易破坏 `.rels` 关系映射表，导致 PPT 损坏。
因此，我们的 `pack.py` 内置了“自愈”校验（Validation Logic）：无论是 `<sldLayout>`、`<sld>` 还是各类图片资源，在最终压缩前，它会自动比对关联 ID，补充缺失的命名空间属性和 `xml:space='preserve'` 标签。这一设计使得大模型（LLM）在修改 XML 时容错率大幅提升。

---

## 结语

Inspire PPT Skill 的开发过程，其实是对“如何让 AI 更好地理解和控制传统结构化软件”的一次成功探索。
通过 解构 (Unpack) -> 面向对象修改/正侧替换 -> 自愈式的重构 (Pack)，我们为繁杂无趣的格式排版工作引入了强有力的自动化流。

下次当你的部门再次迎来视觉大升级时，不妨泡杯咖啡，跑一下脚本，让 Inspire PPT 为你搞定剩下的一切。
