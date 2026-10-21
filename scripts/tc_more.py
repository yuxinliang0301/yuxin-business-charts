"""扩展图表（第二批）。依赖 tc_core 的版面、配色与原语。各图依据见 docs/STYLE_SPEC.md §7。"""
import math
from tc_core import *
from tc_core import _ticks, _legend, _resolve_subtotals
DASH = MSO_LINE_DASH_STYLE.DASH
def lerp(c1, c2, t):
    a = [int(c1[i:i+2],16) for i in (1,3,5)]; b = [int(c2[i:i+2],16) for i in (1,3,5)]
    return "#%02X%02X%02X" % tuple(round(a[k]+(b[k]-a[k])*t) for k in range(3))

# ---------------- 柱形扩展 ----------------
def stacked_clustered(sl, d):
    """堆叠+簇状（手册 sample_stacked_clustered.jpg）：每个类别下多根堆叠柱"""
    cats = d["categories"]; groups = d["groups"]; n = len(cats); g = len(groups)
    X,Y,W,Hh = sl.CHART; pw = W-1.6; slot = pw/n; bw = slot*0.8/g; y0 = Y+Hh-0.6; py = Y+0.4
    tots = [[sum(s["values"][i] for s in gr["series"]) for gr in groups] for i in range(n)]
    sc = (y0-py)/max(max(t) for t in tots); sl.line(X, y0, X+pw, y0)
    names = [s["name"] for s in groups[0]["series"]]
    for i,c in enumerate(cats):
        x0 = X+slot*i+slot*0.1
        for k,gr in enumerate(groups):
            x = x0+k*bw; up = 0; ser = gr["series"]
            for j in range(len(ser)-1, -1, -1):
                v = ser[j]["values"][i]; sl.rect(x+bw*0.06, y0-(up+v)*sc, bw*0.88, v*sc, sl.col(j), fmt(v)); up += v
            sl.text(x+bw/2, y0-up*sc-0.18, fmt(up), w=bw+0.2)
            sl.text(x+bw/2, y0+0.18, gr["name"], w=bw+0.2, size=sl.fs-3, color="#777777")
        sl.text(X+slot*(i+0.5), y0+0.45, c, w=slot)
    x = X+slot*(n-1)+slot*0.1+(g-1)*bw+bw; up = 0; ser = groups[-1]["series"]
    for j in range(len(ser)-1, -1, -1):
        v = ser[j]["values"][-1]; sl.text(x+0.1, y0-(up+v/2)*sc, names[j], w=1.5, align="l"); up += v

def column_error(sl, d):
    """柱 + 误差线（手册 column-line-area-charts errorbars.jpg）"""
    cats = d["categories"]; v = d["values"]; lo = d.get("low") or [a-e for a,e in zip(v,d["errors"])]; hi = d.get("high") or [a+e for a,e in zip(v,d["errors"])]
    X,Y,W,Hh = sl.CHART; n = len(cats); slot = W/n; bw = slot*0.55; y0 = Y+Hh-0.4; py = Y+0.4; sc = (y0-py)/max(hi)
    sl.line(X, y0, X+W, y0)
    for i,c in enumerate(cats):
        cx = X+slot*(i+0.5); sl.rect(cx-bw/2, y0-v[i]*sc, bw, v[i]*sc, sl.col(0))
        sl.line(cx, y0-hi[i]*sc, cx, y0-lo[i]*sc, w=1); sl.line(cx-0.1, y0-hi[i]*sc, cx+0.1, y0-hi[i]*sc, w=1); sl.line(cx-0.1, y0-lo[i]*sc, cx+0.1, y0-lo[i]*sc, w=1)
        sl.text(cx, y0-hi[i]*sc-0.18, fmt(v[i], d.get("format")), w=slot); sl.text(cx, y0+0.22, c, w=slot)

def column_grouped(sl, d):
    """分组类别轴：组间留空隙（手册 axes category_gap.jpg）+ 组名在类别名下方"""
    groups = d["groups"]; cats = [(gi,c,v) for gi,g in enumerate(groups) for c,v in zip(g["categories"], g["values"])]
    X,Y,W,Hh = sl.CHART; gap = d.get("gap", 1.0); n = len(cats) + gap*(len(groups)-1); slot = W/n; bw = slot*0.6
    y0 = Y+Hh-0.75; py = Y+0.4; sc = (y0-py)/max(v for _,_,v in cats); x = X; last = 0; spans = {}
    for k,(gi,c,v) in enumerate(cats):
        if k and gi != last: x += slot*gap
        last = gi; cx = x+slot/2; sl.rect(cx-bw/2, y0-v*sc, bw, v*sc, sl.col(gi % 2 and 1 or 0) if d.get("alternate") else sl.col(0))
        sl.text(cx, y0-v*sc-0.18, fmt(v, d.get("format")), w=slot); sl.text(cx, y0+0.22, c, w=slot)
        a,b = spans.get(gi,(x,x)); spans[gi] = (min(a,x), x+slot); x += slot
    for gi,(a,b) in spans.items():
        sl.line(a+0.05, y0, b-0.05, y0)
        sl.line(a+0.05, y0+0.45, b-0.05, y0+0.45, w=0.5); sl.text((a+b)/2, y0+0.65, groups[gi]["name"], w=b-a, bold=True)

