import re
import json
import html

sections = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
current_section = -1
data = {s: [] for s in sections}
existing_titles = set()

with open("周礼.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Pattern for officials listing and detailed descriptions
lines = text.split('\n')
for i, line in enumerate(lines):
    if "天官冢宰第一" in line: current_section = 0
    elif "地官司徒第二" in line: current_section = 1
    elif "春官宗伯第三" in line: current_section = 2
    elif "夏官司马第四" in line: current_section = 3
    elif "秋官司寇第五" in line: current_section = 4
    elif "冬官考工记第六" in line: current_section = 5
    
    if current_section >= 0:
        line = line.strip()
        # Look for full paragraphs defined as "TITLE之职，..."
        match_desc = re.search(r'^([一-龥]{2,5})之职，(.*)', line)
        if match_desc:
            title = match_desc.group(1).replace('之职', '')
            desc = match_desc.group(2)
            if len(data[sections[current_section]]) < 10 and title not in existing_titles:
                short_desc = desc.split('。')[0] + "。"
                if len(short_desc) > 35:
                    short_desc = short_desc[:33] + "..."
                data[sections[current_section]].append({"title": title, "short_desc": short_desc, "full_desc": desc})
                existing_titles.add(title)
        
        # Capture early introductory declarations if missing detailed later
        match_intro = re.match(r'^([^，、]+)，(.*)', line)
        if match_intro and "之职" not in line and "惟王建" not in line:
            title = match_intro.group(1).strip()
            # If it's a short title and we don't have it
            if len(title) <= 4 and title not in existing_titles and len(data[sections[current_section]]) < 10:
                short_desc = match_intro.group(2).strip().split('。')[0]
                if len(short_desc) > 35: short_desc = short_desc[:33] + "..."
                full_desc = match_intro.group(2).strip()
                data[sections[current_section]].append({"title": title, "short_desc": short_desc, "full_desc": full_desc})
                existing_titles.add(title)

ministers = {
    "天官": {"title": "天官冢宰", "desc": "主管宫廷政务与财政", "seal": "天"},
    "地官": {"title": "地官司徒", "desc": "主管土地、户籍、教化与民政", "seal": "地"},
    "春官": {"title": "春官宗伯", "desc": "主管礼乐、祭祀、宗族与外交", "seal": "春"},
    "夏官": {"title": "夏官司马", "desc": "主管军政、征伐、车马与武备", "seal": "夏"},
    "秋官": {"title": "秋官司寇", "desc": "主管司法、刑狱、监察与治安", "seal": "秋"},
    "冬官": {"title": "冬官司空 / 考工记", "desc": "主管工程、营造、工艺与制作", "seal": "冬"}
}

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
        full_desc = html.escape(role['full_desc']).replace("'", "\\'").replace('"', '&quot;')
        
        block += f"""
                        <div class="sub-node" onclick="openModal('{title}', '{full_desc}')" title="点击查看详情">
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

# Inject modal HTML before </body>
modal_html = """
    <!-- Modal HTML -->
    <div id="infoModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">Title</h2>
            <div class="modal-scroll-area">
                <p id="modalDesc">Desc</p>
            </div>
        </div>
    </div>
"""
if '<div id="infoModal"' not in html_content:
    html_content = html_content.replace('</body>', f'{modal_html}\n</body>')

# Inject CSS before </style>
modal_css = """
        .modal {
            display: none; 
            position: fixed; 
            z-index: 9999; 
            left: 0; top: 0; width: 100%; height: 100%; 
            overflow: hidden; 
            background-color: rgba(43, 76, 80, 0.4); /* 黛青半透明 */
            backdrop-filter: blur(3px);
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            background-color: var(--bg-color);
            background-image: repeating-linear-gradient(90deg, transparent, transparent 30px, rgba(0,0,0,0.03) 30px, rgba(0,0,0,0.03) 31px);
            padding: 30px; 
            border: 2px solid var(--gold);
            width: 85%; 
            max-width: 600px;
            border-radius: 6px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            position: relative;
            max-height: 75vh;
            display: flex;
            flex-direction: column;
            animation: fadeIn 0.3s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .close-btn {
            color: var(--king-bg);
            position: absolute;
            top: 15px; right: 20px;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.2s;
        }
        .close-btn:hover { color: var(--text-dark); }
        #modalTitle { 
            color: var(--king-bg); 
            text-align: center; 
            margin-top: 0; 
            border-bottom: 2px solid rgba(189, 155, 91, 0.3); 
            padding-bottom: 15px;
            letter-spacing: 2px;
        }
        .modal-scroll-area { 
            overflow-y: auto; 
            padding-right: 15px; 
            margin-top: 15px; 
            text-align: justify; 
            line-height: 1.8; 
            font-size: 1.1rem;
            color: #4a3b32;
        }
        .modal-scroll-area::-webkit-scrollbar {
            width: 6px;
        }
        .modal-scroll-area::-webkit-scrollbar-thumb {
            background-color: var(--gold);
            border-radius: 3px;
        }
        .sub-node { cursor: pointer; }
        .sub-node:hover {
            box-shadow: 0 5px 12px rgba(189, 155, 91, 0.4);
            border-color: var(--gold);
        }
"""
if '.modal {' not in html_content:
    html_content = html_content.replace('</style>', f'{modal_css}\n    </style>')

# Inject JS before </body>
modal_js = """
    <script>
        function openModal(title, desc) {
            document.getElementById('modalTitle').innerHTML = title;
            document.getElementById('modalDesc').innerHTML = desc;
            document.getElementById('infoModal').style.display = 'flex';
        }
        function closeModal() {
            document.getElementById('infoModal').style.display = 'none';
        }
        window.onclick = function(event) {
            let modal = document.getElementById('infoModal');
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    </script>
"""
if 'function openModal' not in html_content:
    html_content = html_content.replace('</body>', f'{modal_js}\n</body>')

# Update the departments
import re
new_html = re.sub(r'<div class="departments-row">.*?</div>\s*</div>\s*</div>\s*(?:<!-- Modal HTML -->|<script>)', 
                 f'<div class="departments-row">\n{departments_html}\n            </div>\n        </div>\n    </div>\n', 
                 html_content, flags=re.DOTALL)

# Let me be safer and just replace between <div class="departments-row"> and </div></div></div>
# Actually, the safe way is:
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

print("Interactive Webpage Generated Successfully.")
