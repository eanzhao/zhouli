import re
import json

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
current_section = -1
data = {s: [] for s in sections}
existing_titles = set()

# A dictionary to hold the deep descriptions for each official
detailed_descriptions = {}

with open("周礼.txt", "r", encoding="utf-8") as f:
    text = f.read()

# First pass: Extract the detailed "XXX之职，掌..." paragraphs
lines = text.split('\n')
for line in lines:
    line = line.strip()
    if not line: continue
    
    # Matches "大宰之职，掌..." or similar explicit job descriptions
    match_desc = re.search(r'^([一-龥]{2,5})之职，(.*)', line)
    if match_desc:
        title = match_desc.group(1).replace('之职', '')
        desc = match_desc.group(2)
        detailed_descriptions[title] = desc

# Second pass: Build the hierarchy based on the introductory lists, 
# and try to attach the detailed description from above.
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
        # Match introductory listings like "大宰，卿一人。..." or "膳夫，上士二人..."
        match_intro = re.match(r'^([^，、]+)，(.*)', line)
        if match_intro and "之职" not in line and "惟王建" not in line:
            title = match_intro.group(1).strip()
            # It's a valid title if it's short
            if len(title) <= 5 and title not in existing_titles and len(data[sections[current_section]]) < 15:
                # Short description is the personnel count
                personnel_info = match_intro.group(2).strip()
                short_desc = personnel_info.split('。')[0]
                
                # Check if we have a deep description for this title
                full_desc = detailed_descriptions.get(title, "")
                
                # If we don't have a specific "XXX之职" paragraph, 
                # we'll search the text for paragraphs starting with the title
                if not full_desc:
                    for scan_line in lines:
                        if scan_line.startswith(title) and "之职" not in scan_line and scan_line != line:
                            if len(scan_line) > 20: # Likely a descriptive paragraph
                                full_desc = scan_line
                                break
                
                # If STILL strictly nothing, just use a generic message to prevent duplication
                if not full_desc:
                    full_desc = f"《周礼》关于【{title}】的详细职掌原文未单独立段说明，其官署建置为：{personnel_info}"
                
                data[sections[current_section]].append({
                    "title": title, 
                    "short_desc": short_desc, 
                    "full_desc": full_desc
                })
                existing_titles.add(title)

with open("zhouli_data_deep.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