def column_target(sl, d):
    """实际 vs 目标：目标用横向标记线；达标绿、未达标灰（[约定]，标记线画法同手册 averageline）"""
    cats = d["categories"]; a = d["actual"]; t = d["target"]; X,Y,W,Hh = sl.CHART; n = len(cats)
    slot = W/n; bw = slot*0.5; y0 = Y+Hh-0.4; py = Y+0.85; sc = (y0-py)/max(a+t); sl.line(X, y0, X+W, y0)
    for i,c in enumerate(cats):
        cx = X+slot*(i+0.5); ok = a[i] >= t[i]
        sl.rect(cx-bw/2, y0-a[i]*sc, bw, a[i]*sc, TC["pos"] if ok else TC["accent5"], fmt(a[i]))
        sl.line(cx-bw/2-0.12, y0-t[i]*sc, cx+bw/2+0.12, y0-t[i]*sc, w=2.5)
        sl.text(cx, min(y0-t[i]*sc, y0-a[i]*sc)-0.2, f"{(a[i]/t[i]-1)*100:+.0f}%", w=slot, color="#000000" if ok else TC["bad"], bold=True)
        sl.text(cx, y0+0.22, c, w=slot)
    sl.line(X, Y+0.12, X+0.4, Y+0.12, w=2.5); sl.text(X+0.5, Y+0.12, d.get("target_name","Target"), w=1.5, align="l")
    sl.rect(X+2.0, Y+0.04, 0.16, 0.16, TC["pos"]); sl.text(X+2.25, Y+0.12, "≥ target", w=1.3, align="l")
    sl.rect(X+3.6, Y+0.04, 0.16, 0.16, TC["accent5"]); sl.text(X+3.85, Y+0.12, "< target", w=1.3, align="l")

def column_xbreak(sl, d):
    """横轴（类别轴）破断：在断开处画两条斜线并留出间隙（手册 axes break_x.jpg）"""
    cats = d["categories"]; v = d["values"]; b = d["break_after"]; X,Y,W,Hh = sl.CHART; n = len(cats)+0.6
    slot = W/n; bw = slot*0.6; y0 = Y+Hh-0.4; py = Y+0.4; sc = (y0-py)/max(v); x = X
    for i,c in enumerate(cats):
        if i == b+1:
            xm = x+slot*0.3; sl.line(x, y0, xm-0.06, y0); x += slot*0.6
            for dx in (-0.06, 0.06): sl.line(xm+dx-0.06, y0+0.12, xm+dx+0.06, y0-0.12, w=1)
            xs = xm+0.06
        else: xs = x
        cx = x+slot/2; sl.line(xs, y0, x+slot, y0)
        sl.rect(cx-bw/2, y0-v[i]*sc, bw, v[i]*sc, sl.col(0)); sl.text(cx, y0-v[i]*sc-0.18, fmt(v[i]), w=slot); sl.text(cx, y0+0.22, c, w=slot); x += slot

# ---------------- 瀑布扩展 ----------------
def waterfall_stacked(sl, d):
    """堆叠瀑布：每根柱按系列分段（手册 waterfall 章节：瀑布柱可含多个段，sample_waterfall_signed_sum.jpg）"""
    names = d["series"]; items = d["items"]; n = len(items); X,Y,W,Hh = sl.CHART
    run = 0; bars = []
    for it in items:
        tot = sum(it["values"]); k = it.get("kind","delta")
        if k in ("start","total"): bars.append(0); run = tot
        else: bars.append(run if tot >= 0 else run+tot); run += tot
    top = max(b+abs(sum(it["values"])) for b,it in zip(bars,items)); py = Y+0.6; y0 = Y+Hh-0.4; sc = (y0-py)/top
    slot = (W-1.6)/n; bw = slot*0.6; sl.line(X, y0, X+W-1.6, y0); run = 0
    for i,(it,b) in enumerate(zip(items,bars)):
        cx = X+slot*(i+0.5); up = b
        for j in range(len(names)-1, -1, -1):
            v = abs(it["values"][j]); sl.rect(cx-bw/2, y0-(up+v)*sc, bw, v*sc, sl.col(j), fmt(v)); up += v
        tot = sum(it["values"]); sl.text(cx, y0-up*sc-0.18, (fmt(tot) if it.get("kind") in ("start","total") else f"{tot:+g}"), w=slot)
        sl.text(cx, y0+0.22, it["label"], w=slot)
        lvl = up if (it.get("kind") in ("start","total") or tot >= 0) else b
        if i < n-1: sl.line(cx+bw/2, y0-lvl*sc, cx+slot-bw/2, y0-lvl*sc, w=0.5, dash=DASH)
    up = bars[-1]
    for j in range(len(names)-1, -1, -1):
        v = abs(items[-1]["values"][j]); sl.text(X+slot*(n-0.5)+bw/2+0.1, y0-(up+v/2)*sc, names[j], w=1.5, align="l"); up += v

