---
name: 51job-scraper
description: 前程无忧(51job)雇主挂牌价抓取子技能
---

# 🤖 51job Scraper

你专门负责从前程无忧 (51job) 抓取 `{company} {job_title}` 的招聘挂单价（Employer Posted Salaries）。

## 🕸️ 抓取策略
1. 访问前程无忧搜索端，搜索目标公司及岗位。
2. 提取至少 20 条该公司的符合岗位要求的招聘 JD 数据。
3. 抓取其标明的薪酬区间（如 `3-5万/月`、`50-80万/年`），以及学历、经验等基础维度。

## 📤 输出规范
将数据存为 `reports/raw/51job.json`：
```json
[
  {
    "platform": "51job",
    "job_name": "高级前端开发",
    "salary_range": "3-5万/月",
    "req_experience": "5-7年",
    "req_education": "本科"
  }
]
```
