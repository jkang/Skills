---
name: levels-fyi-scraper
description: Levels.fyi 平台的薪资抓取子技能
---

# 🤖 Levels.fyi Scraper

你专门负责从 Levels.fyi 系统爬取/整理员工薪水数据。
输入参数：`company` 和 `job_title`。

## 🕸️ 抓取策略
1. 根据用户提供的 `company` 和 `job_title`，构造查询语句或URL，例如 `https://www.levels.fyi/companies/{company}/salaries/{role}` 或对应搜索入口。
2. 提取最近日期的至少 20 条相关薪资爆料。如果数据不足，请抓取该公司的尽可能多的相关岗位。
3. 关键字段提取：
   - 职级 (Level/Title)
   - 总包 (TC)
   - 基本薪资 (Base Salary)
   - 股票 (Stock)
   - 奖金 (Bonus)
   - 地点 (Location)
   - 爆料日期 (Date)

## 📤 输出规范
将提取的原始列表数据保存为 `reports/raw/levels_fyi.json`，格式如下：
```json
[
  {
    "platform": "levels_fyi",
    "raw_title": "Software Engineer E5",
    "raw_tc": "300000",
    "raw_base": "200000",
    "raw_stock": "80000",
    "raw_bonus": "20000",
    "raw_date": "2024-03-01",
    "raw_location": "San Francisco, CA"
  }
]
```
