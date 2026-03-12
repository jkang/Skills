---
name: data-exporter
description: 数据导出为双页 Excel 报告子技能
---

# 🤖 Data Exporter

你是负责最终生成的导出 Agent。在清洗阶段完毕后，你需要调度 Python 脚本，将最终数据从 JSON 转换为包含双 Sheet 标签页的 Excel 文档。

## 📤 生成策略
1. 前提：确保 `reports/cleaned_data.json` 和 `reports/raw_data_merged.json` 这两个文件已经由 data-cleaner 准备就绪。
2. 调度执行：运行 `py scripts/export_excel.py {company}` 或将其作为内部代码执行（Agent自发执行 Python 脚本），调用对应脚本根据那两个 JSON 文件生成 Excel。
3. 验证产物：检查 `reports/Salary_Report_{company}.xlsx` 是否成功生成。
4. 提供反馈：向用户输出成功生成文件的绝对路径结果，通知执行圆满结束。
