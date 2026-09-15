#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取古诗文网《黄帝内经》（素问 1-81 + 灵枢 82-162）原文到 raw/neijing/。

来源：古诗文网《黄帝内经》全书页
  https://www.gushiwen.cn/guwen/book_1bf1210e9d1f.aspx
每篇一文件：raw/neijing/suwen/suwen_<NN>.txt、raw/neijing/lingshu/lingshu_<NN>.txt
正文取 <div class="contson">，全角空格分段。
纯标准库（urllib + concurrent.futures）。
"""
import concurrent.futures
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "neijing"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SOURCE = "古诗文网《黄帝内经》全书页 https://www.gushiwen.cn/guwen/book_1bf1210e9d1f.aspx"

# (篇号, 篇名, URL) —— 素问 1-81
SUWEN = [
    (1, "上古天真论", "53d8182777bb"), (2, "四气调神大论", "bc64b64d257b"),
    (3, "生气通天论", "a4a649f6d43d"), (4, "金匮真言论", "da1a639e7f78"),
    (5, "阴阳应象大论", "86edca3658d5"), (6, "阴阳离合论", "0d6883ab38a0"),
    (7, "阴阳别论", "9aa536999e4a"), (8, "灵兰秘典论", "b5483a78b6a4"),
    (9, "六节藏象论", "c9a57be7ae5a"), (10, "五藏生成", "0f86686ab4b2"),
    (11, "五藏别论", "6874128b1ed9"), (12, "异法方宜论", "e30b46282d88"),
    (13, "移精变气论", "bac6f982ed1a"), (14, "汤液醪醴论", "d49f261a8e92"),
    (15, "玉版论要", "227ab5815b7c"), (16, "诊要经终论", "61e6f21e1b4b"),
    (17, "脉要精微论", "9f2417d39628"), (18, "平人气象论", "6b7e270c8dc2"),
    (19, "玉机真藏论", "1782aca5fe96"), (20, "三部九候论", "6b8379153a46"),
    (21, "经脉别论", "aa1c1b681d87"), (22, "藏气法时论", "71eb8ff2a364"),
    (23, "宣明五气", "d71107ebbb88"), (24, "血气形志", "86ab643065e8"),
    (25, "宝命全形论", "fa23d7b20d28"), (26, "八正神明论", "a54f810d9b11"),
    (27, "离合真邪论", "53407ebb4cb3"), (28, "通评虚实论", "47828fbe372c"),
    (29, "太阴阳明论", "aabf184d4c9a"), (30, "阳明脉解", "1cf8c365cb58"),
    (31, "热论", "79951ed25721"), (32, "刺热", "b4fbde49260c"),
    (33, "评热病论", "5950bed8c180"), (34, "逆调论", "65890951c1ff"),
    (35, "疟论", "142155c717ac"), (36, "刺疟", "dd24ffd54ebb"),
    (37, "气厥论", "86d2f2ee1ce1"), (38, "咳论", "c07fdd6ee732"),
    (39, "举痛论", "8250b8d56cf2"), (40, "腹中论", "b28037503364"),
    (41, "刺腰痛", "7affe8053055"), (42, "风论", "43eee6f84ebe"),
    (43, "痹论", "138caf67f10b"), (44, "痿论", "4210697652e3"),
    (45, "厥论", "247a7a8afad2"), (46, "病能论", "442776f64ec3"),
    (47, "奇病论", "02181d3fbb54"), (48, "大奇论", "d05a2d0c6f91"),
    (49, "脉解", "d4675cfc7191"), (50, "刺要论", "99206e3b766b"),
    (51, "刺齐论", "2abe16843485"), (52, "刺禁论", "3bd7802ac00e"),
    (53, "刺志论", "6716b579936b"), (54, "针解", "f7fe5f7a6a04"),
    (55, "长刺节论", "0369a4632c3b"), (56, "皮部论", "f5c30617d75f"),
    (57, "经络论", "b7f966d67a2d"), (58, "气穴论", "130f8f105b7b"),
    (59, "气府论", "0382f8e934fc"), (60, "骨空论", "2767dd560d2d"),
    (61, "水热穴论", "fc4040fe6d1e"), (62, "调经论", "2be7a5dee1c2"),
    (63, "缪刺论", "700792553ce2"), (64, "四时刺逆从论", "ccec7cb97bc5"),
    (65, "标本病传论", "72a665d5cf3a"), (66, "天元纪大论", "125add07829b"),
    (67, "五运行大论", "0b1098cc092d"), (68, "六微旨大论", "8f284a48df5c"),
    (69, "气交变大论", "4cbdcf2d68e3"), (70, "五常政大论", "6e96ff9ee831"),
    (71, "六元正纪大论", "a2fa930cb186"), (72, "刺法论", "bbfed0fe272e"),
    (73, "本病论", "70754507aff3"), (74, "至真要大论", "4e24073702b0"),
    (75, "著至教论", "25497c453a3d"), (76, "示从容论", "413f03552d36"),
    (77, "疏五过论", "6b7435191586"), (78, "徵四失论", "1f10da0fa1ab"),
    (79, "阴阳类论", "2cbbc4c2c007"), (80, "方盛衰论", "9b8985740058"),
    (81, "解精微论", "f482da421029"),
]
# 灵枢 82-162（篇号 1-81）
LINGSHU = [
    (1, "九针十二原", "b6b9be792a1b"), (2, "本输", "bf68286fdb66"),
    (3, "小针解", "54f960ac0430"), (4, "邪气藏府病形", "90c8bf323bf9"),
    (5, "根结", "8ccca3b3baf6"), (6, "寿夭刚柔", "e0bd5b5cb04f"),
    (7, "官针", "ca659eb804ea"), (8, "本神", "c606190a0580"),
    (9, "终始", "b7bf935aafe4"), (10, "经脉", "d72d8d8c8ae0"),
    (11, "经别", "c098c2c341d9"), (12, "经水", "05a7d235756c"),
    (13, "经筋", "2cd643304856"), (14, "骨度", "7b997af17c6c"),
    (15, "五十营", "28f01bf7a847"), (16, "营气", "db12d7e15613"),
    (17, "脉度", "ebae8950dad5"), (18, "营卫生会", "58998b4fe32e"),
    (19, "四时气", "58a326e3972d"), (20, "五邪", "92a21c392bab"),
    (21, "寒热病", "9003f8b283cf"), (22, "癫狂", "f564831dd548"),
    (23, "热病", "b15ea04c85bc"), (24, "厥病", "5fe068a58e76"),
    (25, "病本", "8e268d9f230c"), (26, "杂病", "bb28d0159b3b"),
    (27, "周痹", "72a9a6db175b"), (28, "口问", "cc7d1d9d873b"),
    (29, "师传", "aa68fbc0f178"), (30, "决气", "8bb78efa3fce"),
    (31, "肠胃", "71791e298c5d"), (32, "平人绝谷", "ea4649bbd10b"),
    (33, "海论", "eb54f19df492"), (34, "五乱", "92c576250ac6"),
    (35, "胀论", "310e90e9c5d6"), (36, "五癃津液别", "f5caf18de4f2"),
    (37, "五阅五使", "a885c4dc053c"), (38, "逆顺肥瘦", "4e2f7826b99d"),
    (39, "血络论", "822e344e4ed2"), (40, "阴阳清浊", "c1c1ca944767"),
    (41, "阴阳系日月", "69ab3b65b510"), (42, "病传", "eea940b85304"),
    (43, "淫邪发梦", "4ef0d67f4057"), (44, "顺气一日分为四时", "8a4ec991a77b"),
    (45, "外揣", "c18033e784ca"), (46, "五变", "abcc27b88d18"),
    (47, "本藏", "2bbec5fe38f6"), (48, "禁服", "9b45c2fcaa86"),
    (49, "五色", "e181a12a433b"), (50, "论勇", "72d9e791e18e"),
    (51, "背俞", "386b6764761e"), (52, "卫气", "a4b7998c0b3a"),
    (53, "论痛", "4aa676d80da7"), (54, "天年", "efcd4423396d"),
    (55, "逆顺", "d6abcfd45b51"), (56, "五味", "bd8a559f7552"),
    (57, "水胀", "1e7b73164323"), (58, "贼风", "51cac8c4655e"),
    (59, "卫气失常", "eaf885db2a64"), (60, "玉版", "701aa64629ca"),
    (61, "五禁", "92c2109428fc"), (62, "动输", "8d4b0928cf34"),
    (63, "五味论", "c37f7b58ee1d"), (64, "阴阳二十五人", "33dc100c3b16"),
    (65, "五音五味", "e20cac10bd4a"), (66, "百病始生", "6cd708c8f099"),
    (67, "行针", "6b6b4a3931ad"), (68, "上隔", "f138b3dcd3c6"),
    (69, "忧患无言", "5bfa97d6d37f"), (70, "寒热", "7d8c6dfb23c0"),
    (71, "邪客", "d9f8ad523046"), (72, "通天", "c5a43aac9cca"),
    (73, "官能", "a4635fedda37"), (74, "论疾诊尺", "5a70b7772c04"),
    (75, "刺节真邪", "031d77f5cb9a"), (76, "卫气行", "b38d8dcc3477"),
    (77, "九宫八风", "77daabf60a1c"), (78, "九针论", "c1b6827c0405"),
    (79, "岁露论", "3aaa13e5897f"), (80, "大惑论", "f33e9cd28dcf"),
    (81, "痈疽", "83e3fb6e25ca"),
]


def fetch_one(url: str) -> str:
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))  # 退避 2/4/6s
    raise last


def extract_body(html: str) -> str:
    m = re.search(r'<div class="contson"[^>]*>(.*?)</div>', html, re.S)
    if not m:
        return ""
    body = m.group(1)
    body = re.sub(r"<br\s*/?>", "\n", body)
    body = re.sub(r"<[^>]+>", "", body)
    body = body.replace("\u3000", "\n")  # 全角空格分段
    body = re.sub(r"\n{2,}", "\n", body)
    return body.strip()


def worker(item, sub: str, book: str):
    num, title, hid = item
    out_dir = OUT / sub
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{book}_{num:03d}.txt"
    fpath = out_dir / fname
    if fpath.exists() and fpath.stat().st_size > 100:
        return num, title, "skip"
    url = f"https://www.gushiwen.cn/guwen/bookv_{hid}.aspx"
    html = fetch_one(url)
    body = extract_body(html)
    head = f"# {book} {title}（第{num}篇）\n# 来源：{SOURCE}\n# 抓取页：{url}\n\n"
    (out_dir / fname).write_text(head + body + "\n", encoding="utf-8")
    time.sleep(0.4)
    return num, title, len(body)


def main():
    jobs = [(it, "suwen", "suwen") for it in SUWEN] + [(it, "lingshu", "lingshu") for it in LINGSHU]
    ok, fail = 0, []
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(worker, *j): j for j in jobs}
        for f in concurrent.futures.as_completed(futs):
            j = futs[f]
            try:
                num, title, ln = f.result()
                ok += 1
                if isinstance(ln, int) and ln < 100:
                    print(f"[WARN] 篇内容过短 {title} len={ln}")
            except Exception as e:
                fail.append((j[0][0], j[0][1], str(e)[:60]))
    print(f"完成 {ok}/{len(jobs)}，耗时 {time.time()-t0:.1f}s")
    if fail:
        print("失败数:", len(fail), "前5:", fail[:5])


if __name__ == "__main__":
    main()
