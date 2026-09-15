#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 shiwens.cn《难经》81 难原文到 raw/nanjing/。

来源：https://www.shiwens.cn/book_286.html（一难~八十一难，bookv_17147~17227.html）
"""
import concurrent.futures
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SOURCE = "https://www.shiwens.cn/book_286.html"
CN = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
      "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
      "二十一", "二十二", "二十三", "二十四", "二十五", "二十六", "二十七", "二十八", "二十九", "三十",
      "三十一", "三十二", "三十三", "三十四", "三十五", "三十六", "三十七", "三十八", "三十九", "四十",
      "四十一", "四十二", "四十三", "四十四", "四十五", "四十六", "四十七", "四十八", "四十九", "五十",
      "五十一", "五十二", "五十三", "五十四", "五十五", "五十六", "五十七", "五十八", "五十九", "六十",
      "六十一", "六十二", "六十三", "六十四", "六十五", "六十六", "六十七", "六十八", "六十九", "七十",
      "七十一", "七十二", "七十三", "七十四", "七十五", "七十六", "七十七", "七十八", "七十九", "八十",
      "八十一"]
ITEMS = [(i + 1, f"{CN[i]}难", 17147 + i) for i in range(81)]


def fetch_one(url: str) -> str:
    last = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


def extract_body(html: str) -> str:
    m = re.search(r'<div class="contson"[^>]*>(.*?)</div>', html, re.S)
    if not m:
        return ""
    body = m.group(1)
    body = re.sub(r"<br\s*/?>", "\n", body)
    body = re.sub(r"<[^>]+>", "", body)
    body = body.replace("\u3000", "\n")
    body = re.sub(r"\n{2,}", "\n", body)
    return body.strip()


def worker(item):
    num, title, pid = item
    out_dir = ROOT / "raw" / "nanjing"
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"nanjing_{num:02d}.txt"
    fpath = out_dir / fname
    if fpath.exists() and fpath.stat().st_size > 100:
        return num, title, "skip"
    url = f"https://www.shiwens.cn/bookv_{pid}.html"
    html = fetch_one(url)
    body = extract_body(html)
    head = f"# nanjing {title}（第{num}难）\n# 来源：{SOURCE}\n# 抓取页：{url}\n\n"
    (out_dir / fname).write_text(head + body + "\n", encoding="utf-8")
    time.sleep(0.4)
    return num, title, len(body)


def main():
    ok, fail = 0, []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(worker, it): it for it in ITEMS}
        for f in concurrent.futures.as_completed(futs):
            try:
                num, title, ln = f.result()
                ok += 1
                if isinstance(ln, int) and ln < 100:
                    print(f"[WARN] {title} len={ln}")
            except Exception as e:
                fail.append((futs[f][0], futs[f][1], str(e)[:60]))
    print(f"难经: {ok}/81 完成", f"失败 {len(fail)}" if fail else "")
    if fail:
        print("失败:", fail[:8])


if __name__ == "__main__":
    main()
