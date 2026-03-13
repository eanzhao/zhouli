from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORE_PATH = ROOT / "site-data.core.json"
OUTPUT_JSON = ROOT / "site-data.json"
OUTPUT_JS = ROOT / "site-data.js"
RAW_TEXT_PATH = ROOT / "周礼.txt"
FULL_TITLES_PATH = ROOT / "zhouli_data.json"


SECTION_ORDER = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]

DISPLAY_TITLE_MAP = {
    "疱人": "庖人",
    "司剌": "司刺",
    "\ue11d氏为量": "栗氏为量",
    "陶人为": "陶人为甗",
    "瓬人为簋": "旊人为簋",
    "兵同强": "庐人为庐器",
}

RAW_TITLE_MAP = {
    "庖人": "庖人",
    "司刺": "司刺",
    "栗氏为量": "\ue11d氏为量",
    "陶人为甗": "陶人为",
    "旊人为簋": "瓬人为簋",
    "庐人为庐器": "庐人为庐器",
}

WINTER_EXTRA_ORDER = [
    "栗氏为量",
    "鲍人之事",
    "画缋之事",
    "钟氏染羽",
    "玉人之事",
    "磬氏为磬",
    "矢人为矢",
    "陶人为甗",
    "旊人为簋",
    "梓人为侯",
    "庐人为庐器",
    "匠人建国",
    "匠人营国",
    "车人之事",
    "车人为耒",
    "车人为车",
    "弓人为弓",
]

SECTION_NOTES = {
    "天官": "属天官系统，偏向宫禁、供膳、酒浆、仓府或王室起居事务。",
    "地官": "属地官系统，偏向土地、户口、教化、赋役、市政与交通供给。",
    "春官": "属春官系统，偏向礼乐、祭祀、宗庙、丧纪与礼器服制。",
    "夏官": "属夏官系统，偏向军政、宿卫、车马、兵器与宫廷武备。",
    "秋官": "属秋官系统，偏向司法、禁令、囚徒、盟约和治安管理。",
    "冬官": "属《考工记》工艺规范条目，重点是材料、尺度和制作法则。",
}

KNOWN_LACUNA_TITLES = {
    "掌疆": {
        "summary": "现存通行本此条正文多已缺佚。",
        "translation": "目前常见底本这里只保留编制名单，未见完整职掌正文，通常视作阙文或脱简，不宜硬译。",
        "note": "从官名与编排位置看，它大概与疆界、军防或巡守事务有关，但仍需参看注疏补证。",
    },
}

SECTION_SPECIFIC_NOTES = {
    "医师": "属于天官医官系统中的总领之官，后面还分食医、疾医、疡医、兽医。",
    "食医": "侧重饮食调理，和膳夫、庖人等供膳系统互相配合。",
    "疾医": "偏重内科病证与季节性疾病的诊治。",
    "疡医": "偏重外伤、痈疽和金刃折伤等外科问题。",
    "兽医": "专治牲畜疾病，服务于王室和祭祀用畜体系。",
    "司市": "属于地官中的市场治理核心职位，兼管交易秩序与市令。",
    "质人": "重点在质剂、契据与交易凭证，和司约、司盟可互相参看。",
    "泉府": "常被视作周礼中较早的财政与平准调剂机构。",
    "司门": "偏向城门管理与出入盘检，和司关、掌节相互配合。",
    "司关": "负责关津与通行制度，是地官交通与税关系统的一环。",
    "职丧": "春官丧纪条目之一，重点是凶礼分工与丧仪执行。",
    "大司乐": "是春官里统摄乐教、乐舞和成童教育的重要职位。",
    "候人": "多与烽候、迎送、禁备相关，可视作夏官中的警备哨候官。",
    "虎贲氏": "与旅贲氏同属宿卫精锐，偏向近身护卫。",
    "旅贲氏": "和虎贲氏并举，是王室武卫系统的重要组成部分。",
    "大仆": "属于夏官车马近侍系统，和大驭、仆御传统有关。",
    "司圜": "掌管圜土教化，和单纯收囚不同，更强调悔罪与改过。",
    "掌囚": "偏向看守、械系和移送囚徒。",
    "掌戮": "偏向执行刑戮与战时军法。",
    "布宪": "重在向邦国、都鄙宣布刑禁，属于秋官公开法令的一环。",
    "雍氏": "属于秋官中较偏“禁害”性质的官，侧重沟渎与农田防害。",
    "萍氏": "属于秋官水禁条目，重点在川泽禁令与涉水行为约束。",
    "栗氏为量": "原书多用异体字“㮚”，这里统一写成便于识读的“栗”。",
    "陶人为甗": "原底本此处缺一字，通行本与相关索引多作“甗”，已按常见题名补齐。",
    "旊人为簋": "原底本作“瓬”，这里按通行写法统一成“旊”。",
    "庐人为庐器": "原数据把这一条截成“兵同强”，这里恢复到较完整的标题。",
}