# ---------------- Mekko / 面积变体 ----------------
def variwide(sl, d):
    """变宽柱（单系列单位 Mekko，手册 mekko-unit-axis-example.jpg）：宽=规模，高=指标"""
    cats = d["categories"]; w = d["widths"]; v = d["values"]; X,Y,W,Hh = sl.CHART; lx = X+0.7; pw = W-1.0
    y0 = Y+Hh-0.6; py = Y+0.4; sc = (y0-py)/max(v); tw = sum(w); x = lx
    for t in _ticks(max(v)): sl.text(lx-0.08, y0-t*sc, fmt(t)+d.get("suffix",""), w=0.6, align="r")
    sl.line(lx, y0, lx+pw, y0); sl.line(lx, py, lx, y0)
    for i,c in enumerate(cats):
        ww = pw*w[i]/tw; hl = c in d.get("highlight", [])
        sl.rect(x, y0-v[i]*sc, ww, v[i]*sc, TC["pos"] if hl or not d.get("highlight") else TC["accent5"], outline="#FFFFFF", lw=1.5)
        sl.text(x+ww/2, y0-v[i]*sc-0.18, fmt(v[i])+d.get("suffix",""), w=max(ww,0.6))
        sl.text(x+ww/2, y0+0.2, c, w=max(ww,0.6), size=sl.fs-2 if ww < 1 else None); sl.text(x+ww/2, y0+0.45, fmt(w[i]), w=max(ww,0.6), size=sl.fs-3, color="#777777"); x += ww
    sl.text(lx+pw, y0+0.7, d.get("width_title","Width = market size"), w=4, align="r", size=sl.fs-2, color="#777777")

def proportional_area(sl, d):
    """面积比例图：正方形面积 ∝ 数值，底对齐（[约定]）"""
    items = d["items"]; X,Y,W,Hh = sl.CHART; vmax = max(i["value"] for i in items); smax = min(Hh-0.9, (W-0.4*len(items))/sum(math.sqrt(i["value"]/vmax) for i in items))
    x = X+0.2; yb = Y+Hh-0.5
    for k,it in enumerate(items):
        s = smax*math.sqrt(it["value"]/vmax); f = it.get("color") or sl.col(k)
        sl.rect(x, yb-s, s, s, f, fmt(it["value"]) if s > 0.4 else None)
        if s <= 0.4: sl.text(x+s/2, yb-s-0.2, fmt(it["value"]), w=1)
        sl.text(x+s/2, yb+0.22, it["label"], w=max(s,1.2)); x += s+0.4

# ---------------- 条形扩展 ----------------
def bar_yoy(sl, d):
    """年度对比条形：上年浅灰细条 + 本年绿条 + 右侧变化率列（[约定]，手册 bar-chart.jpg 的条形语言）"""
    cats = d["categories"]; p = d["previous"]; c = d["current"]; X,Y,W,Hh = sl.CHART; lx = X+2.4; pw = W-2.4-2.4
    n = len(cats); top = Y+0.45; slot = (Hh-0.45)/n; sc = pw/max(p["values"]+c["values"])
    sl.line(lx, top, lx, Y+Hh); sl.text(lx+pw+1.4, Y+0.15, "Δ", w=1, bold=True)
    for i,k in enumerate(cats):
        cy = top+slot*(i+0.5); a, b = p["values"][i], c["values"][i]
        sl.rect(lx, cy-slot*0.32, a*sc, slot*0.25, TC["accent5"]); sl.rect(lx, cy-slot*0.05, b*sc, slot*0.33, TC["pos"])
        sl.text(lx+a*sc+0.08, cy-slot*0.2, fmt(a), w=0.8, align="l", size=sl.fs-2, color="#777777", avoid=False)
        sl.text(lx+b*sc+0.08, cy+0.11*slot, fmt(b), w=0.8, align="l", avoid=False)
        ch = (b/a-1)*100; sl.text(lx+pw+1.4, cy, f"{ch:+.0f}%", w=1, bold=True, color=TC["good"] if ch >= 0 else TC["bad"])
        sl.text(lx-0.1, cy, k, w=2.3, align="r")
    sl.rect(X, Y+0.04, 0.16, 0.16, TC["pos"]); sl.text(X+0.22, Y+0.12, c["name"], w=1, align="l")
    sl.rect(X+1.2, Y+0.04, 0.16, 0.16, TC["accent5"]); sl.text(X+1.42, Y+0.12, p["name"], w=1, align="l")

def bar_diverging(sl, d):
    """正负条形：零线居中，正值绿右、负值红左（[约定]）"""
    cats = d["categories"]; v = d["values"]; X,Y,W,Hh = sl.CHART; lx = X+2.4; pw = W-2.4-0.6
    m = max(abs(x) for x in v); mid = lx+pw*(-min(0,min(v)))/(max(0,max(v))-min(0,min(v))); sc = (pw-1.2)/(max(0,max(v))-min(0,min(v)))
    n = len(cats); slot = Hh/n; bh = slot*0.6; sl.line(mid, Y, mid, Y+Hh)
    for i,c in enumerate(cats):
        cy = Y+slot*(i+0.5); x = v[i]
        sl.rect(mid if x>=0 else mid+x*sc, cy-bh/2, abs(x)*sc, bh, TC["good"] if x>=0 else TC["bad"])
        sl.text(mid+x*sc+(0.08 if x>=0 else -0.08), cy, f"{x:+g}"+d.get("suffix",""), w=0.9, align="l" if x>=0 else "r")
        sl.text(mid+(-0.1 if x>=0 else 0.1), cy, c, w=2.3, align="r" if x>=0 else "l", avoid=False)

