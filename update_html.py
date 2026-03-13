import json

with open("zhouli_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# The six minister names and descriptions for the main headers
ministers = {
    "天官": {"title": "天官冢宰", "desc": "主管宫廷政务与财政", "seal": "天"},
    "地官": {"title": "地官司徒", "desc": "主管土地、户籍、教化与民政", "seal": "地"},
    "春官": {"title": "春官宗伯", "desc": "主管礼乐、祭祀、宗族与外交", "seal": "春"},
    "夏官": {"title": "夏官司马", "desc": "主管军政、征伐、车马与武备", "seal": "夏"},
    "秋官": {"title": "秋官司寇", "desc": "主管司法、刑狱、监察与治安", "seal": "秋"},
    "冬官": {"title": "冬官司空 / 考工记", "desc": "主管工程、营造、工艺与制作", "seal": "冬"}
}

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]

html_blocks = []
for sec in sections:
    min_info = ministers[sec]
    block = f"""
                <!-- {sec} -->
                <div class="dept-col">
                    <div class="minister-node">
                        <div class="seal">{min_info['seal']}</div>
                        <h3 class="m-title">{min_info['title']}</h3>
                        <p class="m-sub">{min_info['desc']}</p>
                    </div>
                    <div class="sub-list">"""
    
    # Add up to 8 roles per ministry for visual balance so it doesn't get too long vertically
    for role in data.get(sec, [])[:8]:
        title = role['title']
        desc = role['desc'].split('。')[0] + "。"
        if len(desc) > 40:
            desc = desc[:38] + "..."
        block += f"""
                        <div class="sub-node">
                            <p class="s-title">{title}</p>
                            <p class="s-desc">{desc}</p>
                        </div>"""
    
    block += """
                    </div>
                </div>"""
    html_blocks.append(block)

departments_html = "\n".join(html_blocks)

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
# Replace the contents of <div class="departments-row"> ... </div>
new_html = re.sub(r'<div class="departments-row">.*?</div>\s*</div>\s*</div>\s*</body>', 
                 f'<div class="departments-row">\n{departments_html}\n            </div>\n        </div>\n    </div>\n</body>', 
                 html, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("HTML Updated.")
