---
name: jma-report-generation
description: 基于统计结果生成最终调研报告。
---

# 报告生成子技能

## 工作流
1. **模板填充**: 使用 `assets/report_template.md` 渲染。
2. **AI 分析洞察**:
   - 分析薪资溢价情况。
   - 对比脉脉爆料与猎聘挂牌价的差异（通常爆料价包含总包，挂牌价仅体现 Base + 固定年终）。
   - 针对脉脉大爆料专区的数据给出的谈薪建议。
3. **结果交付**: 生成 `reports/{path}/report.md`。
