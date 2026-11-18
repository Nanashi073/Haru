"""抓取文章中 {{< neodb "URL" >}} 短代码对应的条目信息，写入 data/neodb.json。

用法（在仓库根目录）：
    python scripts/fetch_neodb.py           # 只抓取 data/neodb.json 里还没有的条目
    python scripts/fetch_neodb.py --all     # 全部重新抓取

写新文章用了新的 neodb 短代码后跑一次再提交即可；没抓到的条目在页面上会显示为原链接。
"""

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "data" / "neodb.json"
API = "https://neodb.social/api/"
SHORTCODE = re.compile(r'\{\{<\s*neodb\s+"([^"]+)"')
HEADERS = {"User-Agent": "hugo-blog-neodb-cache/1.0", "Accept": "application/json"}


def api_url(url: str) -> str:
    m = re.match(r"https?://neodb\.social/(.+?)/?$", url)
    if m:
        return API + m.group(1)
    return API + "catalog/fetch?url=" + urllib.parse.quote(url, safe="")


def localized(entries) -> dict:
    """[{lang, text}, ...] -> {lang: text}，同一语言有多条时取第一条。"""
    out = {}
    for e in entries or []:
        if e.get("text"):
            out.setdefault(e.get("lang"), e["text"])
    return out


def fetch(url: str):
    req = urllib.request.Request(api_url(url), headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:  # 会自动跟随 302 跳转到条目
            if r.status != 200:
                return None
            item = json.load(r)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"  ! {url}: {e}", file=sys.stderr)
        return None
    if not item.get("title"):
        return None  # 202：NeoDB 还在后台抓取，下次再试
    titles = localized(item.get("localized_title"))
    descs = localized(item.get("localized_description"))
    brief = descs.get("zh-cn") or descs.get("zh") or descs.get("zh-tw") or item.get("brief") or ""
    return {
        "title": titles.get("zh-cn") or titles.get("zh") or item.get("display_title") or item["title"],
        "cover": item.get("cover_image_url") or "",
        "brief": re.sub(r"\s+", " ", brief.replace("　", " ")).strip(),
        "category": item.get("category") or "",
        "rating": item.get("rating"),
        "neodb": item.get("url") and urllib.parse.urljoin("https://neodb.social", item["url"]),
    }


def main():
    refetch = "--all" in sys.argv
    urls = sorted({u for p in CONTENT.rglob("*.md") for u in SHORTCODE.findall(p.read_text(encoding="utf-8"))})
    data = {} if refetch or not OUT.exists() else json.loads(OUT.read_text(encoding="utf-8"))
    todo = [u for u in urls if u not in data]
    print(f"{len(urls)} 个条目，需要抓取 {len(todo)} 个")
    for i, u in enumerate(todo, 1):
        item = fetch(u)
        print(f"[{i}/{len(todo)}] {'ok ' if item else 'miss'} {u}")
        if item:
            data[u] = item
        time.sleep(1)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"已写入 {OUT.relative_to(ROOT)}：{len(data)}/{len(urls)} 个条目")


if __name__ == "__main__":
    main()
