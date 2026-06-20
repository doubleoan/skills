# wechat-compliance-check

**中文** · [English](#english)

微信公众号文章发布前合规风险检测工具。

## 功能概述

采用双层检测架构对公众号文章进行合规风险检测：

1. **词库扫描层**：基于 DFA 算法 + 本地词库进行高效关键词匹配，覆盖政治敏感、法律法规、色情低俗、暴恐血腥、广告法违禁词、虚假营销等 10 大风险类别
2. **规则审查层**：对照微信官方《微信公众号和服务号推荐运营规范》9 条红线逐条检查，引用官方原文条款和案例，输出结构化合规报告

### 检测覆盖范围

| 优先级 | 类别 | 说明 |
|--------|------|------|
| P0-致命 | 政治敏感 | 领导人、敏感事件、分裂言论等 |
| P0-致命 | 法律法规 | 违法违规、涉黑涉恶、非法物品 |
| P1-严重 | 色情低俗 | 色情、软色情、低俗擦边 |
| P1-严重 | 暴恐血腥 | 暴力、恐怖主义、血腥描述 |
| P1-严重 | 毒品相关 | 毒品名称、制毒方法、贩毒信息 |
| P1-严重 | 赌博相关 | 赌博平台、博彩推广 |
| P2-警告 | 广告法违禁 | 极限用语、虚假宣传、医疗用语 |
| P2-警告 | 虚假营销 | 诱导分享、标题党、虚假承诺 |
| P3-提示 | 低质灌水 | AI 模板化内容、关键词堆砌 |
| P3-提示 | 短视频违禁 | 抖音/短视频平台通用违禁词 |

### 内置规则文档

| 文件 | 用途 |
|------|------|
| `reference/platform-rules.md` | 9 条红线官方规范全文 |
| `reference/platform-rules-basic.md` | 基础运营规范补充条款 |
| `reference/platform-cases.md` | 低创作度违规官方案例 |
| `reference/content-rules.md` | 正文内容合规细则 |
| `reference/title-rules.md` | 标题合规细则 |
| `reference/image-rules.md` | 封面图与配图合规细则 |
| `reference/marketing-rules.md` | 营销表达与广告法合规对照表 |

## 安装

### 前置要求

- [QoderWork](https://qoder.com) 桌面端
- Python 3.8+

### 安装步骤

```bash
# 1. 复制到 QoderWork skills 目录
cp -r wechat-compliance-check ~/.qoderwork/skills/

# 2. 首次使用词库会自动从 GitHub 下载（约 30-60 秒）
# 也可手动初始化：
python3 ~/.qoderwork/skills/wechat-compliance-check/scripts/update_dicts.py --init
```

## 使用方式

在 QoderWork 中直接对 agent 说：
- "帮我检测这篇文章的合规风险"
- "公众号文章审核"
- "这篇文章能发吗"
- "检查红线"

支持的输入方式：
- 直接粘贴文本
- 提供 Markdown / .docx / .txt 文件路径
- 提供 URL

## 词库来源

| 来源 | 许可 | 说明 |
|------|------|------|
| [houbb/sensitive-word-data](https://github.com/houbb/sensitive-word-data) | Apache 2.0 | 6W+ 敏感词 |
| [konsheng/Sensitive-lexicon](https://github.com/konsheng/Sensitive-lexicon) | MIT | 17+ 分类词库 |
| [521xueweihan/advertising_law_checker](https://github.com/521xueweihan/advertising_law_checker) | MIT | 广告法极限词 |

## 词库管理

```bash
# 增量更新词库（建议每月一次）
python3 scripts/update_dicts.py --update-dicts

# 更新运营规范（建议每季度一次）
python3 scripts/update_dicts.py --update-guidelines

# 查看词库状态
python3 scripts/update_dicts.py --status
```

### 自定义词库

编辑以下文件添加自定义内容：
- `dicts/custom.txt` — 自定义检测词（每行一个）
- `dicts/whitelist.txt` — 白名单词（每行一个，匹配时跳过）

格式：每行一个词，支持 `词 #注释` 格式。

## 技术特性

- **DFA 算法**：高性能关键词匹配
- **防绕过检测**：全半角转换、繁简转换、特殊字符过滤、拼音首字母识别
- **纯 Python 实现**：无额外 pip 依赖
- **完全本地运行**：不上传文章内容到任何外部服务

## 局限性

- 无法保证 100% 通过微信审核，检测结果仅供参考
- 图片内容检测仅基于用户文字描述
- P2/P3 级别需人工判断

---

---

<a id="english"></a>

# wechat-compliance-check

**[中文](#wechat-compliance-check)** · English

Pre-publish compliance risk detection tool for WeChat Official Account articles.

## Overview

Uses a dual-layer detection architecture to scan articles for compliance risks:

1. **Dictionary Scanning Layer**: DFA algorithm + local dictionaries for high-performance keyword matching across 10 risk categories including political sensitivity, legal violations, pornography, violence, advertising law violations, and fraudulent marketing
2. **Rule Review Layer**: Checks against WeChat's official "Recommended Operating Standards for WeChat Official Accounts and Service Accounts" — 9 red lines with official clause citations and case references, outputting a structured compliance report

### Risk Categories

| Priority | Category | Description |
|----------|----------|-------------|
| P0-Fatal | Political Sensitivity | Leaders, sensitive events, separatist speech, etc. |
| P0-Fatal | Legal Violations | Illegal activities, organized crime, illegal items |
| P1-Severe | Pornography & Vulgarity | Pornographic, soft-porn, vulgar borderline content |
| P1-Severe | Violence & Gore | Violence, terrorism, gory descriptions |
| P1-Severe | Drug Related | Drug names, manufacturing methods, trafficking info |
| P1-Severe | Gambling Related | Gambling platforms, betting promotion |
| P2-Warning | Advertising Law Violations | Superlative terms, false claims, medical terms |
| P2-Warning | Fraudulent Marketing | Induced sharing, clickbait, false promises |
| P3-Info | Low Quality Content | AI-templated content, keyword stuffing |
| P3-Info | Short Video Violations | Douyin/short-video platform universal banned terms |

### Built-in Rule Documents

| File | Purpose |
|------|---------|
| `reference/platform-rules.md` | Full text of 9 red-line official standards |
| `reference/platform-rules-basic.md` | Basic operating standards supplementary clauses |
| `reference/platform-cases.md` | Low-creativity violation official cases |
| `reference/content-rules.md` | Body content compliance rules |
| `reference/title-rules.md` | Title compliance rules |
| `reference/image-rules.md` | Cover image and inline image compliance rules |
| `reference/marketing-rules.md` | Marketing expression and advertising law compliance reference |

## Installation

### Prerequisites

- [QoderWork](https://qoder.com) desktop client
- Python 3.8+

### Steps

```bash
# 1. Copy to QoderWork skills directory
cp -r wechat-compliance-check ~/.qoderwork/skills/

# 2. Dictionaries will be auto-downloaded from GitHub on first use (~30-60s)
# Or initialize manually:
python3 ~/.qoderwork/skills/wechat-compliance-check/scripts/update_dicts.py --init
```

## Usage

Talk to the agent directly in QoderWork:
- "Check this article for compliance risks"
- "WeChat article review"
- "Can I publish this?"

Supported input methods:
- Paste text directly
- Provide Markdown / .docx / .txt file path
- Provide a URL

## Dictionary Sources

| Source | License | Description |
|--------|---------|-------------|
| [houbb/sensitive-word-data](https://github.com/houbb/sensitive-word-data) | Apache 2.0 | 60K+ sensitive words |
| [konsheng/Sensitive-lexicon](https://github.com/konsheng/Sensitive-lexicon) | MIT | 17+ category dictionaries |
| [521xueweihan/advertising_law_checker](https://github.com/521xueweihan/advertising_law_checker) | MIT | Advertising law extreme terms |

## Dictionary Management

```bash
# Incremental dictionary update (recommended monthly)
python3 scripts/update_dicts.py --update-dicts

# Update operating standards (recommended quarterly)
python3 scripts/update_dicts.py --update-guidelines

# Check dictionary status
python3 scripts/update_dicts.py --status
```

### Custom Dictionaries

Edit the following files to add custom content:
- `dicts/custom.txt` — Custom detection words (one per line)
- `dicts/whitelist.txt` — Whitelist words (one per line, skipped on match)

Format: one word per line, supports `word #comment` format.

## Technical Features

- **DFA Algorithm**: High-performance keyword matching
- **Anti-bypass Detection**: Full/half-width conversion, traditional/simplified Chinese conversion, special character filtering, pinyin initial recognition
- **Pure Python**: No extra pip dependencies
- **Fully Local**: No article content uploaded to any external service

## Limitations

- Cannot guarantee 100% WeChat review approval — detection results are for reference only
- Image content detection is based on user text descriptions only
- P2/P3 level items require human judgment

---

[Apache License 2.0](../LICENSE)
