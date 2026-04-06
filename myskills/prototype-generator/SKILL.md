---
name: prototype-generator
description: 高级原型生成器 —— 根据用户需求直接生成功能完整、设计专业、可直接演示的前端原型。相比基础的 prototype-prompt-generator，本 Skill 不仅生成提示词，而是直接输出完整的 React 项目，包含深度用户场景分析、多 Persona 交互旅程、真实业务数据和多路径演示。当用户需要"直接生成可演示原型"、"包含真实业务场景的演示"、"展示完整用户旅程"时使用此技能。
---

# Prototype Generator (高级原型生成器)

本 Skill 将用户的业务需求转化为可直接运行的 React 原型项目，包含深度用户场景分析、多 Persona 数据建模和完整的交互旅程演示。

## 核心能力

1. **直接生成可演示原型**：输出完整的 React + TypeScript + Tailwind 项目
2. **深度用户场景分析**：自动生成 2-3 个典型用户画像（Personas）
3. **真实业务数据建模**：基于业务场景生成贴近真实的 Mock 数据
4. **多路径交互演示**：覆盖正常流程、异常处理、边缘情况和权限差异

---

## 执行流程

### 步骤 1：需求捕获与澄清

当用户触发此技能时，评估当前信息是否足够生成高质量原型。

**必须澄清的问题：**

1. **产品形态确认**
   - 这是什么类型的产品？（如：电商、教育、SaaS 工具、社交平台）
   - 主要平台？（Web 应用、移动端 Web、小程序、桌面应用）

2. **核心业务流程**
   - 用户主要完成什么任务？（如：购买课程、提交报销、预约服务）
   - 业务中最关键的 2-3 个决策点是什么？

3. **用户角色差异**
   - 是否有明显的用户角色区分？（如：管理员/普通用户、商家/消费者）
   - 不同角色的权限和功能差异有多大？

4. **演示重点**
   - 最想展示的核心场景是什么？
   - 是否有需要特别强调的异常/边缘场景？

**信息足够时的快速确认：**
如果用户描述已包含上述要点，简要总结并确认后直接进入步骤 2。

---

### 步骤 2：用户场景与 Persona 设计

基于业务理解，设计 2-3 个典型用户画像。

**每个 Persona 必须包含：**

```typescript
interface Persona {
  id: string;                    // 唯一标识
  name: string;                  // 姓名（中文）
  role: string;                  // 角色/职位
  avatar: string;                // 头像 URL（使用 dicebear）
  description: string;           // 一句话描述
  
  // 业务相关
  goals: string[];              // 使用本产品的核心目标（2-3个）
  painPoints: string[];         // 当前痛点（2-3个）
  skillLevel: "初级" | "中级" | "高级";
  
  // 使用习惯
  usageContext: string;         // 使用场景（如"每天通勤时"、"办公室工作时"）
  preferredFeatures: string[];  // 最关注的功能
  
  // 数据特征（用于生成真实 Mock 数据）
  dataProfile: {
    typicalValues: Record<string, any>;    // 该角色的典型数据值
    frequency: "高频" | "中频" | "低频";
    typicalErrors: string[];               // 该角色容易犯的错误/异常场景
  };
}
```

**Persona 设计原则：**
- 覆盖主要用户群体（如：新手/专家、高频/低频用户）
- 体现业务角色的核心差异（如：不同权限、不同目标）
- 每个 Persona 都有明确的代表性场景

---

### 步骤 3：业务数据建模

为每个 Persona 生成真实、合理的 Mock 数据。

**数据建模要求：**

1. **业务实体定义**
   - 识别核心数据实体（如：订单、课程、任务、客户）
   - 定义实体间的关联关系

2. **真实数据特征**
   - 数值范围符合业务常识（如：价格、数量、时间）
   - 包含合理的异常值和边界情况
   - 不同 Persona 的数据有明显的差异性

3. **场景化数据包**
   - 为每个核心场景准备完整的数据集
   - 包括：初始状态、用户操作、状态变化、最终结果

