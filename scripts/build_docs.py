"""生成 docs/CATALOG.md 与 gallery/index.html（HTML 遵循 pinguo-apple-design：DM Sans、#0066cc、#f5f5f7、1.2rem 圆角、1px 边框、轻阴影）"""
import glob, os, json, os, html
R = os.path.join(os.path.dirname(__file__), "..")
cat = json.load(open(f"{R}/examples/catalog.json"))
COMMON = '''`theme`（可选）：`consulting_navy`（默认）｜`thinkcell_green`｜`thinkcell_blue`｜`teal_modern`｜`banking_navy_gold`｜`office`｜`mono_smoke`｜`gray_accent`（见 PALETTES.md）；
**四区通用字段（所有 55 种类型都支持，见 docs/STYLE_SPEC.md §9）**

| 区 | 字段 | 说明 |
|---|---|---|
| ① 标题区 | `title`（必填）、`subtitle`、`unit`（必填） | 结论式标题；单位显示在副标题行的括号里 |
| ② 数据标签区 | `format`、`delta_format`、`font_size` | 数字格式和字号；标签会自动防重叠 |
| ③ 重点强调区 | `highlight: [{"category"|"anchor"|"at", "shape":"circle|box|arrow", "w","h","ox","oy","dx","dy"}]` | tc Red 圈、框或箭头 |
| ④ 备注说明区 | `callouts: [{"text", "category"|"anchor"|"at", "dx","dy","w","nth"}]`、`footnote`、`source`（必填） | 引申气泡 + 脚注 + 来源 |

锚点：`category`（柱形/瀑布的类别）；`anchor`（图上任意标签文字，如 "515"、"Hardware|South"）；`at`（图表区比例坐标 [fx,fy]）。

其他：`"palette": "thinkcell"|"office"|[hex...]`；`"decorations": [...]`（仅柱形/瀑布，见下）
'''
SCHEMA = {
 "column": '{"categories":[str], "series":[{"name":str,"values":[num]}], "axis_break"?:{"from":num,"to":num}, "format"?:"{:.1f}"}',
 "stacked": '{"categories":[str], "series":[{"name":str,"values":[num]}]  // 第 1 个系列画在最上面, "show_totals"?:bool}',
 "percent": '{"categories":[str], "series":[{"name":str,"values":[绝对值]}]  // 自动换算百分比，顶部显示绝对总计}',
 "clustered": '{"categories":[str], "series":[{"name":str,"values":[num]}]}',
 "waterfall": '{"items":[{"label":str,"value":num,"kind":"start|delta|total"}], "signed_labels"?:bool, "color_by_sign"?:bool}',
 "waterfall_h": '{"items":[{"label":str,"value":num,"kind":"start|delta|total"}]}',
 "mekko_percent": '{"categories":[str], "widths"?:[num], "series":[{"name":str,"values":[num]}], "total_label"?:str}',
 "mekko_unit": '{"categories":[str], "series":[{"name":str,"values":[绝对值]}]}',
 "bar": '{"categories":[str], "series":[{"name":str,"values":[num]}], "highlight"?:[str]}',
 "bar_sorted": '同 bar，自动降序；"highlight":[类别名] 高亮绿色，其余浅灰',
 "bar_stacked": '{"categories":[str], "series":[{"name":str,"values":[num]}]}',
 "butterfly": '{"categories":[str], "series":[左侧系列, 右侧系列]}',
 "dumbbell": '{"categories":[str], "series":[时点1, 时点2], "min"?:num}',
 "football": '{"categories":[str], "series":[{"name":"Low",...},{"name":"High",...}], "min"?:num, "marker"?:{"value":num,"label":str}}',
 "line": '{"categories":[str], "series":[{"name":str,"values":[num]}], "label_last"?:bool}',
 "area": '{"categories":[str], "series":[{"name":str,"values":[num]}]}',
 "area_percent": '同 area，自动换算 100%',
 "combo": '{"categories":[str], "columns":[{"name":str,"values":[num]}], "line":{"name":str,"values":[num],"suffix"?:"%"}}',
 "scatter": '{"points":[{"x":num,"y":num,"label"?:str,"group"?:str}], "x_title":str, "y_title":str, "partition"?:{"x":num,"y":num}}',
 "bubble": '{"points":[{"x":num,"y":num,"size":num,"label"?:str}], "x_title":str, "y_title":str}',
 "pie": '{"segments":[{"label":str,"value":num,"color"?:hex}]}',
 "doughnut": '{"segments":[...同 pie], "center"?:str}',
 "gantt": '{"start":"YYYY-MM-DD","end":"YYYY-MM-DD","weeks"?:bool,"tasks":[{"name":str,"start"?:date,"end"?:date,"milestone"?:date,"milestone_label"?:str,"owner"?:str}],"shades"?:[{"start","end","label"}],"brackets"?:[{"start","end","label"}],"today"?:date}',
 "timeline": '{"start":date,"end":date,"phases":[{"name","start","end","color"?:int}],"milestones":[{"date","label"}]}',
 "table_harvey": '{"columns":[str], "rows":[{"name":str,"values":[str | {"harvey":0..4} | {"check":bool}]}], "harvey_legend"?:[5 个文字]}',
}
SCHEMA.update({
 "stacked_clustered": '{"categories":[str], "groups":[{"name":str,"series":[{"name":str,"values":[num]}]}]}',
 "column_error": '{"categories":[str], "values":[num], "errors":[num] | "low":[num],"high":[num]}',
 "column_grouped": '{"groups":[{"name":str,"categories":[str],"values":[num]}], "gap"?:num}',
 "column_target": '{"categories":[str], "actual":[num], "target":[num], "target_name"?:str}',
 "column_xbreak": '{"categories":[str], "values":[num], "break_after":int}',
 "waterfall_stacked": '{"series":[str], "items":[{"label":str,"values":[num 每系列],"kind":"start|delta|total"}]}',
 "waterfall_subtotal": '{"items":[{"label":str,"value"?:num,"kind":"start|delta|subtotal|total"}]}  // subtotal/total 不给 value 自动累计',
 "waterfall_percent": '同 waterfall，加 "format":"{:.1f}%", "delta_format":"{:+.1f}pp"',
 "variwide": '{"categories":[str], "widths":[num], "values":[num], "suffix"?:str, "highlight"?:[str]}',
 "proportional_area": '{"items":[{"label":str,"value":num,"color"?:hex}]}',
 "bar_yoy": '{"categories":[str], "previous":{"name":str,"values":[num]}, "current":{"name":str,"values":[num]}}',
 "bar_diverging": '{"categories":[str], "values":[±num], "suffix"?:str}',
 "bar_percent": '{"categories":[str], "series":[{"name":str,"values":[num]}], "colors"?:[hex]}',
 "line_target": '同 line，加 "target":num, "target_label"?:str, "band"?:[lo,hi], "band_label"?:str',
 "slope": '{"left_label":str,"right_label":str,"items":[{"label":str,"a":num,"b":num}],"highlight"?:[str],"red_down"?:bool}',
 "small_multiples": '{"categories":[str], "cols":int, "panels":[{"title":str,"values":[num]}]}',
 "gantt_progress": '同 gantt，task 加 "progress":0..1',
 "gantt_swimlane": '同 gantt，task 可为 {"name":str,"header":true} 分组行；"indent":true 缩进；"color":int',
 "funnel": '{"stages":[{"label":str,"value":num}]}',
 "heatmap": '{"rows":[str], "cols":[str], "values":[[num]], "min"?,"max"?, "low_color"?, "high_color"?}',
 "matrix_2x2": '{"x_title","y_title","quadrants":[左上,右上,左下,右下],"points":[{"x":0..1,"y":0..1,"size":num,"label":str,"focus"?:bool}],"x_range"?,"y_range"?}',
 "pareto": '{"categories":[str], "values":[num]}  // 自动降序 + 累计%',
 "tornado": '{"base":num, "items":[{"label":str,"low":num,"high":num}]}',
 "tree": '{"root":{"label":str,"value":str,"highlight"?:bool,"op"?:"×|÷|+|−","children":[...递归]}}',
 "kpi_cards": '{"cols":int, "cards":[{"label":str,"value":str,"delta":str,"good"?:bool,"spark"?:[num]}]}',
 "bullet": '{"items":[{"label":str,"unit":str,"value":num,"target":num,"ranges":[num,num,num]}]}',
 "progress_bars": '{"expected"?:0..1, "items":[{"label":str,"value":num,"target":num}]}',
 "radar": '{"axes":[str], "max":num, "series":[{"name":str,"values":[num]}]}',
 "tam_sam_som": '{"levels":[{"label":str,"value":num,"display"?:str,"desc"?:str}]}',
 "waffle": '{"items":[{"label":str,"value":num,"color"?:hex}]}',
})
DECO = """装饰（decorations，适用于 column/stacked/percent/clustered/waterfall）：
- `{"type":"cagr","from":i|类别名,"to":j}` CAGR 箭头（手册 chartdecorations: cagr_formula.jpg）
- `{"type":"total_diff","from","to","percent"?:bool,"label"?:str}` 总差折线箭头（手册 differencearrow_abs2.jpg）
- `{"type":"diff","from","to","percent"?:bool}` 水平差值（level difference）箭头（手册 differencearrow_abs1.jpg）
- `{"type":"value_line","value":num,"label"?:str}` 数值线（手册 averageline.jpg）
- `{"type":"highlight","category"}` 红色椭圆圈出重点列
- `{"type":"callout","category","text","dx"?,"dy"?,"w"?}` 红色 callout"""
L = ["# 图表目录（自动生成：scripts/build_docs.py）\n", f"共 **{len(cat)}** 个示例，覆盖 **{len(set(c['type'] for c in cat))}** 种图表类型，分 **{len(set(c['category'] for c in cat))}** 类。\n",
     "通用字段：" + COMMON + "\n", DECO + "\n"]
