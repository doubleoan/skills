# QoderWork Skills

[中文](README.md) · **English**

#### A Collection of Practical AI Agent Skills

Each Skill is a structured instruction set that can be directly loaded by AI agents, following the open Agent Skills standard.

---

## Table of Contents

| Name | Summary | Docs |
|------|---------|------|
| wechat-compliance-check | Pre-publish compliance risk detection for WeChat Official Account articles — DFA dictionary scanning + 9 red-line rule reviews covering 10 risk categories | [docs/wechat-compliance-check.md](docs/wechat-compliance-check.md) |
| wechat-compliance-check-no-wordlib | Pre-publish compliance risk detection for WeChat articles — pure rule review, no dictionary required, ready to use | [docs/wechat-compliance-check-no-wordlib.md](docs/wechat-compliance-check-no-wordlib.md) |

---

## Installation

In any Skill-compatible agent such as Claude Code, Codex, or Qoder, just say:

Install this skill: https://github.com/doubleoan/skills/wechat-compliance-check

# Or install the no-dictionary version (no Python required)
Install this skill: https://github.com/doubleoan/skills/wechat-compliance-check-no-wordlib

```bash
# Clone the repository
git clone https://github.com/doubleoan/skills.git

# Copy the skill to your skills directory
cp -r skills/wechat-compliance-check ~/.cluade/skills/
cp -r skills/wechat-compliance-check ~/.codex/skills/
cp -r skills/wechat-compliance-check ~/.qoderwork/skills/

# Or install the no-dictionary version (no Python, ready to use)
cp -r skills/wechat-compliance-check-no-wordlib ~/.qoderwork/skills/
```

---

## Skills

### wechat-compliance-check

> "Run a check before publishing — peace of mind."

A pre-publish compliance risk detection tool for WeChat Official Account articles. Built on a dual-layer detection architecture:

- **Dictionary Scanning Layer**: DFA algorithm + local dictionaries covering 10 risk categories including political sensitivity, legal violations, pornography & vulgarity, violence & gore, advertising law violations, and fraudulent marketing
- **Rule Review Layer**: Checks against WeChat's official *Recommended Operating Standards for WeChat Official Accounts and Service Accounts* — 9 red lines reviewed clause by clause, with official text citations and case references, producing a structured compliance report

**How to trigger:**
- "Check this article for compliance risks"
- "WeChat article review"
- "Can I publish this?"
- "Check the red lines"

**Features:**
- Fully local execution — no article content is ever uploaded to any external service
- Pure Python implementation — no extra pip dependencies required
- Supports online dictionary updates and custom extensions
- Anti-bypass detection: full/half-width normalization, traditional/simplified Chinese conversion, special character filtering, and pinyin initial recognition

→ [Full Documentation](docs/wechat-compliance-check.md)

---

### wechat-compliance-check-no-wordlib (No Dictionary Version)

> "Run a check before publishing — lightweight, zero dependencies, ready to use."

A pre-publish compliance risk detection tool for WeChat Official Account articles (no dictionary version). Built on a pure rule-based review architecture:

- **Six-Module Review**: Title, cover image, inline images, body content, marketing expressions, and comprehensive assessment — covering the full article lifecycle
- **Red-Line Check**: Checks against WeChat's official *Recommended Operating Standards* — 9 red lines reviewed clause by clause, with official citations and case references

**How to trigger:**
- "Check this article for compliance risks"
- "WeChat article review"
- "Can I publish this?"
- "Check the red lines"

**Features:**
- No Python, no dictionary download — ready to use out of the box
- Fully local execution — no article content uploaded to any external service
- Ideal for lightweight, offline environments
- Supports title-only, image-only, and quick sensitive-word detection modes

**Difference from the full version:** No DFA dictionary scanning layer. Sensitive word detection relies on the Agent's comprehension of reference documents. For precise keyword matching, use [wechat-compliance-check](wechat-compliance-check/).

→ [Full Documentation](docs/wechat-compliance-check-no-wordlib.md)

---

## About

I'm Xi (曦), passionate about exploring new technology, AI, and productivity tools. Let's work smarter and live better together.

All the open-sourced skills here are ones I use daily in my own workflow. If you find them helpful, a star would mean a lot. If you have ideas or feedback, feel free to reach out — follow my WeChat Official Account: **IT信息在线**, or add me on WeChat: **wxid_pmt5svoowseu12**.

## License

[Apache License 2.0](LICENSE)