def bar_percent(sl, d):
    """100% 堆叠条形（李克特/调研）（手册 sample_100perc 的条形版）"""
    cats = d["categories"]; ser = d["series"]; X,Y,W,Hh = sl.CHART; lx = X+2.4; pw = W-2.4-0.3
    n = len(cats); top = Y+0.45; slot = (Hh-0.45)/n; bh = slot*0.6; cols = d.get("colors"); cols = TC["likert"] if cols == "likert" else cols
    for i,c in enumerate(cats):
        cy = top+slot*(i+0.5); tot = sum(s["values"][i] for s in ser); x = lx
        for j,s in enumerate(ser):
            w = pw*s["values"][i]/tot; f = cols[j] if cols else sl.col(j); sl.rect(x, cy-bh/2, w, bh, f, f"{s['values'][i]/tot*100:.0f}%" if w > 0.45 else None, outline="#FFFFFF", lw=0.75); x += w
        sl.text(lx-0.1, cy, c, w=2.3, align="r")
    x = lx
    for j,s in enumerate(ser):
        f = cols[j] if cols else sl.col(j); sl.rect(x, Y+0.04, 0.16, 0.16, f); sl.text(x+0.22, Y+0.12, s["name"], w=1.8, align="l"); x += 0.6+0.1*len(s["name"])

# ---------------- 折线扩展 ----------------
def slope(sl, d):
    """斜率图：两时点对比，重点项着色、其余浅灰（[约定]）"""
    items = d["items"]; X,Y,W,Hh = sl.CHART; xa, xb = X+3.2, X+W-3.2; py = Y+0.5; y0 = Y+Hh-0.2
    vals = [v for it in items for v in (it["a"], it["b"])]; lo, hi = min(vals), max(vals); yy = lambda v: y0-(v-lo)/(hi-lo)*(y0-py)
    sl.text(xa, Y+0.1, d["left_label"], w=2, bold=True); sl.text(xb, Y+0.1, d["right_label"], w=2, bold=True)
    sl.line(xa, py-0.1, xa, y0+0.1, w=0.5, color="#C0C0C0"); sl.line(xb, py-0.1, xb, y0+0.1, w=0.5, color="#C0C0C0")
    hl = set(d.get("highlight", []))
    for it in sorted(items, key=lambda i: i["label"] in hl):
        c = TC["pos"] if it["label"] in hl else (TC["bad"] if it["b"] < it["a"] and d.get("red_down") else TC["accent5"])
        sl.line(xa, yy(it["a"]), xb, yy(it["b"]), w=2.25 if it["label"] in hl else 1.25, color=c)
        for x,v in ((xa,it["a"]),(xb,it["b"])): sl.rect(x-0.06, yy(v)-0.06, 0.12, 0.12, c, shape=MSO_SHAPE.OVAL)
    for it in items:
        sl.text(xa-0.12, yy(it["a"]), f"{it['label']}  {fmt(it['a'])}", w=3, align="r")
        sl.text(xb+0.12, yy(it["b"]), f"{fmt(it['b'])}  {it['label']}", w=3, align="l")

def small_multiples(sl, d):
    """小倍数：多面板同刻度小柱图（[约定]；同刻度思想见手册 axes same_scale_*.jpg）"""
    panels = d["panels"]; cats = d["categories"]; cols = d.get("cols", 3); rows = math.ceil(len(panels)/cols)
    X,Y,W,Hh = sl.CHART; pw = W/cols; ph = Hh/rows; vmax = max(max(p["values"]) for p in panels)
    for k,p in enumerate(panels):
        r, c = divmod(k, cols); x0 = X+c*pw+0.15; y0 = Y+r*ph; w = pw-0.4; base = y0+ph-0.35; top = y0+0.55
        sl.text(x0, y0+0.15, p["title"], w=w, align="l", bold=True)
        sl.line(x0, base, x0+w, base, w=0.5); n = len(cats); slot = w/n; bw = slot*0.6
        for i,v in enumerate(p["values"]):
            h = (base-top)*v/vmax; f = TC["pos"] if i == n-1 else TC["accent5"]
            sl.rect(x0+slot*(i+0.5)-bw/2, base-h, bw, h, f)
            if i in (0, n-1): sl.text(x0+slot*(i+0.5), base-h-0.15, fmt(v), w=slot+0.3, size=sl.fs-3, avoid=False)
        if r == rows-1 or k+cols >= len(panels):
            sl.text(x0+slot*0.5, base+0.15, cats[0], w=slot+0.4, size=sl.fs-4, color="#777777"); sl.text(x0+slot*(n-0.5), base+0.15, cats[-1], w=slot+0.4, size=sl.fs-4, color="#777777")
        g = (p["values"][-1]/p["values"][0])**(1/(n-1))-1 if p["values"][0] else 0
        sl.text(x0+w, y0+0.15, f"CAGR {g*100:+.0f}%", w=1.6, align="r", size=sl.fs-3, color=TC["good"] if g>=0 else TC["bad"])

