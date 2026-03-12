---
name: data-cleaner
description: 原始薪资数据清洗与标准化子技能
---

# 🤖 Data Cleaner

你负责将来自四家不同平台（Levels.fyi, 脉脉, 猎聘, 51job）格式各异的原始JSON数据（`reports/raw/*.json`），合并并清洗为统一的标准化结构。

## 🧹 清洗策略
1. **统一合并原始数据**：先读取原始数据文件内容合并至一个对象或数组结构（如需），保存一份 `reports/raw_data_merged.json` 备份。
2. **字段标准化映射**：遍历并清洗每条数据记录，统一转换为以下格式字段：
   - `company`: (从用户输入或数据中补全)
   - `job_title`: (统一映射)
   - `level`: (若有)
   - `base_salary`: 提取出具体数字（人民币/元 或 万/年）。（若外币请保留原币种单位或简单按照固定汇率算，但优先保持原本形式并备注）
   - `stock_value`: 取股票/期权部分估值
   - `bonus_value`: 奖金/年终奖部分估值
   - `tc` (Total Compensation): 算总包数字
   - `source`: 数据来源 (levels_fyi / maimai / liepin / 51job)
   - `data_type`: employee_reported (员工爆料如 levels/maimai) 或 employer_posted (挂出薪资如 liepin/51job)
3. **文本解析转换**：
   - 对脉脉的诸如 `30*16` 解析出：`base = 30k*12`，`bonus = 30k*4`。计算 TC。
   - 对猎聘/51job的如 `40-60k·16薪`，可取中位数 `50k * 16` 作为 TC 估算或分别记录区间上下限。

## 📤 输出规范
将清洗和统一好格式的 JSON 数组输出到 `reports/cleaned_data.json` 中：
```json
[
  {
    "company": "阿里巴巴",
    "job_title": "产品经理",
    "level": "P7",
    "base_salary": "420,000",
    "stock_value": "200,000",
    "bonus_value": "140,000",
    "tc": "760,000",
    "source": "maimai",
    "data_type": "employee_reported"
  }
]
```
