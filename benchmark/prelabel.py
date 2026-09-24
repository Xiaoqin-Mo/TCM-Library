#!/usr/bin/env python3
"""prelabel.py — AI 预标注（MainAgent 规则引擎），人工只做 Review。

流程：
  1. 加载 benchmark/data/pool_v1.json（查询 → 候选条文全文）
  2. 对每个 (query, candidate) 用 QUERY_RULES 词表判 relevance 0–3
     （直接回答=3 / 相关=2 / 概念沾边=1 / 无关=0；命中排除词降档）
  3. 回填 benchmark/gold/annotation_batch*.csv 的 relevance 列，notes 标注
     "AI预标注，待人工复核"；已有人工填写的行不覆盖。

复核说明（标注指南）：人工 Review 时只改错判行；改动比例 = 人工复核比例，
跑 benchmark/merge_annotations.py 冻结金标准并报告 IAA。

用法：
    python benchmark/prelabel.py            # 全量回填
    python benchmark/prelabel.py --stats    # 仅打印分布，不写文件
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "benchmark", "data", "pool_v1.json")
GLOB = os.path.join(ROOT, "benchmark", "gold", "annotation_batch*.csv")

# ---------------------------------------------------------------- 查询规则
# 命中 high → 3（直接回答）；否则 mid → 2（相关）；否则 low → 1（概念沾边）；
# exclude 命中且已有分 → 降一档（反证/异证）。词在 section_title/原文/白话/book/chapter 中匹配。
QUERY_RULES: dict[str, dict] = {
    # ---- modern 现代术语（q001–q018）----
    "q001": dict(high=["感冒", "外感风寒", "太阳中风", "太阳伤寒", "解表散寒", "风寒表证"],
                 mid=["风寒", "表证", "解表", "桂枝汤", "麻黄汤", "荆防败毒散", "辛温解表"],
                 low=["卫气", "肺卫", "六淫", "风邪", "外感"],
                 exclude=[]),
    "q002": dict(high=["失眠", "不寐", "不得眠", "失眠多梦"],
                 mid=["安神", "养心安神", "酸枣仁", "心脾", "心神不宁"],
                 low=["心", "神", "营血"],
                 exclude=["嗜睡", "多寐"]),
    "q003": dict(high=["咳嗽", "久咳"],
                 mid=["宣肺", "止咳", "化痰", "肺气", "止嗽"],
                 low=["肺", "风邪犯肺"],
                 exclude=[]),
    "q004": dict(high=["胃痛", "胃脘痛", "胃脘胀痛"],
                 mid=["和胃", "理气", "脾胃", "香砂", "良附丸", "保和丸"],
                 low=["脾胃", "气机"],
                 exclude=[]),
    "q005": dict(high=["便秘", "大便不通", "大便干结"],
                 mid=["通便", "润肠", "承气汤", "麻子仁丸", "泻下"],
                 low=["大肠", "津液"],
                 exclude=["泄泻", "腹泻"]),
    "q006": dict(high=["泄泻", "腹泻", "水泻"],
                 mid=["止泻", "健脾", "藿香正气", "参苓白术", "运脾"],
                 low=["脾胃", "湿"],
                 exclude=["便秘"]),
    "q007": dict(high=["头痛", "头风", "偏头痛"],
                 mid=["川芎", "祛风", "止痛", "清空", "头窍"],
                 low=["风邪", "经络"],
                 exclude=[]),
    "q008": dict(high=["眩晕", "头晕", "头眩"],
                 mid=["平肝", "熄风", "天麻", "痰浊", "清阳"],
                 low=["肝", "风", "痰"],
                 exclude=[]),
    "q009": dict(high=["腰痛", "腰脊痛", "腰腿痛"],
                 mid=["补肾", "独活寄生", "腰府", "强腰", "活络"],
                 low=["肾", "经络"],
                 exclude=[]),
    "q010": dict(high=["月经不调", "月经先期", "月经后期", "经期"],
                 mid=["调经", "逍遥散", "四物汤", "冲任", "血海"],
                 low=["肝", "血"],
                 exclude=[]),
    "q011": dict(high=["痛经", "经行腹痛", "行经腹痛"],
                 mid=["温经", "化瘀", "少腹逐瘀", "调经止痛"],
                 low=["冲任", "寒凝"],
                 exclude=[]),
    "q012": dict(high=["高血压", "头晕目眩", "面红目赤", "肝阳上亢"],
                 mid=["平肝潜阳", "天麻钩藤", "镇肝熄风", "清肝"],
                 low=["肝", "阳亢"],
                 exclude=[]),
    "q013": dict(high=["糖尿病", "消渴", "口渴多饮"],
                 mid=["滋阴", "生津", "玉液汤", "消渴方", "清热生津"],
                 low=["肺", "胃", "肾", "燥"],
                 exclude=[]),
    "q014": dict(high=["风湿", "痹证", "关节疼痛"],
                 mid=["祛风除湿", "独活寄生", "蠲痹", "通络止痛", "寒湿"],
                 low=["痹", "湿"],
                 exclude=[]),
    "q015": dict(high=["湿疹", "湿疮", "皮肤瘙痒"],
                 mid=["祛风止痒", "清热利湿", "除湿止痒", "燥湿"],
                 low=["湿", "血热"],
                 exclude=[]),
    "q016": dict(high=["耳鸣", "耳聋"],
                 mid=["补肾", "聪耳", "泻肝", "耳窍", "六味地黄"],
                 low=["肾", "肝"],
                 exclude=[]),
    "q017": dict(high=["口疮", "口腔溃疡", "口糜"],
                 mid=["清热泻火", "导赤", "清胃", "滋阴降火"],
                 low=["心火", "胃火", "虚火"],
                 exclude=[]),
    "q018": dict(high=["小儿积食", "积滞", "食积", "厌食"],
                 mid=["消食导滞", "保和丸", "健脾", "山楂", "运脾"],
                 low=["脾胃", "乳食"],
                 exclude=[]),
    # ---- classical 文言术语（q019–q036）----
    "q019": dict(high=["太阳中风", "表虚证", "桂枝汤证", "恶风"],
                 mid=["桂枝汤", "太阳病", "脉浮缓", "自汗", "解肌"],
                 low=["六经辨证", "太阳经证", "外感"],
                 exclude=["伤寒表实", "无汗"]),
    "q020": dict(high=["阳明病", "阳明经证", "阳明腑证"],
                 mid=["白虎汤", "承气汤", "胃家实", "阳明"],
                 low=["六经辨证", "里热"],
                 exclude=["太阳", "少阴"]),
    "q021": dict(high=["少阳病", "少阳证", "寒热往来"],
                 mid=["小柴胡汤", "少阳", "半表半里", "口苦"],
                 low=["六经辨证", "枢机"],
                 exclude=["阳明", "太阴"]),
    "q022": dict(high=["往来寒热", "寒热往来"],
                 mid=["小柴胡汤", "少阳", "疟疾"],
                 low=["少阳枢机", "半表半里"],
                 exclude=[]),
    "q023": dict(high=["少阴病", "少阴证", "脉微细"],
                 mid=["四逆汤", "少阴", "但欲寐", "附子"],
                 low=["六经辨证", "心肾"],
                 exclude=["太阳", "厥阴"]),
    "q024": dict(high=["太阴病", "太阴证", "腹满而吐"],
                 mid=["理中汤", "太阴", "脾虚寒"],
                 low=["六经辨证", "脾胃"],
                 exclude=["少阴", "阳明"]),
    "q025": dict(high=["厥阴病", "厥阴证", "消渴气上撞心"],
                 mid=["乌梅丸", "厥阴", "寒热错杂"],
                 low=["六经辨证", "肝"],
                 exclude=["太阴", "少阳"]),
    "q026": dict(high=["消渴", "口渴多饮"],
                 mid=["滋阴", "生津", "玉液汤", "消渴方"],
                 low=["燥热", "肺胃"],
                 exclude=[]),
    "q027": dict(high=["百合病", "百合地黄", "意欲食复不能食"],
                 mid=["百合", "心肺阴虚", "虚热"],
                 low=["金匮", "虚劳"],
                 exclude=[]),
    "q028": dict(high=["胸痹", "心痛彻背", "胸背痛"],
                 mid=["瓜蒌薤白", "通阳", "痰浊", "胸中"],
                 low=["金匮", "心"],
                 exclude=["胃痛"]),
    "q029": dict(high=["心下悸", "心悸"],
                 mid=["茯苓", "桂枝", "水饮", "温阳"],
                 low=["水气", "心"],
                 exclude=[]),
    "q030": dict(high=["不得眠", "不寐", "失眠"],
                 mid=["酸枣仁", "安神", "虚烦"],
                 low=["心", "神"],
                 exclude=["嗜睡"]),
    "q031": dict(high=["积聚", "癥积", "瘕聚"],
                 mid=["化瘀", "软坚", "鳖甲", "行气"],
                 low=["金匮", "气血"],
                 exclude=[]),
    "q032": dict(high=["水气病", "水肿"],
                 mid=["利水", "越婢", "防己黄芪", "发汗利水"],
                 low=["金匮", "肺脾肾"],
                 exclude=[]),
    "q033": dict(high=["肠痈", "少腹肿痞", "右下腹痛"],
                 mid=["大黄牡丹汤", "薏苡附子败酱散", "痈"],
                 low=["金匮", "大肠"],
                 exclude=[]),
    "q034": dict(high=["梅核气", "咽中如有炙脔"],
                 mid=["半夏厚朴汤", "化痰利咽", "气郁"],
                 low=["金匮", "痰气"],
                 exclude=[]),
    "q035": dict(high=["奔豚气", "奔豚", "气从少腹上冲"],
                 mid=["桂枝加桂汤", "茯苓桂枝甘草", "降逆"],
                 low=["金匮", "冲气"],
                 exclude=[]),
    "q036": dict(high=["咳逆上气", "咳逆", "上气"],
                 mid=["射干麻黄", "降气", "化痰平喘"],
                 low=["金匮", "肺"],
                 exclude=[]),
    # ---- case 临床案例式（q037–q056）----
    "q037": dict(high=["外感风寒", "恶寒发热无汗", "麻黄汤", "周身疼痛"],
                 mid=["辛温解表", "发汗", "解表散寒", "风寒", "表实"],
                 low=["太阳病", "外感", "表证"],
                 exclude=["风热", "有汗", "银翘"]),
    "q038": dict(high=["汗出恶风", "脉浮缓", "桂枝汤", "表虚"],
                 mid=["解肌", "调和营卫", "太阳中风"],
                 low=["太阳病", "表证"],
                 exclude=["无汗", "麻黄汤"]),
    "q039": dict(high=["痰黄黏稠", "咽喉肿痛", "清热化痰", "风热咳嗽"],
                 mid=["桑菊饮", "银翘", "清肺", "利咽", "黄芩"],
                 low=["肺热", "风热"],
                 exclude=["风寒", "痰白"]),
    "q040": dict(high=["久咳不愈", "痰白清稀", "畏寒", "寒咳", "小青龙"],
                 mid=["温肺", "散寒", "止咳化痰", "细辛"],
                 low=["肺寒", "风寒"],
                 exclude=["痰黄", "风热"]),
    "q041": dict(high=["失眠多梦", "心烦易怒", "不寐"],
                 mid=["疏肝", "安神", "龙胆泻肝", "酸枣仁", "清心"],
                 low=["肝火", "心神"],
                 exclude=[]),
    "q042": dict(high=["头晕目眩", "面红目赤", "肝阳上亢", "高血压"],
                 mid=["天麻钩藤", "平肝潜阳", "镇肝熄风", "清肝泻火"],
                 low=["肝", "阳亢"],
                 exclude=[]),
    "q043": dict(high=["口渴多饮", "消渴", "糖尿病"],
                 mid=["滋阴生津", "玉液汤", "消渴方", "清热"],
                 low=["燥热", "肺胃"],
                 exclude=[]),
    "q044": dict(high=["胃痛", "饥饿时加重", "虚痛", "胃脘痛"],
                 mid=["益气", "建中", "小建中", "黄芪建中", "温中"],
                 low=["脾胃", "虚寒"],
                 exclude=["湿热", "食积"]),
    "q045": dict(high=["关节疼痛", "遇寒加重", "寒痹", "痛痹"],
                 mid=["乌头汤", "温经散寒", "祛风散寒", "独活"],
                 low=["痹证", "寒湿"],
                 exclude=["热痹", "红肿"]),
    "q046": dict(high=["风团瘙痒", "瘾疹", "荨麻疹", "时起时消"],
                 mid=["祛风止痒", "消风散", "疏风", "凉血"],
                 low=["风邪", "血热"],
                 exclude=[]),
    "q047": dict(high=["产后乳汁不足", "缺乳", "通乳"],
                 mid=["通草", "穿山甲", "下乳", "益气养血", "王不留行"],
                 low=["气血", "乳汁"],
                 exclude=[]),
    "q048": dict(high=["小儿积食", "积滞", "食积", "腹胀"],
                 mid=["保和丸", "消食导滞", "健脾", "山楂"],
                 low=["脾胃", "乳食"],
                 exclude=[]),
    "q049": dict(high=["口腔溃疡", "口疮", "口糜"],
                 mid=["清胃", "导赤", "泻火", "滋阴降火"],
                 low=["心火", "胃火", "虚火"],
                 exclude=[]),
    "q050": dict(high=["更年期", "潮热汗出", "心烦失眠", "绝经前后"],
                 mid=["滋阴降火", "知柏地黄", "调补肝肾", "安神"],
                 low=["肾阴", "天癸"],
                 exclude=[]),
    "q051": dict(high=["下肢水肿", "按之凹陷", "小便不利", "水肿"],
                 mid=["利水", "五苓散", "真武汤", "健脾利湿"],
                 low=["脾肾", "水湿"],
                 exclude=[]),
    "q052": dict(high=["耳鸣耳聋", "腰膝酸软", "肾虚耳鸣"],
                 mid=["补肾", "六味地黄", "聪耳", "滋肾"],
                 low=["肾", "耳窍"],
                 exclude=["肝火上炎"]),
    "q053": dict(high=["目赤肿痛", "迎风流泪", "针眼"],
                 mid=["睛明", "太阳穴", "风池", "疏风清热"],
                 low=["目", "肝"],
                 exclude=[]),
    "q054": dict(high=["足三里"],
                 mid=["足三里", "胃经", "保健", "强壮"],
                 low=["下肢", "阳明"],
                 exclude=[]),
    "q055": dict(high=["感冒发热", "针灸", "按摩", "穴位"],
                 mid=["风池", "大椎", "合谷", "曲池", "疏风解表"],
                 low=["腧穴", "外感"],
                 exclude=[]),
    "q056": dict(high=["鼻塞流清涕", "遇冷加重", "鼻鼽", "鼻渊"],
                 mid=["通窍", "辛夷", "苍耳子", "温肺散寒", "玉屏风"],
                 low=["肺", "鼻窍", "气虚"],
                 exclude=["痰黄", "风热"]),
}


# 人工修正（MainAgent 抽查后）：(query_id, candidate_id) -> relevance
# 规则引擎的已知误判，显式覆盖；人工 Review 阶段可继续增补。
OVERRIDES: dict[tuple[str, str], int] = {
    ("q037", "fujin_mai_001"): 2,   # 浮紧脉是辨证佐证，非"用何方"直接回答
    ("q054", "ertongtiaoyang_001"): 2,  # 儿童调养提及揉足三里，非足三里主治直接条目
}


def score_candidate(query: str, doc: dict) -> int:
    hit = OVERRIDES.get((query, doc.get("candidate_id", "")))
    if hit is not None:
        return hit
    text = " ".join([
        doc.get("book", ""), doc.get("chapter", ""), doc.get("section_title", ""),
        doc.get("original", ""), doc.get("baihua", ""),
    ])
    r = QUERY_RULES.get(query)
    if r is None:
        return 0
    if any(t in text for t in r["high"]):
        s = 3
    elif any(t in text for t in r["mid"]):
        s = 2
    elif any(t in text for t in r["low"]):
        s = 1
    else:
        s = 0
    if s > 0 and any(t in text for t in r["exclude"]):
        s -= 1
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true", help="只打印分布")
    ap.add_argument("--force", action="store_true", help="覆盖 AI 预标注行（notes 含 AI预标注）；人工已填行仍跳过")
    args = ap.parse_args()

    pool = json.load(open(POOL, encoding="utf-8"))
    by_q = {p["qid"]: {c["candidate_id"]: c for c in p["candidates"]} for p in pool}

    dist: Counter = Counter()
    n_filled = 0
    for path in sorted(glob.glob(GLOB)):
        rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
        if not rows:
            continue
        fieldnames = list(rows[0].keys())
        changed = False
        for r in rows:
            qid, cid = r["query_id"], r["candidate_id"]
            if (r.get("relevance") or "").strip():
                is_ai = "AI预标注" in (r.get("notes") or "")
                if not (args.force and is_ai):
                    continue  # 人工已填，或非强制重跑
            doc = by_q.get(qid, {}).get(cid)
            if doc is None:
                print(f"[warn] {path}: 池中无 {qid}/{cid}")
                continue
            rel = score_candidate(qid, doc)
            r["relevance"] = str(rel)
            notes = r.get("notes") or ""
            if "AI预标注" not in notes:
                r["notes"] = (notes + "；AI预标注，待人工复核").strip("；")
            dist[rel] += 1
            n_filled += 1
            changed = True
        if args.stats:
            continue
        if changed:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
            print(f"[fill] {os.path.basename(path)}: {len(rows)} 行")

    print(f"\n预标注完成：{n_filled} 行")
    print("分布:", dict(sorted(dist.items())))


if __name__ == "__main__":
    main()
