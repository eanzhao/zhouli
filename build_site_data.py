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
EXTRAS_PATH = ROOT / "zhouli_extras.json"


SECTION_ORDER = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]
SECTION_MARKERS = {
    "天官": "天官冢宰第一",
    "地官": "地官司徒第二",
    "春官": "春官宗伯第三",
    "夏官": "夏官司马第四",
    "秋官": "秋官司寇第五",
    "冬官": "冬官考工记第六",
}

DISPLAY_TITLE_MAP = {
    "疱人": "庖人",
    "司剌": "司刺",
    "司虣": "司暴",
    "赞阝长": "酂长",
    "眡": "视瞭",
    "眡祲": "视祲",
    "鏄师": "镈师",
    "槀人": "槁人",
    "荒氏湅丝": "㡛氏湅丝",
    "\ue11d氏为量": "栗氏为量",
    "陶人为": "陶人为甗",
    "瓬人为簋": "旊人为簋",
    "兵同强": "庐人为庐器",
}

RAW_TITLE_MAP = {
    "庖人": "庖人",
    "司刺": "司刺",
    "司暴": "司虣",
    "酂长": "赞阝长",
    "视瞭": "眡",
    "视祲": "眡祲",
    "镈师": "鏄师",
    "槁人": "槀人",
    "㡛氏湅丝": "荒氏湅丝",
    "栗氏为量": "\ue11d氏为量",
    "陶人为甗": "陶人为",
    "旊人为簋": "瓬人为簋",
    "庐人为庐器": "庐人为庐器",
    "神仕": "凡以神仕者",
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

SECTION_COMMENTARY_URLS = {
    "天官": "https://ctext.org/rites-of-zhou/tian-guan-zhong-zai/zhs",
    "地官": "https://ctext.org/rites-of-zhou/di-guan-si-tu/zhs",
    "春官": "https://ctext.org/rites-of-zhou/chun-guan-zong-bo/zhs",
    "夏官": "https://ctext.org/rites-of-zhou/xia-guan-si-ma/zhs",
    "秋官": "https://ctext.org/rites-of-zhou/qiu-guan-si-kou/zhs",
    "冬官": "https://ctext.org/rites-of-zhou/dong-guan-kao-gong-ji/zhs",
}

KNOWN_LACUNA_TITLES = {
    "掌疆": {
        "summary": "现存通行本此条正文多已缺佚。",
        "translation": "目前常见底本这里只保留编制名单，未见完整职掌正文，通常视作阙文或脱简，不宜硬译。",
        "note": "从官名与编排位置看，它大概与疆界、军防或巡守事务有关，但仍需参看注疏补证。",
    },
    "司禄": {
        "summary": "此条正文今已亡佚，仅存叙官编制。",
        "translation": "现存通行本只见司禄的建置名单，不见展开的职掌正文；5000言对应页也直接标作“司禄（阙）”。",
        "note": "可知它属于地官仓廪赋禄系统的一环，但具体职责已难从现存经文复原。",
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
    "大宰": {
        "groupLabel": "所属序官",
        "group": "治官之属",
        "peerLabel": "同列官",
        "peer": "大宰、小宰、宰夫",
    },
    "小宰": {
        "groupLabel": "所属序官",
        "group": "治官之属",
        "peerLabel": "同列官",
        "peer": "大宰、小宰、宰夫",
    },
    "宰夫": {
        "groupLabel": "所属序官",
        "group": "治官之属",
        "peerLabel": "同列官",
        "peer": "大宰、小宰、宰夫",
    },
    "女史": {
        "summary": "掌王后礼职、内政副本与内宫文令，凡礼事皆执礼书随从。",
        "classical": "女史掌王后之礼职，掌内治之贰，以诏后治内政。逆内宫，书内令。凡后之事，以礼从。",
        "translation": "女史掌管王后礼职，保存内政法令副本，用来禀告王后处理内政；并核计内宫财用、书写内令，凡王后参与礼事都执礼书随从提醒。",
        "note": "相当于王后内廷中的女官书记与礼仪官。",
    },
    "内司服": {
        "summary": "掌王后六服及内外命妇服制的辨别与供掌。",
        "classical": "内司服掌王后之六服：袆衣、揄狄、阙狄、鞠衣、展衣、缘衣，素沙。辨外、内命妇之服，鞠衣、展衣、缘衣，素沙。",
        "translation": "内司服掌管王后所穿的六种服装，并辨别内外命妇各自应服的等差制度。",
        "note": "职责重在统掌后妃命妇服制等级，不是单纯的缝制工官。",
    },
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
    "巾车": {
        "summary": "掌公车政令、车用旗物与车辆出入调度。",
        "classical": "巾车掌公车之政令，辨其用与其旗物，而等叙之，以治其出入。",
        "translation": "巾车掌管公家车辆的制度与调度，辨别各种车的用途及所建旌旗，依等级次序配置，并统理车辆出入。",
        "note": "后文还细分王之五路、丧车与年终会计，这里先保留总职掌。",
    },
    "司暴": {
        "metaLabel": "建置",
        "meta": "十肆则一人。",
    },
    "车仆": {
        "summary": "掌诸戎车副贰，军旅会同供车，并掌大射三乏。",
        "classical": "车仆掌戎路之萃，广车之萃，阙车之萃，苹车之萃，轻车之萃。凡师共革车，各以其萃。会同亦如之。大丧廞革车。大射，共三乏。",
        "translation": "车仆掌管戎路、广车、阙车、苹车、轻车的副贰车辆；征伐和会同时供给相应革车，大丧时陈列明器车，又在大射礼中供给三乏。",
        "note": "“萃”指副车或备用车，是正车之外的随从车辆。",
    },
    "酂长": {
        "metaLabel": "建置",
        "meta": "每酂中士一人。",
    },
    "矿人": {
        "summary": "掌金玉锡石产地，划禁守护，并勘图授权开采。",
        "metaLabel": "建置",
        "meta": "中士二人、下士四人、府二人、史二人、胥四人、徒四十人。",
        "classical": "矿人掌金玉锡石之地，而为之厉禁以守之。若以时取之，则物其地图而授之，巡其禁令。",
        "translation": "矿人掌管金玉、锡石等矿产之地，划定禁界并加以守护；到了应当开采的时候，还要勘定矿区、绘图授人，并巡视是否有人违犯禁令。",
        "note": "兼具矿产保护、测绘分授与禁令巡察几项职责。",
    },
    "饎人": {
        "summary": "掌祭祀、王后日常与宾客飨食所需的簠簋饭食。",
        "classical": "饎人掌凡祭祀共盛，共王及后之六食。凡宾客共其簠簋之食，飨、食亦如之。",
        "translation": "饎人负责祭祀所用簠簋熟食的供给，也供王和王后的六谷饭食；接待宾客以及举行飨礼、食礼时，所需饭食同样由饎人备办。",
        "note": "5000言对应页题名缺字，但正文和叙官编制都能与“饎人”互相印证。",
    },
    "瞽矇": {
        "summary": "掌歌诗与诸乐器演奏，并佐大师教授《九德》、六诗。",
        "classical": "瞽矇掌播鼗、柷、敔、埙、箫、管、弦、歌，讽诵诗，世奠系，鼓琴瑟。掌《九德》、六诗之歌，以役大师。",
        "translation": "瞽矇掌演奏鼗、柷、敔、埙、箫、管、弦等乐器与歌唱，讽诵诗篇、世系等文字，并鼓琴瑟；又掌《九德》和六诗的歌唱，听从大师调度。",
        "note": "属于春官乐官体系中的盲乐工与歌诵之官。",
    },
    "视瞭": {
        "metaLabel": "建置",
        "meta": "三百人、府四人、史八人、胥十有二人、徒百有二十人。",
    },
    "廋人": {
        "summary": "掌十二闲政教与养马训练，并主持祭马祖等马政礼事。",
        "classical": "廋人掌十有二闲之政教，以阜马、佚特、教駣、攻驹，及祭马祖、祭闲之先牧，及执驹、散马耳、圉马。",
        "translation": "廋人掌十二闲的政令和教养事务，负责育肥马匹、安养种马、训练小马、调教驹马；并主持祭马祖、祭闲先牧，以及执驹、散马耳、圉马等养马事务。",
        "note": "原站对应页疑似串到了别条，这里按通行古籍所存正文补回。",
    },
    "原师": {
        "summary": "掌四方地名与原隰等地形物产，并辨可封邑之地。",
        "classical": "原师掌四方之地名，辨其丘、陵、坟、衍、原、隰之名物、之可以封邑者。",
        "translation": "原师掌管四方地形地名，辨别丘、陵、坟、衍、原、隰等地貌的名称与物产，并判断哪些地方适合划出封邑。",
        "note": "属于夏官中与地形、封邑和测土事务相连的一类官。",
    },
    "修闾氏": {
        "summary": "掌考核都城守宿巡夜与追胥捕盗之事，并行赏罚。",
        "classical": "修闾氏掌比国中宿、互、柝者，与其国粥，而比其追胥者，而赏罚之。",
        "translation": "修闾氏负责考核都城中值宿守卫、设互巡夜和击柝的人，以及由国家供食的羡卒，并按他们追捕外寇、伺察盗贼的成效施行赏罚。",
        "note": "偏向都城夜禁、巡逻和基层治安考核。",
    },
    "雕人": {
        "summary": "通行本正文已阙，现仅知其为负责雕琢的一类工匠。",
        "classical": "雕人，阙。",
        "translation": "现存《考工记》已不见雕人的正文。5000言仅保留解释说它大致属于负责雕琢的工匠，可能与骨角等器物的雕饰有关。",
        "note": "相关注疏多据字义推测其职责，难像其他工官那样恢复完整工序。",
    },
    "段氏": {
        "summary": "通行本正文已阙，题名只存于攻金之工次序中。",
        "classical": "段氏，阙。",
        "translation": "现存《考工记》没有保留下“段氏”的正文，通行整理本通常直接标作“段氏（阙）”。目前只能确认它列在攻金之工中，具体工序已不可详考。",
        "note": "多种整理本和考工图书都把这一条视作缺文。",
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

SECTION_ITEM_OVERRIDES = {
    ("地官", "槁人"): {
        "summary": "掌内外朝值勤口粮，并供养老飨礼之食，兼养祭犬。",
        "metaLabel": "建置",
        "meta": "奄八人、女槁每奄二人、奚五人。",
        "classical": "槁人掌共外、内朝冗食者之食。若飨耆老、孤子、士、庶子，共其食。掌豢祭祀之犬。",
        "translation": "地官槁人负责供给外朝、内朝值勤人员的饭食；国家以飨礼款待老人、孤子、士与庶子时，也由他供食，并兼管祭祀用犬的豢养。",
        "note": "这一条属于地官供给系统，和夏官掌兵工财料的同名“槁人”不是一回事。",
    },
    ("夏官", "槁人"): {
        "summary": "掌受财给工、考课弓矢成品，并总记出入账册。",
        "classical": "槁人掌受财于职金，以赍其工。弓六物为三等，弩四物亦如之。矢八物皆三等，箙亦如之。春献素，秋献成，书其等以飨工。乘其事，试其弓弩，以下上其食而诛赏。乃入功于司弓矢及缮人。凡赍财与其出入，皆在槁人，以待会而考之，亡者阙之。",
        "translation": "夏官槁人从职金领取财货转授工匠，分等登记弓、弩、矢、箙的成品质量，按春献素、秋献成的节点验收考课，并据制作优劣决定食粮与赏罚；财货和成品出入账册也都由槁人掌管。",
        "note": "相当于夏官兵甲工官里的财料发放、质检和会计角色。",
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


def strip_leading_clause_punctuation(text: str) -> str:
    return text.lstrip("，,：:；;。!?！？ ")


def strip_prefix(title: str, text: str) -> str:
    raw_title = raw_lookup_title(title)
    if text.startswith(raw_title + "之职，"):
        return "掌" + text[len(raw_title + "之职，") :]
    if text.startswith(raw_title + "掌"):
        return text[len(raw_title) :]
    if text.startswith(raw_title + "，"):
        return text[len(raw_title) + 1 :]
    if text.startswith(raw_title):
        return strip_leading_clause_punctuation(text[len(raw_title) :])
    return text


def normalize_punctuation(text: str) -> str:
    return (
        text.replace("　", "")
        .replace("..", "。")
        .replace("；。", "。")
        .replace("，，", "，")
        .strip()
    )


def normalize_fulltext(text: str) -> str:
    text = text.replace("\r", "")
    for raw_title, display_title in DISPLAY_TITLE_MAP.items():
        text = text.replace(raw_title, display_title)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
    lead = normalize_punctuation(text).split("。", 1)[0].strip()
    if not lead:
        return False
    if lead.startswith(("每", "凡")) and "掌" not in lead[:24]:
        return True
    if lead.startswith(PERSONNEL_START_MARKERS):
        return True
    if any(marker in lead[:24] for marker in ("掌", "之职", "为", "之事")):
        return False
    return looks_like_personnel(lead)


def build_orders(core_data: dict, raw_titles: dict) -> dict[str, list[str]]:
    orders: dict[str, list[str]] = {}
    core_sections = {section["key"]: section for section in core_data["sections"]}

    for section_key in SECTION_ORDER:
        existing = [
            normalize_display_title(item["title"])
            for item in core_sections[section_key]["items"]
        ]
        desired = []
        for item in raw_titles[section_key]:
            title = normalize_display_title(item["title"])
            if title not in desired:
                desired.append(title)

        for title in existing:
            if title not in desired:
                desired.append(title)

        orders[section_key] = desired

    return orders


def build_section_indexes(raw_text: str) -> dict[str, list[str]]:
    section_lines = {section: [] for section in SECTION_ORDER}
    current_section = None

    for raw_line in raw_text.splitlines():
        line = raw_line.strip().lstrip("　")
        if not line:
            continue

        for section_key, marker in SECTION_MARKERS.items():
            if marker in line:
                current_section = section_key
                break

        if current_section:
            section_lines[current_section].append(line)

    return section_lines


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


def find_description_indexes(lines: list[str], titles: list[str]) -> dict[str, int]:
    indexes: dict[str, int] = {}
    cursor = 0

    for title in titles:
        raw_title = raw_lookup_title(title)
        for idx in range(cursor, len(lines)):
            line = lines[idx]
            if not line.startswith(raw_title):
                continue
            if is_personnel_line(strip_leading_title(line, title)):
                continue
            indexes[title] = idx
            cursor = idx + 1
            break

    return indexes


def build_section_fulltexts(lines: list[str], titles: list[str]) -> tuple[str, dict[str, str]]:
    indexes = find_description_indexes(lines, titles)
    available_titles = [title for title in titles if title in indexes]
    item_texts: dict[str, str] = {}

    for position, title in enumerate(available_titles):
        start = indexes[title]
        end = indexes[available_titles[position + 1]] if position + 1 < len(available_titles) else len(lines)
        item_texts[title] = normalize_fulltext("\n".join(lines[start:end]))

    first_start = indexes[available_titles[0]] if available_titles else len(lines)
    prelude = normalize_fulltext("\n".join(lines[:first_start]))
    return prelude, item_texts


def normalize_personnel_text(text: str) -> str:
    text = (
        text.replace("", "。")
        .replace("．", "。")
        .replace("：", "")
        .replace(":", "")
        .replace("\n", "")
    )
    text = normalize_punctuation(text)
    return text.strip("，、； ")


def append_personnel_text(base: str, extra: str) -> str:
    base = base.strip()
    extra = extra.strip("，、； ")
    if not base:
        return extra
    if not extra:
        return base
    if base.endswith("。") or extra.startswith("。"):
        return base + extra
    return base + "。" + extra


def looks_like_personnel(snippet: str) -> bool:
    text = snippet.strip("，、； ")
    if not text:
        return False
    if text.startswith(("之职", "掌", "帅", "率", "使", "若", "凡", "乃", "以")):
        return False
    if text.startswith(PERSONNEL_START_MARKERS):
        return True
    if text.startswith(("每", "王", "倍", "旅", "五家", "二乡", "三乡", "四乡")):
        return True
    return bool(re.search(r"[一二三四五六七八九十百千两有]+人", text))


def build_personnel_map(prelude_text: str, titles: list[str]) -> dict[str, str]:
    normalized = normalize_fulltext(prelude_text)
    personnel_map: dict[str, str] = {}
    title_lookup = [(raw_lookup_title(title), title) for title in titles]

    for raw_line in normalized.splitlines():
        line = normalize_personnel_text(raw_line)
        if not line:
            continue

        previous_title: str | None = None
        sentences = [part for part in re.split(r"(?<=。)", line) if part]
        for sentence in sentences:
            matches = []
            for raw_title, title in title_lookup:
                start = 0
                while True:
                    pos = sentence.find(raw_title, start)
                    if pos == -1:
                        break
                    matches.append((pos, -len(raw_title), raw_title, title))
                    start = pos + len(raw_title)

            matches.sort()

            filtered = []
            for pos, neg_len, raw_title, title in matches:
                if filtered and pos == filtered[-1][0]:
                    continue
                if filtered and pos < filtered[-1][0] + len(filtered[-1][2]):
                    continue
                filtered.append((pos, neg_len, raw_title, title))

            if filtered:
                for idx, (pos, _neg_len, raw_title, title) in enumerate(filtered):
                    next_pos = filtered[idx + 1][0] if idx + 1 < len(filtered) else len(sentence)
                    snippet = normalize_personnel_text(sentence[pos + len(raw_title) : next_pos])
                    snippet = snippet.lstrip("，、； ").rstrip("，、； ")
                    if looks_like_personnel(snippet):
                        personnel_map[title] = snippet
                        previous_title = title
                continue

            extra = normalize_personnel_text(sentence).rstrip("，、； ")
            if previous_title and extra:
                personnel_map[previous_title] = append_personnel_text(personnel_map.get(previous_title, ""), extra)

    return personnel_map


def build_generated_item(
    lines: list[str], section_key: str, title: str, prelude_personnel: dict[str, str] | None = None
) -> dict:
    personnel = (prelude_personnel or {}).get(title) or find_personnel(lines, title)
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

    if personnel:
        item["metaLabel"] = "建置"
        item["meta"] = personnel

    return item


def apply_item_overrides(item: dict, section_key: str) -> dict:
    patched = dict(item)
    section_override = SECTION_ITEM_OVERRIDES.get((section_key, patched["title"]))
    if section_override:
        patched.update(section_override)
    override = ITEM_OVERRIDES.get(patched["title"])
    if override:
        patched.update(override)
    return patched


def extra_key(section_key: str, title: str) -> str:
    return f"{section_key}|||{title}"


def main() -> None:
    core_data = json.loads(CORE_PATH.read_text(encoding="utf-8"))
    full_titles = json.loads(FULL_TITLES_PATH.read_text(encoding="utf-8"))
    section_lines = build_section_indexes(RAW_TEXT_PATH.read_text(encoding="utf-8"))
    extras = json.loads(EXTRAS_PATH.read_text(encoding="utf-8")) if EXTRAS_PATH.exists() else {"sections": {}, "items": {}}
    extra_sections = extras.get("sections", {})
    extra_items = extras.get("items", {})

    core_sections = {section["key"]: section for section in core_data["sections"]}
    core_items = {
        section["key"]: {
            normalize_display_title(item["title"]): {**item, "title": normalize_display_title(item["title"])}
            for item in section["items"]
        }
        for section in core_data["sections"]
    }

    orders = build_orders(core_data, full_titles)

    output = {
        "meta": core_data["meta"],
        "sections": [],
    }

    for section_key in SECTION_ORDER:
        base_section = core_sections[section_key]
        prelude_text, local_fulltexts = build_section_fulltexts(section_lines[section_key], orders[section_key])
        prelude_personnel = build_personnel_map("\n".join(section_lines[section_key]), orders[section_key])
        section = {
            "key": base_section["key"],
            "title": base_section["title"],
            "seal": base_section["seal"],
            "desc": base_section["desc"],
            "sourceUrl": base_section["sourceUrl"],
            "commentaryUrl": SECTION_COMMENTARY_URLS.get(section_key, ""),
            "translationUrl": extra_sections.get(section_key, {}).get("translationUrl", ""),
            "items": [],
        }
        section_full_parts = [prelude_text] if prelude_text else []

        for title in orders[section_key]:
            if title in core_items[section_key]:
                item = dict(core_items[section_key][title])
            else:
                item = build_generated_item(section_lines[section_key], section_key, title, prelude_personnel)

            if not item.get("meta") and title in prelude_personnel:
                item["metaLabel"] = item.get("metaLabel") or "建置"
                item["meta"] = prelude_personnel[title]

            item = apply_item_overrides(item, section_key)

            extra_item = extra_items.get(extra_key(section_key, title), {})
            full_classical = extra_item.get("fullClassical") or local_fulltexts.get(title) or item.get("classical", "")
            full_translation = extra_item.get("fullTranslation") or item.get("translation", "")

            if full_classical:
                item["fullClassical"] = normalize_fulltext(full_classical)
                section_full_parts.append(item["fullClassical"])
            if full_translation:
                item["fullTranslation"] = normalize_fulltext(full_translation)
            if extra_item.get("pageUrl") and (extra_item.get("fullClassical") or extra_item.get("fullTranslation")):
                item["pageUrl"] = extra_item["pageUrl"]

            section["items"].append(item)

        section["fullClassical"] = "\n\n".join(part for part in section_full_parts if part)

        output["sections"].append(section)

    OUTPUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_JS.write_text("window.__SITE_DATA__ = " + json.dumps(output, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    counts = ", ".join(f"{section['key']} {len(section['items'])}" for section in output["sections"])
    print("built site-data:", counts)


if __name__ == "__main__":
    main()
