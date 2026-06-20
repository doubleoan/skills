#!/usr/bin/env python3
"""
微信公众号文章合规检测脚本
基于 DFA 算法的本地敏感词检测引擎

用法:
  python3 detect.py --text "文章内容" --dicts /path/to/dicts/
  python3 detect.py --file article.txt --dicts /path/to/dicts/
  python3 detect.py --text "文章内容" --dicts /path/to/dicts/ --json
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ─── 类别配置 ───────────────────────────────────────────────

CATEGORY_CONFIG = {
    "political": {
        "label": "政治敏感",
        "priority": "P0-致命",
        "level": 0,
        "file": "political.txt",
        "suggestion_template": "涉及政治敏感内容，建议删除相关表述",
    },
    "legal": {
        "label": "法律法规",
        "priority": "P0-致命",
        "level": 0,
        "file": "legal.txt",
        "suggestion_template": "涉及法律法规风险，建议删除或咨询法律顾问",
    },
    "porn": {
        "label": "色情低俗",
        "priority": "P1-严重",
        "level": 1,
        "file": "porn.txt",
        "suggestion_template": "涉及色情低俗内容，建议替换为合规表达",
    },
    "violence": {
        "label": "暴恐血腥",
        "priority": "P1-严重",
        "level": 1,
        "file": "violence.txt",
        "suggestion_template": "涉及暴力恐怖内容，建议删除相关描述",
    },
    "drugs": {
        "label": "毒品相关",
        "priority": "P1-严重",
        "level": 1,
        "file": "drugs.txt",
        "suggestion_template": "涉及毒品相关内容，建议删除",
    },
    "gambling": {
        "label": "赌博相关",
        "priority": "P1-严重",
        "level": 1,
        "file": "gambling.txt",
        "suggestion_template": "涉及赌博相关内容，建议删除",
    },
    "advertising": {
        "label": "广告法违禁",
        "priority": "P2-警告",
        "level": 2,
        "file": "advertising.txt",
        "suggestion_template": "广告法极限用语，建议替换为合规表达",
    },
    "fraud": {
        "label": "虚假营销",
        "priority": "P2-警告",
        "level": 2,
        "file": "fraud.txt",
        "suggestion_template": "可能构成虚假宣传或诱导，建议修改表述",
    },
    "lowquality": {
        "label": "低质灌水",
        "priority": "P3-提示",
        "level": 3,
        "file": "lowquality.txt",
        "suggestion_template": "可能被判定为低质内容，建议优化",
    },
    "shortvideo": {
        "label": "短视频违禁",
        "priority": "P3-提示",
        "level": 3,
        "file": "shortvideo.txt",
        "suggestion_template": "短视频平台违禁词，如需同步发布建议修改",
    },
}

# 广告法常见替换建议
ADVERTISING_REPLACEMENTS = {
    "最": "非常/十分/极为",
    "最好": "优质/出色/优秀",
    "最佳": "优质/出色/优秀",
    "最优": "优质/出色",
    "最强": "强劲/出色/优秀",
    "最大": "大型/大规模",
    "最小": "小型/精巧",
    "第一": "领先/前列/优质",
    "首选": "推荐/优选",
    "唯一": "独特/少有",
    "独家": "特色/专属",
    "顶级": "高端/优质",
    "极致": "出色/优秀",
    "绝对": "相当/非常",
    "万能": "多功能/实用",
    "100%": "高度/充分",
    "国家级": "高级/专业级",
    "世界级": "国际水准/高水准",
    "全网最低": "优惠价格/特惠",
    "史上最": "非常/极为",
    "全球首发": "新品发布",
    "永久": "长期/持久",
    "无敌": "出色/强劲",
    "销量第一": "热销/畅销",
    "冠军": "领先/佼佼者",
    "之王": "佳品/精品",
    "NO.1": "领先/优质",
    "TOP1": "领先/优质",
}


# ─── DFA 敏感词树 ──────────────────────────────────────────

class DFANode:
    """DFA 树节点"""
    __slots__ = ("children", "is_end", "category", "original_word")

    def __init__(self):
        self.children: Dict[str, "DFANode"] = {}
        self.is_end: bool = False
        self.category: Optional[str] = None
        self.original_word: Optional[str] = None


class DFAEngine:
    """DFA 敏感词检测引擎"""

    def __init__(self):
        self.root = DFANode()
        self.word_count = 0

    def add_word(self, word: str, category: str):
        """添加敏感词到 DFA 树"""
        normalized = self._normalize(word)
        if not normalized:
            return
        node = self.root
        for char in normalized:
            if char not in node.children:
                node.children[char] = DFANode()
            node = node.children[char]
        node.is_end = True
        node.category = category
        node.original_word = word.strip()
        self.word_count += 1

    def search(self, text: str) -> List[Dict]:
        """在文本中搜索敏感词，返回所有匹配结果"""
        normalized_text = self._normalize(text)
        results = []
        text_len = len(normalized_text)

        for i in range(text_len):
            node = self.root
            j = i
            while j < text_len and j - i < 50:  # 限制最大匹配长度
                char = normalized_text[j]
                if char in node.children:
                    node = node.children[char]
                    if node.is_end:
                        # 找到匹配，映射回原文位置
                        original_match = text[i : j + 1]
                        results.append({
                            "word": node.original_word,
                            "matched_text": original_match,
                            "category": node.category,
                            "position": i,
                            "end_position": j + 1,
                        })
                    j += 1
                else:
                    break

        # 去重：如果短词被长词完全包含，保留长词
        results = self._deduplicate(results)
        return results

    def _normalize(self, text: str) -> str:
        """文本归一化：全角转半角、大写转小写、繁体转简体、移除干扰字符"""
        # 全角转半角
        result = self._fullwidth_to_halfwidth(text)
        # 大写转小写
        result = result.lower()
        # 繁体转简体（基本转换）
        result = self._traditional_to_simplified(result)
        return result

    def _normalize_for_search(self, text: str) -> str:
        """搜索用归一化（移除干扰字符）"""
        result = self._normalize(text)
        # 移除常见干扰字符
        result = re.sub(r"[*\.\-_~\s\|\\\/`!@#$%^&()\[\]{}<>?,;:'\"，。！？、；：""''【】《》]", "", result)
        return result

    @staticmethod
    def _fullwidth_to_halfwidth(text: str) -> str:
        """全角字符转半角"""
        result = []
        for char in text:
            code = ord(char)
            if 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            elif code == 0x3000:
                result.append(" ")
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def _traditional_to_simplified(text: str) -> str:
        """基本繁体转简体（常用字映射）"""
        # 常见繁简对照（政治敏感词相关的高频繁体字）
        trad_map = {
            "國": "国", "黨": "党", "導": "导", "領": "领", "會": "会",
            "書": "书", "記": "记", "總": "总", "統": "统", "獨": "独",
            "義": "义", "運": "运", "動": "动", "從": "从", "變": "变",
            "點": "点", "開": "开", "關": "关", "門": "门", "問": "问",
            "電": "电", "話": "话", "機": "机", "車": "车", "學": "学",
            "術": "术", "專": "专", "業": "业", "產": "产", "權": "权",
            "軍": "军", "隊": "队", "戰": "战", "鬥": "斗", "衛": "卫",
            "傳": "传", "號": "号", "團": "团", "組": "组", "織": "织",
            "機": "机", "構": "构", "體": "体", "製": "制", "設": "设",
            "備": "备", "認": "认", "識": "识", "議": "议", "論": "论",
            "證": "证", "據": "据", "調": "调", "査": "查", "報": "报",
            "導": "导", "彈": "弹", "藥": "药", "賭": "赌", "賻": "博",
            "黃": "黄", "賭": "赌", "毒": "毒", "槍": "枪", "砲": "炮",
            "彈": "弹", "殺": "杀", "傷": "伤", "殘": "残", "廢": "废",
            "廣": "广", "東": "东", "灣": "湾", "區": "区",
        }
        return text.translate(str.maketrans(trad_map))

    @staticmethod
    def _deduplicate(results: List[Dict]) -> List[Dict]:
        """去重：保留最长匹配"""
        if not results:
            return results
        # 按长度降序排序
        results.sort(key=lambda x: len(x["matched_text"]), reverse=True)
        kept = []
        occupied: Set[Tuple[int, int]] = set()
        for r in results:
            span = set(range(r["position"], r["end_position"]))
            overlap = False
            for start, end in occupied:
                if r["position"] < end and r["end_position"] > start:
                    overlap = True
                    break
            if not overlap:
                kept.append(r)
                occupied.add((r["position"], r["end_position"]))
        # 按位置排序
        kept.sort(key=lambda x: x["position"])
        return kept


# ─── 检测主逻辑 ──────────────────────────────────────────────

class ComplianceChecker:
    """合规检测主类"""

    def __init__(self, dicts_dir: str):
        self.dicts_dir = Path(dicts_dir)
        self.engine = DFAEngine()
        self.whitelist: Set[str] = set()
        self._load_dicts()

    def _load_dicts(self):
        """加载所有词库"""
        # 先加载白名单
        whitelist_path = self.dicts_dir / "whitelist.txt"
        if whitelist_path.exists():
            for line in whitelist_path.read_text(encoding="utf-8").splitlines():
                word = line.split("#")[0].strip()
                if word:
                    self.whitelist.add(word.lower())

        # 加载各类别词库
        for cat_key, cat_config in CATEGORY_CONFIG.items():
            dict_path = self.dicts_dir / cat_config["file"]
            if not dict_path.exists():
                continue
            count = 0
            for line in dict_path.read_text(encoding="utf-8").splitlines():
                word = line.split("#")[0].strip()
                if word and word.lower() not in self.whitelist:
                    self.engine.add_word(word, cat_key)
                    count += 1

        # 加载自定义词库
        custom_path = self.dicts_dir / "custom.txt"
        if custom_path.exists():
            count = 0
            for line in custom_path.read_text(encoding="utf-8").splitlines():
                word = line.split("#")[0].strip()
                if word and word.lower() not in self.whitelist:
                    self.engine.add_word(word, "custom")
                    count += 1

    def check(self, text: str) -> Dict:
        """执行合规检测"""
        if not text or not text.strip():
            return self._empty_result()

        # DFA 扫描
        raw_hits = self.engine.search(text)

        # 过滤白名单
        hits = [h for h in raw_hits if h["word"].lower() not in self.whitelist]

        # 构建详情
        details = []
        for hit in hits:
            cat_key = hit["category"]
            cat_config = CATEGORY_CONFIG.get(cat_key, {
                "label": "自定义",
                "priority": "P2-警告",
                "level": 2,
                "suggestion_template": "自定义检测词命中，请检查",
            })

            # 提取上下文（前后各 20 字）
            start = max(0, hit["position"] - 20)
            end = min(len(text), hit["end_position"] + 20)
            context = text[start:end]
            # 标记命中词
            marker_start = hit["position"] - start
            marker_end = hit["end_position"] - start
            context_marked = (
                context[:marker_start]
                + "【" + context[marker_start:marker_end] + "】"
                + context[marker_end:]
            )

            # 生成建议
            suggestion = cat_config["suggestion_template"]
            if cat_key == "advertising":
                word_lower = hit["word"].lower()
                for kw, replacement in ADVERTISING_REPLACEMENTS.items():
                    if kw in hit["matched_text"]:
                        suggestion = f"广告法极限用语，建议替换为「{replacement}」"
                        break

            details.append({
                "category": cat_config["label"],
                "category_key": cat_key,
                "priority": cat_config["priority"],
                "level": cat_config["level"],
                "word": hit["word"],
                "matched_text": hit["matched_text"],
                "position": hit["position"],
                "context": context_marked,
                "suggestion": suggestion,
            })

        # 按优先级排序
        details.sort(key=lambda x: (x["level"], x["position"]))

        # 统计
        p0 = sum(1 for d in details if d["level"] == 0)
        p1 = sum(1 for d in details if d["level"] == 1)
        p2 = sum(1 for d in details if d["level"] == 2)
        p3 = sum(1 for d in details if d["level"] == 3)

        # 确定风险等级
        if p0 > 0:
            risk_level = "critical"
            passed = False
        elif p1 > 0:
            risk_level = "high"
            passed = False
        elif p2 > 3:
            risk_level = "medium"
            passed = True  # 广告法词汇少量可通过
        elif p2 > 0:
            risk_level = "low"
            passed = True
        else:
            risk_level = "safe"
            passed = True

        # 生成标注预览
        preview = self._generate_preview(text, hits)

        return {
            "summary": {
                "total_hits": len(details),
                "risk_level": risk_level,
                "categories_hit": len(set(d["category_key"] for d in details)),
                "p0_fatal": p0,
                "p1_severe": p1,
                "p2_warning": p2,
                "p3_info": p3,
                "pass": passed,
                "word_count_loaded": self.engine.word_count,
            },
            "details": details,
            "article_preview": preview,
        }

    def _generate_preview(self, text: str, hits: List[Dict]) -> str:
        """生成带标注的文章预览（截取前 500 字）"""
        preview_text = text[:500]
        # 在预览中标注命中词
        offset_map = {}
        for hit in hits:
            if hit["position"] < 500:
                offset_map[hit["position"]] = hit

        if not offset_map:
            return preview_text + ("..." if len(text) > 500 else "")

        result = []
        last_end = 0
        for pos in sorted(offset_map.keys()):
            hit = offset_map[pos]
            end = hit["end_position"]
            if end > 500:
                end = 500
            if pos >= last_end:
                result.append(preview_text[last_end:pos])
                result.append(f"⚠️【{preview_text[pos:end]}】")
                last_end = end
        result.append(preview_text[last_end:])
        if len(text) > 500:
            result.append("...")
        return "".join(result)

    @staticmethod
    def _empty_result() -> Dict:
        return {
            "summary": {
                "total_hits": 0,
                "risk_level": "safe",
                "categories_hit": 0,
                "p0_fatal": 0,
                "p1_severe": 0,
                "p2_warning": 0,
                "p3_info": 0,
                "pass": True,
                "word_count_loaded": 0,
            },
            "details": [],
            "article_preview": "",
        }


# ─── CLI 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="微信公众号文章合规检测")
    parser.add_argument("--text", type=str, help="要检测的文章文本")
    parser.add_argument("--file", type=str, help="要检测的文章文件路径")
    parser.add_argument("--dicts", type=str, required=True, help="词库目录路径")
    parser.add_argument("--json", action="store_true", help="输出纯 JSON（便于程序解析）")
    parser.add_argument("--preview-length", type=int, default=500, help="预览截取长度")

    args = parser.parse_args()

    # 获取文本
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(json.dumps({"error": f"文件不存在: {args.file}"}, ensure_ascii=False))
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8")
    else:
        # 从 stdin 读取
        text = sys.stdin.read()

    if not text.strip():
        print(json.dumps({"error": "文本内容为空"}, ensure_ascii=False))
        sys.exit(1)

    # 检查词库是否已初始化，未初始化则自动下载
    dicts_path = Path(args.dicts)
    essential_files = ["political.txt", "porn.txt", "legal.txt"]
    has_dicts = any(
        (dicts_path / f).exists() and (dicts_path / f).stat().st_size > 10
        for f in essential_files
    )

    if not has_dicts:
        print("⚠️  词库未初始化，正在从远程仓库下载全量词库...", file=sys.stderr)
        print("   （首次使用需要联网，后续均为本地检测）", file=sys.stderr)
        print(file=sys.stderr)
        # 调用同目录下的 update_dicts.py --init
        import subprocess
        update_script = Path(__file__).parent / "update_dicts.py"
        ret = subprocess.run(
            [sys.executable, str(update_script), "--init"],
            cwd=str(Path(__file__).parent),
        )
        if ret.returncode != 0:
            print(json.dumps({"error": "词库初始化失败，请检查网络连接后重试"}, ensure_ascii=False))
            sys.exit(1)
        print(file=sys.stderr)
        print("✅ 词库初始化完成，开始检测...", file=sys.stderr)
        print(file=sys.stderr)

    # 执行检测
    checker = ComplianceChecker(args.dicts)
    result = checker.check(text)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 人类可读输出
        print_report(result)


def print_report(result: Dict):
    """打印人类可读的报告"""
    summary = result["summary"]
    details = result["details"]

    # 风险等级 emoji 映射
    level_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
        "safe": "✅",
    }

    level_labels = {
        "critical": "严重（存在致命风险）",
        "high": "高（存在严重风险）",
        "medium": "中（存在多项警告）",
        "low": "低（少量警告）",
        "safe": "安全",
    }

    icon = level_icons.get(summary["risk_level"], "❓")
    label = level_labels.get(summary["risk_level"], "未知")
    pass_mark = "✅ 通过" if summary["pass"] else "❌ 不通过"

    print()
    print("═" * 50)
    print("  微信公众号文章合规检测报告")
    print("═" * 50)
    print()
    print(f"总体评估：{pass_mark}（风险等级：{label}）{icon}")
    print(f"命中词数：{summary['total_hits']} 个 | 涉及类别：{summary['categories_hit']} 个")
    print(f"词库加载：{summary['word_count_loaded']} 条")
    print()

    if not details:
        print("🎉 未发现合规风险，文章可以安全发布。")
        print()
        return

    # 按优先级分组输出
    priority_groups = [
        (0, "P0-致命", "必须修改", "━" * 40),
        (1, "P1-严重", "强烈建议修改", "━" * 40),
        (2, "P2-警告", "建议检查", "━" * 40),
        (3, "P3-提示", "可选优化", "━" * 40),
    ]

    for level, priority_label, action, separator in priority_groups:
        group = [d for d in details if d["level"] == level]
        if not group:
            continue
        print(f"━━━━ {priority_label} ━━━ {action} ━━━━")
        print()
        for item in group:
            print(f"  [{item['category']}] 第 {item['position']} 字")
            print(f"    命中词：「{item['word']}」")
            if item.get("matched_text") and item["matched_text"] != item["word"]:
                print(f"    匹配到：「{item['matched_text']}」")
            print(f"    上下文：{item['context']}")
            print(f"    建议：{item['suggestion']}")
            print()

    # 预览
    if result.get("article_preview"):
        print("━━━━ 文章预览（标注风险词）━━━━")
        print()
        print(result["article_preview"][:1000])
        print()

    print("═" * 50)
    print()


if __name__ == "__main__":
    main()
