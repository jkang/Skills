---
name: jma-data-analysis
description: 对清洗后的薪资数据进行统计分析，产出统计图表数据。
---

# 数据统计子技能

## 工作流
1. **调用分析脚本**: 
   直接运行 `python3 scripts/salary_calculator.py reports/{path}/cleaned_data.json`。
2. **多维统计**:
   - 总体统计: 中位数, P25, P75, 平均值, 样本数。
   - 分类统计: 区分爆料价 (Employee) 与挂牌价 (Employer) 的中位数对比。
3. **输出**:
   保存为 `reports/{path}/stats.json`。
