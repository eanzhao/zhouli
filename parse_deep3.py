import re
import json

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
current_section = -1
data = {s: [] for s in sections}

detailed_descriptions = {}

with open("周礼.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Pass 1: Grab pure functional titles
lines = text.split('\n')
for line in lines:
    line = line.strip()
    if not line: continue
    
    # Matches explicit descriptions, this time prioritizing them
    # Because earlier I extracted personnel listed in the 1st paragraph instead of the actual roles
    match_desc = re.search(r'^([一-龥]{2,5})之职，(.*)', line)
    if match_desc:
        title = match_desc.group(1).replace('之职', '')
        desc = match_desc.group(2)
        detailed_descriptions[title] = desc

# Second pass: only add to the data if we have a detailed description, unless it's the only ones available
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
        match_desc = re.search(r'^([一-龥]{2,5})之职，(.*)', line)
        if match_desc:
            title = match_desc.group(1).replace('之职', '')
            desc = match_desc.group(2)
            
            # Ensure we haven't already added this title in this section
            if not any(d['title'] == title for d in data[sections[current_section]]) and len(data[sections[current_section]]) < 10:
                short_desc = desc.split('。')[0] + "。"
                if len(short_desc) > 35:
                    short_desc = short_desc[:33] + "..."
                
                data[sections[current_section]].append({
                    "title": title, 
                    "short_desc": short_desc, 
                    "full_desc": f"{title}之职，{desc}" # preserve full sentence
                })

# Fallback for Winter (冬官) since it's Kaogongji and formulated differently
for line in lines:
    line = line.strip()
    if not line: continue
    if "冬官考工记第六" in line: current_section = 5
    
    if current_section == 5:
        # Match introductory listings like "攻木之工：轮、舆..."
        match_intro = re.match(r'^([^，、]+)，(.*)', line)
        if match_intro and "之职" not in line and "惟王建" not in line and "之状" not in line:
            title = match_intro.group(1).strip()
            if len(title) <= 5 and not any(d['title'] == title for d in data["冬官"]) and len(data["冬官"]) < 10:
                desc = match_intro.group(2).strip()
                short_desc = desc.split('。')[0]
                if len(short_desc) > 35: short_desc = short_desc[:33] + "..."
                # Search for any detailed paragraph starting with the title
                full_desc = desc
                for scan_line in lines:
                    if scan_line.startswith(title) and scan_line != line and len(scan_line) > 30:
                        full_desc = scan_line
                        break
                
                data["冬官"].append({
                    "title": title, 
                    "short_desc": short_desc, 
                    "full_desc": full_desc
                })

with open("zhouli_data_deep.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