ITEM_OVERRIDES = {
    "栗氏为量": {
        "summary": "讲铜量器的校准流程和标准容量。",
        "translation": "这条说的是铸量器的工序：先反复熔炼金锡，确认材质稳定，再称重、校平、校准，最后制成标准量器。后面的尺寸条文则规定了鬴、豆等量器的深浅、方圆和耳臂比例，用来统一容量标准。",
        "note": "这里的“量”是容量标准器，不是普通炊器。",
    },
    "鲍人之事": {
        "summary": "讲治革之后怎样验看皮革好坏。",
        "translation": "鲍人负责治革。这里一连列出验革的方法：先看颜色，再摸手感，再卷起来看会不会起皱变形，还要看纹理和缝线藏得住不露。意思很明确，皮革要白净、柔韧、厚薄匀，做出来的器具才耐用。",
        "note": "“鲍人”这里是治皮工，不是后世说的鲍鱼商贩。",
    },
    "画缋之事": {
        "summary": "讲设色时怎样安排五色次序。",
        "translation": "这条先列青、赤、白、黑、玄、黄几种基本颜色，再说明哪些颜色应该相配、相次。它说的不是随意上色，而是礼器、车服和图绘常用的设色规则。",
        "note": "常被用来说明古代礼制配色和画工设色的基本原则。",
    },
    "钟氏染羽": {
        "summary": "讲羽毛染色的原料、火候和上色层次。",
        "translation": "钟氏负责给羽毛染色。文中用朱湛、丹秫等染料，按蒸煮和浸染的次数区分纁、緅、缁等颜色，所以这条本质上是在交代羽饰染色的工艺配方。",
        "note": "多和车服、仪仗、礼饰上的羽毛染色有关。",
    },
    "玉人之事": {
        "summary": "讲礼玉的尺寸、名称和使用等级。",
        "translation": "这条把不同尺寸和名称的圭、璧、琮分给天子、公、侯、伯等不同等级，并分别对应朝聘、祭天、祭庙、礼日月等场合。重点不在雕刻技巧，而在礼玉的尺寸制度。",
        "note": "这类玉器的尺寸直接连着身份等级和礼仪场合。",
    },
    "磬氏为磬": {
        "summary": "讲石磬的形制比例和厚薄算法。",
        "translation": "磬氏做石磬，要先定弯角、宽度、股和鼓等部位的比例，再按鼓部宽度反推厚薄。整条都在说明石磬怎样做才既合形制，又能发声稳定。",
        "note": "石磬既是乐器，也是礼器，所以尺寸和音响都要兼顾。",
    },
    "矢人为矢": {
        "summary": "讲不同箭矢的前后比例和装羽尺度。",
        "translation": "矢人按用途区分鍭矢、茀矢、兵矢、田矢、杀矢，并分别规定前后比例、箭杆长度、羽长和刃部尺寸。说白了，这条是在给不同用途的箭制定统一规格。",
        "note": "不同箭型分别对应战争、田猎等不同场合。",
    },
    "陶人为甗": {
        "summary": "讲甗、盆、甑、鬲等陶器的容量和尺寸。",
        "translation": "这条把甗、盆、甑、鬲几种陶器的容量、厚度、口沿尺寸和穿孔数都定出来，属于很典型的器形规格条文。重点是做出来的陶器要容量准、壁厚匀、形制统一。",
        "note": "甗、甑、鬲都和蒸煮炊具有关，这里更像一份官方规格书。",
    },
    "旊人为簋": {
        "summary": "讲簋、豆等陶礼器的容量和验收标准。",
        "translation": "旊人负责做簋、豆一类陶器。这条先定容量和高度，再补一句凡有裂痕、坯体不匀、烧坏的器物不得入市，说明它不只讲尺寸，也讲成品验收。",
        "note": "末句已经带有明显的成品检验意味。",
    },
    "梓人为侯": {
        "summary": "讲射侯的尺寸分配和不同用途。",
        "translation": "梓人做的是射礼用的侯。文中按侯面的宽高、鹄位、上下纲和张设方式分配尺寸，并区分皮侯、五采侯、兽侯各自对应的用途。",
        "note": "“侯”在这里是射礼的靶，不是诸侯。",
    },
    "庐人为庐器": {
        "summary": "讲戈、殳、矛等长兵器的尺度上限。",
        "translation": "这条给戈柲、殳、车戟、酋矛、夷矛等长兵器规定长度，并强调兵器不能长得超过使用者身长的一定比例，否则反而难以操控，还可能伤到自己人。",
        "note": "这里讨论的是兵器尺度，不是军营里的居庐器具。",
    },
    "匠人建国": {
        "summary": "讲建城之前怎样量地定向。",
        "translation": "匠人建国先不是直接动工，而是先量地、立表、看日影，白天用太阳、夜里用极星来校正方向，再据此确定城邑的朝向和基准。它更像营建前的测绘程序。",
        "note": "经常被拿来讨论古代都城营建前的测量技术。",
    },
    "匠人营国": {
        "summary": "讲都城规划的基本格局。",
        "translation": "这条最出名。它规定理想都城应是方九里、三门、九经九纬、左祖右社、面朝后市，后面又补出夏后氏世室的尺度。换成今天的话，就是把城郭、宗庙、社稷和市场的标准布局写成了条文。",
        "note": "“左祖右社、面朝后市”就出自这一条。",
    },
    "车人之事": {
        "summary": "讲车部构件的一套基准尺度。",
        "translation": "这条先把宣、欘、柯、磬折几个尺寸单位连起来，等于先定一套车器制作时反复使用的比例尺。它像后面车具各条的起算规则。",
        "note": "可以把它看作后面车制条文的比例起点。",
    },
    "车人为耒": {
        "summary": "讲耒的尺寸和适合不同土质的形制。",
        "translation": "车人做耒，要把耒底、直段、弯段和内外弦线的长度都算准，还要区分坚地适合直庛、柔地适合句庛。也就是说，这条把农具尺寸和土地性质直接连了起来。",
        "note": "这也说明《考工记》并不只谈兵车和礼器，也兼收农具。",
    },
    "车人为车": {
        "summary": "讲车轮与车体关键构件的配比。",
        "translation": "这条继续讲车制，把柯、毂、辐等部件的长度、厚薄和围度一一列出，再区分行泽、行山时短毂长毂、反輮仄輮的差别。核心是让车辆在不同地形上兼顾稳和利。",
        "note": "这条关注的是车制与路况之间的适配。",
    },
    "弓人为弓": {
        "summary": "讲制弓的材料、时令和受力原则。",
        "translation": "弓人制弓要按时节取六材，再把木、角、筋、胶、丝、漆各自的作用配合起来：有的求远，有的求疾，有的求深，有的求牢。后文其实是一整套材料选择、加工时序和受力校验的方法。",
        "note": "原文极长，这里只节录开头一段，后面还有大量材料与受力细则。",
    },
}

