import re
import json

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
current_section = -1
data = {s: [] for s in sections}
existing_titles = set()

with open("周礼.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Pattern for officials listing: "　　TITLE，DESC"
# And then we try to find their detailed job description later
for line in text.split('\n'):
    if "天官冢宰第一" in line: current_section = 0
    elif "地官司徒第二" in line: current_section = 1
    elif "春官宗伯第三" in line: current_section = 2
    elif "夏官司马第四" in line: current_section = 3
    elif "秋官司寇第五" in line: current_section = 4
    elif "冬官考工记第六" in line: current_section = 5
    
    if current_section >= 0:
        line = line.strip()
        # Look for exactly "TITLE，" at the start of paragraphs in the intro sections
        # Or look for "TITLE之职，"
        match_desc = re.search(r'^([一-龥]{2,5})之职，(掌.*?)。', line)
        if match_desc:
            title = match_desc.group(1).replace('之职', '')
            desc = match_desc.group(2) + "。"
            if len(data[sections[current_section]]) < 30 and title not in existing_titles:
                data[sections[current_section]].append({"title": title, "desc": desc})
                existing_titles.add(title)
        
        # If still looking for more in the section, catch the introductory declarations
        match_intro = re.match(r'^([^，、]+)，(.*)', line)
        if match_intro and "之职" not in line and "惟王建" not in line:
            title = match_intro.group(1).strip()
            # If it's a short title and we don't have it
            if len(title) <= 4 and title not in existing_titles and len(data[sections[current_section]]) < 30:
                data[sections[current_section]].append({"title": title, "desc": match_intro.group(2).strip()[:50] + "..."})
                existing_titles.add(title)

with open("zhouli_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

