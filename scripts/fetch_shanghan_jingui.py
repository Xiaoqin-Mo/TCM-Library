#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取古诗文网《伤寒论》(24篇) 与《金匮要略》(25篇) 原文。

来源：
  伤寒论 https://www.gushiwen.cn/guwen/book_37.aspx
  金匮要略 https://www.gushiwen.cn/guwen/book.aspx?id=193
每篇一文件：raw/shanghan/shanghan_<NN>.txt、raw/jingui/jingui_<NN>.txt
正文取 <div class="contson">。低并发 + 重试退避，避免限流。
"""
import concurrent.futures
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# (篇号, 篇名, hash)
SHANGHAN = [
    (1, "辨脉法", "7e7d78aa554e"), (2, "平脉法", "fbe3cc533c22"),
    (3, "伤寒例", "8a3d9408f561"), (4, "辨痉湿暍脉证", "e54900649bbc"),
    (5, "辨太阳病脉证并治上", "76830830c37f"), (6, "辨太阳病脉证并治中", "d933b0c0b061"),
    (7, "辨太阳病脉证并治下", "fbae5ba41d2a"), (8, "辨阳明病脉证并治", "89f74c9eb41e"),
    (9, "辨少阳病脉证并治", "61ea42119afe"), (10, "辨太阴病脉证并治", "2d644310e118"),
    (11, "辨少阴病脉证并治", "9f14c49a0d06"), (12, "辨厥阴病脉证并治", "c79d6aa70c36"),
    (13, "辨霍乱病脉证并治", "962cd3cf3049"), (14, "辨阴阳易差后劳复病脉证并治", "97aa7b64b65d"),
    (15, "辨不可发汗病脉证并治", "7de92cfae3d4"), (16, "辨可发汗脉证并治", "9809939940d1"),
    (17, "辨发汗后病脉证并治", "ed5a26ca1a35"), (18, "辨不可吐", "7d1e195da222"),
    (19, "辨可吐", "92dee3809514"), (20, "辨不可下病脉证并治", "668892c3e0e1"),
    (21, "辨可下病脉证并治", "cd4cc91889db"), (22, "辨发汗吐下后脉证并治", "f413ab74bdda"),
    (23, "伤寒论序一", "670906246500"), (24, "伤寒论序二", "3932bed39b65"),
]
JINGUI = [
    (1, "脏腑经络先后病脉证", "1cc4b889d405"), (2, "痉湿暍病脉证治", "67af335cd918"),
    (3, "百合狐惑阴阳毒病证治", "be9ca65b159f"), (4, "疟病脉证并治", "7096fe110677"),
    (5, "中风历节病脉证并治", "346fded321f4"), (6, "血痹虚劳病脉证并治", "7c0e14e4a702"),
    (7, "肺痿肺痈咳嗽上气病脉证治", "090dfb1f296d"), (8, "奔豚气病脉证治", "6011efdb146c"),
    (9, "胸痹心痛短气病脉证治", "031c11141249"), (10, "腹满寒疝宿食病脉证治", "173e7ff163bd"),
    (11, "五藏风寒积聚病脉证并治", "17fc18e7352c"), (12, "痰饮咳嗽病脉证并治", "f31eded928f7"),
    (13, "消渴小便不利淋病脉证并治", "e4723c49896a"), (14, "水气病脉证并治", "944b026f6e13"),
    (15, "黄疸病脉证并治", "9f5df33df05b"), (16, "惊悸吐血下血胸满瘀血病脉证治", "207ff725f743"),
    (17, "呕吐哕下利病脉证治", "3b123175a353"), (18, "疮痈肠痈浸淫病脉证并治", "a7d0c2cd5e31"),
    (19, "趺蹶手指臂肿转筋阴狐疝蛔虫病脉证治", "f8068c7c536a"), (20, "妇人妊娠病脉证并治", "c0aa1a435718"),
    (21, "妇人产后病脉证治", "20c214e0a49b"), (22, "妇人杂病脉证并治", "c27f211057ac"),
    (23, "杂疗方", "36a5caec0eca"), (24, "禽兽鱼虫禁忌并治", "cc897e8e1c1b"),
    (25, "果实菜谷禁忌并治", "128ad09ed57b"),
]


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


def worker(item, sub: str, book: str, source_url: str):
    num, title, hid = item
    out_dir = ROOT / "raw" / sub
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{book}_{num:02d}.txt"
    fpath = out_dir / fname
    if fpath.exists() and fpath.stat().st_size > 100:
        return num, title, "skip"
    url = f"https://www.gushiwen.cn/guwen/bookv_{hid}.aspx"
    html = fetch_one(url)
    body = extract_body(html)
    head = f"# {book} {title}（第{num}篇）\n# 来源：{source_url}\n# 抓取页：{url}\n\n"
    (out_dir / fname).write_text(head + body + "\n", encoding="utf-8")
    time.sleep(0.4)
    return num, title, len(body)


def run(name, items, sub, book, source_url):
    ok, fail = 0, []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(worker, it, sub, book, source_url): it for it in items}
        for f in concurrent.futures.as_completed(futs):
            try:
                num, title, ln = f.result()
                ok += 1
                if isinstance(ln, int) and ln < 100:
                    print(f"[WARN] {title} len={ln}")
            except Exception as e:
                fail.append((futs[f][0], futs[f][1], str(e)[:60]))
    print(f"{name}: {ok}/{len(items)} 完成", f"失败 {len(fail)}" if fail else "")
    if fail:
        print("失败:", fail[:8])


def main():
    run("伤寒论", SHANGHAN, "shanghan", "shanghan",
        "https://www.gushiwen.cn/guwen/book_37.aspx")
    time.sleep(3)
    run("金匮要略", JINGUI, "jingui", "jingui",
        "https://www.gushiwen.cn/guwen/book.aspx?id=193")


if __name__ == "__main__":
    main()