**示例数据结构：**
```typescript
// 场景：职场新人购买课程
const SCENARIO_NEWBIE_PURCHASE = {
  // 用户初始状态
  user: {
    id: "u_001",
    name: "小李",
    level: "初级",
    points: 120,
    completedCourses: 2,
    balance: 0  // 未充值
  },
  
  // 浏览场景数据
  browse: {
    recommendedCourses: [...],     // 3-5 门推荐课程
    learningPath: {...},           // 个性化学习路径
    progress: {...}                // 当前学习进度
  },
  
  // 购买场景数据
  purchase: {
    selectedCourse: {...},
    price: 299,
    discount: { type: "新人优惠", amount: 50 },
    finalPrice: 249,
    paymentMethods: [...]
  },
  
  // 异常场景
  errors: {
    insufficientBalance: {...},    // 余额不足
    networkError: {...},           // 网络异常
    alreadyPurchased: {...}        // 重复购买
  }
};
```

---

### 步骤 4：交互旅程与路径设计

为每个核心场景设计完整的用户旅程，覆盖所有可能的路径。

**旅程设计框架：**

```
场景：[场景名称]
Persona：[目标用户]
目标：[用户想要完成什么]

主流程（Happy Path）：
1. [起始状态] → [用户操作] → [系统响应] → [新状态]
2. ...

分支路径：
├─ 路径 A：[条件触发] → [替代流程] → [结果]
├─ 路径 B：[条件触发] → [替代流程] → [结果]
└─ 路径 C：[条件触发] → [替代流程] → [结果]

异常处理：
- 异常 1：[错误类型] → [系统反馈] → [恢复路径]
- 异常 2：[错误类型] → [系统反馈] → [恢复路径]

边缘情况：
- 情况 1：[极端条件] → [系统行为]
- 情况 2：[极端条件] → [系统行为]
```

**必须覆盖的路径类型：**
1. **主流程**：最常见、最理想的用户路径
2. **分支流程**：基于不同选择产生的变体路径
3. **异常流程**：错误处理、失败恢复
4. **边缘情况**：空状态、极限值、长时间未操作
5. **跨角色流程**：涉及多角色协作的场景

---

### 步骤 5：原型架构设计

设计可支持多 Persona 切换和多路径演示的原型架构。

**推荐架构模式：**

```
app/
├── page.tsx                    # 主页面：Persona 选择 + 场景导航
├── layout.tsx                  # 根布局
├── globals.css                 # 全局样式
│
├── components/                 # 可复用组件
│   ├── persona-switcher.tsx   # Persona 切换器
│   ├── scenario-player.tsx    # 场景播放器
│   └── [domain-components]    # 业务组件
│
├── scenarios/                  # 场景定义
│   ├── [scenario-1]/
│   │   ├── data.ts            # 场景数据
│   │   ├── journey.tsx        # 旅程组件
│   │   └── paths/
│   │       ├── main.tsx       # 主路径
│   │       ├── error-a.tsx    # 异常路径 A
│   │       └── edge-b.tsx     # 边缘情况 B
│   └── [scenario-2]/
│       └── ...
│
├── data/                       # 数据层
│   ├── personas.ts            # Persona 定义
│   ├── mock-data.ts           # Mock 数据生成器
│   └── scenarios-data.ts      # 场景数据集
│
└── hooks/                      # 自定义 Hooks
    ├── use-persona.ts         # Persona 状态管理
    └── use-scenario.ts        # 场景状态管理
```

**架构原则：**
- Persona 切换实时更新整个界面
- 场景内支持路径切换和重置
- 数据与视图分离，便于维护和扩展

---

### 步骤 6：界面与交互实现

基于架构实现具体的 UI 组件和交互逻辑。

**技术要求：**

1. **技术栈**
   - React 18 + TypeScript
   - Tailwind CSS + shadcn/ui 组件库
   - Lucide React 图标

