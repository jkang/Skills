---
name: maimai-scraper
description: 脉脉大爆料专区的薪资抓取子技能
---

# 🤖 Maimai Scraper

你专门负责从脉脉平台抓取“大爆料专区”的员工爆料薪资数据。
输入参数：`company` 和 `job_title`。

## 🕸️ 抓取策略
1. 使用搜索引擎指令精确制导（如果有能力可以联网/读取搜索工具）：
   `site:maimai.cn "大爆料" {company} {job_title}`
2. 至少获取 20 条来自真实发帖的爆料信息。如果匹配的爆料不够，可以扩大搜索至 `{company} 薪资` 或 `{company} 总包`。
3. 从帖子的非结构化文本中智能提取具体数字及构成。脉脉常含有黑话，比如 `30k*16`，或者 `150w tc = 80w base + 50w rsu + 20w base`，须保留原始爆料文本以备后续清洗。

## 📤 输出规范
将提取的部分半结构化或文本数据保存为 `reports/raw/maimai.json`，格式如下：
```json
[
  {
    "platform": "maimai",
    "post_title": "阿里P7大爆料",
    "post_content": "入职包，三十五给十六个月，外加一千股三年",
    "extracted_numbers": "35k * 16, 1000 RSU 3 years",
    "post_date": "2023-10-12"
  }
]
```
