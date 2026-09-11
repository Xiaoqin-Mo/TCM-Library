#!/usr/bin/env python3
"""recall_regression.py — 召回回归测试（确定性断言）。

用法: python3 tests/recall_regression.py
退出码: 0=全部通过, 1=有失败
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scripts.retrieve import load_manifest, query  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = load_manifest(os.path.join(ROOT, "manifest.json"))


def ids(cond, include_general=False, limit=None):
    return [e["id"] for e in query(MANIFEST, cond, include_general=include_general, limit=limit)]


def check(name, got, expected):
    ok = sorted(got) == sorted(expected)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {sorted(got)}")
    if not ok:
        print(f"       expected: {sorted(expected)}")
    return ok


def main() -> None:
    results = []
    # 结构化维度命中
    results.append(check("按证型 太阳中风",
                         ids({"zhengxing": ["太阳中风"]}), ["guizhitang_001"]))
    results.append(check("按治法 解表散寒",
                         ids({"zhifa": ["解表散寒"]}),
                         ["baizhi_001", "qianghuo_001", "shengjiang_001", "xixin_001", "zisuye_001"]))
    results.append(check("按治法 发汗解表",
                         ids({"zhifa": ["发汗解表"]}), ["mahuang_001", "xiangru_001"]))
    results.append(check("按方名 桂枝汤",
                         ids({"fangming": ["桂枝汤"]}), ["guizhi_001", "guizhitang_001"]))
    results.append(check("按药名 桂枝",
                         ids({"yaoming": ["桂枝"]}), ["guizhi_001", "guizhitang_001"]))
    results.append(check("按腧穴 足三里",
                         ids({"xuewei": ["足三里"]}), ["zusanli_001"]))
    results.append(check("按经络 足阳明胃经",
                         ids({"jingluo": ["足阳明胃经"]}), ["zusanli_001"]))
    # 药性维度（schema 2.1）
    # 断言策略：药性/归经维度的命中随库扩充而增长，逐条写死全集不可维护；
    # 改为「旧基线子集 + 新增抽查」：旧基线条目必须仍在命中内（防回归），
    # 并从后续批量收录中抽查代表性新增条目确认纳入检索。
    WEN = ["baizhi_001", "cangerzi_001", "ebushicao_001", "gaoben_001", "guizhi_001",
           "mahuang_001", "qianghuo_001", "shengjiang_001", "xiheliu_001", "xinyi_001",
           "xixin_001", "zisugeng_001", "zisuye_001"]
    WEN_NEW = ["buguzhi_001", "danggui_001", "lurong_001", "roudoukou_001", "yinyanghuo_001"]
    XIN = ["baizhi_001", "bohe_001", "cangerzi_001", "chaihu_001", "dandouchi_001",
           "ebushicao_001", "fangfeng_001", "fuping_001", "gaoben_001", "gegen_001",
           "guizhi_001", "jingjie_001", "mahuang_001", "manjingzi_001", "niubangzi_001",
           "qianghuo_001", "shengjiang_001", "shengma_001", "xiangru_001", "xiheliu_001",
           "xinyi_001", "xixin_001", "zisugeng_001", "zisuye_001"]
    XIN_NEW = ["changshan_001", "chansu_001", "qingfen_001", "xianmao_001", "zaojia_001"]
    FEI = ["baizhi_001", "bohe_001", "cangerzi_001", "chaihu_001", "chantui_001",
           "dandouchi_001", "ebushicao_001", "fuping_001", "gegen_001", "guizhi_001",
           "jingjie_001", "juhua_001", "mahuang_001", "muzei_001", "niubangzi_001",
           "sangye_001", "shengjiang_001", "shengma_001", "xiangru_001", "xiheliu_001",
           "xinyi_001", "xixin_001", "zisugeng_001", "zisuye_001"]
    FEI_NEW = ["beishashen_001", "huangqi_001", "maidong_001", "mahuanggen_001", "xiebai_001"]
    for name, got, base, new in (
        ("按四气 温", set(ids({"siqi": ["温"]})), WEN, WEN_NEW),
        ("按五味 辛", set(ids({"wuwei": ["辛"]})), XIN, XIN_NEW),
        ("按归经 肺经", set(ids({"guijing": ["肺经"]})), FEI, FEI_NEW),
    ):
        ok = set(base) <= got and set(new) <= got
        print(f"{'PASS' if ok else 'FAIL'}  {name}: 命中 {len(got)}，基线 {len(base)} 全含={set(base) <= got}，抽查 {new} 全含={set(new) <= got}")
        results.append(ok)
    # 同字段多值 OR：任一命中即该字段命中（桂枝汤 zhengxing 含太阳中风）
    results.append(check("同字段多值 OR",
                         ids({"zhengxing": ["太阳中风", "风寒束表"]}), ["guizhitang_001"]))
    # 跨字段 AND：zhengxing 命中但 zhifa 不命中 → 不召回
    results.append(check("跨字段 AND 不匹配",
                         ids({"zhengxing": ["太阳中风"], "zhifa": ["发汗解表"]}), []))
    # 维度间 OR + 排序：桂枝汤 命中特异性 2（zhengxing+yaoming）> 麻黄 1
    r = query(MANIFEST, {"zhengxing": ["太阳中风"], "yaoming": ["桂枝"]}, include_general=False)
    top = [e["id"] for e in r[:1]]
    results.append(check("特异性优先排序", top, ["guizhitang_001"]))
    # keywords 包含召回
    results.append(check("keywords 解表剂",
                         ids({"keywords": ["解表剂"]}), ["guizhitang_001"]))
    results.append(check("keywords 无命中",
                         ids({"keywords": ["消渴"]}), []))
    # 空查询静默（不返回全部）
    results.append(check("空查询静默", ids({}), []))
    # 结构完整性
    results.append(check("manifest 非空", [str(MANIFEST["total"])], ["570"]))
    results.append(check("match_fields 齐全",
                         MANIFEST["match_fields"],
                         ["zhengxing", "zhifa", "bingzheng", "zhengzhuang",
                          "fangming", "yaoming", "xuewei", "jingluo",
                          "siqi", "wuwei", "guijing"]))

    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} 通过")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