# ---------------- 咨询常用 ----------------
def funnel(sl, d):
    st = d["stages"]; X,Y,W,Hh = sl.CHART; n = len(st); slot = Hh/n; bh = slot*0.78; cx = X+W/2-1.0; mw = W-4.5; v0 = st[0]["value"]
    for i,s in enumerate(st):
        cy = Y+slot*(i+0.5); w = mw*s["value"]/v0; f = TC["pos"] if i == n-1 else (TC["accent6"] if i % 2 == 0 else TC["accent5"])
        sl.rect(cx-w/2, cy-bh/2, w, bh, f, fmt(s["value"]) if w > 0.5 else None)
        if w <= 0.5: sl.text(cx+w/2+0.3, cy, fmt(s["value"]), w=0.8)
        sl.text(X, cy, s["label"], w=2.2, align="l", bold=True)
        if i:
            sl.text(cx+mw/2+0.4, cy-slot/2, f"↓ {s['value']/st[i-1]['value']*100:.0f}%", w=1.4, align="l", color="#777777")
    sl.text(cx+mw/2+0.4, Y-0.05, "Conversion", w=1.6, align="l", bold=True, size=sl.fs-2)
    sl.text(cx+mw/2+0.4, Y+Hh-0.05, f"Overall {st[-1]['value']/v0*100:.1f}%", w=2.2, align="l", bold=True, color=TC["pos"])

def heatmap(sl, d):
    rows, cols, v = d["rows"], d["cols"], d["values"]; X,Y,W,Hh = sl.CHART; c0 = 2.6
    cw = (W-c0)/len(cols); rh = (Hh-0.45)/len(rows); flat = [x for r in v for x in r]; lo, hi = d.get("min", min(flat)), d.get("max", max(flat))
    c_lo, c_hi = d.get("low_color", "#FFFFFF"), d.get("high_color", TC["pos"])
    for j,c in enumerate(cols): sl.text(X+c0+cw*(j+0.5), Y+0.2, c, w=cw, bold=True)
    for i,r in enumerate(rows):
        sl.text(X+c0-0.1, Y+0.45+rh*(i+0.5), r, w=c0-0.1, align="r")
        for j in range(len(cols)):
            t = (v[i][j]-lo)/(hi-lo) if hi > lo else 0; f = lerp(c_lo, c_hi, t)
            b = sl.rect(X+c0+cw*j, Y+0.45+rh*i, cw, rh, f, outline="#FFFFFF", lw=1.5)
            sl._tf(b.text_frame, fmt(v[i][j], d.get("format")), color=ink(f)); sl.mark(f"{rows[i]}|{cols[j]}", X+c0+cw*(j+0.5), Y+0.45+rh*(i+0.5), 0.35, 0.3)

def matrix_2x2(sl, d):
    """战略矩阵（二乘二）+ 气泡：背景象限、象限名在角上、气泡位置（[约定]；气泡样式同手册 sample_bubble.jpg）"""
    X,Y,W,Hh = sl.CHART; lx = X+0.3; pw = W-0.7; py = Y+0.45; ph = Hh-1.0; q = d["quadrants"]
    xr, yr = d.get("x_range",[0,1]), d.get("y_range",[0,1]); xx = lambda v: lx+(v-xr[0])/(xr[1]-xr[0])*pw; yy = lambda v: py+ph-(v-yr[0])/(yr[1]-yr[0])*ph
    for k,(x0,y0) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        sl.rect(lx+x0*pw/2, py+y0*ph/2, pw/2, ph/2, "#F2F2F2" if k in (0,3) else "#E6E6E6", outline="#FFFFFF", lw=2)
        sl.text(lx+x0*pw/2+(0.12 if x0 == 0 else pw/2-0.12), py+y0*ph/2+0.2, q[k], w=3, align="l" if x0 == 0 else "r", bold=True, color="#777777")
    smax = max(p.get("size",1) for p in d["points"])
    for p in d["points"]:
        r = 0.12+0.4*math.sqrt(p.get("size",1)/smax); f = TC["pos"] if p.get("focus") else TC["muted"]
        sl.rect(xx(p["x"])-r, yy(p["y"])-r, 2*r, 2*r, f, shape=MSO_SHAPE.OVAL, outline="#FFFFFF", lw=0.75)
        sl.text(xx(p["x"])+r+0.05, yy(p["y"]), p["label"], w=2, align="l")
    sl.line(lx, py+ph, lx+pw, py+ph, tail="triangle"); sl.line(lx, py+ph, lx, py, tail="triangle")
    sl.text(lx+pw, py+ph+0.25, d["x_title"]+"  →", w=5, align="r", bold=True); sl.text(lx, py-0.25, "↑  "+d["y_title"], w=5, align="l", bold=True)

