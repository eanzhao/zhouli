import re
import json

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
current_section = -1
data = {s: [] for s in sections}

detailed_descriptions = {}
personnel_info = {}

with open("周礼.txt", "r", encoding="utf-8") as f:
    text = f.read()
lines = text.split('\n')

# Pass 1: Grab detailed descriptions "XXX之职，掌..."
for line in lines:
    line = line.strip()
    if not line: continue
    match_desc = re.search(r'^([一-龥]{2,5})之职，(.*)', line)
    if match_desc:
        title = match_desc.group(1).replace('之职', '')
        desc = match_desc.group(2)
        detailed_descriptions[title] = desc

# Pass 2: Grab personnel info and build the main list
existing_titles = set()
for line in lines:
    line = line.strip()
    if not line: continue
    if "天官冢宰第一" in line: current_section = 0
    elif "地官司徒第二" in line: current_section = 1
    elif "春官宗伯第三" in line: current_section = 2
    elif "夏官司马第四" in line: current_section = 3
    elif "秋官司寇第五" in line: current_section = 4
    elif "冬官考工记第六" in line: current_section = 5
    
    if current_section >= 0:
        match_intro = re.match(r'^([^，、]+)，(.*)', line)
        if match_intro and "之职" not in line and "惟王建" not in line and "之状" not in line:
            title = match_intro.group(1).strip()
            
            # Stop grabbing generic long sentences as titles
            if len(title) <= 5 and title not in existing_titles and len(data[sections[current_section]]) < 10:
                personnel = match_intro.group(2).strip()
                personnel_info[title] = personnel
                
                short_desc = personnel.split('。')[0]
                if len(short_desc) > 35: short_desc = short_desc[:33] + "..."
                
                # Combine info
                full_desc_text = detailed_descriptions.get(title, "")
                if not full_desc_text:
                    # Generic fallback if no specific desc paragraph
                    for scan_line in lines:
                        if scan_line.startswith(title) and scan_line != line and len(scan_line) > 30:
                            full_desc_text = scan_line
                            break
                            
                data[sections[current_section]].append({
                    "title": title, 
                    "personnel": personnel,
                    "short_desc": short_desc, 
                    "full_desc": full_desc_text
                })
                existing_titles.add(title)

with open("zhouli_data_combined.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