2. **响应式设计**
   - 移动端优先（< 640px）
   - 平板适配（640px - 1024px）
   - 桌面端优化（> 1024px）

3. **核心组件规范**

**Persona Switcher（角色切换器）：**
```tsx
// 功能：
// - 展示所有 Persona 卡片
// - 点击切换当前角色
// - 显示当前角色的关键信息
// - 切换时触发全局数据更新
```

**Scenario Navigator（场景导航）：**
```tsx
// 功能：
// - 列出所有可演示的场景
// - 每个场景显示：名称、描述、涉及 Persona
// - 点击进入场景演示
```

**Path Controller（路径控制器）：**
```tsx
// 功能：
// - 在场景内显示可选路径
// - 主路径（默认）
// - 分支路径（条件触发）
// - 异常路径（错误模拟）
// - 边缘情况（特殊条件）
// - 一键重置到初始状态
```

**State Indicator（状态指示器）：**
```tsx
// 功能：
// - 显示当前 Persona
// - 显示当前场景和路径
// - 显示关键数据状态
// - 支持快速跳转
```

---

### 步骤 7：原型输出与交付

将完整原型输出为可运行的项目结构。

**输出文件清单：**

```
prototype-[project-name]/
├── README.md                   # 项目说明和运行指南
├── SCENARIOS.md               # 场景与路径说明文档
├── DATA-GUIDE.md              # 数据字典和说明
│
├── app/
│   ├── page.tsx               # 主入口页面
│   ├── layout.tsx             # 根布局
│   └── globals.css            # 全局样式
│
├── components/
│   └── ui/                    # shadcn/ui 组件
│       ├── button.tsx
│       ├── card.tsx
│       ├── badge.tsx
│       ├── avatar.tsx
│       ├── progress.tsx
│       ├── tabs.tsx
│       ├── scroll-area.tsx
│       └── ...
│   ├── persona-switcher.tsx   # 角色切换组件
│   ├── scenario-navigator.tsx # 场景导航组件
│   ├── path-controller.tsx    # 路径控制组件
│   └── state-indicator.tsx    # 状态指示组件
│
├── lib/
│   ├── utils.ts               # 工具函数
│   └── data.ts                # 数据和类型定义
│
├── components.json            # shadcn/ui 配置
├── next.config.js             # Next.js 配置
├── tailwind.config.ts         # Tailwind 配置
├── tsconfig.json              # TypeScript 配置
└── package.json               # 依赖配置
```

**交付物说明：**

1. **README.md**
   - 项目概述
   - 快速开始指南
   - 场景使用说明
   - 技术栈说明

2. **SCENARIOS.md**
   - 每个场景的详细说明
   - 所有路径的描述
   - Persona 在各场景中的行为差异

3. **DATA-GUIDE.md**
   - 数据实体说明
   - Mock 数据生成逻辑
   - 如何扩展数据

---

## 输出质量标准

### 数据真实性标准

✅ **符合要求的数据：**
- 数值在合理业务范围内（如：价格 9.9-9999 元）
- 时间戳符合逻辑（如：创建时间 < 更新时间）
- 状态流转合理（如：待支付 → 已支付 → 已完成）
- 不同 Persona 数据有明显差异

❌ **不符合要求的数据：**
- 随机生成的无意义字符串
- 超出常识范围的数值
- 无关联关系的孤立数据
- 所有 Persona 使用同一套数据

### 路径完整性标准

✅ **符合要求的路径覆盖：**
- 至少 1 条完整的主流程
- 至少 2 条分支流程
- 至少 2 种异常处理
- 至少 1 个边缘情况

❌ **不符合要求的覆盖：**
- 只有主流程，无异常处理
- 异常只显示错误信息，无恢复路径
- 路径之间无法切换

### 演示友好性标准

✅ **符合要求的演示：**
- 界面美观、布局清晰
- 操作有明确的视觉反馈
- 状态变化一目了然
- 路径切换简单直观

