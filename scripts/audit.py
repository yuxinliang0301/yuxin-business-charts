"""四区审核：对比修复前（/workspace/thinkcell-eval/examples_before_audit）与当前 examples，输出 docs/AUDIT.md"""
import json, os, sys
R = os.path.join(os.path.dirname(__file__), ".."); B = sys.argv[1] if len(sys.argv) > 1 else "/workspace/thinkcell-eval/examples_before_audit"
cat = json.load(open(f"{R}/examples/catalog.json"))
# 修复前目检发现的数据标签区问题（逐张看图记录）
LABEL_BUG_BEFORE = {"pareto": "累计 % 标签压在柱子上", "line_target": "系列名、目标线标签、区间标签挤在右端", "combo": "图例混入中文“右轴”，与英文图不一致",
                    "table_harvey": "Harvey 图例为中文且贴近脚注"}
BUILTIN_EMPH = {"bar_sorted","variwide","slope","matrix_2x2","column_target","waterfall_signed","waterfall_negative_end","bar_diverging","funnel","pareto","progress_bars"}
rows = []; fails = 0; fixes = 0
def emph(s):
    d = [x for x in s.get("decorations", []) if x.get("type") in ("highlight","callout")]
    return bool(s.get("highlight") or s.get("callouts") or d)
for c in cat:
    i = c["id"]; old = json.load(open(f"{B}/{i}.json")); new = json.load(open(f"{R}/examples/{i}.json"))
    r = {"id": i, "type": c["type"]}
    # ① 标题区
    ok0 = bool(old.get("title")) and bool(old.get("unit")); ok1 = bool(new.get("title")) and bool(new.get("unit"))
    r["t"] = ("合格" if ok0 else "不合格：缺单位") + " → " + ("合格" if ok1 else "不合格")
    r["tf"] = "" if ok0 else f"补单位「{new.get('unit')}」"
    # ② 数据标签区
    r["l"] = ("不合格：" + LABEL_BUG_BEFORE[i] if i in LABEL_BUG_BEFORE else "合格") + " → 合格（目检）"
    r["lf"] = {"pareto":"累计 % 改为图上方独立一行，柱子缩到下半区","line_target":"目标标签移到线左端上方，区间标签放区间内右下，取消末值标签",
               "combo":"图例改英文 (right axis)","table_harvey":"图例改英文并上移到图表区内"}.get(i, "")
    # ③ 强调区
    e0 = emph(old) or i in BUILTIN_EMPH; e1 = emph(new) or i in BUILTIN_EMPH
    r["e"] = ("有" if e0 else "无") + " → " + ("合格：" + ("圈/框 + 气泡" if new.get("highlight") and new.get("callouts") else ("气泡" if new.get("callouts") else "数据内高亮色")) if e1 else "未启用（可选）")
    r["ef"] = ("新增 " + ", ".join(k for k in ("highlight","callouts") if new.get(k))) if (new.get("highlight") or new.get("callouts")) else ""
    # ④ 备注说明区
    n0 = bool(old.get("source")) and bool(old.get("footnote")); n1 = bool(new.get("source")) and bool(new.get("footnote"))
    r["n"] = ("合格" if n0 else "不合格：缺脚注") + " → " + ("合格" + ("（含引申气泡）" if new.get("callouts") else "") if n1 else "不合格")
    r["nf"] = "" if n0 else "补脚注"
    f = (not ok0) + (i in LABEL_BUG_BEFORE) + (not n0); fails += f; fixes += f + (1 if not emph(old) and emph(new) else 0)
    rows.append(r)
n_ann = sum(1 for c in cat if json.load(open(f"{R}/examples/{c['id']}.json")).get("callouts"))
L = ["# 四区审核表（标题区 / 数据标签区 / 重点强调区 / 备注说明区）\n",
     f"- 示例数：{len(cat)}；修复前不合格项：**{fails}**；本轮修复/补齐项：**{fixes}**（含为示例新增强调+气泡）",
     f"- 启用“强调 + 引申气泡”的示例：**{n_ann}/{len(cat)}**（要求 ≥ 一半）",
     "- 每格写法：修复前 → 修复后。数据标签区按逐张目检判断（PNG 在 examples/）。\n",
     "| # | 示例 | ① 标题区 | ② 数据标签区 | ③ 重点强调区 | ④ 备注说明区 | 修复方式 |", "|---|---|---|---|---|---|---|"]
for k, r in enumerate(rows, 1):
    fx = "；".join(x for x in (r["tf"], r["lf"], r["ef"], r["nf"]) if x) or "—"
    L.append(f"| {k} | `{r['id']}` | {r['t']} | {r['l']} | {r['e']} | {r['n']} | {fx} |")
L.append("\n## 引擎层通用修复\n- 新增 `annotate()`：所有 55 种类型都支持 `highlight`、`callouts`（锚点可用柱形类别 / 任意标签文字 / 图表区比例坐标）\n- 来源 `source` 必显，缺失时显示 `[missing – add source]` 提醒\n- callout 的锚点圆点贴在标签文字外框边缘，不压数字\n- 瀑布图圈选改为只圈住该柱（以前会一直圈到基线）")
open(f"{R}/docs/AUDIT.md", "w").write("\n".join(L)); print(fails, fixes, n_ann)
