from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
FULL_TITLES_PATH = ROOT / "zhouli_data.json"
OUTPUT_PATH = ROOT / "zhouli_extras.json"
BASE_URL = "https://zhouli.5000yan.com/"

SECTION_BY_PATH = {
    "tianguan": "天官",
    "diguan": "地官",
    "chunguan": "春官",
    "xiaguan": "夏官",
    "qiuguan": "秋官",
    "dongguan": "冬官",
}

TITLE_NORMALIZATION = {
    "疱人": "庖人",
    "司剌": "司刺",
    "司虣": "司暴",
    "赞阝长": "酂长",
    "眡": "视瞭",
    "眡祲": "视祲",
    "鏄师": "镈师",
    "槀人": "槁人",
    "荒氏湅丝": "㡛氏湅丝",
    "氏为量": "栗氏为量",
    "陶人为": "陶人为甗",
    "瓬人为簋": "旊人为簋",
    "兵同强": "庐人为庐器",
    "司禄（阙）": "司禄",
    "x人": "饎人",
}

PAGE_URL_OVERRIDES = {
    ("地官", "饎人"): "https://zhouli.5000yan.com/diguan/ren/",
    ("春官", "瞽矇"): "https://zhouli.5000yan.com/chunguan/gu_/",
    ("夏官", "廋人"): "https://zhouli.5000yan.com/xiaguan/_ren/",
}

SKIP_FETCH = {
    ("夏官", "廋人"),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_URL,
}


def normalize_title(title: str) -> str:
    return TITLE_NORMALIZATION.get(title.strip(), title.strip())


def clean_text(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def parse_page(session: requests.Session, url: str) -> dict[str, str]:
    response = session.get(url, timeout=20)
    response.encoding = "utf-8"
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    classical_parts: list[str] = []
    translation_parts: list[str] = []

    for block in soup.select("div.list-group-flush.xiahuaxian1"):
        classical_node = block.select_one("div.d-flex.w-100.justify-content-between.pb-1")
        translation_node = block.select_one("p.mb-1.suiji")

        classical = clean_text(classical_node.get_text(" ", strip=True)) if classical_node else ""
        translation = clean_text(translation_node.get_text(" ", strip=True)) if translation_node else ""

        if classical:
            classical_parts.append(classical)
        if translation:
            translation_parts.append(translation)

    return {
        "fullClassical": "\n\n".join(classical_parts),
        "fullTranslation": "\n\n".join(translation_parts),
    }


def main() -> None:
    desired_titles = {
        section: {normalize_title(item["title"]) for item in items}
        for section, items in json.loads(FULL_TITLES_PATH.read_text(encoding="utf-8")).items()
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    homepage = session.get(BASE_URL, timeout=20)
    homepage.encoding = "utf-8"
    homepage.raise_for_status()
    soup = BeautifulSoup(homepage.text, "html.parser")

    section_data = {
        key: {
            "translationUrl": "",
            "commentaryUrl": "",
        }
        for key in desired_titles
    }
    item_urls: dict[tuple[str, str], str] = {}

    for anchor in soup.select("a[href]"):
        text = clean_text(anchor.get_text(" ", strip=True))
        href = anchor["href"]
        parsed = urlparse(href)
        parts = [part for part in parsed.path.split("/") if part]
        if not parts:
            continue

        path_key = parts[0]
        section_key = SECTION_BY_PATH.get(path_key)
        if not section_key:
            continue

        absolute_url = urljoin(BASE_URL, href)
        if len(parts) == 1:
            section_data[section_key]["translationUrl"] = absolute_url
            continue

        title = normalize_title(text)
        if title in desired_titles[section_key] and (section_key, title) not in item_urls:
            item_urls[(section_key, title)] = absolute_url

    for item_key, url in PAGE_URL_OVERRIDES.items():
        item_urls[item_key] = url

    output = {
        "sections": section_data,
        "items": {},
    }

    for (section_key, title), url in sorted(item_urls.items()):
        if (section_key, title) in SKIP_FETCH:
            continue

        try:
            page_data = parse_page(session, url)
        except Exception:
            continue

        if not page_data["fullClassical"] and not page_data["fullTranslation"]:
            continue

        entry = {"pageUrl": url}
        if page_data["fullClassical"]:
            entry["fullClassical"] = page_data["fullClassical"]
        if page_data["fullTranslation"]:
            entry["fullTranslation"] = page_data["fullTranslation"]
        output["items"][f"{section_key}|||{title}"] = entry

    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"wrote {OUTPUT_PATH.name}: {len(output['items'])} item refs")


if __name__ == "__main__":
    main()