❌ **不符合要求的演示：**
- 需要代码修改才能看到不同路径
- 界面过于简单，无法体现业务复杂度
- 状态变化不明显

---

## 执行检查清单

在生成交付前，逐项确认：

**需求理解**
- [ ] 产品形态已确认
- [ ] 核心业务流程已明确
- [ ] 用户角色差异已识别
- [ ] 演示重点已确定

**Persona 设计**
- [ ] 设计了 2-3 个 Persona
- [ ] 每个 Persona 都有明确的目标和痛点
- [ ] Persona 覆盖了主要用户群体
- [ ] Persona 数据特征已定义

**数据建模**
- [ ] 识别了核心数据实体
- [ ] 为每个场景准备了完整数据
- [ ] 数据符合业务常识
- [ ] 包含异常和边缘数据

**路径设计**
- [ ] 设计了完整的主流程
- [ ] 覆盖了分支流程
- [ ] 包含异常处理
- [ ] 包含边缘情况

**原型实现**
- [ ] 使用 React + TypeScript + Tailwind
- [ ] 实现 Persona 切换功能
- [ ] 实现路径切换功能
- [ ] 界面响应式设计
- [ ] 代码结构清晰

**文档交付**
- [ ] README.md 完整
- [ ] SCENARIOS.md 详细
- [ ] DATA-GUIDE.md 清晰

---

## 使用示例

**用户输入：**
> "帮我生成一个在线教育平台的原型，核心功能是课程购买和学习进度跟踪。目标用户包括职场新人和有经验的产品经理。"

**执行流程：**

1. **需求澄清**（已足够详细，快速确认）
2. **设计 Persona**：
   - Persona 1: 小李 - 职场新人，目标快速入门，痛点不知从何学起
   - Persona 2: 王经理 - 资深 PM，目标提升管理，痛点时间有限
   - Persona 3: 张工程师 - 转岗开发者，目标思维转型，痛点技术惯性

3. **数据建模**：
   - 为每个 Persona 生成推荐课程数据
   - 设计不同难度和方向的学习路径
   - 准备购买流程的完整数据

4. **路径设计**：
   - 主流程：浏览 → 选择 → 购买 → 学习
   - 分支：使用优惠券、分期付款
   - 异常：余额不足、网络错误、重复购买
   - 边缘：首次使用空状态、课程下架

5. **原型生成**：
   - 实现 Persona 切换器
   - 实现课程推荐页面
   - 实现购买流程
   - 实现学习进度页面
   - 添加路径控制器

6. **交付文档**：
   - README.md
   - SCENARIOS.md
   - DATA-GUIDE.md

---

## 与基础版的关系

| 特性 | prototype-prompt-generator（基础版） | prototype-generator（高级版） |
|------|-------------------------------------|------------------------------|
| 输出形式 | 结构化提示词 | 可直接运行的 React 项目 |
| 用户场景 | 描述性说明 | 完整 Persona + 数据建模 |
| 交互演示 | 概念性描述 | 多路径可切换演示 |
| 业务数据 | 简要建议 | 真实 Mock 数据 |
| 适用场景 | 给 AI 工具生成原型 | 直接演示业务概念 |
| 使用时机 | 需要 v0/Artifacts 生成 | 需要直接展示给客户/团队 |

**选择建议：**
- 需要快速生成提示词 → 使用基础版
- 需要直接演示完整场景 → 使用高级版

---

## 附录：组件库说明

本 Skill 生成的原型使用 **shadcn/ui** 组件库，包含以下核心组件：

- **Layout**: Card, Tabs, ScrollArea, Separator
- **Form**: Button, Input, Select, Checkbox, RadioGroup
- **Feedback**: Badge, Progress, Alert, Toast
- **Data Display**: Avatar, Table, Collapsible
- **Navigation**: Breadcrumb, Command, Navigation Menu
- **Overlay**: Dialog, Dropdown Menu, Popover, Sheet, Tooltip

所有组件均基于 Tailwind CSS 和 Radix UI，风格统一，易于定制。
