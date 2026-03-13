import re
import json

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
current_section = -1
data = {s: [] for s in sections}
existing_titles = set()

with open("周礼.txt", "r", encoding="utf-8") as f:
    text = f.read()

# First pass: standard "之职" pattern
for line in text.split('\n'):
    line = line.strip()
    if not line: continue
    
    if "天官冢宰第一" in line: current_section = 0
    elif "地官司徒第二" in line: current_section = 1
    elif "春官宗伯第三" in line: current_section = 2
    elif "夏官司马第四" in line: current_section = 3
    elif "秋官司寇第五" in line: current_section = 4
    elif "冬官考工记第六" in line: current_section = 5
    
    if current_section >= 0:
        match = re.search(r'([从一-龥]{2,5})之职，(掌.*?)。', line)
        if match:
            title = match.group(1).replace('之职', '')
            desc = match.group(2) + "。"
            if title not in existing_titles and not title.endswith("官"):
                data[sections[current_section]].append({"title": title, "desc": desc})
                existing_titles.add(title)

# Second pass: just grab titles from the initial listing if not found
current_section = -1
for line in text.split('\n'):
    line = line.strip()
    if not line: continue
    if "天官冢宰第一" in line: current_section = 0
    elif "地官司徒第二" in line: current_section = 1
    elif "春官宗伯第三" in line: current_section = 2
    elif "夏官司马第四" in line: current_section = 3
    elif "秋官司寇第五" in line: current_section = 4
    elif "冬官考工记第六" in line: current_section = 5
    
    if current_section >= 0 and line.startswith("　　") or line.startswith(" "):
        match = re.match(r'^([^，、]+)，(.*)', line)
        if match:
            title = match.group(1).strip()
            desc = match.group(2).strip()
            # If it's just personnel count, we might just put a placeholder if we really want them all
            if title not in existing_titles and "人" in desc and len(data[sections[current_section]]) < 10:
                data[sections[current_section]].append({"title": title, "desc": "（参见《周礼》原文具体职能描述）"})
                existing_titles.add(title)

with open("zhouli_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