PERSONNEL_START_MARKERS = (
    "卿一人",
    "中大夫",
    "下大夫",
    "上士",
    "中士",
    "下士",
    "府",
    "史",
    "胥",
    "徒",
    "奄",
    "女御",
    "工",
    "贾",
    "狂夫",
)


def normalize_display_title(title: str) -> str:
    return DISPLAY_TITLE_MAP.get(title, title)


def raw_lookup_title(display_title: str) -> str:
    return RAW_TITLE_MAP.get(display_title, display_title)


def strip_prefix(title: str, text: str) -> str:
    raw_title = raw_lookup_title(title)
    if text.startswith(raw_title + "之职，"):
        return "掌" + text[len(raw_title + "之职，") :]
    if text.startswith(raw_title + "掌"):
        return text[len(raw_title) :]
    if text.startswith(raw_title + "，"):
        return text[len(raw_title) + 1 :]
    if text.startswith(raw_title):
        return text[len(raw_title) :]
    return text


def normalize_punctuation(text: str) -> str:
    return (
        text.replace("　", "")
        .replace("..", "。")
        .replace("；。", "。")
        .replace("，，", "，")
        .strip()
    )


def take_excerpt(text: str, limit: int = 84) -> str:
    text = normalize_punctuation(text)
    sentences = re.split(r"(?<=。)", text)
    excerpt = ""
    for sentence in sentences:
        if not sentence:
            continue
        if len(excerpt) + len(sentence) > limit and excerpt:
            break
        excerpt += sentence
        if len(excerpt) >= 46:
            break
    excerpt = excerpt or text[:limit]
    excerpt = excerpt.strip("，；、 ")
    if len(excerpt) < len(text) and not excerpt.endswith(("。", "！", "？", "…")):
        excerpt += "…"
    return excerpt


