#!/usr/bin/env python3
"""
微信公众号合规检测 - 词库与规则管理

功能：
1. 首次使用时从远程仓库全量下载词库到本地（--init）
2. 增量更新词库（--update-dicts）
3. 更新微信官方运营规范（--update-guidelines）
4. 查看词库状态（--status）
5. 判断是否已初始化（--check-init）

词库来源：
- houbb/sensitive-word-data — 6W+ 敏感词，按分类标签归入各词库
- konsheng/Sensitive-lexicon — 17+ 分类词库，政治/色情/暴恐/广告等
- 521xueweihan/advertising_law_checker — 广告法极限词
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, Set


# ─── 路径配置 ──────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
DICTS_DIR = SKILL_DIR / "dicts"
REFERENCE_DIR = SKILL_DIR / "reference"
META_FILE = DICTS_DIR / "meta.json"


# ─── 词库来源配置 ──────────────────────────────────────────

DICT_SOURCES = {
    "sensitive_word_data": {
        "name": "houbb/sensitive-word-data",
        "license": "Apache 2.0",
        "base_url": "https://raw.githubusercontent.com/houbb/sensitive-word-data/master/src/main/resources",
        "files": {
            "sensitive_word_dict.txt": "主词库（6W+词条）",
            "sensitive_word_tags.txt": "标签映射（词 → 分类编码）",
        },
        "tag_mapping": {
            "0": "political",  # 政治
            "1": "drugs",      # 毒品
            "2": "porn",       # 色情
            "3": "gambling",   # 赌博
            "4": "legal",      # 违法犯罪
        },
    },
    "sensitive_lexicon": {
        "name": "konsheng/Sensitive-lexicon",
        "license": "MIT",
        "base_url": "https://raw.githubusercontent.com/konsheng/Sensitive-lexicon/main/Vocabulary",
        "files": {
            "政治类型.txt": "political",
            "色情类型.txt": "porn",
            "色情词库.txt": "porn",
            "广告类型.txt": "advertising",
            "暴恐词库.txt": "violence",
            "贪腐词库.txt": "political",
            "民生词库.txt": "legal",
            "涉枪涉爆.txt": "violence",
            "反动车库.txt": "political",
            "补充词库.txt": "fraud",
        },
    },
    "advertising_law_checker": {
        "name": "521xueweihan/advertising_law_checker",
        "license": "MIT",
        "base_url": "https://raw.githubusercontent.com/521xueweihan/advertising_law_checker/gh-pages/static/js",
        "files": {
            "initStore.js": "广告法极限词（JS 解析）",
        },
    },
}



# ─── 工具函数 ──────────────────────────────────────────────

def download_file(url: str, timeout: int = 30) -> str:
    """下载文件内容"""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "WeChatComplianceChecker/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        print(f"  ⚠️  下载失败: {url} -> {e}")
        return ""


def load_meta() -> dict:
    """加载元数据"""
    if META_FILE.exists():
        return json.loads(META_FILE.read_text(encoding="utf-8"))
    return {
        "initialized": False,
        "last_dict_update": None,
        "last_guideline_update": None,
        "dict_versions": {},
        "word_counts": {},
    }


def save_meta(meta: dict):
    """保存元数据"""
    DICTS_DIR.mkdir(parents=True, exist_ok=True)
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def count_words_in_file(filepath: Path) -> int:
    """统计词库文件中的有效词条数"""
    if not filepath.exists():
        return 0
    count = 0
    for line in filepath.read_text(encoding="utf-8").splitlines():
        word = line.split("#")[0].strip()
        if word:
            count += 1
    return count


def is_initialized() -> bool:
    """检查词库是否已初始化"""
    meta = load_meta()
    if meta.get("initialized"):
        return True
    # 也检查文件是否存在
    essential_files = ["political.txt", "porn.txt", "legal.txt"]
    for f in essential_files:
        if (DICTS_DIR / f).exists() and count_words_in_file(DICTS_DIR / f) > 0:
            return True
    return False


# ─── 词库下载与更新 ────────────────────────────────────────

def update_from_sensitive_word_data() -> Dict[str, int]:
    """从 houbb/sensitive-word-data 更新词库"""
    source = DICT_SOURCES["sensitive_word_data"]
    print(f"\n📦 从 {source['name']} 下载词库（{source['license']}）...")

    # 下载标签文件
    tags_url = f"{source['base_url']}/sensitive_word_tags.txt"
    tags_content = download_file(tags_url)

    if not tags_content:
        # 尝试直接下载主词库作为兜底
        print("  标签文件下载失败，尝试主词库...")
        dict_url = f"{source['base_url']}/sensitive_word_dict.txt"
        dict_content = download_file(dict_url)
        if dict_content:
            words = set()
            for line in dict_content.splitlines():
                word = line.strip()
                if word and not word.startswith("#"):
                    words.add(word)
            if words:
                filepath = DICTS_DIR / "legal.txt"
                _append_words(filepath, words, source["name"])
                print(f"  ✅ 无标签版: {len(words)} 条词条归入 legal")
                return {"legal": len(words)}
        print("  ❌ 无法下载，跳过")
        return {}

    # 解析标签映射
    categorized: Dict[str, Set[str]] = {cat: set() for cat in ["political", "drugs", "porn", "gambling", "legal"]}
    uncategorized: Set[str] = set()
    total = 0

    for line in tags_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            uncategorized.add(parts[0])
            continue

        word = parts[0]
        tags = parts[1].split(",")
        total += 1

        matched = False
        for tag in tags:
            tag = tag.strip()
            if tag in source["tag_mapping"]:
                target_cat = source["tag_mapping"][tag]
                categorized[target_cat].add(word)
                matched = True
            elif "政治" in tag or "国家" in tag:
                categorized["political"].add(word)
                matched = True
            elif "毒品" in tag:
                categorized["drugs"].add(word)
                matched = True
            elif "色情" in tag:
                categorized["porn"].add(word)
                matched = True
            elif "赌" in tag:
                categorized["gambling"].add(word)
                matched = True

        if not matched:
            uncategorized.add(word)

    # 未分类归入 legal
    categorized["legal"].update(uncategorized)

    # 写入文件
    result = {}
    for cat, words in categorized.items():
        if not words:
            continue
        filepath = DICTS_DIR / f"{cat}.txt"
        count = _append_words(filepath, words, source["name"])
        if count > 0:
            result[cat] = count
            print(f"  ✅ {cat}: 新增 {count} 条")

    print(f"  📊 共处理 {total} 条标签词条 + {len(uncategorized)} 条未分类")
    return result


def update_from_sensitive_lexicon() -> Dict[str, int]:
    """从 konsheng/Sensitive-lexicon 更新词库"""
    source = DICT_SOURCES["sensitive_lexicon"]
    print(f"\n📦 从 {source['name']} 下载词库（{source['license']}）...")

    result = {}
    for filename, target_cat in source["files"].items():
        url = f"{source['base_url']}/{urllib.request.quote(filename)}"
        content = download_file(url)
        if not content:
            continue

        words = set()
        for line in content.splitlines():
            word = line.strip()
            if word and not word.startswith("#"):
                words.add(word)

        if not words:
            continue

        filepath = DICTS_DIR / f"{target_cat}.txt"
        count = _append_words(filepath, words, f"{source['name']}/{filename}")
        if count > 0:
            result[target_cat] = result.get(target_cat, 0) + count
            print(f"  ✅ {filename} → {target_cat}: 新增 {count} 条")

    return result


def update_advertising_words() -> Dict[str, int]:
    """从 advertising_law_checker 提取广告法极限词"""
    source = DICT_SOURCES["advertising_law_checker"]
    print(f"\n📦 从 {source['name']} 下载广告法词库（{source['license']}）...")

    url = f"{source['base_url']}/initStore.js"
    content = download_file(url)
    if not content:
        print("  ❌ 无法下载，跳过")
        return {}

    match = re.search(r"words:\s*\[([^\]]+)\]", content)
    if not match:
        print("  ❌ 无法解析 JS 文件，跳过")
        return {}

    words = set()
    for m in re.finditer(r"'([^']+)'", match.group(1)):
        word = m.group(1).strip()
        if word:
            words.add(word)

    if not words:
        print("  ⏭️  未提取到词条")
        return {}

    filepath = DICTS_DIR / "advertising.txt"
    count = _append_words(filepath, words, source["name"])
    if count > 0:
        print(f"  ✅ 广告法: 新增 {count} 条")
        return {"advertising": count}
    else:
        print(f"  ⏭️  无新增词条")
        return {}



def _append_words(filepath: Path, words: Set[str], source_name: str) -> int:
    """向词库文件追加新词（去重），返回新增词条数"""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    existing = set()
    if filepath.exists():
        for line in filepath.read_text(encoding="utf-8").splitlines():
            w = line.split("#")[0].strip()
            if w:
                existing.add(w)

    new_words = words - existing
    if not new_words:
        return 0

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n# === 来自 {source_name} ({datetime.now().strftime('%Y-%m-%d')}) ===\n")
        for word in sorted(new_words):
            f.write(f"{word}\n")

    return len(new_words)


# ─── 初始化（首次使用）─────────────────────────────────────

def init_dicts():
    """首次初始化：从远程仓库全量下载词库"""
    print("🚀 首次初始化：下载全量词库...")
    print(f"📂 词库目录: {DICTS_DIR}")
    print()

    DICTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 下载全量词库
    print("=" * 50)
    print(" 第一步：下载敏感词库")
    print("=" * 50)

    stats = {}
    r1 = update_from_sensitive_word_data()
    r2 = update_from_sensitive_lexicon()
    r3 = update_advertising_words()

    for r in [r1, r2, r3]:
        for cat, count in r.items():
            stats[cat] = stats.get(cat, 0) + count

    # 2. 获取微信官方运营规范
    print()
    print("=" * 50)
    print(" 第二步：获取微信官方运营规范")
    print("=" * 50)

    _fetch_official_guidelines()

    # 3. 更新元数据
    meta = load_meta()
    meta["initialized"] = True
    meta["init_date"] = datetime.now().isoformat()
    meta["last_dict_update"] = datetime.now().isoformat()
    meta["last_guideline_update"] = datetime.now().isoformat()
    meta["dict_versions"] = {k: v["name"] for k, v in DICT_SOURCES.items()}

    word_counts = {}
    for f in DICTS_DIR.glob("*.txt"):
        if f.name in ("whitelist.txt", "custom.txt"):
            continue
        word_counts[f.stem] = count_words_in_file(f)
    meta["word_counts"] = word_counts

    save_meta(meta)

    # 汇总
    total_words = sum(word_counts.values())
    print()
    print("═" * 50)
    print("🎉 初始化完成！")
    print(f"   词库总量: {total_words} 条")
    print(f"   词库来源: {len(DICT_SOURCES)} 个")
    print(f"   参考文档: 已内置于 skill 中")
    print()
    print("📊 各类别词条数:")
    for cat, count in sorted(word_counts.items()):
        print(f"   {cat}: {count} 条")
    print("═" * 50)


# ─── 词库增量更新 ──────────────────────────────────────────

def update_all_dicts():
    """增量更新所有词库"""
    if not is_initialized():
        print("⚠️  词库尚未初始化，将执行首次初始化...")
        init_dicts()
        return

    print("🔄 增量更新词库...")
    print(f"📂 词库目录: {DICTS_DIR}")

    stats = {}
    r1 = update_from_sensitive_word_data()
    r2 = update_from_sensitive_lexicon()
    r3 = update_advertising_words()

    for r in [r1, r2, r3]:
        for cat, count in r.items():
            stats[cat] = stats.get(cat, 0) + count

    # 更新元数据
    meta = load_meta()
    meta["last_dict_update"] = datetime.now().isoformat()

    word_counts = {}
    for f in DICTS_DIR.glob("*.txt"):
        if f.name in ("whitelist.txt", "custom.txt"):
            continue
        word_counts[f.stem] = count_words_in_file(f)
    meta["word_counts"] = word_counts
    save_meta(meta)

    total_new = sum(stats.values())
    print(f"\n{'═' * 40}")
    print(f"✅ 词库增量更新完成")
    print(f"   新增词条: {total_new} 条")
    for cat, count in stats.items():
        print(f"   {cat}: +{count}")
    print(f"\n📊 词库总量:")
    total = sum(word_counts.values())
    for cat, count in sorted(word_counts.items()):
        print(f"   {cat}: {count} 条")
    print(f"   ─────────────")
    print(f"   总计: {total} 条")
    print(f"{'═' * 40}")


# ─── 运营规范更新 ──────────────────────────────────────────

def _fetch_official_guidelines():
    """从官方页面获取运营规范（内部方法）"""
    guidelines_url = "https://mp.weixin.qq.com/mp/opshowpage?action=newoplaw"
    print(f"\n  📡 获取官方运营规范: {guidelines_url}")
    content = download_file(guidelines_url, timeout=60)

    if content:
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 100:
            guideline_path = REFERENCE_DIR / "wechat_official_guidelines.txt"
            guideline_path.write_text(text, encoding="utf-8")
            print(f"  ✅ 官方运营规范已保存")
        else:
            print(f"  ⚠️  获取内容过少（可能需登录态），跳过")
    else:
        print(f"  ⚠️  获取失败")


def update_guidelines():
    """更新运营规范参考文档"""
    print("🔄 更新运营规范...")

    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    # 从官方页面更新
    _fetch_official_guidelines()

    # 更新元数据
    meta = load_meta()
    meta["last_guideline_update"] = datetime.now().isoformat()
    save_meta(meta)

    print(f"\n✅ 运营规范更新完成")
    print(f"   提示：运营规范变更频率较低，建议每季度检查一次")


# ─── 状态查看 ──────────────────────────────────────────────

def show_status():
    """显示词库状态"""
    meta = load_meta()

    print("📊 词库状态")
    print("═" * 40)

    # 初始化状态
    if meta.get("initialized"):
        print(f"初始化: ✅ 已完成（{meta.get('init_date', '未知')}）")
    else:
        print(f"初始化: ❌ 未初始化（首次检测时将自动下载）")

    # 更新时间
    if meta.get("last_dict_update"):
        print(f"词库更新: {meta['last_dict_update']}")
    else:
        print("词库更新: 从未更新")

    if meta.get("last_guideline_update"):
        print(f"规范更新: {meta['last_guideline_update']}")
    else:
        print("规范更新: 从未更新")

    # 词库统计
    print(f"\n📁 词库文件 ({DICTS_DIR}):")
    total = 0
    found_any = False
    for f in sorted(DICTS_DIR.glob("*.txt")):
        if f.name in ("whitelist.txt", "custom.txt"):
            continue
        count = count_words_in_file(f)
        if count > 0:
            found_any = True
        total += count
        print(f"  {f.name}: {count} 条")

    if not found_any:
        print(f"  （空 — 请执行 --init 下载词库）")
    else:
        print(f"  ─────────────")
        print(f"  总计: {total} 条")

    # 参考文档
    print(f"\n📁 参考文档 ({REFERENCE_DIR}):")
    ref_files = list(REFERENCE_DIR.glob("*.md")) + list(REFERENCE_DIR.glob("*.txt"))
    if ref_files:
        for f in sorted(ref_files):
            size_kb = f.stat().st_size / 1024
            print(f"  {f.name} ({size_kb:.1f} KB)")
    else:
        print(f"  （空 — 请执行 --init 下载规则文档）")

    # 更新建议
    print(f"\n💡 建议:")
    now = datetime.now()
    if not meta.get("initialized"):
        print(f"  ⚠️  请执行 --init 进行首次初始化")
    else:
        if meta.get("last_dict_update"):
            last = datetime.fromisoformat(meta["last_dict_update"])
            days = (now - last).days
            if days > 30:
                print(f"  ⚠️  词库已 {days} 天未更新，建议执行 --update-dicts")
            else:
                print(f"  ✅ 词库状态良好（{days} 天前更新）")

        if meta.get("last_guideline_update"):
            last = datetime.fromisoformat(meta["last_guideline_update"])
            days = (now - last).days
            if days > 90:
                print(f"  ⚠️  运营规范已 {days} 天未检查，建议执行 --update-guidelines")
            else:
                print(f"  ✅ 运营规范状态良好（{days} 天前检查）")


# ─── CLI 入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="微信公众号合规检测 - 词库管理")
    parser.add_argument("--init", action="store_true", help="首次初始化：全量下载词库和参考文档")
    parser.add_argument("--check-init", action="store_true", help="检查是否已初始化（返回 exit code）")
    parser.add_argument("--update-dicts", action="store_true", help="增量更新敏感词库")
    parser.add_argument("--update-guidelines", action="store_true", help="更新运营规范")
    parser.add_argument("--status", action="store_true", help="查看词库状态")

    args = parser.parse_args()

    if args.init:
        init_dicts()
    elif args.check_init:
        if is_initialized():
            print("initialized")
            sys.exit(0)
        else:
            print("not_initialized")
            sys.exit(1)
    elif args.update_dicts:
        update_all_dicts()
    elif args.update_guidelines:
        update_guidelines()
    elif args.status:
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
