"""把 NeoDB「已看完」书架同步到 data/neodb_shelf.json，供「展馆」页面（content/museum）使用。
（博文里的 neodb 卡片用的是另一个文件 data/neodb.json，由 fetch_neodb.py 生成，两者互不影响。）

用法（在博客根目录）：
    PowerShell:  $env:NEODB_TOKEN = "你的 token"; python scripts/neodb_sync.py
    Bash:        NEODB_TOKEN=你的token python scripts/neodb_sync.py

token 在 NeoDB 网站「设置 → 更多 → 开发者」(https://neodb.social/developer/) 里生成，
不要写进仓库。跑完后提交 data/neodb_shelf.json 即可，Vercel 构建时只读这个文件，不联网。
GitHub Action（.github/workflows/neodb-sync.yml）每天会自动跑一次。

自动处理：
- 公开和「仅关注者可见」的标记都收录，只有「仅自己可见」的不放出来；
- 同一部剧的同一季在 NeoDB 有多个条目（比如豆瓣、TMDB 各一个）又都标记了的，只保留一条；
- 封面是豆瓣「暂无海报」占位图的，依次尝试：这部剧的总封面 → NeoDB 上同名条目的封面；
- 分类直接用 NeoDB 自己的类别：书籍、电影、剧集、游戏、音乐；播客和演出归到「其他」，卡片上带小标签。
  想改某一条的分类，在 neodb_overrides.json 里用 category 指定。
- 每次都重新拉整个书架，条目标题、封面在 NeoDB 上改了也会跟着更新；
  剧集详情（用来判断重复的季）的缓存 7 天过期，过期后重新取。
手动修正写在 scripts/neodb_overrides.json（见文件里的说明）。
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://neodb.social/api"
SITE = "https://neodb.social"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "neodb_shelf.json"
OVERRIDES = Path(__file__).resolve().parent / "neodb_overrides.json"
# 条目详情的本地缓存（只用来少发请求，不提交，删掉也没关系）
CACHE = Path(__file__).resolve().parent / ".neodb-cache.json"

# NeoDB 类别 → 展馆分类；不在这里的（播客、演出等）归到「其他」
CATEGORY = {"book": "book", "movie": "movie", "tv": "tv", "game": "game", "music": "music"}
# 「其他」里的小标签
SUBTYPE = {"podcast": "播客", "performance": "演出"}
# 详情缓存多久过期（秒）
CACHE_MAX_AGE = 7 * 24 * 3600

# 豆瓣「暂无海报」占位图只有几 KB，真封面都远大于这个
PLACEHOLDER_MAX_BYTES = 8000

TOKEN = ""


def request(url, method="GET"):
    headers = {
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        # NeoDB 会拒绝 Python 默认的 User-Agent（403），换成自己的名字
        "User-Agent": "neodb-sync-script/1.0",
    }
    if TOKEN and url.startswith(API):
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers, method=method)
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError:
            raise
        except Exception as e:  # 网络抖动时重试两次
            if attempt == 2:
                raise
            print(f"  请求失败，重试：{e}", file=sys.stderr)
            time.sleep(2)


def get(path):
    with request(API + path) as r:
        return json.load(r)


def absolute(url):
    return SITE + url if url and url.startswith("/") else (url or "")


_cache = {}


def cached(api_path):
    entry = _cache.get(api_path)
    return isinstance(entry, dict) and time.time() - entry.get("t", 0) < CACHE_MAX_AGE


def detail(api_path):
    """条目详情（类型、季号等），带本地缓存"""
    if not cached(api_path):
        try:
            _cache[api_path] = {"t": time.time(), "d": get(api_path)}
        except urllib.error.HTTPError as e:
            # 条目在 NeoDB 上已不存在（404 等），记下来，下次不再请求
            _cache[api_path] = {"t": time.time(), "d": {}}
            print(f"  取详情失败：{api_path} {e}", file=sys.stderr)
        except Exception as e:  # 网络问题不缓存，下次再试
            print(f"  取详情失败：{api_path} {e}", file=sys.stderr)
            return {}
    return _cache[api_path]["d"]


def is_placeholder(cover):
    if not cover:
        return True
    try:
        with request(cover, method="HEAD") as r:
            size = int(r.headers.get("Content-Length") or 0)
            return 0 < size < PLACEHOLDER_MAX_BYTES
    except Exception:
        return True


def better_cover(item):
    """占位封面的替代：这部剧的总封面 → 同名条目的封面"""
    parent = item.get("parent_uuid")
    if parent:
        try:
            cover = absolute(get(f"/tv/{parent}").get("cover_image_url"))
            if not is_placeholder(cover):
                return cover
        except Exception:
            pass
    title = item.get("display_title") or item.get("title") or ""
    results = []
    # 先用完整标题搜，搜不到再用空格前的剧名（「热血司祭 第二季」→「热血司祭」）
    for query in dict.fromkeys([title, title.split(" ")[0]]):
        try:
            q = urllib.parse.quote(query)
            results += get(f"/catalog/search?query={q}&category={item['category']}").get("data", [])
        except Exception:
            pass
    for other in results:
        if other.get("uuid") == item.get("uuid"):
            continue
        if other.get("type") == item.get("type") and other.get("display_title") == item.get("display_title"):
            cover = absolute(other.get("cover_image_url"))
            if not is_placeholder(cover):
                return cover
    return ""


def main():
    global TOKEN
    TOKEN = os.environ.get("NEODB_TOKEN", "").strip()
    if not TOKEN:
        sys.exit("没有找到 NEODB_TOKEN 环境变量，用法见脚本开头的说明。")

    overrides = {}
    if OVERRIDES.exists():
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")).get("items", {})

    # 不按类别分开请求（分开请求会漏条目），一次拉完整个书架
    marks, page, pages = [], 1, 1
    while page <= pages:
        data = get(f"/me/shelf/complete?page={page}&page_size=100")
        pages = data.get("pages") or 1
        marks += data.get("data", [])
        print(f"书架：第 {page}/{pages} 页")
        page += 1

    # 只排除「仅自己可见」（visibility = 2）
    marks = [m for m in marks if m.get("visibility", 0) != 2]

    # 同一部剧有多个季的条目时，要看详情里的季号判断是否重复，先一起取（有缓存的不再请求）
    global _cache
    if CACHE.exists():
        _cache = json.loads(CACHE.read_text(encoding="utf-8"))
    parents = {}
    for m in marks:
        if m["item"].get("type") == "TVSeason" and m["item"].get("parent_uuid"):
            parents[m["item"]["parent_uuid"]] = parents.get(m["item"]["parent_uuid"], 0) + 1
    paths = {m["item"]["api_url"].removeprefix("/api") for m in marks if parents.get(m["item"].get("parent_uuid"), 0) > 1}
    todo = [p for p in paths if not cached(p)]
    print(f"条目详情：{len(paths)} 个，需要请求 {len(todo)} 个")
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(detail, todo))
    CACHE.write_text(json.dumps(_cache, ensure_ascii=False), encoding="utf-8")

    # 同一部剧的同一季有多个条目时只留一条（优先留有短评/评分的，其次留最新标记的）
    seasons = {}
    for m in marks:
        item = m.get("item") or {}
        if item.get("type") == "TVSeason" and item.get("parent_uuid"):
            seasons.setdefault(item["parent_uuid"], []).append(m)
    drop = set()
    for parent, group in seasons.items():
        if len(group) < 2:
            continue
        # 季号和集数都相同才算同一季（JOJO 石之海 Part.1/Part.2 季号相同但是不同部分）
        by_season = {}
        for m in group:
            d = detail(m["item"]["api_url"].removeprefix("/api"))
            key = (d.get("season_number"), d.get("episode_count"))
            by_season.setdefault(key, []).append(m)
        for (season, _), dups in by_season.items():
            if season is None or len(dups) < 2:
                continue
            dups.sort(key=lambda m: (bool(m.get("comment_text") or m.get("rating_grade")), m["created_time"]), reverse=True)
            keep = dups[0]["item"]
            for m in dups[1:]:
                item = m["item"]
                # 标题一样，或者其中一个是没有外部来源的「空壳」条目，才当作重复
                bare = not item.get("external_resources") or not keep.get("external_resources")
                if item.get("display_title") == keep.get("display_title") or bare:
                    drop.add(item["uuid"])
                    print(f"  重复的季，已去掉：{item['display_title']} {absolute(item['url'])}")
    marks = [m for m in marks if m["item"]["uuid"] not in drop]

    def classify(item):
        return CATEGORY.get(item.get("category", ""), "other")

    items = []
    for m in marks:
        item = m["item"]
        url = absolute(item.get("url"))
        cat = item.get("category", "")
        grade = m.get("rating_grade")
        entry = {
            "category": classify(item),
            "subtype": SUBTYPE.get(cat, ""),
            "title": item.get("display_title") or item.get("title") or "",
            "url": url,
            "cover": absolute(item.get("cover_image_url")),
            # 标记为「看过」的时间，按它分年份
            "date": (m.get("created_time") or "")[:10],
            # NeoDB 的打分是 1–10，页面上换算成 5 星
            "rating": grade / 2 if grade else None,
            "comment": (m.get("comment_text") or "").strip(),
        }
        fix = overrides.get(url, {})
        if fix.get("hide"):
            continue
        if not fix.get("cover") and entry["cover"].endswith(".png") and is_placeholder(entry["cover"]):
            # 豆瓣的占位图都是 png，只检查 png 封面，省得每张都请求一次
            new = better_cover(item)
            print(f"  占位封面：{entry['title']} → {new or '没找到替代，请写进 neodb_overrides.json'}")
            entry["cover"] = new
        entry.update({k: v for k, v in fix.items() if k != "hide"})
        items.append(entry)

    items.sort(key=lambda x: x["date"], reverse=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    count = {}
    for it in items:
        count[it["category"]] = count.get(it["category"], 0) + 1
    print(f"完成，共 {len(items)} 条：{count}，已写入 {OUT}")


if __name__ == "__main__":
    main()