def pareto(sl, d):
    """帕累托：降序柱 + 累计% 折线（右轴）+ 80% 参考线（[约定]；组合图结构同手册 sample_combi.jpg）"""
    pairs = sorted(zip(d["categories"], d["values"]), key=lambda p: -p[1]); cats = [p[0] for p in pairs]; v = [p[1] for p in pairs]
    tot = sum(v); cum = []; s = 0
    for x in v: s += x; cum.append(s/tot*100)
    X,Y,W,Hh = sl.CHART; lx = X+0.6; pw = W-1.4; py = Y+0.55; y0 = Y+Hh-0.4; n = len(v); slot = pw/n; bw = slot*0.6
    sc = (y0-py)/max(v)*0.55; yr = lambda p: y0-p/100*(y0-py)   # 柱只占下半部，累计线在上方不压柱; yr = lambda p: y0-p/100*(y0-py)
    sl.line(lx, y0, lx+pw, y0); sl.line(lx+pw, py, lx+pw, y0)
    for t in (0, 20, 40, 60, 80, 100): sl.text(lx+pw+0.08, yr(t), f"{t}%", w=0.6, align="l", size=sl.fs-2)
    sl.line(lx, yr(80), lx+pw, yr(80), dash=DASH, color=TC["target"]); sl.text(lx+0.05, yr(80)-0.18, "80%", w=0.6, align="l", color=TC["target"])
    pts = []
    for i,(c,x) in enumerate(zip(cats,v)):
        cx = lx+slot*(i+0.5); f = TC["pos"] if cum[i-1 if i else 0] <= 80 or i == 0 else TC["accent5"]
        sl.rect(cx-bw/2, y0-x*sc, bw, x*sc, f, fmt(x))
        if x*sc < label_h(sl.fs):
            sl.text(cx, y0-x*sc-0.14, fmt(x), w=slot, size=sl.fs-2, avoid=False)
        sl.text(cx, y0+0.22, c, w=slot, size=sl.fs-2); pts.append((cx, yr(cum[i])))
    sl.poly(pts, outline="#000000", lw=1.5, closed=False)
    sl.text(lx-0.1, py-0.3, "Cum. %", w=1, align="r", size=sl.fs-2, bold=True, avoid=False)
    for (x,y),c in zip(pts,cum):
        sl.rect(x-0.05, y-0.05, 0.1, 0.1, "#000000", shape=MSO_SHAPE.OVAL); sl.text(x, py-0.3, f"{c:.0f}%", w=0.8, size=sl.fs-2, avoid=False)

def tornado(sl, d):
    """龙卷风/敏感性：按影响幅度排序，低于基准红、高于基准绿，中线为基准（[约定]）"""
    base = d["base"]; items = sorted(d["items"], key=lambda i: -(abs(i["high"]-i["low"]))); X,Y,W,Hh = sl.CHART
    lx = X+2.8; pw = W-2.8-0.8; lo = min(min(i["low"],i["high"]) for i in items); hi = max(max(i["low"],i["high"]) for i in items)
    span = max(base-lo, hi-base)*1.15; xx = lambda v: lx+pw/2+(v-base)/span*pw/2; top = Y+0.5; n = len(items); slot = (Hh-0.5)/n; bh = slot*0.6
    sl.line(xx(base), top-0.1, xx(base), Y+Hh); sl.text(xx(base), Y+0.15, f"Base case {fmt(base)}", w=3, bold=True)
    for i,it in enumerate(items):
        cy = top+slot*(i+0.5)
        for v,lab in ((it["low"], it.get("low_label","")), (it["high"], it.get("high_label",""))):
            f = TC["good"] if v >= base else TC["bad"]
            a, b = sorted((xx(base), xx(v))); sl.rect(a, cy-bh/2, b-a, bh, f)
            right = v >= base; sl.text(xx(v)+(0.08 if right else -0.08), cy, fmt(v)+(f" ({lab})" if lab else ""), w=2, align="l" if right else "r", size=sl.fs-2)
        sl.text(X, cy, it["label"], w=2.5, align="l")

def tree(sl, d):
    """指标拆解树（驱动树）：方框 + 直角连接线，从左到右（[约定]）"""
    root = d["root"]; X,Y,W,Hh = sl.CHART
    def depth(n): return 1+max([depth(c) for c in n.get("children",[])] or [0])
    def leaves(n): return sum(leaves(c) for c in n["children"]) if n.get("children") else 1
    D = depth(root); L = leaves(root); colw = W/D; bw = min(2.4, colw-0.6); rowh = Hh/L; bh = min(0.75, rowh*0.8)
    def place(n, lvl, r0):
        k = leaves(n); cy = Y+rowh*(r0+k/2); x = X+lvl*colw
        hl = n.get("highlight"); f = TC["pos"] if lvl == 0 else ("#FFFFFF")
        b = sl.rect(x, cy-bh/2, bw, bh, f, outline=TC["callout"] if hl else ("#000000" if lvl else None), lw=2 if hl else 0.75)
        sl._tf(b.text_frame, f"{n['label']}\n{n.get('value','')}", color="#FFFFFF" if lvl == 0 else "#000000", size=sl.fs-1); sl.mark(n["label"], x+bw/2, cy)
        r = r0
        for c in n.get("children", []):
            ccy = place(c, lvl+1, r); r += leaves(c); xm = x+bw+(colw-bw)/2
            sl.line(x+bw, cy, xm, cy, w=0.75); sl.line(xm, cy, xm, ccy, w=0.75); sl.line(xm, ccy, x+colw, ccy, w=0.75)
            if c.get("op"): sl.text(xm+0.12, ccy-0.15, c["op"], w=0.3, bold=True, size=sl.fs-2, avoid=False)
        return cy
    place(root, 0, 0)

