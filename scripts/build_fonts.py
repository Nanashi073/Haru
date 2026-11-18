"""把 font/ 里的 TTF 切成按需加载的 woff2 分片，生成 static/fonts/<名字>/ 和 assets/css/fonts.css。

用法（在仓库根目录，需要 pip install fonttools brotli）：
    python scripts/build_fonts.py

分片方式（与 Google Fonts 的中文字体相同思路）：
  - 第 0 片：ASCII、拉丁字母、常用标点、全角符号
  - 之后：站内文章里出现过的字，按出现频率每 FREQ_CHUNK 个字一片
  - 兜底：字体里的全部字按码位每 TAIL_CHUNK 个一片（与上面重叠，保证 unicode-range 是连续区间、CSS 小）
每片在 @font-face 里用 unicode-range 声明，浏览器只下载页面上实际出现的字所在的分片。
多个 @font-face 覆盖同一个字时，后声明的优先，所以 CSS 里按“兜底 → 常用 → 基础”的顺序输出。
字体本身的覆盖范围不变，新文章不需要重新生成；想让常用字分片更贴合新内容时再跑一次即可。
"""

import os
import re
import shutil
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "font"
OUT = ROOT / "static" / "fonts"
CSS = ROOT / "assets" / "css" / "fonts.css"

# 字体文件名 -> CSS font-family 名（要和 assets/css/root.css 里的变量一致）
FONTS = {"jinghua": "jinghua", "zhaohuaA": "zhaohuaA"}
FREQ_CHUNK = 300
FREQ_LIMIT = 3000   # 站内最常用的前 N 个字单独成片（目前约覆盖 99.9% 的正文）
TAIL_CHUNK = 500
BASE_RANGES = [(0x20, 0x7E), (0xA0, 0x24F), (0x2000, 0x206F), (0x2100, 0x214F), (0x2190, 0x21FF),
               (0x2460, 0x24FF), (0x2500, 0x25FF), (0x2600, 0x26FF), (0x3000, 0x303F), (0xFF00, 0xFFEF)]


def content_frequency() -> Counter:
    c = Counter()
    for p in (ROOT / "content").rglob("*.md"):
        c.update(ord(ch) for ch in p.read_text(encoding="utf-8"))
    return c


def plan_chunks(cmap: set[int], freq: Counter) -> list[list[int]]:
    base = sorted(cp for lo, hi in BASE_RANGES for cp in range(lo, hi + 1) if cp in cmap)
    taken = set(base)
    common = [cp for cp, _ in freq.most_common() if cp in cmap and cp not in taken][:FREQ_LIMIT]
    tail = sorted(cmap - taken)
    # 按声明顺序返回：兜底 -> 常用（低频到高频）-> 基础，后声明的优先匹配
    chunks = [tail[i:i + TAIL_CHUNK] for i in range(0, len(tail), TAIL_CHUNK)]
    freq_chunks = [common[i:i + FREQ_CHUNK] for i in range(0, len(common), FREQ_CHUNK)]
    chunks += freq_chunks[::-1]
    chunks.append(base)
    return [c for c in chunks if c]


def unicode_range(cps: list[int]) -> str:
    cps = sorted(cps)
    parts, start, prev = [], cps[0], cps[0]
    for cp in cps[1:] + [None]:
        if cp is not None and cp == prev + 1:
            prev = cp
            continue
        parts.append(f"U+{start:x}" if start == prev else f"U+{start:x}-{prev:x}")
        if cp is not None:
            start = prev = cp
    return ",".join(parts)


def build_chunk(args):
    src, dst, cps = args
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.hinting = False
    opts.desubroutinize = True
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    font = TTFont(src, recalcBBoxes=False, recalcTimestamp=False)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=cps)
    sub.subset(font)
    font.flavor = "woff2"
    font.save(dst)
    return dst.stat().st_size


def main():
    freq = content_frequency()
    css = ["/* 由 scripts/build_fonts.py 生成，请勿手改 */"]
    jobs, meta = [], []
    for name, family in FONTS.items():
        src = SRC / f"{name}.ttf"
        cmap = set(TTFont(src, lazy=True).getBestCmap())
        chunks = plan_chunks(cmap, freq)
        out = OUT / name
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)
        for i, cps in enumerate(chunks):
            jobs.append((src, out / f"{i:03d}.woff2", cps))
            css.append(
                "@font-face{font-family:'%s';font-style:normal;font-weight:400;font-display:swap;"
                "src:url('/fonts/%s/%03d.woff2') format('woff2');unicode-range:%s}"
                % (family, name, i, unicode_range(cps)))
        meta.append((name, len(chunks)))
    with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
        sizes = list(ex.map(build_chunk, jobs))
    CSS.write_text("\n".join(css) + "\n", encoding="utf-8", newline="\n")
    for name, n in meta:
        total = sum((OUT / name / f"{i:03d}.woff2").stat().st_size for i in range(n))
        print(f"{name}: {n} 片，共 {total / 1e6:.1f} MB")
    print(f"已写入 {CSS.relative_to(ROOT)}（{CSS.stat().st_size / 1e3:.0f} KB）")


if __name__ == "__main__":
    main()