cur = None
for c in cat:
    if c["category"] != cur: cur = c["category"]; L.append(f"\n## {cur}\n")
    spec = json.load(open(f"{R}/examples/{c['id']}.json"))
    L += [f"### `{c['id']}`（type: `{c['type']}`）\n", f"- **适合场景**：{c['use']}", f"- **data 格式**：`{SCHEMA[c['type']]}`",
          f"- **示例**：[examples/{c['id']}.json](../examples/{c['id']}.json)\n", f"![{c['id']}](../examples/{c['id']}.png)\n",
          "<details><summary>完整样例 JSON</summary>\n\n```json\n" + json.dumps(spec, ensure_ascii=False, indent=1) + "\n```\n</details>\n"]
L += ["\n## 多图拼版（dashboard / facet）\n", "一页多图：自由区域或网格拼版（`dashboard`）、行×列分面（`facet`）；支持分段虚线、多层共享横轴、条件着色、时间进度线、圈注/箭头/批注。完整字段见 [DASHBOARD.md](DASHBOARD.md)。\n"]
for f in sorted(glob.glob(f"{R}/examples/dashboards/*.json")):
    b = os.path.basename(f)[:-5]; L += [f"### `{b}`（type: `{json.load(open(f))['type']}`）\n", f"- **示例**：[examples/dashboards/{b}.json](../examples/dashboards/{b}.json)\n", f"![{b}](../examples/dashboards/{b}.png)\n"]
