# QoderWork Skills

[中文](README.md) · **English**

#### A Collection of Practical AI Agent Skills

Each Skill is a structured instruction set that can be directly loaded by AI agents, following the open Agent Skills standard.

---

## Table of Contents

| Name | Summary | Docs |
|------|---------|------|
| wechat-compliance-check | Pre-publish compliance risk detection for WeChat Official Account articles — DFA dictionary scanning + 9 red-line rule reviews covering 10 risk categories | [docs/wechat-compliance-check.md](docs/wechat-compliance-check.md) |

---

## Installation

In any Skill-compatible agent such as Claude Code, Codex, or Qoder, just say:

Install this skill: https://github.com/doubleoan/skills/wechat-compliance-check

```bash
# Clone the repository
git clone https://github.com/doubleoan/skills.git

# Copy the skill to your skills directory
cp -r skills/wechat-compliance-check ~/.cluade/skills/
cp -r skills/wechat-compliance-check ~/.qoderwork/skills/
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

## About

I'm Xi (曦), passionate about exploring new technology, AI, and productivity tools. Let's work smarter and live better together.

All the open-sourced skills here are ones I use daily in my own workflow. If you find them helpful, a star would mean a lot. If you have ideas or feedback, feel free to reach out — follow my WeChat Official Account: **IT信息在线**, or add me on WeChat: **wxid_pmt5svoowseu12**.

## License

[Apache License 2.0](LICENSE)
