#!/usr/bin/env python3
"""数据分析 + 图表推荐（规则引擎）。
用法：
  python tc_advise.py data.csv [--intent "想说明收入增长主要靠线上"] [-o draft.json] [--json report.json]
  cat table.txt | python tc_advise.py - --intent "..."
支持 CSV / TSV / Excel(.xlsx) / JSON / 粘贴的表格（制表符、逗号、竖线 markdown 表、多空格对齐）。
输出：中文大白话报告（stdout）+ JSON（--json 指定文件，"-" 表示打印到 stdout）+ 首选图的可渲染 spec 草稿（-o）。
规则说明见 docs/CHART_SELECTION.md。规则只是起点，Agent 应结合用户语境做最终判断。"""
import sys, os, re, json, csv, io, math, argparse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------ 读入
def _read_text(txt):
    lines = [l.rstrip("\n\r") for l in txt.strip().splitlines() if l.strip()]
    lines = [l for l in lines if not re.fullmatch(r"\s*\|?\s*:?-{2,}.*", l)]          # markdown 分隔行
    if lines and lines[0].count("|") >= 2:
        return [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines]
    sample = "\n".join(lines[:5])
    if "\t" in sample: return [l.split("\t") for l in lines]
    if sample.count(",") >= len(lines[:5]) and not re.search(r"\d,\d{3}", sample.split("\n")[0]):
        return list(csv.reader(io.StringIO("\n".join(lines))))
    if ";" in sample: return [l.split(";") for l in lines]
    if "," in sample: return list(csv.reader(io.StringIO("\n".join(lines))))
    return [re.split(r"\s{2,}", l.strip()) for l in lines]

def read_table(path):
    if path == "-": return _read_text(sys.stdin.read())
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        try: import openpyxl
        except ImportError: sys.exit("读取 Excel 需要 openpyxl：pip install openpyxl（或另存为 CSV）。")
        ws = openpyxl.load_workbook(path, data_only=True).active
        rows = [["" if c is None else (c.isoformat()[:10] if isinstance(c, (datetime.date, datetime.datetime)) else str(c)) for c in r] for r in ws.iter_rows(values_only=True)]
        return [r for r in rows if any(x.strip() for x in r)]
    if ext == ".json":
        j = json.load(open(path, encoding="utf-8"))
        if isinstance(j, dict) and "rows" in j and "columns" in j: return [j["columns"]] + j["rows"]
        if isinstance(j, dict): j = [dict(zip(j, r)) for r in zip(*j.values())]
        if isinstance(j, list) and j and isinstance(j[0], dict):
            keys = list(dict.fromkeys(k for r in j for k in r)); return [keys] + [[r.get(k, "") for k in keys] for r in j]
        return j
    return _read_text(open(path, encoding="utf-8-sig").read())

def pnum(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool): return float(x)
    s = str(x).strip().replace("−", "-").replace("–", "-").replace("\u00a0", "")
    if s in ("", "-", "—", "n/a", "NA", "N/A"): return None
    neg = s.startswith("(") and s.endswith(")"); s = s.strip("()")
    s = re.sub(r"^[\$€£¥￥]|[\$€£¥￥]$", "", s).replace(",", "").replace(" ", "")
    s = re.sub(r"(?i)(%|pp|pts?|x|bn|b|m|k|亿|万|元)$", "", s)
    try: v = float(s)
    except ValueError: return None
    return -v if neg else v

PERIOD = re.compile(r"(?i)^((19|20)\d{2}([EABF]|年)?|(FY|CY)\s?'?\d{2,4}[EAB]?|Q[1-4](\s?'?\d{2,4})?|(19|20)\d{2}\s?[-/ ]?(Q[1-4]|H[12]|M?\d{1,2})|H[12](\s?\d{2,4})?|"
                    r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december|"
                    r"\d{1,2}月|第?[一二三四1-4]季度|W\d{1,2})\.?$")
def is_period(s): return bool(PERIOD.match(str(s).strip()))
def is_date(s):
    try: datetime.date.fromisoformat(str(s).strip()[:10]); return len(str(s).strip()) >= 10
    except ValueError: return False

ROLE = {
    "target": r"(?i)target|plan|budget|goal|目标|计划|预算",
    "low": r"(?i)^(low|min|下限|最低|悲观)|low$", "high": r"(?i)^(high|max|上限|最高|乐观)|high$", "base": r"(?i)^base|基准",
    "width": r"(?i)width|size|market|规模|市场|weight|权重|宽度|volume|销量",
    "start": r"(?i)^(start|begin|from|开始|起始)", "end": r"(?i)^(end|finish|to|due|结束|完成日)", "progress": r"(?i)progress|完成度|% ?complete",
    "x": r"(?i)^x$", "y": r"(?i)^y$", "size": r"(?i)^(size|bubble|气泡)",
}
START_KW = r"(?i)^(start|opening|begin|期初|起点|基期|上年|去年|prior|base)|(19|20)\d{2}"
TOTAL_KW = r"(?i)(end|closing|total|net|期末|合计|总计|净|终点|本年|今年)|(19|20)\d{2}"
SUB_KW = r"(?i)gross|ebit|ebitda|operating|subtotal|小计|毛利|营业利润|税前"
STAGE_KW = r"(?i)visit|view|lead|signup|sign-up|cart|checkout|order|purchase|convert|trial|paid|访问|浏览|注册|加购|下单|支付|转化|线索|商机|成交"
CJK = re.compile(r"[\u4e00-\u9fff]")

