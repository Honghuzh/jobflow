---
name: resume-optimization
description: 针对目标职位优化简历，包括 STAR 法则改写、量化成果、ATS 关键词优化
author: JobFlow Team
version: 1.0.0
allowed-tools:
  - parse_resume
  - parse_jd
  - match_score
---

# 简历优化技能

## 工作目标

帮助求职者将通用简历转化为针对目标职位高度定制的版本，提高 ATS 通过率和招聘官关注度。

## 工作流程

### 步骤 1：读取现有简历

使用 `parse_resume` 工具解析简历，获取结构化内容。

### 步骤 2：分析目标 JD

使用 `parse_jd` 解析目标职位要求，使用 `match_score` 计算当前匹配度，识别差距。

### 步骤 3：逐项对比优化

逐一检查简历中每项工作经验：
- 是否与目标职位相关？
- 是否使用了量化数据？
- 是否遵循 STAR 结构？

### 步骤 4：STAR 法则改写

对每条工作经历进行 STAR 改写：
- **Situation**：业务背景
- **Task**：具体任务
- **Action**：你的行动
- **Result**：量化结果

### 步骤 5：ATS 关键词优化

- 确保包含 JD 中的核心技术关键词
- 使用标准化术语（如 "React.js" 而非 "ReactJS"）
- 避免创意排版（ATS 无法解析）

### 步骤 6：输出结果

- `resume_optimized.md`：优化后的完整简历
- `resume_changes.md`：修改说明（原文 → 新文，改写理由）

## 优化原则

1. **真实性**：不编造经历，只是更好地表达真实经历
2. **针对性**：每份简历都应针对具体职位定制
3. **简洁性**：一页纸原则（应届/1-3年），最多两页（资深）
4. **数字说话**：至少 60% 的工作经历条目包含具体数字
