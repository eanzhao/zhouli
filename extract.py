import re
import json

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
current_section = -1
data = {s: [] for s in sections}

with open("周礼.txt", "r", encoding="utf-8") as f:
    text = f.read()

# The text has parts like "天职：大宰：掌建邦之六典..."
# Let's try to extract from the main text directly
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
        # Looking for pattern "Title：Description" or "Title，Description" in the text
        # The text format is like "大宰之职，掌建邦之六典，..."
        match = re.search(r'([一-龥]{2,4})之职，(掌.*?)。', line)
        if match:
            title = match.group(1)
            desc = match.group(2) + "。"
            # print(f"Found {title}: {desc}")
            data[sections[current_section]].append({"title": title, "desc": desc})

with open("zhouli_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    
print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
