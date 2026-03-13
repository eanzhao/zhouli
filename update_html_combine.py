import json
import html
import re

with open("zhouli_data_combined.json", "r", encoding="utf-8") as f:
    data = json.load(f)

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
    
    for role in data.get(sec, [])[:10]:
        title = html.escape(role['title'])
        short_desc = html.escape(role['short_desc'])
        
        # Prepare content for the modal
        personnel = html.escape(role['personnel'])
        full_desc_raw = role.get('full_desc', '')
        
        if full_desc_raw:
            full_desc_html = f"<div style='margin-bottom:15px; padding-bottom:10px; border-bottom:1px dashed #bd9b5b80;'><strong>【建置】</strong>{personnel}</div><strong>【职掌】</strong><br>{full_desc_raw}"
        else:
            full_desc_html = f"<strong>【建置】</strong>{personnel}<br><br><span style='color:#777; font-size: 0.9em;'>(未见该官吏长段【某某之职】专门论述，见于全卷分散记录中)</span>"
        
        # Format for JS onClick
        modal_content = full_desc_html.replace("'", "\\'").replace('"', '&quot;').replace('\n', '<br>')
        
        block += f"""
                        <div class="sub-node" onclick="openModal('{title}', '{modal_content}')" title="点击查看详情">
                            <p class="s-title">{title} <span style="font-size:0.7rem; color: #bd9b5b; float:right;">[详]</span></p>
                            <p class="s-desc">{short_desc}</p>
                        </div>"""
    
    block += """
                    </div>
                </div>"""
    html_blocks.append(block)

departments_html = "\n".join(html_blocks)

with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Safe replacement logic
split_parts = html_content.split('<div class="departments-row">')
if len(split_parts) > 1:
    pre_row = split_parts[0]
    post_row_split = split_parts[1].split('</div>\n        </div>\n    </div>')
    post_row = "</div>\n        </div>\n    </div>" + "</div>\n        </div>\n    </div>".join(post_row_split[1:])
    new_html = pre_row + f'<div class="departments-row">\n{departments_html}\n            ' + post_row
else:
    new_html = html_content

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("Updated HTML with Combined Personnel and Duties.")
