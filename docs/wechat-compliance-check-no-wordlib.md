# wechat-compliance-check-no-wordlib

**中文** · [English](#english)

微信公众号文章发布前合规风险检测工具（无词库版）。

## 功能概述

采用纯规则审查架构对公众号文章进行合规风险检测，无需下载词库，开箱即用：

1. **六大模块逐项审查**：标题、封面图、正文配图、正文内容、营销表达、综合评估，覆盖文章全生命周期
2. **红线逐条对照**：对照微信官方《微信公众号和服务号推荐运营规范》9 条红线逐条检查，引用官方原文条款和案例，输出结构化合规报告

### 与 wechat-compliance-check 的区别

| 特性 | wechat-compliance-check | wechat-compliance-check-no-wordlib |
|------|------------------------|-------------------------------------|
| 词库扫描（DFA 算法） | ✅ 10 大风险类别词库 | ❌ 无词库 |
| 规则审查（红线对照） | ✅ 9 条红线 | ✅ 9 条红线 |
| 首次使用需联网 | 是（下载词库） | 否 |
| Python 依赖 | Python 3.8+ | 无 |
| 适用场景 | 需要精确词库扫描 | 轻量级、即装即用 |

> 如果你需要 DFA 词库扫描能力（覆盖政治敏感、色情低俗、暴恐血腥等 10 大类别的精确关键词匹配），请使用 [wechat-compliance-check](wechat-compliance-check.md)。

### 检测模块

| 模块 | 检测内容 |
|------|----------|
| 标题检测 | 标题党/夸大虚假、关键信息缺失、政治敏感、诱导行为、广告法极限词 |
| 封面图检测 | 内容相关性、高风险内容、诱导信息、AIGC 图片 |
| 正文配图检测 | 内容相关性、截图脱敏、版权标注、诱导信息、AIGC 图片 |
| 正文内容检测 | 低创作度、不良信息、不实信息、营销推广、政治敏感、过时信息、侵权、虚假人设 |
| 营销与广告表达 | 广告法极限词、虚假误导、对比贬低、诱导消费、行业专属禁词 |
| 综合风险评估 | 9 条红线逐条审查、整体风险等级判定 |

### 参考文件

| 文件 | 用途 |
|------|------|
| `references/platform-rules.md` | 九条红线官方规范全文（主要判定依据） |
| `references/platform-rules-basic.md` | 基础运营规范补充条款 |
| `references/platform-cases.md` | 低创作度违规官方案例 |
| `references/compliance-rules.md` | 政治敏感词规则 + 广告法违禁词库 + 合规替代速查表 |

## 安装

### 前置要求

- [QoderWork](https://qoder.com) 桌面端（或 Claude Code、Codex 等支持 Skill 的 Agent）
- 无需 Python，无需网络

### 安装步骤

```bash
# 复制到对应 skills 目录
cp -r wechat-compliance-check-no-wordlib ~/.qoderwork/skills/
cp -r wechat-compliance-check-no-wordlib ~/.claude/skills/
cp -r wechat-compliance-check-no-wordlib ~/.codex/skills/
```

无需 Python，无需下载词库，即装即用。

## 使用方式

在支持 Skills 的 Agent（Claude Code、Codex、Qoder 等）中直接说：

- "帮我检测这篇文章的合规风险"
- "公众号文章审核"
- "这篇文章能发吗"
- "检查红线"
- "快速检测一下敏感词"
- "帮我看看这个标题合不合规"

支持的输入方式：
- 直接粘贴文本
- 提供 Markdown / .docx / .txt 文件路径
- 提供 URL

### 工作流示例

| 场景 | 触发方式 | 检测范围 |
|------|----------|----------|
| 全量检测 | "帮我检测这篇文章有没有违规" | 六大模块全量扫描 |
| 快速敏感词检测 | "快速检测一下敏感词" | 政治敏感 + 广告法 |
| 标题专项检测 | "帮我看看这个标题合不合规" | 标题模块 |
| 配图合规检测 | "这些配图有没有问题" | 封面图 + 配图模块 |

## 技术特性

- **纯规则审查**：基于 Agent 理解力 + 内置参考文档，无需外部词库
- **完全本地运行**：不上传文章内容到任何外部服务
- **零依赖**：无需 Python，无需 pip，无需网络
- **即装即用**：复制即可使用，无初始化步骤

## 局限性

- 无法保证 100% 通过微信审核，检测结果仅供参考
- 无词库扫描，敏感词检测依赖 Agent 对参考文档中违禁词库的理解和比对能力
- 图片内容检测仅基于用户文字描述
- P2/P3 级别需人工判断
- 微信采用人工 + AI 双重审核，规则持续更新，存在误判可能

---

<a id="english"></a>

# wechat-compliance-check-no-wordlib

**[中文](#wechat-compliance-check-no-wordlib)** · English

Pre-publish compliance risk detection tool for WeChat Official Account articles (No Dictionary Version).

## Overview

Uses a pure rule-based review architecture — no dictionary download required, ready to use out of the box:

1. **Six-Module Review**: Title, cover image, inline images, body content, marketing expressions, and comprehensive assessment
2. **Red-Line Check**: Checks against WeChat's official 9 red-line operating standards with official clause citations and case references

### Comparison with wechat-compliance-check

| Feature | wechat-compliance-check | wechat-compliance-check-no-wordlib |
|---------|------------------------|-------------------------------------|
| Dictionary Scanning (DFA) | ✅ 10 risk categories | ❌ No dictionary |
| Rule Review (Red Lines) | ✅ 9 red lines | ✅ 9 red lines |
| Internet Required (First Use) | Yes (download dicts) | No |
| Python Dependency | Python 3.8+ | None |
| Best For | Precise keyword scanning | Lightweight, instant use |

> If you need DFA dictionary scanning (covering political sensitivity, pornography, violence, etc. across 10 categories), use [wechat-compliance-check](wechat-compliance-check.md).

## Installation

### Prerequisites

- [QoderWork](https://qoder.com) desktop client (or any Skill-compatible agent such as Claude Code, Codex)
- No Python required, no network needed

### Steps

```bash
cp -r wechat-compliance-check-no-wordlib ~/.qoderwork/skills/
```

No Python, no dictionary download, ready to use.

## Usage

Talk to the agent directly:
- "Check this article for compliance risks"
- "WeChat article review"
- "Can I publish this?"

Supported input methods:
- Paste text directly
- Provide Markdown / .docx / .txt file path
- Provide a URL

## Technical Features

- **Pure Rule Review**: Based on Agent comprehension + built-in reference documents
- **Fully Local**: No article content uploaded to any external service
- **Zero Dependencies**: No Python, no pip, no network required
- **Instant Setup**: Copy and use, no initialization needed

## Limitations

- Cannot guarantee 100% WeChat review approval — detection results are for reference only
- No dictionary scanning — sensitive word detection relies on Agent's ability to compare against reference documents
- Image content detection is based on user text descriptions only
- P2/P3 level items require human judgment

---

[Apache License 2.0](../LICENSE)
