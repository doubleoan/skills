# Skills

**中文** · [English](README.en.md)

#### 实用 AI Agent Skills 合集

每个 Skill 都遵循 Agent Skills 开放标准。Claude Code、Codex、Qoder、OpenCode、OpenClaw 即装即用。

---

## 目录

| 名字 | 一句话 | 详细文档 |
|------|--------|----------|
| wechat-compliance-check（公众号合规检测） | 微信公众号文章发布前合规风险检测，DFA 词库扫描 + 9 条红线逐条审查，覆盖 10 大风险类别 | [docs/wechat-compliance-check.md](docs/wechat-compliance-check.md) |
| wechat-compliance-check-no-wordlib（公众号合规检测·无词库版） | 微信公众号文章发布前合规风险检测，纯规则审查，无需词库即装即用 | [docs/wechat-compliance-check-no-wordlib.md](docs/wechat-compliance-check-no-wordlib.md) |

---

## 安装方式

在 Claude Code、Codex、Qoder 等支持 Skill 的 Agent 里，直接说：

帮我安装这个 skill：https://github.com/doubleoan/skills/wechat-compliance-check

# 安装无词库版
帮我安装这个 skill：https://github.com/doubleoan/skills/wechat-compliance-check-no-wordlib

```bash
# 克隆仓库
git clone https://github.com/doubleoan/skills.git

# 复制 skill 到 对应 skills 目录
cp -r skills/wechat-compliance-check ~/.cluade/skills/
cp -r skills/wechat-compliance-check ~/.codex/skills/
cp -r skills/wechat-compliance-check ~/.qoderwork/skills/

# 或安装无词库版（无需 Python，即装即用）
cp -r skills/wechat-compliance-check-no-wordlib ~/.cluade/skills/
cp -r skills/wechat-compliance-check-no-wordlib ~/.codex/skills/
cp -r skills/wechat-compliance-check-no-wordlib ~/.qoderwork/skills/

```

---

## Skills

### wechat-compliance-check（公众号合规检测）

> "发公众号之前跑一遍，心里踏实。"

微信公众号文章发布前的合规风险检测工具。采用双层检测架构：

- **词库扫描层**：基于 DFA 算法 + 本地词库，覆盖政治敏感、法律法规、色情低俗、暴恐血腥、广告法违禁词、虚假营销等 10 大风险类别
- **规则审查层**：对照微信官方《微信公众号和服务号推荐运营规范》9 条红线逐条检查，引用官方原文条款和案例，输出结构化合规报告

**怎么触发：**
- "帮我检测这篇文章的合规风险"
- "公众号文章审核"
- "这篇文章能发吗"
- "检查红线"

**特性：**
- 完全本地运行，不上传文章内容到任何外部服务
- 纯 Python 实现，无额外 pip 依赖
- 支持词库在线更新和自定义扩展
- 防绕过检测：全半角转换、繁简转换、特殊字符过滤、拼音首字母识别

→ [详细文档](docs/wechat-compliance-check.md)

---

### wechat-compliance-check-no-wordlib（公众号合规检测·无词库版）

> "发公众号之前跑一遍，轻量无依赖，即装即用。"

微信公众号文章发布前的合规风险检测工具（无词库版）。采用纯规则审查架构：

- **六大模块逐项审查**：标题、封面图、正文配图、正文内容、营销表达、综合评估，覆盖文章全生命周期
- **红线逐条对照**：对照微信官方《微信公众号和服务号推荐运营规范》9 条红线逐条检查，引用官方原文条款和案例

**怎么触发：**
- "帮我检测这篇文章的合规风险"
- "公众号文章审核"
- "这篇文章能发吗"
- "检查红线"

**特性：**
- 无需 Python，无需下载词库，即装即用
- 完全本地运行，不上传文章内容到任何外部服务
- 适合轻量级、无网络环境的场景
- 支持标题专项、配图专项、快速敏感词等多种检测模式

**与有词库版本的区别：** 无 DFA 词库扫描层，敏感词检测依赖 Agent 对参考文档中违禁词库的理解和比对能力。如需精确关键词匹配，请使用 [wechat-compliance-check](wechat-compliance-check/)。

→ [详细文档](docs/wechat-compliance-check-no-wordlib.md)

---

## 关于

我是曦，热爱研究新科技，AI人工智能和生产力工具。期待和你一起聪明工作，好好生活。

开源出来的 skill 都是我自己日常一直在用的，如果觉得对你有帮助，给个就star就行。

如果有想法和建议欢迎找我交流，可以关注我公众号：羲说科技
<img width="300" height="300" alt="IMG_6192" src="https://github.com/user-attachments/assets/093eeed2-f0e0-431d-8acf-adc5a0115e18" />

或者加我微信：wxid_pmt5svoowseu12。

## 许可证

[Apache License 2.0](LICENSE)