# ------------------------------------------------------------ 形态分析
def analyse(rows):
    hdr = [str(h).strip() for h in rows[0]]; body = [list(r) + [""] * (len(hdr) - len(r)) for r in rows[1:]]
    body = [r[:len(hdr)] for r in body if any(str(c).strip() for c in r)]
    cols = list(zip(*body)) if body else [[] for _ in hdr]
    kinds = []
    for h, c in zip(hdr, cols):
        ne = [x for x in c if str(x).strip()]
        if ne and sum(is_date(x) for x in ne) >= 0.8 * len(ne): kinds.append("date")
        elif ne and sum(pnum(x) is not None for x in ne) >= 0.8 * len(ne) and not all(is_period(x) and re.fullmatch(r"(19|20)\d{2}", str(x).strip()) for x in ne): kinds.append("num")
        elif ne and sum(is_period(x) for x in ne) >= 0.8 * len(ne): kinds.append("period")
        else: kinds.append("text")
    pct = any("%" in str(x) for c, k in zip(cols, kinds) if k == "num" for x in c) or any("%" in h for h, k in zip(hdr, kinds) if k == "num")
    unit = next((m.group(1) for h in hdr for m in [re.search(r"[\(（]([^\)）]+)[\)）]", h)] if m), None) or ("%" if pct else None)
    roles = {}
    for i, h in enumerate(hdr):
        for r, pat in ROLE.items():
            if r not in roles and kinds[i] in ("num", "date") and re.search(pat, h): roles[r] = i
    A = dict(headers=hdr, kinds=kinds, n_rows=len(body), unit=unit, pct=pct, roles={k: hdr[v] for k, v in roles.items()}, rows=body)
    dims = [i for i, k in enumerate(kinds) if k in ("text", "period")]; meas = [i for i, k in enumerate(kinds) if k == "num"]; dates = [i for i, k in enumerate(kinds) if k == "date"]
    A.update(n_dims=len(dims), n_measures=len(meas), dims=[hdr[i] for i in dims], measures=[hdr[i] for i in meas])
    # 甘特：有开始/结束日期
    if len(dates) >= 2:
        si = roles.get("start", dates[0]); ei = roles.get("end", dates[1] if dates[1] != si else dates[0])
        A["shape"] = "schedule"; A["tasks"] = [dict(name=str(r[dims[0]]) if dims else f"Task {k+1}", start=str(r[si])[:10], end=str(r[ei])[:10],
                                                     **({"progress": pnum(r[roles["progress"]]) / (100 if pnum(r[roles["progress"]]) and pnum(r[roles["progress"]]) > 1 else 1)} if "progress" in roles and pnum(r[roles["progress"]]) is not None else {}))
                                                for k, r in enumerate(body)]
        return A
    # 宽表：度量列名是时间（2021, 2022…）→ 转置
    wide = len(meas) >= 3 and sum(is_period(hdr[i]) for i in meas) >= 0.8 * len(meas)
    if wide:
        cats = [hdr[i] for i in meas]; ser = [dict(name=str(r[dims[0]]) if dims else f"S{k+1}", values=[pnum(r[i]) for i in meas]) for k, r in enumerate(body)]
        A.update(layout="宽表（时间在列上，已转置）", cats=cats, series=ser, time=True, dim2=None)
    elif len(dims) >= 2 and len(meas) == 1:
        d1, d2 = dims[0], dims[1]; c1 = list(dict.fromkeys(str(r[d1]) for r in body)); c2 = list(dict.fromkeys(str(r[d2]) for r in body))
        if kinds[d2] == "period" and kinds[d1] != "period": d1, d2, c1, c2 = d2, d1, c2, c1
        val = {(str(r[d1]), str(r[d2])): pnum(r[meas[0]]) for r in body}
        ser = [dict(name=b, values=[val.get((a, b)) for a in c1]) for b in c2]
        A.update(layout=f"长表两层分类（{hdr[d1]} × {hdr[d2]}，已透视）", cats=c1, series=ser, time=kinds[d1] == "period" or all(is_period(x) for x in c1), dim2=hdr[d2])
    else:
        ci = dims[0] if dims else None
        cats = [str(r[ci]) for r in body] if ci is not None else [f"#{k+1}" for k in range(len(body))]
        use = [i for i in meas if i not in [roles.get(x) for x in ("target", "low", "high", "base", "width", "progress")]]
        ser = [dict(name=hdr[i], values=[pnum(r[i]) for r in body]) for i in use]
        A.update(layout="长表（每行一个类别）", cats=cats, series=ser, time=ci is not None and (kinds[ci] == "period" or all(is_period(x) for x in cats)), dim2=None)
        for r in ("target", "low", "high", "base", "width"):
            if r in roles and kinds[roles[r]] == "num": A[r] = [pnum(x[roles[r]]) for x in body]
        if "base" in A: A["base"] = A["base"][0]
    # ---- 特征 ----
    S = A["series"]; cats = A["cats"]; vals = [v for s in S for v in s["values"] if v is not None]
    A["n_cats"] = len(cats); A["n_series"] = len(S)
    A["has_missing"] = any(v is None for s in S for v in s["values"])
    A["has_neg"] = any(v < 0 for v in vals); A["mixed_sign"] = A["has_neg"] and any(v > 0 for v in vals)
    A["max_label_len"] = max((len(str(c)) for c in cats), default=0)
    col_sums = [sum(s["values"][i] or 0 for s in S) for i in range(len(cats))] if S else []
    A["col_sums"] = col_sums
    A["sums_100"] = len(S) >= 2 and bool(col_sums) and all(abs(x - 100) <= 1.5 for x in col_sums)
    A["single_sum_100"] = len(S) == 1 and abs(sum(vals) - 100) <= 1.5 and not A["has_neg"]
    pv = sorted([v for v in (col_sums if len(S) > 1 else vals) if v > 0], reverse=True)
    A["extreme_ratio"] = round(pv[0] / pv[1], 1) if len(pv) >= 3 and pv[1] > 0 else 1.0
    A["two_points"] = len(S) == 2 and not A["time"] and (all(is_period(s["name"]) for s in S) or bool(re.search(r"(?i)before|after|prior|current|previous|plan|actual|前|后|去年|今年|上年|本年", " ".join(s["name"] for s in S))))
    A["series_are_periods"] = len(S) >= 2 and all(is_period(s["name"]) for s in S)
    A["monotone_down"] = len(S) == 1 and len(vals) >= 3 and all(b <= a for a, b in zip(vals, vals[1:]))
    A["stage_like"] = sum(bool(re.search(STAGE_KW, str(c))) for c in cats) >= max(2, len(cats) // 2)
    # 起止桥：首项 + 中间增量 ≈ 末项
    A["bridge"] = False; A["subtotal_idx"] = []
    if len(S) == 1 and len(cats) >= 3 and None not in S[0]["values"]:
        v = S[0]["values"]; run = v[0]; sub = []
        for i in range(1, len(v) - 1):
            if re.search(SUB_KW, str(cats[i])) and abs(v[i] - run) <= max(0.5, abs(run) * 0.01): sub.append(i); continue
            run += v[i]
        bal = abs(run - v[-1]) <= max(0.5, abs(v[-1]) * 0.01)
        A["bridge_gap"] = round(v[-1] - run, 4)
        kw = bool(re.search(START_KW, str(cats[0]))) and bool(re.search(TOTAL_KW, str(cats[-1])))
        A["bridge"] = A["mixed_sign"] and (bal or kw); A["bridge_balanced"] = bal; A["subtotal_idx"] = sub
        A["builddown"] = v[0] > 0 and all(x < 0 for k, x in enumerate(v[1:], 1) if k not in sub) and not bal
    RATIO = r"(?i)%|margin|率|rate|ratio|share|score|index|指数|得分"
    mags = [max((abs(v) for v in s["values"] if v is not None), default=0) for s in S]
    A["additive"] = len(S) >= 2 and not A.get("series_are_periods") and not any(re.search(RATIO, s["name"]) for s in S) and (min(mags) > 0 and max(mags) / min(mags) < 8)
    if len(S) >= 2 and not A["time"] and not A["sums_100"] and A["n_cats"] >= 6 and len(S) <= 3: A["additive"] = A["additive"] and not (len(S) in (2, 3) and not A.get("dim2"))
    A["similar_scale"] = len(S) >= 3 and bool(vals) and max(vals) <= 10 and min(vals) >= 0
    if len(S) == 2 and not A["time"]:
        a, b = [s["values"] for s in S]; A["series_ratio"] = (max(abs(x) for x in a if x is not None) or 1) / (max(abs(x) for x in b if x is not None) or 1)
    return A

# ------------------------------------------------------------ 意图
INTENTS = {
    "trend": r"增长|趋势|变化趋势|走势|上升|下降|growth|grew|trend|over time|cagr|增速",
    "composition": r"构成|占比|份额|结构|组成|mix|share|split|breakdown|composition|贡献占",
    "ranking": r"排名|最大|最小|领先|落后|top|rank|largest|biggest|leader|对比哪",
    "bridge": r"桥|拆解|驱动|从.*到|变动原因|bridge|walk|driver|drove|explain the change",
    "target": r"目标|达成|完成率|预算|计划|target|budget|plan|goal|vs plan",
    "correlation": r"相关|关系|越.*越|correlat|relationship|vs\.? ",
    "range": r"区间|范围|敏感|估值|range|sensitiv|valuation",
    "change": r"同比|环比|前后|对比两|两年|变化最大|yoy|before|after|change",
    "schedule": r"计划表|进度|时间表|里程碑|gantt|timeline|roadmap|schedule",
    "concentration": r"集中|二八|80/20|帕累托|主要原因|pareto|few causes",
}
def parse_intent(t):
    return [k for k, p in INTENTS.items() if t and re.search(p, t, re.I)]

# ------------------------------------------------------------ 结论候选
def fmt(v):
    if v is None: return "-"
    return f"{v:,.0f}" if abs(v) >= 100 else (f"{v:.1f}".rstrip("0").rstrip(".") if v != int(v) else f"{int(v)}")
def insights(A):
    zh = bool(CJK.search(" ".join(map(str, A.get("cats", []) + A["headers"]))))
    S, cats = A.get("series", []), A.get("cats", []); out = []
    T = (lambda z, e: z) if zh else (lambda z, e: e)
    if A.get("shape") == "schedule":
        t = A["tasks"]; end = max(x["end"] for x in t)
        return [T(f"项目在 {end} 前完成，共 {len(t)} 项工作", f"Programme completes by {end} across {len(t)} workstreams")], zh
    tot = A["col_sums"]
    if "low" in A and "high" in A:
        lo, hi = A["low"], A["high"]
        if "base" in A:
            sw = max(range(len(cats)), key=lambda i: abs(hi[i] - lo[i])); out.append(T(f"{cats[sw]}对结果影响最大（{fmt(lo[sw])}–{fmt(hi[sw])}）", f"{cats[sw]} is the biggest swing factor ({fmt(lo[sw])}–{fmt(hi[sw])})"))
        ov = (max(lo), min(hi))
        if "base" not in A: out.append(T(f"各方法重叠区间约 {fmt(ov[0])}–{fmt(ov[1])}" if ov[0] <= ov[1] else f"各方法区间 {fmt(min(lo))}–{fmt(max(hi))}", f"Methods overlap at {fmt(ov[0])}–{fmt(ov[1])}" if ov[0] <= ov[1] else f"Range {fmt(min(lo))}–{fmt(max(hi))}"))
        return out, zh
    if not S: return out, zh
    if A["n_series"] in (2, 3) and not A["time"] and not A["additive"] and not A["sums_100"] and A["n_cats"] >= 6 and not A.get("two_points"):
        x, y = S[0]["values"], S[1]["values"]; P = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
        mx, my = sum(a for a, _ in P) / len(P), sum(b for _, b in P) / len(P)
        cov = sum((a - mx) * (b - my) for a, b in P); sx = math.sqrt(sum((a - mx) ** 2 for a, _ in P)); sy = math.sqrt(sum((b - my) ** 2 for _, b in P))
        r = cov / (sx * sy) if sx and sy else 0
        out.append(T(f"{S[0]['name']}与{S[1]['name']}{'基本无关' if abs(r) < 0.3 else ('正相关' if r > 0 else '负相关')}（相关系数 {r:.2f}）", f"{'No clear link' if abs(r) < 0.3 else ('Positive link' if r > 0 else 'Negative link')} between {S[0]['name']} and {S[1]['name']} (r = {r:.2f})"))
        return out, zh
    if A.get("stage_like") and A.get("monotone_down"):
        v = S[0]["values"]; dr = min(range(1, len(v)), key=lambda i: v[i] / v[i - 1])
        out.append(T(f"整体转化率 {v[-1]/v[0]*100:.1f}%，{cats[dr]}这一步流失最大（只剩 {v[dr]/v[dr-1]*100:.0f}%）", f"Only {v[-1]/v[0]*100:.1f}% convert; biggest drop at {cats[dr]} ({v[dr]/v[dr-1]*100:.0f}% pass)"))
        return out, zh
    if A.get("sums_100"):
        f = S[0]; top = max(range(len(cats)), key=lambda i: f["values"][i] or 0); low = min(range(len(cats)), key=lambda i: f["values"][i] or 0)
        out.append(T(f"{cats[top]}的“{f['name']}”比例最高（{fmt(f['values'][top])}%），{cats[low]}最低（{fmt(f['values'][low])}%）", f"{cats[top]} has the highest '{f['name']}' share ({fmt(f['values'][top])}%), {cats[low]} the lowest ({fmt(f['values'][low])}%)"))
        return out, zh
    if A.get("series_are_periods") and len(S) == 2:
        a, b = S[0]["values"], S[1]["values"]; g = sum(x or 0 for x in b) / (sum(x or 0 for x in a) or 1) - 1
        best = max(range(len(cats)), key=lambda i: (b[i] or 0) - (a[i] or 0))
        out.append(T(f"{S[1]['name']}每个{'' if zh else ''}类别都高于{S[0]['name']}，合计 {g*100:+.0f}%" if all((y or 0) >= (x or 0) for x, y in zip(a, b)) else f"{S[1]['name']}合计比{S[0]['name']} {g*100:+.0f}%",
                     f"{S[1]['name']} above {S[0]['name']} in every period ({g*100:+.0f}% overall)" if all((y or 0) >= (x or 0) for x, y in zip(a, b)) else f"{S[1]['name']} {g*100:+.0f}% vs {S[0]['name']}"))
        out.append(T(f"{cats[best]}增量最大", f"{cats[best]} saw the largest increase")); return out, zh
    if A["time"] and len(S) >= 2 and not A["additive"]:
        for s_ in S:
            v = [x for x in s_["values"] if x is not None]
            if len(v) >= 2 and v[0]: out.append(T(f"{s_['name']}从 {fmt(v[0])} 到 {fmt(v[-1])}（{(v[-1]/v[0]-1)*100:+.0f}%）", f"{s_['name']} {fmt(v[0])} → {fmt(v[-1])} ({(v[-1]/v[0]-1)*100:+.0f}%)"))
        return out[:3], zh
    if A.get("bridge"):
        v = S[0]["values"]; mid = [(cats[i], v[i]) for i in range(1, len(v) - 1) if i not in A["subtotal_idx"]]
        up = max(mid, key=lambda p: p[1]); dn = min(mid, key=lambda p: p[1])
        if up[1] > 0: out.append(T(f"{cats[-1]}从 {fmt(v[0])} 变为 {fmt(v[-1])}，{up[0]}贡献最大（{up[1]:+g}）", f"{cats[0]} {fmt(v[0])} to {cats[-1]} {fmt(v[-1])}: {up[0]} the largest driver ({up[1]:+g})"))
        else: out.append(T(f"从{cats[0]} {fmt(v[0])} 到{cats[-1]} {fmt(v[-1])}，{dn[0]}是最大扣减项（{dn[1]:+g}）", f"From {cats[0]} {fmt(v[0])} to {cats[-1]} {fmt(v[-1])}; {dn[0]} the largest deduction ({dn[1]:+g})")); dn = (dn[0], 0)
        if dn[1] < 0: out.append(T(f"{dn[0]}是最大拖累（{dn[1]:+g}）", f"{dn[0]} was the biggest drag ({dn[1]:+g})"))
    elif A["time"] and len(S) == 1 and A["extreme_ratio"] >= 3:
        k = max(range(len(cats)), key=lambda i: tot[i]); rest = [tot[i] for i in range(len(cats)) if i != k]
        out.append(T(f"{cats[k]}是异常值（{fmt(tot[k])}），约为其他各期平均的 {tot[k]/(sum(rest)/len(rest)):.0f} 倍", f"{cats[k]} was an outlier ({fmt(tot[k])}), ~{tot[k]/(sum(rest)/len(rest)):.0f}x the other years"))
        if rest[0] and rest[-1]: out.append(T(f"剔除 {cats[k]} 后，从 {fmt(rest[0])} 增至 {fmt(rest[-1])}", f"Excluding {cats[k]}, grew from {fmt(rest[0])} to {fmt(rest[-1])}"))
    elif A["time"] and len(cats) >= 2 and tot[0] and tot[0] > 0 and tot[-1] > 0:
        n = len(cats) - 1; g = tot[-1] / tot[0] - 1; cagr = (tot[-1] / tot[0]) ** (1 / n) - 1 if n else 0
        out.append(T(f"{cats[0]}–{cats[-1]} 增长 {g*100:.0f}%（CAGR {cagr*100:+.1f}%）" if g >= 0 else f"{cats[0]}–{cats[-1]} 下降 {-g*100:.0f}%",
                     f"{'Grew' if g >= 0 else 'Fell'} {abs(g)*100:.0f}% from {cats[0]} to {cats[-1]} (CAGR {cagr*100:+.1f}%)"))
        if len(S) >= 2:
            gr = [(s["name"], (s["values"][-1] or 0) / s["values"][0] - 1) for s in S if s["values"][0]]
            if gr:
                f = max(gr, key=lambda p: p[1]); sh0 = next(s for s in S if s["name"] == f[0])
                out.append(T(f"{f[0]}增长最快（{f[1]*100:+.0f}%），占比从 {sh0['values'][0]/tot[0]*100:.0f}% 升到 {sh0['values'][-1]/tot[-1]*100:.0f}%",
                             f"{f[0]} grew fastest ({f[1]*100:+.0f}%), share {sh0['values'][0]/tot[0]*100:.0f}% → {sh0['values'][-1]/tot[-1]*100:.0f}%"))
        pk = max(range(len(cats)), key=lambda i: tot[i])
        if 0 < pk < len(cats) - 1: out.append(T(f"{cats[pk]}是峰值（{fmt(tot[pk])}），之后回落", f"Peak in {cats[pk]} ({fmt(tot[pk])}), declining since"))
    elif A.get("two_points"):
        a, b = S[0]["values"], S[1]["values"]; d = [(cats[i], (b[i] or 0) - (a[i] or 0)) for i in range(len(cats))]
        up = max(d, key=lambda p: p[1]); dn = min(d, key=lambda p: p[1])
        out.append(T(f"{up[0]}提升最多（{up[1]:+g}）", f"{up[0]} gained most ({up[1]:+g})"))
        if dn[1] < 0: out.append(T(f"{dn[0]}是唯一/最大下降项（{dn[1]:+g}）", f"{dn[0]} declined most ({dn[1]:+g})"))
    elif "target" in A:
        a = S[0]["values"]; t = A["target"]; hit = [cats[i] for i in range(len(cats)) if a[i] is not None and t[i] is not None and a[i] >= t[i]]
        out.append(T(f"{len(cats)} 项中 {len(hit)} 项达标", f"{len(hit)} of {len(cats)} hit target"))
    else:
        s = tot; tsum = sum(x for x in s if x and x > 0) or 1; order = sorted(range(len(cats)), key=lambda i: -(s[i] or 0))
        top = order[0]
        if len(S) == 1 and not A["has_neg"]:
            out.append(T(f"{cats[top]}最大，占 {s[top]/tsum*100:.0f}%", f"{cats[top]} is largest at {s[top]/tsum*100:.0f}% of total"))
            if len(cats) >= 5: out.append(T(f"前 3 项合计占 {sum(s[i] for i in order[:3])/tsum*100:.0f}%", f"Top 3 account for {sum(s[i] for i in order[:3])/tsum*100:.0f}%"))
            if len(order) > 1 and s[order[1]]: out.append(T(f"{cats[top]}是第二名的 {s[top]/s[order[1]]:.1f} 倍", f"{cats[top]} is {s[top]/s[order[1]]:.1f}x the next"))
        elif A["has_neg"]:
            out.append(T(f"{sum(1 for x in s if x > 0)} 项为正、{sum(1 for x in s if x < 0)} 项为负，{cats[top]}最高", f"{sum(1 for x in s if x > 0)} up, {sum(1 for x in s if x < 0)} down; {cats[top]} leads"))
        else:
            out.append(T(f"{cats[top]}总量最大（{fmt(s[top])}）", f"{cats[top]} is largest overall ({fmt(s[top])})"))
            if len(S) >= 2:
                big = max(S, key=lambda x: sum(v or 0 for v in x["values"]))
                out.append(T(f"{big['name']}是最主要的组成部分", f"{big['name']} is the main component"))
    return out, zh

# ------------------------------------------------------------ 候选图表打分
def candidates(A, intents):
    C = {}
    def add(t, sc, why, emph="", marks=""):
        if t not in C or C[t]["score"] < sc: C[t] = dict(type=t, score=sc, why=why, emphasis=emph, marks=marks)
    if A.get("shape") == "schedule":
        if any("progress" in t for t in A["tasks"]): add("gantt_progress", 96, "有开始/结束日期和完成度，适合进度甘特", "圈出落后的任务", "today 线")
        add("gantt", 92, "每行都有开始和结束日期，是典型的项目计划", "关键路径任务", "today 线、里程碑菱形、阶段括号")
        add("timeline", 70, "只想展示阶段和里程碑、不关心每个任务时", "关键里程碑", "里程碑")
        add("gantt_swimlane", 65, "任务能分成几个工作流时可以分泳道", "", "")
        return C
    n, m, S = A["n_cats"], A["n_series"], A["series"]; time = A["time"]; pos = not A["has_neg"]
    if "low" in A and "high" in A:
        if "base" in A: add("tornado", 95, "每个因素有低/高两个结果和一个基准值，是敏感性分析", "影响最大的因素", "基准线")
        add("football", 90, "每行有下限和上限，是区间/估值范围", "包含报价的区间", "报价/当前值竖线")
        add("dumbbell", 62, "把下限、上限当两个点，强调区间宽度", "最宽的区间", "")
        add("table_harvey", 35, "只需要列出数字时用表格", "", "")
    if "target" in A:
        if time and m == 1: add("line_target", 80, "随时间的指标对比一个目标值", "跌破/突破目标的点", "目标线、目标区间带")
        add("column_target", 90 if n <= 10 else 70, "每个类别都有实际值和目标值", "未达标的类别", "目标横线、差值标签")
        add("progress_bars", 72, "看完成率而不是绝对值时", "落后项", "进度期望线")
        add("bullet", 60, "如果还有差/中/好分档，可做子弹图（需补 ranges）", "", "")
    if A.get("width") and m >= 1 and not time:
        if m >= 2 or A.get("sums_100"): add("mekko_percent", 92, "有每列的规模（宽度）和各段占比，Mekko 同时表达市场大小和结构", "最大市场里的领先者", "列宽标签")
        else: add("variwide", 88, "宽度=规模、高度=指标，变宽柱能同时看两者", "又大又高的类别", "")
    if A.get("bridge"):
        if A["subtotal_idx"]: add("waterfall_subtotal", 97, "首项+各增量=末项，中间还有小计（如毛利/EBIT），是带小计的桥图", "最大的增量", "总差箭头")
        add("waterfall", 95, "首项 + 中间正负增量 = 末项，是标准的起止桥（瀑布图）", "最大的正/负驱动", "总差箭头（起点→终点）")
        add("waterfall_h", 70, "增量名字很长时用横向瀑布", "", "")
        add("bar_diverging", 55, "只看各因素正负贡献、不需要起止时", "", "")
    elif A.get("builddown"):
        add("waterfall_h", 88, "第一项是总额、后面都是扣减，适合横向成本拆解", "最大的成本项", "")
        add("waterfall_subtotal", 80, "如果最后要落到利润，加 total 行即可", "", "")
    elif len(S) == 1 and A["mixed_sign"]:
        add("bar_diverging", 88, "同一指标有正有负，正负条形从零线向两侧展开最直观", "最大正值和最大负值", "")
        add("waterfall", 62, "如果这些是对某个总数的贡献，可补起点/终点做桥图", "", "")
        add("bar_sorted", 55, "只比较大小时", "", "")
    if A.get("two_points") and m == 2:
        add("bar_yoy", 88 if n <= 10 else 70, "两个时点的同一指标，条形上下对比并标出变化率", "变化最大的类别", "Δ% 列")
        add("dumbbell", 82, "强调“从哪里到哪里”的移动距离", "移动最大的项", "")
        add("slope", 78 if n <= 8 else 55, "关注排名/方向的变化", "逆势下降的项", "")
    if time:
        if m == 1:
            v = S[0]["values"]
            add("column", 88 if n <= 12 else 60, "单一指标按时间排列，柱形最直接，可加 CAGR 箭头", "最后一年 / 峰值", "CAGR 箭头（首年→末年）")
            add("line", 82 if n > 8 else 70, "时间点较多时折线更清楚", "拐点", "")
            if A["extreme_ratio"] >= 3: add("column", 92 if n <= 12 else 70, f"某一期是其余的 {A['extreme_ratio']} 倍，用数值轴破断保持其他柱可读", "离群值", "轴破断")
            add("kpi_cards", 45, "只想放一个大数字+趋势", "", "")
        else:
            if A.get("sums_100"):
                add("percent", 92, "每期各部分加起来是 100%，用 100% 堆叠柱看结构变化", "占比变化最大的部分", "")
                add("area_percent", 75 if n > 6 else 60, "期数多时用 100% 面积图", "", "")
            elif A.get("series_are_periods"):
                add("clustered", 88 if n <= 8 else 60, "系列本身是不同年份/时期，逐类别并排对比两期", "增幅最大的类别", "差值箭头")
                add("line", 80, "按季度/月份看两年走势", "", "")
                add("column_grouped", 72, "按年分组、组内按季度排列", "", "")
            elif pos and A["additive"]:
                add("stacked", 90 if m <= 6 else 70, "各部分可加总，堆叠柱同时看总量增长和构成", "增长最快的部分", "总量 CAGR 箭头、总差箭头")
                add("area", 78 if n > 8 else 55, "期数多时用堆叠面积", "", "")
                add("percent", 68, "如果重点是结构（占比）而不是总量，100% 堆叠柱直接显示各部分占比", "占比变化最大的系列（最后一期）", "首末两期占比差值（callout）")
                add("line", 72 if m <= 5 else 50, "各系列不必加总、只比走势时", "", "")
                add("clustered", 66 if n <= 6 and m <= 4 else 40, "逐期并排比较各系列", "", "")
                if m >= 5: add("small_multiples", 80, "系列太多，每个系列一个小图更清楚", "增长最快的面板", "每个面板 CAGR")
            else:
                add("line", 80, "各系列不能加总（单位或含义不同）或有负值，用折线看走势", "", ""); add("clustered", 65, "逐期并排比较", "", "")
            if m == 2:
                r = max(abs(x) for x in S[0]["values"] if x is not None) / (max(abs(x) for x in S[1]["values"] if x is not None) or 1)
                if r > 8 or r < 1 / 8 or any(re.search(r"%|margin|率|rate|ratio", s["name"], re.I) for s in S):
                    add("combo", 89, "两个指标量级差很多（或一个是比率），柱+线双轴组合", "", "右轴折线")
    elif not A.get("bridge") and not A.get("two_points"):
        if m == 1 and not A["mixed_sign"]:
            v = S[0]["values"]
            if A["stage_like"] and A["monotone_down"]: add("funnel", 94, "各阶段逐级递减且名字是转化步骤，是典型漏斗", "流失最大的一步", "阶段转化率")
            if A["single_sum_100"] or "composition" in intents:
                add("pie" if n <= 5 else "bar_sorted", 84, "各项加起来是 100%（整体的构成）" if A["single_sum_100"] else "要表达构成", "最大的一块", "")
                add("doughnut", 80 if n <= 5 else 50, "构成 + 中间放总数", "", "中心总数")
                add("waffle", 70 if n <= 3 else 40, "只有 2–3 项时用华夫格表达“百分之几”", "", "")
            add("bar_sorted", 86 if n > 6 or A["max_label_len"] > 10 else 80, "单一指标比较大小，排序条形最好读，名字长也放得下", "第一名或要讨论的那一项", "")
            add("column", 76 if n <= 8 and A["max_label_len"] <= 10 else 50, "类别少且名字短时也可用柱形", "", "")
            if n >= 5: add("pareto", 74, "类别多、想说明“少数几项占大头”时", "前几项", "累计% 线、80% 线")
            if A["extreme_ratio"] >= 4: add("proportional_area", 70, f"最大值是第二名的 {A['extreme_ratio']} 倍，面积图更能体现量级差", "", "")
        elif m >= 2:
            if A.get("sums_100"):
                lng = A["max_label_len"] > 8 or n > 5
                add("bar_percent", 90 if lng else 80, "每个类别的各部分加起来是 100%（调研量表/结构），横向条形放得下长类别名", "最好/最差的类别", "")
                add("percent", 80 if lng else 90, "每个类别的各部分加起来是 100%，竖向 100% 堆叠柱", "", "")
            if m == 3 and n >= 5: add("bubble", 84, "三个数值指标（x、y、大小），适合气泡图", "右上角的项", "象限分割线")
            if m == 2 and n >= 6:
                add("scatter", 82, "两个数值指标、很多个体，看相关关系", "离群点", "均值分割线")
                add("matrix_2x2", 64, "想按两个指标的高/低把对象分成四类（需把数值换算成 0–1 得分）", "右上象限", "象限名")
                add("bar_sorted", 50, "只关心其中一个指标的排名", "", "")
            if pos and not A.get("sums_100") and A["additive"]:
                add("bar_stacked", 80, "各部分可加总，横向堆叠条形比较总量和构成", "", "")
                add("stacked", 74 if n <= 8 and A["max_label_len"] <= 10 else 50, "", "", "")
                add("mekko_unit", 72 if n <= 6 else 40, "想同时表达各类别的规模和内部构成", "", "")
                add("clustered", 70 if m <= 4 and n <= 8 else 40, "逐类别并排比较各系列", "", "")
            if m == 2 and pos and A["additive"]: add("butterfly", 76, "两组左右对照（如男/女、我方/对手）", "差异最大的一项", "")
            if A["similar_scale"] or (m >= 3 and n >= 3): add("heatmap", 78, "行×列的数值矩阵，用颜色深浅看高低", "最低/最高格", "")
            if m >= 3 and n <= 3 and A["similar_scale"]: add("radar", 72, "少数对象在多个评分维度上的对比", "", "")
    # 意图加权
    boost = {"trend": ["line", "column", "stacked", "area", "combo", "small_multiples", "line_target"],
             "composition": ["pie", "doughnut", "percent", "stacked", "mekko_percent", "mekko_unit", "waffle", "bar_percent", "area_percent"],
             "ranking": ["bar_sorted", "pareto", "bar", "column"], "bridge": ["waterfall", "waterfall_subtotal", "waterfall_h", "waterfall_stacked"],
             "target": ["column_target", "bullet", "progress_bars", "line_target"], "correlation": ["scatter", "bubble", "matrix_2x2"],
             "range": ["football", "tornado"], "change": ["bar_yoy", "dumbbell", "slope", "waterfall"], "schedule": ["gantt", "gantt_progress", "timeline"],
             "concentration": ["pareto", "bar_sorted"]}
    for it in intents:
        for t in boost[it]:
            if t in C:
                C[t]["score"] += 12 + (24 if it == "composition" and t in ("percent", "area_percent", "bar_percent", "mekko_percent", "pie", "doughnut") else 0)
                C[t]["why"] += f"；符合你想表达的“{it}”"
    return C

# ------------------------------------------------------------ spec 草稿
def build(t, A, title):
    S, cats = A.get("series", []), A.get("cats", [])
    clean = lambda vs: [0 if v is None else (int(v) if float(v).is_integer() else round(v, 4)) for v in vs]
    sp = dict(type=t, title=title, unit=A.get("unit") or "", footnote="", source="")
    d = {}; hl = []; deco = []; call = []
    one = S[0] if S else None; last = cats[-1] if cats else None
    if t in ("column", "line", "bar", "bar_sorted", "pareto"):
        if t == "pareto": d = dict(categories=cats, values=clean(one["values"]))
        else: d = dict(categories=cats, series=[dict(name=one["name"], values=clean(one["values"]))])
        if t == "column":
            if A["time"] and len(cats) >= 3 and all((v or 0) > 0 for v in one["values"]): deco.append(dict(type="cagr", **{"from": 0, "to": len(cats) - 1}))
            if A["extreme_ratio"] >= 3:
                pv = sorted([v for v in one["values"] if v], reverse=True); d["axis_break"] = {"from": round(pv[1] * 1.3), "to": round(pv[0] * 0.85)}
            big = cats[max(range(len(cats)), key=lambda i: one["values"][i] or 0)]
            hl = [dict(category=big if A["extreme_ratio"] >= 3 else last if A["time"] else cats[max(range(len(cats)), key=lambda i: one["values"][i] or 0)])]
        if t == "bar_sorted": d["highlight"] = [cats[max(range(len(cats)), key=lambda i: one["values"][i] or 0)]]
    elif t in ("stacked", "percent", "clustered", "area", "area_percent", "bar_stacked", "bar_percent", "mekko_unit", "butterfly", "line"):
        d = dict(categories=cats, series=[dict(name=s["name"], values=clean(s["values"])) for s in S])
        if t == "stacked" and A["time"] and len(cats) >= 3: deco.append(dict(type="cagr", **{"from": 0, "to": len(cats) - 1}))
        if t in ("stacked", "percent", "clustered"): hl = [dict(category=last)] if A["time"] else []
    elif t == "mekko_percent":
        d = dict(categories=cats, widths=clean(A["width"]), series=[dict(name=s["name"], values=clean(s["values"])) for s in S])
    elif t == "variwide":
        d = dict(categories=cats, widths=clean(A["width"]), values=clean(one["values"]))
    elif t == "combo":
        a, b = S[0], S[1]
        if re.search(r"%|margin|率|rate|ratio", a["name"], re.I): a, b = b, a
        d = dict(categories=cats, columns=[dict(name=a["name"], values=clean(a["values"]))], line=dict(name=b["name"], values=clean(b["values"])))
    elif t == "small_multiples":
        d = dict(categories=cats, cols=3, panels=[dict(title=s["name"], values=clean(s["values"])) for s in S])
    elif t in ("pie", "doughnut", "waffle", "proportional_area", "funnel"):
        key = "segments" if t in ("pie", "doughnut") else "stages" if t == "funnel" else "items"
        d = {key: [dict(label=c, value=v) for c, v in zip(cats, clean(one["values"]))]}
        if t == "doughnut": d["center"] = fmt(sum(one["values"]))
    elif t in ("waterfall", "waterfall_subtotal", "waterfall_h"):
        v = clean(one["values"]); items = [dict(label=cats[0], value=v[0], kind="start")]
        for i in range(1, len(v) - 1):
            items.append(dict(label=cats[i], kind="subtotal") if i in A["subtotal_idx"] else dict(label=cats[i], value=v[i]))
        items.append(dict(label=cats[-1], kind="total") if A.get("bridge") else dict(label=cats[-1], value=v[-1]))
        if t == "waterfall_h" and not A.get("bridge"): items[-1] = dict(label=cats[-1], value=v[-1])
        d = dict(items=items)
        if t == "waterfall_h" and A.get("builddown"): d["items"].append(dict(label="Remaining" if not CJK.search(cats[0]) else "剩余", kind="total"))
        if t != "waterfall_h": deco.append(dict(type="total_diff", **{"from": 0, "to": len(items) - 1}, percent=True))
        mid = [i for i in range(1, len(items) - 1) if "value" in items[i]]
        if mid: hl = [dict(category=items[max(mid, key=lambda i: abs(items[i]["value"]))]["label"])]
    elif t == "bar_diverging":
        d = dict(categories=cats, values=clean(one["values"]))
    elif t in ("bar_yoy", "dumbbell", "slope"):
        a, b = S
        if t == "bar_yoy": d = dict(categories=cats, previous=dict(name=a["name"], values=clean(a["values"])), current=dict(name=b["name"], values=clean(b["values"])))
        elif t == "dumbbell": d = dict(categories=cats, series=[dict(name=a["name"], values=clean(a["values"])), dict(name=b["name"], values=clean(b["values"]))])
        else: d = dict(left_label=a["name"], right_label=b["name"], items=[dict(label=c, a=x, b=y) for c, x, y in zip(cats, clean(a["values"]), clean(b["values"]))])
    elif t == "column_target":
        d = dict(categories=cats, actual=clean(one["values"]), target=clean(A["target"]))
    elif t == "line_target":
        d = dict(categories=cats, series=[dict(name=one["name"], values=clean(one["values"]))], target=A["target"][0], target_label=f"Target {fmt(A['target'][0])}")
    elif t == "progress_bars":
        d = dict(items=[dict(label=c, value=v, target=g) for c, v, g in zip(cats, clean(one["values"]), clean(A["target"]))])
    elif t == "football":
        d = dict(categories=cats, series=[dict(name="Low", values=clean(A["low"])), dict(name="High", values=clean(A["high"]))])
    elif t == "tornado":
        d = dict(base=A["base"], items=[dict(label=c, low=l, high=h) for c, l, h in zip(cats, clean(A["low"]), clean(A["high"]))])
    elif t == "heatmap":
        d = dict(rows=cats, cols=[s["name"] for s in S], values=[clean([s["values"][i] for s in S]) for i in range(len(cats))])
    elif t in ("scatter", "bubble"):
        pts = [dict(label=c, x=S[0]["values"][i], y=S[1]["values"][i], **({"size": S[2]["values"][i]} if t == "bubble" else {})) for i, c in enumerate(cats)]
        d = dict(points=pts, x_title=S[0]["name"], y_title=S[1]["name"])
    elif t == "radar":
        d = dict(axes=[s["name"] for s in S], series=[dict(name=c, values=clean([s["values"][i] for s in S])) for i, c in enumerate(cats)])
    elif t in ("gantt", "gantt_progress", "gantt_swimlane", "timeline"):
        tk = A["tasks"]; st, en = min(x["start"] for x in tk), max(x["end"] for x in tk)
        if t == "timeline": d = dict(start=st, end=en, phases=[dict(name=x["name"], start=x["start"], end=x["end"]) for x in tk])
        else: d = dict(start=st, end=en, tasks=[dict(name=x["name"], start=x["start"], end=x["end"], **({"progress": x["progress"]} if t == "gantt_progress" and "progress" in x else {})) for x in tk])
    else:
        return None
    if t == "bar_percent" and len(S) == 4: d["colors"] = "likert"
    sp["data"] = d
    if deco: sp["decorations"] = deco
    if hl: sp["highlight"] = hl
    return sp

# ------------------------------------------------------------ 主流程
NAMES = {}
def multi_panel(A):
    """多指标 × 多分组（× 时间）的长表 → 推荐分面 / 拼版，并给出可渲染的 facet 草稿。"""
    if A.get("shape") == "schedule" or A["n_measures"] < 2 or A["n_dims"] < 2: return None
    hdr, kinds, body = A["headers"], A["kinds"], A["rows"]
    dims = [i for i, k in enumerate(kinds) if k in ("text", "period")]; meas = [i for i, k in enumerate(kinds) if k == "num"]
    ti = next((i for i in dims if kinds[i] == "period"), None)
    if ti is None: return None
    gi = next(i for i in dims if i != ti)
    periods = list(dict.fromkeys(str(r[ti]) for r in body)); groups = list(dict.fromkeys(str(r[gi]) for r in body))
    if len(periods) < 3 or not 2 <= len(groups) <= 8: return None
    val = {(str(r[gi]), str(r[ti]), m): pnum(r[m]) for r in body for m in meas}
    rows_ = [dict(label=hdr[m], chart=dict(kind="lines", decimals=0 if all((val.get((g, t, m)) or 0) >= 100 for g in groups for t in periods) else 1)) for m in meas]
    cells = [[dict(categories=periods, series=[dict(name=hdr[m], values=[val.get((g, t, m)) for t in periods])]) for g in groups] for m in meas]
    spec = dict(type="facet", title=f"{' / '.join(hdr[m] for m in meas)} by {hdr[gi]}", cols=groups, rows=rows_, cells=cells, shared_y="row")
    recs = [dict(type="facet", score=95, why=f"有 {len(meas)} 个指标 × {len(groups)} 个{hdr[gi]} × {len(periods)} 个时间点：一张图放不下，按“行=指标、列={hdr[gi]}”分面，同行共用纵轴便于横向比较", emphasis="同行共用纵轴；用 segments 标注分段、annotations 圈出异常", marks="小图标题、行表头、虚线分隔"),
            dict(type="dashboard", score=80, why="若各指标想用不同图型（如构成用堆积面积、单价用折线），用自由拼版 dashboard 手动划分区域", emphasis="每个子图一个红色下划线小标题", marks="统一页脚来源"),
            dict(type="line", score=60, why=f"只看一个指标时，用多折线（每个{hdr[gi]}一条）", emphasis="", marks="")]
    return recs, spec
def advise(rows, intent=""):
    A = analyse(rows)
    mp = multi_panel(A)
    if mp:
        import tc_validate
        recs, spec = mp; ins = [f"数据含 {A['n_measures']} 个指标、多个分组和时间维度，建议多图拼版"]
        for c in recs: c["title"] = spec["title"]
        return dict(features=dict({k: A.get(k) for k in ("layout", "n_rows", "n_dims", "n_measures", "dims", "measures", "n_cats", "n_series", "time", "has_neg", "mixed_sign", "bridge",
                                  "bridge_balanced", "subtotal_idx", "sums_100", "single_sum_100", "two_points", "extreme_ratio", "max_label_len", "has_missing", "unit", "roles", "dim2", "stage_like")}, layout="长表多指标 × 分组 × 时间（建议分面）", target=False, range=False, width=False, schedule=False), intents=parse_intent(intent), intent_text=intent,
                    conclusions=ins, conclusion_source="从数据推断", recommendations=[dict(rank=i + 1, **c) for i, c in enumerate(recs)], spec=spec, spec_validation=tc_validate.validate(spec))
    intents = parse_intent(intent); ins, zh = insights(A)
    C = sorted(candidates(A, intents).values(), key=lambda c: -c["score"])
    top = []
    for c in C:
        if c["type"] in [x["type"] for x in top]: continue
        top.append(c)
        if len(top) == 3: break
    if not top: top = [dict(type="table_harvey", score=0, why="没识别出可画的数值结构，建议先整理成“类别 + 数值”两列", emphasis="", marks="")]
    concl = ins[0] if ins else ""
    if intent: concl_src = "用户给定的意图"
    else: concl_src = "从数据推断"
    for c in top:
        c["title"] = title_for(c["type"], A, ins, intent, zh)
    spec = None; vr = None
    for c in top:
        spec = build(c["type"], A, c["title"])
        if spec:
            if c is not top[0]: top.remove(c); top.insert(0, c)
            break
    if spec:
        import tc_validate
        vr = tc_validate.validate(spec)
    feat = {k: A.get(k) for k in ("layout", "n_rows", "n_dims", "n_measures", "dims", "measures", "n_cats", "n_series", "time", "has_neg", "mixed_sign", "bridge",
                                  "bridge_balanced", "subtotal_idx", "sums_100", "single_sum_100", "two_points", "extreme_ratio", "max_label_len", "has_missing", "unit", "roles", "dim2", "stage_like")}
    feat["target"] = "target" in A; feat["range"] = "low" in A and "high" in A; feat["width"] = "width" in A; feat["schedule"] = A.get("shape") == "schedule"
    return dict(features=feat, intents=intents, intent_text=intent, conclusions=ins, conclusion_source=concl_src,
                recommendations=[dict(rank=i + 1, **c) for i, c in enumerate(top)], spec=spec, spec_validation=vr)

def title_for(t, A, ins, intent, zh):
    if ins:
        if t in ("pie", "doughnut", "waffle", "bar_sorted", "pareto") and len(ins) > 1 and "前 3" in ins[1]: return ins[0]
        if t in ("stacked", "percent", "area_percent", "small_multiples") and len(ins) > 1: return ins[1] if t != "stacked" else ins[0]
        return ins[0]
    return intent or ("请填写结论式标题" if zh else "TODO: action title")

def fmt_report(R):
    F = R["features"]; L = ["【数据分析与图表推荐】", "", "一、数据长什么样"]
    if F["schedule"]: L.append(f"  - 这是一份计划表：{F['n_rows']} 行任务，每行有开始和结束日期。")
    else:
        L.append(f"  - 表格结构：{F['layout']}；{F['n_cats']} 个类别 × {F['n_series']} 个数值系列（维度列 {F['n_dims']} 个：{', '.join(F['dims']) or '无'}；度量列 {F['n_measures']} 个）。")
        L.append(f"  - 类别{'是时间序列' if F['time'] else '不是时间'}；最长类别名 {F['max_label_len']} 个字符{'（偏长，横向条形更好放）' if F['max_label_len'] > 10 else ''}。")
        tags = []
        if F["bridge"]: tags.append("首项+中间增量" + ("=末项（起止桥成立）" if F["bridge_balanced"] else "≈末项（按关键词判断为起止桥，但没对平，见校验）"))
        if F["subtotal_idx"]: tags.append(f"含 {len(F['subtotal_idx'])} 个小计行")
        if F["mixed_sign"] and not F["bridge"]: tags.append("有正有负")
        if F["sums_100"]: tags.append("每个类别的各部分加起来 = 100%（构成关系）")
        if F["single_sum_100"]: tags.append("各项加起来 = 100%（整体构成）")
        if F["two_points"]: tags.append("两个时点/前后对比")
        if F["target"]: tags.append("有目标值列")
        if F["range"]: tags.append("有下限/上限（区间）")
        if F["width"]: tags.append("有规模/宽度列")
        if F["dim2"]: tags.append(f"两层分类（第二层：{F['dim2']}）")
        if F["extreme_ratio"] >= 3: tags.append(f"最大值是第二大的 {F['extreme_ratio']} 倍（需要轴破断）")
        if F["stage_like"]: tags.append("类别像转化阶段")
        if F["has_missing"]: tags.append("有空值（草稿里暂填 0，请补真实数）")
        L.append("  - 识别到的特征：" + ("；".join(tags) if tags else "普通的类别+数值"))
        if F["unit"]: L.append(f"  - 单位：{F['unit']}")
    L += ["", "二、可能想表达的结论（" + R["conclusion_source"] + "）"]
    if R["intent_text"]: L.append(f"  - 你的意图：{R['intent_text']}（识别为：{', '.join(R['intents']) or '未匹配到关键词'}）")
    for c in R["conclusions"] or ["（没算出明显结论，请告诉我想说明什么）"]: L.append(f"  - {c}")
    L += ["", "三、推荐图表"]
    for r in R["recommendations"]:
        tag = "首选" if r["rank"] == 1 else "备选"
        L.append(f"  {r['rank']}. 【{tag}】{r['type']}  —— {r['why']}")
        L.append(f"     建议标题：{r['title']}")
        if r["emphasis"]: L.append(f"     建议强调：{r['emphasis']}")
        if r["marks"]: L.append(f"     建议标记：{r['marks']}")
    L += ["", "四、首选图的 spec 草稿"]
    if R["spec"]:
        v = R["spec_validation"]
        L.append(f"  - 已生成（用 -o 保存）；数据校验结论：{v['status']}。")
        for i in v["issues"]: L.append(f"    · {i['msg']}" + (f" → {i['fix']}" if i.get('fix') else ""))
        L.append("  - 还需要你补：source（数据来源）；标题里的结论请确认是否准确。")
    else: L.append("  - 首选图暂不能自动生成草稿，请按 docs/CATALOG.md 手写。")
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser(description="数据分析 + 图表推荐")
    ap.add_argument("data"); ap.add_argument("--intent", default="", help="想表达的结论（可选）")
    ap.add_argument("-o", "--out", help="把首选图的 spec 草稿写到这个文件"); ap.add_argument("--json", help="把完整结果 JSON 写到这个文件；- 表示打印")
    a = ap.parse_args()
    rows = read_table(a.data)
    if not rows or len(rows) < 2: sys.exit("没有读到数据：至少要有表头 + 1 行。")
    R = advise(rows, a.intent)
    print(fmt_report(R))
    if a.out and R["spec"]:
        json.dump(R["spec"], open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2); print(f"\nspec 草稿已保存：{a.out}")
    if a.json:
        s = json.dumps(R, ensure_ascii=False, indent=2, default=str)
        print("\n" + s) if a.json == "-" else open(a.json, "w", encoding="utf-8").write(s)

if __name__ == "__main__": main()