open(f"{R}/docs/CATALOG.md","w").write("\n".join(L))
# ---------- HTML ----------
cards = []; cur = None; sections = []
for c in cat:
    if c["category"] != cur:
        cur = c["category"]; sections.append([cur, []])
    sections[-1][1].append(c)
nav = "".join(f'<a href="#s{i}">{html.escape(s)}</a>' for i,(s,_) in enumerate(sections))
body = ""
for i,(s, items) in enumerate(sections):
    body += f'<section id="s{i}"><h2>{html.escape(s)}<span>{len(items)}</span></h2><div class="grid">'
    for c in items:
        body += f'''<article class="card"><img src="../examples/{c["id"]}.png" alt="{c["id"]}" loading="lazy"><div class="meta"><div class="row"><h3>{c["id"]}</h3><code>{c["type"]}</code></div><p>{html.escape(c["use"])}</p><a href="../examples/{c["id"]}.json">JSON 样例</a></div></article>'''
    body += "</div></section>"
page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>think-cell 风格图表总览</title><link rel="stylesheet" href="colors_and_type.css">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
:root{{--blue:#0066cc;--black:#0a0a0a;--mist:#f5f5f7;--line:#e5e5ea;--r:1.2rem;--ease:cubic-bezier(.32,.72,0,1)}}
*{{box-sizing:border-box}} body{{margin:0;font-family:"DM Sans",-apple-system,system-ui,sans-serif;color:var(--black);background:#fff;font-size:15px;line-height:1.55}}
header{{padding:96px 32px 48px;max-width:1280px;margin:0 auto}} header h1{{font-size:72px;font-weight:600;letter-spacing:-.04em;line-height:.92;margin:0 0 24px}}
header p{{font-size:17px;color:#6e6e73;max-width:720px;margin:0}} .stats{{display:flex;gap:32px;margin-top:32px;font-family:"JetBrains Mono",monospace;font-size:13px;color:#6e6e73}} .stats b{{display:block;font-size:32px;color:var(--black);font-family:"DM Sans";font-weight:600}}
nav{{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.8);backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid var(--line)}}
nav div{{max-width:1280px;margin:0 auto;padding:12px 32px;display:flex;gap:8px;overflow-x:auto}} nav a{{white-space:nowrap;padding:6px 16px;border-radius:999px;color:var(--black);text-decoration:none;font-size:14px;transition:background 150ms var(--ease)}} nav a:hover{{background:var(--mist)}}
main{{max-width:1280px;margin:0 auto;padding:0 32px 128px}} section{{padding-top:64px}} h2{{font-size:32px;font-weight:600;letter-spacing:-.02em;margin:0 0 24px;display:flex;align-items:baseline;gap:12px}} h2 span{{font-size:14px;color:#6e6e73;font-family:"JetBrains Mono",monospace;font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:24px}}
.card{{border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:#fff;box-shadow:0 1px 2px 0 rgba(0,0,0,.04);transition:box-shadow 250ms var(--ease)}} .card:hover{{box-shadow:0 8px 24px -8px rgba(0,0,0,.08)}}
.card img{{width:100%;display:block;background:#fff;border-bottom:1px solid var(--line)}} .meta{{padding:16px 24px 24px}} .row{{display:flex;justify-content:space-between;align-items:center;gap:12px}}
h3{{margin:0;font-size:17px;font-weight:600}} code{{font-family:"JetBrains Mono",monospace;font-size:12px;background:var(--mist);padding:2px 8px;border-radius:999px;color:#6e6e73}} .meta p{{margin:8px 0 12px;color:#424245;font-size:14px}} .meta a{{color:var(--blue);text-decoration:none;font-size:14px}}
footer{{border-top:1px solid var(--line);padding:32px;text-align:center;color:#6e6e73;font-size:13px}}
</style></head><body>
<header><h1>think-cell<br>风格图表。</h1><p>每张图都是 python-pptx 生成的可编辑 PowerPoint 形状，配色取自 think-cell 官方手册，版面依据官方示例图。数据用 JSON，一条命令出 PPTX + PNG。</p>
<div class="stats"><div><b>{len(cat)}</b>示例</div><div><b>{len(set(c["type"] for c in cat))}</b>图表类型</div><div><b>{len(sections)}</b>分类</div></div></header>
<nav><div>{nav}</div></nav><main>{body}</main><footer>yuxin-business-charts skill · 渲染：LibreOffice · PPTX：gallery/thinkcell-gallery.pptx</footer></body></html>'''
open(f"{R}/gallery/index.html","w").write(page); print("ok")
