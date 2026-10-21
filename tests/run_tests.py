#!/usr/bin/env python3
"""测试：推荐（tests/data）+ 校验（tests/specs）+ 渲染前自动校验拦截。用法：python tests/run_tests.py"""
import sys, os, json, subprocess, tempfile
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); sys.path.insert(0, os.path.join(R, "scripts"))
import tc_advise, tc_validate
PY = sys.executable
# 数据集 → 首选图应在集合内；备选里应包含（可选）
ADV = {
 "01_revenue_by_year.csv": ({"column"}, None), "02_segments_wide.csv": ({"stacked"}, "percent"), "03_ebit_bridge.csv": ({"waterfall"}, None),
 "04_pnl_subtotal.csv": ({"waterfall_subtotal"}, "waterfall"), "05_channel_share.tsv": ({"pie", "doughnut"}, None), "06_survey.md": ({"bar_percent"}, None),
 "07_yoy.json": ({"bar_yoy", "dumbbell"}, "slope"), "08_actual_target.csv": ({"column_target"}, None), "09_valuation_range.csv": ({"football"}, None),
 "10_sensitivity.csv": ({"tornado"}, "football"), "11_project_plan.csv": ({"gantt"}, "timeline"), "12_funnel.txt": ({"funnel"}, None),
 "13_margin_change.csv": ({"bar_diverging"}, None), "14_market_mekko.csv": ({"mekko_percent"}, None), "15_price_csat.csv": ({"scatter"}, None),
 "16_region_product_long.csv": ({"bar_stacked", "stacked", "heatmap", "mekko_unit"}, None), "17_deals_outlier.csv": ({"column"}, None),
 "18_rev_margin.csv": ({"combo"}, None), "19_quarters.xlsx": ({"clustered", "line"}, None),
 "20_multi_metric_teams.csv": ({"facet"}, "dashboard"),
}
INTENT = [("02_segments_wide.csv", "想说明结构变化：Seg C 占比提升", {"percent"}), ("05_channel_share.tsv", "show the ranking of channels", {"bar_sorted", "pie"})]
VAL = {"v01_waterfall_unbalanced": "不能做", "v02_pie_not_100": "能做但有问题", "v03_mekko_no_widths": "不能做", "v04_gantt_no_dates": "不能做",
       "v05_column_too_many_long": "能做但有问题", "v06_length_mismatch": "不能做", "v07_football_low_gt_high": "不能做", "v08_line_target_missing": "不能做",
       "v09_butterfly_3_series": "不能做", "v10_text_numbers": "不能做", "v11_ok_percent": "能做", "v12_pie_too_many": "能做但有问题",
       "v13_wf_stacked_unbalanced": "不能做", "v14_unknown_type": "不能做",
       "v15_dashboard_bad": "不能做", "v16_facet_bad": "不能做"}
ok = fail = 0
def check(cond, msg):
    global ok, fail
    print(("  PASS " if cond else "  FAIL ") + msg); ok += cond; fail += (not cond)
print("== 推荐")
tmp = tempfile.mkdtemp(); drafts = []
for f, (want, alt) in ADV.items():
    r = tc_advise.advise(tc_advise.read_table(os.path.join(H, "data", f)))
    types = [x["type"] for x in r["recommendations"]]
    check(types[0] in want and len(types) == 3 and (alt is None or alt in types), f"{f}: {types} 期望首选∈{sorted(want)}" + (f"，备选含 {alt}" if alt else ""))
    check(r["spec"] is not None and r["spec_validation"]["status"] != "不能做", f"{f}: spec 草稿可渲染（校验：{r['spec_validation']['status'] if r['spec'] else '无草稿'}）")
    if r["spec"]:
        p = os.path.join(tmp, f + ".json"); s = dict(r["spec"], source="Test data", id=f.split(".")[0]); json.dump(s, open(p, "w"), ensure_ascii=False); drafts.append(p)
for f, it, want in INTENT:
    r = tc_advise.advise(tc_advise.read_table(os.path.join(H, "data", f)), it); t = r["recommendations"][0]["type"]
    check(t in want, f"意图“{it}” → {t}（期望 ∈ {sorted(want)}）")
print("== 草稿渲染")
p = subprocess.run([PY, os.path.join(R, "scripts", "tc_render.py"), *drafts, "-o", os.path.join(tmp, "drafts.pptx")], capture_output=True, text=True)
check(p.returncode == 0, f"{len(drafts)} 个推荐草稿一次渲染成 PPTX（exit {p.returncode}）" + ("" if p.returncode == 0 else p.stderr[-400:]))
print("== 校验")
for n, want in VAL.items():
    r = tc_validate.validate(json.load(open(os.path.join(H, "specs", n + ".json"))))
    check(r["status"] == want, f"{n}: {r['status']}（期望 {want}）")
print("== 全部 61 个示例校验均为“能做”")
import glob
bad = []
for f in glob.glob(os.path.join(R, "examples", "*.json")):
    j = json.load(open(f))
    if isinstance(j, dict) and "type" in j:
        r = tc_validate.validate(j)
        if r["status"] != "能做": bad.append((os.path.basename(f), r["status"]))
check(not bad, f"示例校验 {bad or '全部通过'}")
print("== 多图拼版")
D = sorted(glob.glob(os.path.join(R, "examples", "dashboards", "*.json")))
check(len(D) == 5, f"examples/dashboards 有 {len(D)} 个拼版示例（期望 5）")
for f in D:
    r = tc_validate.validate(json.load(open(f))); check(r["status"] == "能做", f"{os.path.basename(f)} 校验：{r['status']}")
p = subprocess.run([PY, os.path.join(R, "scripts", "tc_render.py"), *D, "-o", os.path.join(tmp, "dash.pptx")], capture_output=True, text=True)
check(p.returncode == 0 and os.path.exists(os.path.join(tmp, "dash.pptx")), f"5 个拼版一次渲染成 PPTX（exit {p.returncode}）" + ("" if p.returncode == 0 else p.stderr[-400:]))
r = tc_validate.validate(json.load(open(os.path.join(H, "specs", "v15_dashboard_bad.json"))))
check(all(k in json.dumps(r, ensure_ascii=False) for k in ("长度对不上", "segments", "不存在的系列", "超出边界", "pie")), "坏拼版的 5 类问题都被指出（长度/分段/系列名/区域越界/未知子图类型）")
print("== 渲染前自动拦截")
p = subprocess.run([PY, os.path.join(R, "scripts", "tc_render.py"), os.path.join(H, "specs", "v01_waterfall_unbalanced.json"), "-o", os.path.join(tmp, "x.pptx")], capture_output=True, text=True)
check(p.returncode != 0 and "瀑布不平" in p.stderr and not os.path.exists(os.path.join(tmp, "x.pptx")), "瀑布不平时 tc_render 拒绝渲染并给出大白话原因")
p = subprocess.run([PY, os.path.join(R, "scripts", "tc_render.py"), os.path.join(H, "specs", "v01_waterfall_unbalanced.json"), "-o", os.path.join(tmp, "x.pptx"), "--force"], capture_output=True, text=True)
check(p.returncode == 0, "--force 可强制渲染")
print(f"\n合计：{ok} 通过，{fail} 失败")
sys.exit(1 if fail else 0)