def kpi_cards(sl, d):
    """KPI 卡片：大数字 + 变化 + 迷你走势（[约定]）"""
    cards = d["cards"]; X,Y,W,Hh = sl.CHART; cols = d.get("cols", min(4, len(cards))); rows = math.ceil(len(cards)/cols)
    cw = W/cols; ch = Hh/rows
    for k,c in enumerate(cards):
        r, j = divmod(k, cols); x = X+j*cw+0.1; y = Y+r*ch+0.1; w = cw-0.3; h = ch-0.3
        sl.rect(x, y, w, h, "#FFFFFF", outline="#C0C0C0", lw=0.75); sl.rect(x, y, 0.08, h, TC["pos"])
        sl.text(x+0.25, y+0.3, c["label"], w=w-0.3, align="l", color="#777777")
        sl.text(x+0.25, y+0.85, c["value"], w=w-0.3, align="l", size=32, bold=True, avoid=False)
        good = c.get("good", True); sl.text(x+0.25, y+1.4, c.get("delta",""), w=w-0.3, align="l", bold=True, color=TC["good"] if good else TC["bad"])
        sp = c.get("spark")
        if sp:
            lo, hi = min(sp), max(sp); sx = x+0.25; sw = w-0.5; sy = y+h-0.25; sh = min(0.8, h-2.0)
            pts = [(sx+sw*i/(len(sp)-1), sy-(v-lo)/(hi-lo or 1)*sh) for i,v in enumerate(sp)]
            sl.poly(pts, outline=TC["accent6"], lw=1.5, closed=False); sl.rect(pts[-1][0]-0.05, pts[-1][1]-0.05, 0.1, 0.1, TC["pos"], shape=MSO_SHAPE.OVAL)

def bullet(sl, d):
    """子弹图：灰度区间带 + 实际值条 + 目标竖线（[约定]）"""
    items = d["items"]; X,Y,W,Hh = sl.CHART; lx = X+2.6; pw = W-2.6-1.2; n = len(items); slot = Hh/n; bh = min(0.55, slot*0.6)
    for i,it in enumerate(items):
        cy = Y+slot*(i+0.5); mx = it["ranges"][-1]; sc = pw/mx; prev = 0
        for k,r in enumerate(it["ranges"]): sl.rect(lx+prev*sc, cy-bh/2, (r-prev)*sc, bh, ["#E6E6E6","#D0D0D0","#B8B8B8"][k % 3]); prev = r
        sl.rect(lx, cy-bh/6, it["value"]*sc, bh/3, TC["bullet"])
        sl.line(lx+it["target"]*sc, cy-bh/2-0.05, lx+it["target"]*sc, cy+bh/2+0.05, w=2.5, color=TC["target"])
        sl.text(lx-0.1, cy-0.1, it["label"], w=2.5, align="r", bold=True); sl.text(lx-0.1, cy+0.16, it.get("unit",""), w=2.5, align="r", size=sl.fs-3, color="#777777")
        sl.text(lx+pw+0.1, cy, f"{fmt(it['value'])} / {fmt(it['target'])}", w=1.2, align="l", size=sl.fs-2)
    sl.line(lx, Y-0.1, lx+0.3, Y-0.1, w=2.5, color=TC["target"]); sl.text(lx+0.4, Y-0.1, "Target", w=1, align="l", size=sl.fs-2)

def progress_bars(sl, d):
    """目标进度条：灰轨道 + 完成度（达标绿、落后灰）+ 百分比（[约定]）"""
    items = d["items"]; X,Y,W,Hh = sl.CHART; lx = X+3.0; pw = W-3.0-1.4; n = len(items); slot = Hh/n; bh = min(0.32, slot*0.4)
    exp = d.get("expected")
    for i,it in enumerate(items):
        cy = Y+slot*(i+0.5); p = min(it["value"]/it["target"], 1.0)
        sl.rect(lx, cy-bh/2, pw, bh, "#E6E6E6"); ok = exp is None or p >= exp
        sl.rect(lx, cy-bh/2, pw*p, bh, TC["pos"] if ok else TC["bad"])
        sl.text(lx-0.15, cy, it["label"], w=2.8, align="r"); sl.text(lx+pw+0.1, cy, f"{it['value']/it['target']*100:.0f}%", w=0.8, align="l", bold=True)
        sl.text(lx+pw+0.8, cy, f"{fmt(it['value'])}/{fmt(it['target'])}", w=1.4, align="l", size=sl.fs-3, color="#777777")
    if exp is not None:
        sl.line(lx+pw*exp, Y, lx+pw*exp, Y+Hh, dash=DASH, color=TC["target"]); sl.text(lx+pw*exp, Y-0.12, d.get("expected_label", f"Plan to date {exp*100:.0f}%"), w=2.4, color=TC["target"], size=sl.fs-2)

