---
name: jma-data-collection
description: 采集各平台的薪酬数据。包含 Levels.fyi、脉脉大爆料专区和猎聘。
---

# 采集子技能

## 工作流

### 1. Levels.fyi 采集
- 构造 URL: `https://www.levels.fyi/companies/{company}/salaries/{role}/levels/{level}`
- 提取: Base Salary, Stock, Bonus, TC.

### 2. 脉脉大爆料采集 (重点权重)
- **目标**: 针对脉脉"大爆料专区"进行重点搜集。
- **搜索策略**: 
  - 使用 `site:maimai.cn "大爆料" {company} {job_title}`
  - 使用 `site:maimai.cn "爆料" {company} {level}`
- **提取重点**: 解析爆料帖中的具体数字 (Base, 股票, 签字费, 年终月数)。
- **记录来源**: 标注为 "脉脉大爆料专区"。

### 3. 猎聘网采集 (市场参照)
- **目标**: 取代 Boss直聘，获取当前雇主在市场的挂牌价。
- **采集逻辑**:
  - 访问 `https://www.liepin.com/zhaopin/?key={company} {job_title}`
  - 提取前 5-10 条职位卡片的薪资范围（如 `30-50k·16薪`）。
  - 标注数据类型为 `employer_posted`。

## 输出规格
每个采集项需包含: `source` (平台), `type` (爆料/挂牌), `raw_text`, `url`.
写入 `reports/{path}/raw_data.json`.
