#!/usr/bin/env python3
"""
验证《周礼》数据校准。
检查标题匹配、描述截断和边界问题。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
RAW_TEXT_PATH = ROOT / "周礼.txt"
FULL_TITLES_PATH = ROOT / "zhouli_data.json"
SITE_DATA_PATH = ROOT / "site-data.json"

# 从 build_site_data.py 导入必要的映射和函数（简化）
DISPLAY_TITLE_MAP = {
    "疱人": "庖人",
    "司剌": "司刺",
    "司虣": "司暴",
    "赞阝长": "酂长",
    "眡": "视瞭",
    "眡祲": "视祲",
    "鏄师": "镈师",
    "槀人": "槁人",
    "荒氏湅丝": "㡛氏湅丝",
    "\ue11d氏为量": "栗氏为量",
    "陶人为": "陶人为甗",
    "瓬人为簋": "旊人为簋",
    "兵同强": "庐人为庐器",
    "丱人": "矿人",
}

RAW_TITLE_MAP = {
    "庖人": "庖人",
    "司刺": "司刺",
    "司暴": "司虣",
    "酂长": "赞阝长",
    "视瞭": "眡",
    "视祲": "眡祲",
    "镈师": "鏄师",
    "槁人": "槀人",
    "㡛氏湅丝": "荒氏湅丝",
    "栗氏为量": "\ue11d氏为量",
    "陶人为甗": "陶人为",
    "旊人为簋": "瓬人为簋",
    "庐人为庐器": "庐人为庐器",
    "神仕": "凡以神仕者",
    "矿人": "丱人",
}

def normalize_display_title(title: str) -> str:
    return DISPLAY_TITLE_MAP.get(title, title)

def raw_lookup_title(display_title: str) -> str:
    return RAW_TITLE_MAP.get(display_title, display_title)

def load_raw_text():
    return RAW_TEXT_PATH.read_text(encoding='utf-8')

def load_titles():
    with open(FULL_TITLES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    titles_by_section = {}
    for section, items in data.items():
        titles_by_section[section] = [item['title'] for item in items]
    return titles_by_section

def load_site_data():
    with open(SITE_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_title_positions(raw_text: str, title: str):
    """返回标题在原始文本中出现的行号列表（0起始）"""
    raw_title = raw_lookup_title(title)
    lines = raw_text.splitlines()
    positions = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(raw_title):
            positions.append(i)
    return positions

def main():
    raw_text = load_raw_text()
    titles_by_section = load_titles()
    site_data = load_site_data()

    print("=== 周礼数据验证报告 ===\n")

    # 1. 检查标题是否存在
    print("1. 标题匹配检查")
    missing_titles = []
    for section, titles in titles_by_section.items():
        for title in titles:
            positions = find_title_positions(raw_text, title)
            if not positions:
                missing_titles.append((section, title))

    if missing_titles:
        print(f"  警告：{len(missing_titles)} 个标题在原始文本中未找到：")
        for section, title in missing_titles:
            print(f"    {section}: {title}")
    else:
        print("  所有标题均在原始文本中找到。")

    # 2. 检查描述完整性（粗略检查）
    print("\n2. 描述完整性检查")
    # 对于每个条目，检查 fullClassical 是否包含完整文本
    # 这里仅检查长度是否过短（可能截断）
    short_items = []
    for section in site_data['sections']:
        for item in section['items']:
            classical = item.get('fullClassical') or item.get('classical', '')
            if classical and len(classical) < 20 and '阙' not in classical:
                short_items.append((section['key'], item['title'], len(classical)))

    if short_items:
        print(f"  警告：{len(short_items)} 个条目的原文可能截断：")
        for sec, title, length in short_items[:10]:
            print(f"    {sec}: {title} (长度: {length})")
        if len(short_items) > 10:
            print(f"    ... 共 {len(short_items)} 个")
    else:
        print("  未发现明显截断的条目。")

    # 3. 检查边界重叠（高级）
    print("\n3. 边界重叠检查（需要解析原始文本结构）")
    print("  此检查需要更复杂的解析，建议人工核对。")

    # 4. 统计信息
    print("\n4. 统计信息")
    total_items = sum(len(items) for items in titles_by_section.values())
    print(f"  总条目数: {total_items}")
    for section, titles in titles_by_section.items():
        print(f"  {section}: {len(titles)} 条目")

    print("\n=== 验证完成 ===")
    if missing_titles or short_items:
        print("发现潜在问题，请进一步检查。")
    else:
        print("未发现明显问题。")

if __name__ == '__main__':
    main()