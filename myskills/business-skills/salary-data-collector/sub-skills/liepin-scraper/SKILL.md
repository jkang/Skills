---
name: liepin-scraper
description: 猎聘雇主挂牌价抓取子技能
---

# 🤖 Liepin Scraper

你专门负责从猎聘网页端抓取 `{company} {job_title}` 的招聘挂单价（Employer Posted Salaries）。

## 🕸️ 抓取策略
1. 访问 `https://www.liepin.com/zhaopin/?key={company} {job_title}` 或对应搜索站。
2. 提取至少 20 条该公司的符合岗位要求的招聘 JD 数据。
3. 需要抓取猎聘特有的薪水范围写法（如 `40-60k·16薪`），以及学历、年限要求和具体岗位 title。

## 📤 输出规范
将数据存为 `reports/raw/liepin.json`：
```json
[
  {
    "platform": "liepin",
    "job_name": "高级前端工程师",
    "salary_range": "40-60k·16薪",
    "req_experience": "5-10年",
    "req_education": "本科"
  }
]
```
