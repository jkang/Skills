---
name: jma-data-cleaning
description: 清洗和翻译原始薪资数据，统一映射为标准化 JSON 格式。
---

# 数据清洗子技能

## 核心任务
将采集到的非结构化"黑话"和各平台差异化数据转化为统一的统计模型。

## 工作流
1. **黑话匹配**:
   - `30k*16` -> Base=30, Months=16.
   - `tc 80` -> TC=80.
   - `签字费/入职奖` -> `sign_on_bonus`.
2. **数据源处理**:
   - 如果 `source` 是 `liepin`，设置 `data_type: "employer_posted"`。
   - 如果 `source` 是 `maimai` 或 `levels.fyi`，设置 `data_type: "employee_reported"`。
3. **输出标准化**:
   将清洗后的数据写入 `reports/{path}/cleaned_data.json`。

## 字段规范
见宏技能定义的 JSON 格式（base_monthly, bonus_months, tc_annual 等）。