def to_baihua(text: str) -> str:
    text = normalize_punctuation(text)

    if text.startswith("掌共"):
        text = text.replace("掌共", "负责供给", 1)
    elif text.startswith("掌"):
        text = text.replace("掌", "负责", 1)
    elif text.startswith("帅其属"):
        text = text.replace("帅其属", "率属员", 1)
    elif text.startswith("率其属"):
        text = text.replace("率其属", "率属员", 1)
    elif text.startswith("掌建"):
        text = text.replace("掌建", "负责建立", 1)

    replacements = [
        ("备掌其", "各掌其"),
        ("帅其属", "率属员"),
        ("率其属", "率属员"),
        ("掌其", "掌管其"),
        ("听其狱讼", "审理诉讼"),
        ("听狱讼", "审理诉讼"),
        ("以待", "以备"),
        ("以共", "用来供给"),
        ("共其", "供给其"),
        ("辨其", "辨别其"),
        ("受而藏之", "收存"),
        ("徵", "征"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"(^|[。；，])共", r"\1供", text)
    text = text.replace("辨别别", "辨别")

    text = text.strip("，；、 ")
    if text and not text.endswith(("。", "！", "？")):
        text += "。"
    return text


def make_summary(translation: str) -> str:
    text = translation.strip()
    for sep in ["。", "；"]:
        idx = text.find(sep)
        if 0 < idx <= 28:
            return text[: idx + 1]
    comma = text.find("，")
    if 0 < comma <= 20:
        return text[:comma].rstrip("，；、 ") + "…"
    if len(text) <= 30:
        return text
    return text[:29].rstrip("，；、 ") + "…"


def strip_leading_title(line: str, title: str) -> str:
    raw_title = raw_lookup_title(title)
    if line.startswith(raw_title):
        line = line[len(raw_title) :]
    return line.lstrip("，,：: ")


def is_personnel_line(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    if text.startswith(("每", "凡")) and "掌" not in text[:24]:
        return True
    return text.startswith(PERSONNEL_START_MARKERS)


def build_orders(core_data: dict, raw_titles: dict) -> dict[str, list[str]]:
    orders: dict[str, list[str]] = {}
    core_sections = {section["key"]: section for section in core_data["sections"]}

    for section_key in SECTION_ORDER:
        existing = [item["title"] for item in core_sections[section_key]["items"]]
        remaining = []
        for item in raw_titles[section_key]:
            title = normalize_display_title(item["title"])
            if title not in existing and title not in remaining:
                remaining.append(title)

        if section_key == "冬官":
            for title in WINTER_EXTRA_ORDER:
                if title not in existing and title not in remaining:
                    remaining.append(title)

        orders[section_key] = existing + remaining

    return orders


def build_text_index(raw_text: str) -> list[str]:
    return [line.strip().lstrip("　") for line in raw_text.splitlines() if line.strip()]


def find_personnel(lines: list[str], title: str) -> str | None:
    raw_title = raw_lookup_title(title)
    if title in {"国有六职"} or title.endswith(("之事", "为轮", "为盖", "为车", "为削", "为剑", "为钟", "为量", "为甲", "为磬", "为矢", "为甗", "为簋", "建国", "营国", "为耒", "为弓", "庐器")):
        return None

    for line in lines:
        if line.startswith(raw_title):
            rest = strip_leading_title(line, title)
            if is_personnel_line(rest):
                return normalize_punctuation(rest)
    return None


def find_description(lines: list[str], title: str) -> str | None:
    raw_title = raw_lookup_title(title)
    candidates = []
    for line in lines:
        if line.startswith(raw_title):
            if is_personnel_line(strip_leading_title(line, title)):
                continue
            candidates.append(normalize_punctuation(line))

    if not candidates:
        return None

    for line in candidates:
        if "掌" in line or "之职" in line or "为" in line or "之事" in line:
            return line

    return candidates[0]


def build_generated_item(lines: list[str], section_key: str, title: str) -> dict:
    personnel = find_personnel(lines, title)
    description = find_description(lines, title)

    if title in KNOWN_LACUNA_TITLES and (not description or "阙" in description):
        item = {
            "title": title,
            "summary": KNOWN_LACUNA_TITLES[title]["summary"],
            "classical": take_excerpt(raw_lookup_title(title) + "，阙。"),
            "translation": KNOWN_LACUNA_TITLES[title]["translation"],
            "note": KNOWN_LACUNA_TITLES[title]["note"],
        }
        if personnel:
            item["metaLabel"] = "建置"
            item["meta"] = personnel
        return item

    if not description:
        description = title + "，原文待续考。"

    if "阙" in description:
        item = {
            "title": title,
            "summary": "现存底本此条作“阙”，未见展开职掌。",
            "classical": take_excerpt(description),
            "translation": "现存底本这里只保留题名或编制，未见展开的职掌正文，所以暂不硬译。",
            "note": "可以先据序官编制认名，后续仍需参看他本或注疏补足。",
        }
        if personnel:
            item["metaLabel"] = "建置"
            item["meta"] = personnel
        return item

    core_text = strip_prefix(title, description)
    translation = to_baihua(take_excerpt(core_text, limit=96))
    summary = make_summary(translation)

    item = {
        "title": title,
        "summary": summary,
        "classical": take_excerpt(description),
        "translation": translation,
        "note": SECTION_SPECIFIC_NOTES.get(title, SECTION_NOTES[section_key]),
    }

    if title in ITEM_OVERRIDES:
        item.update(ITEM_OVERRIDES[title])

    if personnel:
        item["metaLabel"] = "建置"
        item["meta"] = personnel

    return item


def main() -> None:
    core_data = json.loads(CORE_PATH.read_text(encoding="utf-8"))
    full_titles = json.loads(FULL_TITLES_PATH.read_text(encoding="utf-8"))
    lines = build_text_index(RAW_TEXT_PATH.read_text(encoding="utf-8"))

    core_sections = {section["key"]: section for section in core_data["sections"]}
    core_items = {
        section["key"]: {item["title"]: item for item in section["items"]}
        for section in core_data["sections"]
    }

    orders = build_orders(core_data, full_titles)

    output = {
        "meta": core_data["meta"],
        "sections": [],
    }

    for section_key in SECTION_ORDER:
        base_section = core_sections[section_key]
        section = {
            "key": base_section["key"],
            "title": base_section["title"],
            "seal": base_section["seal"],
            "desc": base_section["desc"],
            "sourceUrl": base_section["sourceUrl"],
            "items": [],
        }

        for title in orders[section_key]:
            if title in core_items[section_key]:
                item = core_items[section_key][title]
            else:
                item = build_generated_item(lines, section_key, title)
            section["items"].append(item)

        output["sections"].append(section)

    OUTPUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_JS.write_text("window.__SITE_DATA__ = " + json.dumps(output, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    counts = ", ".join(f"{section['key']} {len(section['items'])}" for section in output["sections"])
    print("built site-data:", counts)


if __name__ == "__main__":
    main()