def radar(sl, d):
    """雷达图（[约定]）：灰色同心多边形网格 + 系列折线"""
    axes = d["axes"]; ser = d["series"]; mx = d.get("max", max(max(s["values"]) for s in ser)); X,Y,W,Hh = sl.CHART
    cx, cy = X+W/2-1.2, Y+Hh/2+0.05; R = Hh/2-0.45; n = len(axes)
    pt = lambda k, r: (cx+r*math.sin(2*math.pi*k/n), cy-r*math.cos(2*math.pi*k/n))
    for lvl in range(1, 5): sl.poly([pt(k, R*lvl/4) for k in range(n)], outline="#C0C0C0", lw=0.5)
    for k,a in enumerate(axes):
        sl.line(cx, cy, *pt(k, R), w=0.5, color="#C0C0C0"); x, y = pt(k, R+0.3)
        sl.text(x, y, a, w=2, align="c" if abs(x-cx) < 0.3 else ("l" if x > cx else "r"))
    for j,s in enumerate(ser):
        pts = [pt(k, R*v/mx) for k,v in enumerate(s["values"])]; sl.poly(pts, outline=sl.col(j), lw=2.25)
        for x,y in pts: sl.rect(x-0.05, y-0.05, 0.1, 0.1, sl.col(j), shape=MSO_SHAPE.OVAL)
    for j,s in enumerate(ser): sl.rect(X+W-2.2, Y+0.3+j*0.35-0.08, 0.16, 0.16, sl.col(j)); sl.text(X+W-1.98, Y+0.3+j*0.35, s["name"], w=1.9, align="l")

def tam_sam_som(sl, d):
    """TAM/SAM/SOM 嵌套圆：面积 ∝ 规模，底部对齐，右侧引线标注（[约定]）"""
    lv = d["levels"]; X,Y,W,Hh = sl.CHART; R0 = Hh/2-0.1; cx = X+R0+0.8; yb = Y+Hh; v0 = lv[0]["value"]
    cols = TC["tam"]
    for k,l in enumerate(lv):
        r = R0*math.sqrt(l["value"]/v0); sl.rect(cx-r, yb-2*r, 2*r, 2*r, l.get("color") or cols[k % 3], shape=MSO_SHAPE.OVAL, outline="#FFFFFF", lw=1.5)
        ty = yb-2*r+0.25; tx = X+2*R0+2.0
        sl.line(cx+r*0.35, ty, tx-0.1, ty, w=0.5); sl.rect(cx+r*0.35-0.04, ty-0.04, 0.08, 0.08, "#000000", shape=MSO_SHAPE.OVAL)
        sl.text(tx, ty, f"{l['label']}  {l.get('display', fmt(l['value']))}", w=4, align="l", bold=True, size=sl.fs+2)
        if l.get("desc"): sl.text(tx, ty+0.32, l["desc"], w=W-(tx-X), align="l", color="#555555", size=sl.fs-2)

def waffle(sl, d):
    """华夫图：10×10 方格表示百分比（[约定]）"""
    items = d["items"]; X,Y,W,Hh = sl.CHART; s = (Hh-0.1)/10; x0 = X+0.2; k = 0; cells = []
    tot = sum(i["value"] for i in items)
    for j,it in enumerate(items): cells += [j]*round(it["value"]/tot*100)
    cells = (cells+[len(items)-1]*100)[:100]
    for idx,j in enumerate(cells):
        r, c = divmod(idx, 10); sl.rect(x0+c*s+0.02, Y+(9-r)*s+0.02, s-0.04, s-0.04, items[j].get("color") or sl.col(j))
    for j,it in enumerate(items):
        y = Y+0.3+j*0.6; f = it.get("color") or sl.col(j); sl.rect(x0+10*s+0.5, y-0.12, 0.24, 0.24, f)
        sl.text(x0+10*s+0.9, y, f"{it['value']/tot*100:.0f}%  {it['label']}", w=5, align="l", bold=j == 0, size=sl.fs+2 if j == 0 else None)

RENDER.update({
 "stacked_clustered": stacked_clustered, "column_error": column_error, "column_grouped": column_grouped, "column_target": column_target, "column_xbreak": column_xbreak,
 "waterfall_stacked": waterfall_stacked, "waterfall_subtotal": waterfall, "waterfall_percent": waterfall,
 "variwide": variwide, "proportional_area": proportional_area,
 "bar_yoy": bar_yoy, "bar_diverging": bar_diverging, "bar_percent": bar_percent,
 "line_target": lambda s,d: line_area(s,d,"line"), "slope": slope, "small_multiples": small_multiples,
 "gantt_progress": lambda s,d: gantt(s,d), "gantt_swimlane": lambda s,d: gantt(s,d),
 "funnel": funnel, "heatmap": heatmap, "matrix_2x2": matrix_2x2, "pareto": pareto, "tornado": tornado, "tree": tree,
 "kpi_cards": kpi_cards, "bullet": bullet, "progress_bars": progress_bars, "radar": radar, "tam_sam_som": tam_sam_som, "waffle": waffle,
})

# 多图拼版（不计入 55 种单图）：dashboard / facet，渲染入口在 tc_core.render → tc_dash.render
RENDER.update({"dashboard": None, "facet": None})
