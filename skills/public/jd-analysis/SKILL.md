---
name: jd-analysis
description: 深度分析职位描述（JD），提取技能矩阵，发现隐藏信息，识别红旗信号
author: JobFlow Team
version: 1.0.0
allowed-tools:
  - parse_jd
  - match_score
  - web_search
---

# JD 深度分析技能

## 工作目标

对职位描述（Job Description）进行系统性深度分析，帮助求职者：
1. 快速了解岗位核心要求
2. 识别技能缺口
3. 发现 JD 中的隐藏信息和潜在风险

## 工作流程

### 步骤 1：获取 JD

接收 JD 文本或 URL，提取完整内容。

### 步骤 2：结构化解析

使用 `parse_jd` 工具将 JD 解析为结构化数据：
- 基础信息（职位名称、公司、地点、薪资）
- 职责列表
- 要求列表

### 步骤 3：技能需求矩阵

将技能分为：
- **Must-Have**：JD 明确要求的技能（通常用"必须/require/must"等词标记）
- **Nice-to-Have**：优先考虑的加分技能（"优先/preferred/plus"等）
- **隐式要求**：从职责推断出的隐含技能

### 步骤 4：匹配度预评估

如果已有简历，使用 `match_score` 计算初步匹配度，识别：
- 已具备的技能
- 需要补充或强化的技能

### 步骤 5：输出报告

生成 Markdown 格式分析报告，保存到 `/mnt/user-data/outputs/jd_analysis.md`

## 报告模板

```markdown
# JD 分析报告

## 基础信息
| 字段 | 内容 |
|------|------|
| 职位 | ... |
| 公司 | ... |
| 地点 | ... |
| 薪资 | ... |

## 技能需求矩阵
### Must-Have（必备）
- ...

### Nice-to-Have（加分项）
- ...

## 岗位画像
...

## 隐藏信息推断
...

## ⚠️ 红旗信号
...

## 📊 匹配度初评
总分：xx/100
```
