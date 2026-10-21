#!/usr/bin/env python3
"""数据充分性校验：用户点名某种图表时，检查数据能不能支撑这张图。
用法：
  python tc_validate.py spec.json [--json]        # 校验一份（或多份）spec
  在代码里：from tc_validate import validate; r = validate(spec)
结论三档：能做 / 能做但有问题 / 不能做。tc_render.py 渲染前会自动调用，"不能做" 时拒绝渲染（--force 可强制）。"""
import sys, json, re, datetime

OK, WARN, FAIL = "能做", "能做但有问题", "不能做"
LIMITS = dict(column=12, stacked=10, percent=10, clustered=8, line=24, area=24, bar=15, pie=6, doughnut=6, series=6, kpi=6, funnel=7)

def _num(x): return isinstance(x, (int, float)) and not isinstance(x, bool)
def _date(x):
    if not isinstance(x, str): return False
    try: datetime.date.fromisoformat(x); return True
    except ValueError: return False

class V:
    def __init__(self, spec):
        self.spec = spec; self.t = spec.get("type"); self.d = spec.get("data") if isinstance(spec.get("data"), dict) else {}
        self.issues = []; self.alts = []; self.compromise = []
    # ---- 记录问题 ----
    def fatal(self, msg, fix=None, ex=None): self.issues.append(dict(level="fatal", msg=msg, fix=fix, example=ex))
    def warn(self, msg, fix=None, ex=None): self.issues.append(dict(level="warn", msg=msg, fix=fix, example=ex))
    def alt(self, t, why):
        if t != self.t and all(a["type"] != t for a in self.alts): self.alts.append(dict(type=t, why=why))
    # ---- 基础检查 ----
    def need(self, key, kind, ex, where=None, label=None):
        d = self.d if where is None else where; v = d.get(key) if isinstance(d, dict) else None; nm = label or f"data.{key}"
        if v is None:
            self.fatal(f"缺少字段 {nm}。", f"请补上 {nm}。", ex); return None
        ok = {"list": isinstance(v, list), "str": isinstance(v, str), "num": _num(v), "dict": isinstance(v, dict),
              "date": _date(v), "int": isinstance(v, int) and not isinstance(v, bool)}[kind]
        if not ok:
            self.fatal(f"{nm} 的类型不对：应该是{dict(list='列表', str='文字', num='数字', dict='对象', date='日期（YYYY-MM-DD）', int='整数')[kind]}，现在是 {json.dumps(v, ensure_ascii=False)[:40]}。",
                       f"把 {nm} 改成正确类型。", ex); return None
        if kind == "list" and not v:
            self.fatal(f"{nm} 是空的。", f"至少填 1 项。", ex); return None
        return v
    def nums(self, vals, nm, n=None, nonneg=False, allow_none=False):
        if not isinstance(vals, list): self.fatal(f"{nm} 应该是数字列表。", ex=f'"{nm.split(".")[-1]}": [10, 20, 30]'); return False
        bad = [x for x in vals if not (_num(x) or (allow_none and x is None))]
        if bad:
            self.fatal(f"{nm} 里有非数字：{json.dumps(bad[:3], ensure_ascii=False)}。", "去掉单位、百分号、千分位逗号，只留数字（例如 \"12%\" 写成 12）。"); return False
        if n is not None and len(vals) != n:
            self.fatal(f"{nm} 有 {len(vals)} 个数，但类别有 {n} 个，长度对不上。", f"让 {nm} 刚好 {n} 个数，每个类别一个；缺的值请补上真实数字（不要编）。"); return False
        if nonneg and any(_num(x) and x < 0 for x in vals):
            self.fatal(f"{nm} 里有负数，这种图画不了负值。", "负值请改用瀑布图或正负条形图（bar_diverging）。"); self.alt("bar_diverging", "数据里有负值"); return False
        return True
    def cats(self, key="categories", cap=None, long_hint=True):
        c = self.need(key, "list", f'"{key}": ["2021", "2022", "2023"]')
        if c is None: return None
        c = [str(x) for x in c]
        if len(set(c)) < len(c): self.warn(f"{key} 里有重复的名字：{sorted({x for x in c if c.count(x) > 1})}。", "重复的类别会让标签和高亮指错位置，建议改成唯一名字。")
        if cap and len(c) > cap:
            self.warn(f"类别有 {len(c)} 个，超过这种图的可读上限（约 {cap} 个），标签会挤在一起。",
                      f"建议只保留最重要的 {cap-1} 个，其余合并成“Other”；或换成条形图。")
            self.alt("bar_sorted", "类别太多，横向条形更好读"); self.compromise.append("把尾部类别合并为 Other 再画")
        if long_hint and self.t in ("column", "stacked", "percent", "clustered", "column_target", "column_error") and max(len(x) for x in c) > 12 and len(c) > 5:
            self.warn(f"类别名比较长（最长 {max(len(x) for x in c)} 个字符），竖柱下面放不下会换行。", "缩写类别名，或换成横向条形图。"); self.alt("bar", "类别名长，条形图左侧能放下完整名字")
        return c
    def series(self, n, key="series", lo=1, hi=None, nonneg=False, ex=None):
        s = self.need(key, "list", ex or f'"{key}": [{{"name": "Sales", "values": [10, 12, 15]}}]')
        if s is None: return None
        for i, x in enumerate(s):
            if not isinstance(x, dict) or "values" not in x:
                self.fatal(f"{key}[{i}] 缺少 values。", ex='{"name": "Seg A", "values": [1, 2, 3]}'); return None
            if not x.get("name"): self.warn(f"{key}[{i}] 没有 name，图例会显示空白。", '给每个系列加 "name"。')
            self.nums(x["values"], f"{key}[{i}].values", n, nonneg)
        if len(s) < lo: self.fatal(f"这种图至少要 {lo} 个系列，现在只有 {len(s)} 个。", f"再补 {lo-len(s)} 个系列。", ex)
        if hi and len(s) > hi: self.warn(f"系列有 {len(s)} 个，超过 {hi} 个后颜色难以区分。", f"把小系列合并成“Other”，控制在 {hi} 个以内。")
        return s
    def items(self, key, fields, lo=1, hi=None, ex=None):
        it = self.need(key, "list", ex)
        if it is None: return None
        for i, x in enumerate(it):
            if not isinstance(x, dict): self.fatal(f"{key}[{i}] 应该是对象。", ex=ex); return None
            for f, kind in fields.items():
                opt = f.endswith("?"); f = f.rstrip("?")
                if f not in x:
                    if not opt: self.fatal(f"{key}[{i}] 缺少 {f}。", f"每一项都要有 {f}。", ex)
                    continue
                v = x[f]
                if kind == "num" and not _num(v): self.fatal(f"{key}[{i}].{f} 应该是数字，现在是 {json.dumps(v, ensure_ascii=False)}。", "只留数字。")
                if kind == "date" and not _date(v): self.fatal(f"{key}[{i}].{f} 应该是日期 YYYY-MM-DD，现在是 {json.dumps(v, ensure_ascii=False)}。", '例如 "2026-05-04"。')
        if len(it) < lo: self.fatal(f"{key} 至少要 {lo} 项，现在只有 {len(it)} 项。", ex=ex)
        if hi and len(it) > hi: self.warn(f"{key} 有 {len(it)} 项，超过可读上限（约 {hi} 项）。", "合并或删减次要项。")
        return it
    def pct_sum(self, cols, what="每一列"):
        sums = [round(sum(v for v in c if _num(v)), 2) for c in cols]
        near = [s for s in sums if 90 <= s <= 110]
        if near and len(near) == len(sums) and any(abs(s-100) > 0.5 for s in sums):
            bad = [s for s in sums if abs(s-100) > 0.5]
            self.warn(f"看起来是百分比数据，但{what}加起来不是 100（例如 {bad[:3]}）。图会按比例拉伸到 100%，标签显示的百分比会和原始数字对不上。",
                      "检查是否漏了一项（如“其他”），或把差额补成“Other”；如果是四舍五入造成的 ±1，可以忽略。")
            self.compromise.append("自动按比例归一到 100%（标签会是归一后的值）")
    def axis_break_hint(self, vals):
        v = sorted([x for x in vals if _num(x) and x > 0], reverse=True)
        if len(v) >= 3 and v[1] > 0 and v[0]/v[1] >= 3 and not self.d.get("axis_break"):
            self.warn(f"最大值 {v[0]:g} 是第二大值 {v[1]:g} 的 {v[0]/v[1]:.1f} 倍，其他柱子会被压得很矮。",
                      f'加数值轴破断：在 data 里写 "axis_break": {{"from": {v[1]*1.3:.0f}, "to": {v[0]*0.85:.0f}}}。', '"axis_break": {"from": 40, "to": 350}')

    # ---- 各类图 ----
    def run(self):
        t, d = self.t, self.d
        import tc_more; from tc_core import RENDER
        if t not in RENDER:
            self.fatal(f"不认识的图表类型 \"{t}\"。", "从 docs/CATALOG.md 的 55 种里选一个 type。"); return
        if t in ("dashboard", "facet"):
            if not self.spec.get("source"): self.warn("没有填 source（数据来源），页脚会显示红字提醒。", '加 "source": "..."。')
            if not self.spec.get("title"): self.warn("拼版页没有总标题。", "加一句总标题，可配 title_tag 标签块。")
            return getattr(self, "c_" + t)()
        if "data" not in self.spec or not isinstance(self.spec.get("data"), dict):
            self.fatal("缺少 data 对象。", "参考 examples/<type>.json 的 data 写法。"); return
        if not self.spec.get("source"): self.warn("没有填 source（数据来源），图上会显示红字提醒。", '加 "source": "公司年报 2025"。')
        if not self.spec.get("title"): self.warn("没有标题。", "加一句结论式标题，例如“收入五年增长 67%”。")
        fam = getattr(self, "c_" + t, None)
        fam() if fam else self.generic()

    def _catser(self, cap, lo=1, hi=None, nonneg=False, pct=False):
        c = self.cats(cap=cap)
        if c is None: return None, None
        s = self.series(len(c), lo=lo, hi=hi, nonneg=nonneg)
        if s and pct: self.pct_sum([list(col) for col in zip(*[x["values"] for x in s])])
        return c, s
    def c_column(self):
        c, s = self._catser(LIMITS["column"], hi=None)
        if s:
            if len(s) > 1: self.warn(f"column 只画第 1 个系列，你给了 {len(s)} 个。", "多系列请用 stacked（叠加）或 clustered（并排）。"); self.alt("stacked", "多个系列可加总"); self.alt("clustered", "多个系列并排对比")
            self.axis_break_hint(s[0]["values"])
            if any(x < 0 for x in s[0]["values"] if _num(x)): self.alt("bar_diverging", "有负值，正负条形更直观")
    def c_stacked(self):
        c, s = self._catser(LIMITS["stacked"], lo=1, hi=LIMITS["series"])
        if s:
            if len(s) == 1: self.warn("只有 1 个系列，堆叠没有意义。", "用 column。"); self.alt("column", "单系列")
            if any(v < 0 for x in s for v in x["values"] if _num(v)): self.warn("堆叠柱里有负值，正负段会叠在一起很难读。", "负值项单独拿出来，或改用瀑布图。"); self.alt("waterfall", "有正负变化")
    def c_percent(self):
        c, s = self._catser(LIMITS["percent"], lo=2, hi=LIMITS["series"], nonneg=True, pct=True)
    def c_clustered(self):
        c, s = self._catser(LIMITS["clustered"], lo=2, hi=4)
        if s and len(c) * len(s) > 24: self.warn(f"{len(c)} 个类别 × {len(s)} 个系列 = {len(c)*len(s)} 根柱，太密。", "减少系列，或改用 small_multiples。"); self.alt("small_multiples", "每个系列一个小图")
    def c_line(self):
        c, s = self._catser(LIMITS["line"], hi=LIMITS["series"])
        if c and len(c) < 3: self.warn("折线只有 2 个点，看不出趋势。", "2 个时点对比建议用 slope 或 bar_yoy。"); self.alt("slope", "只有两个时点")
    def c_line_target(self):
        self.c_line()
        if self.d.get("target") is None: self.fatal("缺少目标值 data.target。", "补上目标值数字。", '"target": 2.0, "target_label": "Target 2.0%"')
        elif not _num(self.d["target"]): self.fatal("data.target 应该是数字。")
        b = self.d.get("band")
        if b is not None and not (isinstance(b, list) and len(b) == 2 and all(_num(x) for x in b) and b[0] < b[1]): self.fatal("data.band 应该是 [下限, 上限] 两个数，且下限 < 上限。", ex='"band": [1.5, 2.5]')
    def c_area(self): self._catser(LIMITS["area"], hi=LIMITS["series"], nonneg=True)
    def c_area_percent(self): self._catser(LIMITS["area"], lo=2, hi=LIMITS["series"], nonneg=True, pct=True)
    def c_bar(self):
        c, s = self._catser(LIMITS["bar"])
        if s and len(s) > 1: self.warn("bar 只画第 1 个系列。", "多系列用 bar_stacked 或 bar_yoy。"); self.alt("bar_stacked", "多系列")
    def c_bar_sorted(self):
        self.c_bar(); hl = self.d.get("highlight") or []; c = [str(x) for x in self.d.get("categories") or []]
        for h in hl:
            if str(h) not in c: self.warn(f"highlight 里的 “{h}” 不在 categories 里，高亮不会生效。", "highlight 写类别原名。")
    def c_bar_stacked(self): self._catser(LIMITS["bar"], lo=2, hi=LIMITS["series"], nonneg=True)
    def c_bar_percent(self): self._catser(LIMITS["bar"], lo=2, hi=LIMITS["series"], nonneg=True, pct=True)
    def c_butterfly(self):
        c, s = self._catser(LIMITS["bar"], lo=2, nonneg=True)
        if s and len(s) != 2: self.fatal(f"蝴蝶图要刚好 2 个系列（左、右），现在有 {len(s)} 个。", "只保留要左右对比的两组。")
    def c_dumbbell(self):
        c, s = self._catser(LIMITS["bar"], lo=2)
        if s and len(s) != 2: self.fatal(f"哑铃图要刚好 2 个系列（前、后两个时点），现在有 {len(s)} 个。", "只保留两个时点。")
    def c_football(self):
        c, s = self._catser(LIMITS["bar"], lo=2)
        if s:
            if len(s) != 2: self.fatal("区间图要 2 个系列：第 1 个是下限 Low，第 2 个是上限 High。", ex='"series": [{"name":"Low","values":[18,20]}, {"name":"High","values":[27,26]}]'); return
            bad = [c[i] for i, (a, b) in enumerate(zip(s[0]["values"], s[1]["values"])) if _num(a) and _num(b) and a > b]
            if bad: self.fatal(f"这些类别的下限大于上限：{bad}。", "检查是不是两个系列写反了。")
    def c_bar_yoy(self):
        c = self.cats(cap=LIMITS["bar"])
        for k in ("previous", "current"):
            x = self.need(k, "dict", f'"{k}": {{"name": "2024", "values": [480, 350]}}')
            if x is not None and c: self.nums(x.get("values"), f"data.{k}.values", len(c))
    def c_bar_diverging(self):
        c = self.cats(cap=LIMITS["bar"]); v = self.need("values", "list", '"values": [4.2, 2.1, -1.5]')
        if c and v and self.nums(v, "data.values", len(c)):
            if all(x >= 0 for x in v) or all(x <= 0 for x in v): self.warn("所有值同号，正负条形没有发挥作用。", "用 bar_sorted。"); self.alt("bar_sorted", "数据没有正负之分")
    def c_column_error(self):
        c = self.cats(cap=LIMITS["column"]); v = self.need("values", "list", '"values": [100, 112]')
        if c and v: self.nums(v, "data.values", len(c), nonneg=True)
        if "errors" in self.d: self.nums(self.d["errors"], "data.errors", len(c) if c else None, nonneg=True)
        elif "low" in self.d and "high" in self.d: self.nums(self.d["low"], "data.low", len(c) if c else None); self.nums(self.d["high"], "data.high", len(c) if c else None)
        else: self.fatal("缺少误差：data.errors（± 误差），或 data.low + data.high。", ex='"errors": [3, 4, 5, 2]')
    def c_column_grouped(self):
        g = self.items("groups", {"name": "str", "categories": "list", "values": "list"}, lo=2, ex='"groups": [{"name":"2024","categories":["Q1","Q2"],"values":[22,25]}]')
        if g:
            for i, x in enumerate(g):
                if isinstance(x.get("categories"), list): self.nums(x.get("values"), f"groups[{i}].values", len(x["categories"]), nonneg=True)
            if sum(len(x.get("categories") or []) for x in g) > 16: self.warn("总柱数超过 16，太密。", "减少分组或类别。")
    def c_column_target(self):
        c = self.cats(cap=LIMITS["column"])
        for k in ("actual", "target"):
            v = self.need(k, "list", f'"{k}": [52, 38, 47]')
            if v and c: self.nums(v, f"data.{k}", len(c), nonneg=True)
    def c_column_xbreak(self):
        c = self.cats(cap=LIMITS["column"]); v = self.need("values", "list", '"values": [50, 78, 86]')
        if c and v: self.nums(v, "data.values", len(c), nonneg=True)
        b = self.need("break_after", "int", '"break_after": 0')
        if c and b is not None and not (0 <= b < len(c)-1): self.fatal(f"break_after={b} 超出范围，应在 0 到 {len(c)-2} 之间（在第几个类别后断开）。")
    def c_combo(self):
        c = self.cats(cap=LIMITS["column"])
        if c is None: return
        self.series(len(c), key="columns", nonneg=True, ex='"columns": [{"name":"Services","values":[20,24]}]')
        ln = self.need("line", "dict", '"line": {"name": "EBIT margin", "values": [8, 9.5], "suffix": "%"}')
        if ln: self.nums(ln.get("values"), "data.line.values", len(c))
    def c_stacked_clustered(self):
        c = self.cats(cap=6)
        g = self.items("groups", {"name": "str", "series": "list"}, lo=2, hi=3, ex='"groups": [{"name":"Plan","series":[{"name":"A","values":[1,2]}]}]')
        if c and g:
            names = None
            for i, x in enumerate(g):
                for j, s in enumerate(x.get("series") or []): self.nums(s.get("values"), f"groups[{i}].series[{j}].values", len(c), nonneg=True)
                nm = [s.get("name") for s in x.get("series") or []]
                if names is not None and nm != names: self.warn("各组的系列名或顺序不一致，颜色会对不上。", "让每组的 series 名字和顺序一致。")
                names = nm
    def _mekko(self, need_w):
        c = self.cats(cap=8)
        if c is None: return
        s = self.series(len(c), lo=1, hi=LIMITS["series"], nonneg=True)
        if need_w:
            if "widths" not in self.d:
                self.fatal("百分比 Mekko 缺少列宽 data.widths（每一列的市场规模/总量），没有它就不知道每列多宽。",
                           "补充每个类别的规模，例如市场规模（$B）。", '"widths": [50, 30, 20]')
                self.alt("mekko_unit", "如果手上是各段的绝对值，用单位 Mekko：列宽 = 各段之和，不需要另给宽度")
                self.alt("percent", "没有规模数据时，用 100% 堆叠柱（等宽）")
                self.compromise.append("不补宽度就退化成等宽的 100% 堆叠柱（percent）")
            else:
                if self.nums(self.d["widths"], "data.widths", len(c), nonneg=True) and any(w == 0 for w in self.d["widths"]): self.fatal("data.widths 里有 0，该列会消失。")
            if s: self.pct_sum([list(col) for col in zip(*[x["values"] for x in s])])
    def c_mekko_percent(self): self._mekko(True)
    def c_mekko_unit(self): self._mekko(False)
    def c_variwide(self):
        c = self.cats(cap=8)
        for k in ("widths", "values"):
            v = self.need(k, "list", f'"{k}": [40, 25, 15]')
            if v and c: self.nums(v, f"data.{k}", len(c), nonneg=True)
    def _wf(self, key="value"):
        it = self.items("items", {"label": "str"}, lo=3, ex='"items": [{"label":"2024","value":100,"kind":"start"}, {"label":"Price","value":15}, {"label":"2025","kind":"total"}]')
        if not it: return None
        kinds = [x.get("kind", "delta") for x in it]
        for i, (x, k) in enumerate(zip(it, kinds)):
            if k not in ("start", "delta", "subtotal", "total"): self.fatal(f"items[{i}].kind=\"{k}\" 不认识，只能是 start / delta / subtotal / total。")
            if k in ("start", "delta") and key not in x: self.fatal(f"items[{i}]（{x.get('label')}）缺少 {key}。", "起点和每个增量都要有数值。")
            if key in x:
                v = x[key]
                if (key == "value" and not _num(v)) or (key == "values" and not (isinstance(v, list) and all(_num(a) for a in v))): self.fatal(f"items[{i}].{key} 不是数字：{json.dumps(v, ensure_ascii=False)}。", "只留数字，负数写成 -12。")
        if kinds[0] != "start": self.warn("第一项不是起点（kind=\"start\"），整张桥会从 0 开始累计。", '把第一项标成 "kind": "start"。')
        if kinds[-1] not in ("total", "subtotal") and len(it) > 2: self.warn("最后一项不是终点（kind=\"total\"），读者看不到最终结果。", '加一项 {"label": "2025", "kind": "total"}，数值可以不填，自动算。')
        return it, kinds
    def _wf_balance(self, it, kinds, getv=lambda x: x.get("value")):
        run = 0; tol = lambda a: max(0.5, abs(a)*0.005)
        for x, k in zip(it, kinds):
            v = getv(x)
            if k == "start": run = v
            elif k == "delta": run += v
            elif v is not None and _num(v) and abs(v - run) > tol(run):
                self.fatal(f"瀑布不平：到“{x.get('label')}”为止，起点+增量累计 = {run:g}，但你写的{('小计' if k=='subtotal' else '终点')}是 {v:g}，差 {v-run:+g}。",
                           f"三选一：① 检查增量是否漏项或符号写反；② 加一个“Other / 其他”增量 {v-run:+g} 把桥补平；③ 删掉这一项的 value，让程序自动算（会显示 {run:g}）。",
                           f'{{"label": "Other", "value": {v-run:g}}}')
                self.compromise.append(f"加“Other”增量 {v-run:+g} 补平，或去掉终点数值让它自动等于 {run:g}")
                run = v
    def c_waterfall(self):
        r = self._wf()
        if r: self._wf_balance(*r)
    c_waterfall_h = c_waterfall; c_waterfall_percent = c_waterfall
    def c_waterfall_subtotal(self):
        r = self._wf()
        if r:
            self._wf_balance(*r)
            if "subtotal" not in r[1]: self.warn("没有任何小计（kind=\"subtotal\"），和普通瀑布图一样。", '在中间加 {"label":"Gross profit","kind":"subtotal"}。'); self.alt("waterfall", "没有小计")
    def c_waterfall_stacked(self):
        ser = self.need("series", "list", '"series": ["Product A", "Product B"]')
        r = self._wf("values")
        if not (ser and r): return
        it, kinds = r
        for i, x in enumerate(it):
            if isinstance(x.get("values"), list) and len(x["values"]) != len(ser): self.fatal(f"items[{i}].values 有 {len(x['values'])} 个数，但 series 有 {len(ser)} 个。", "每一项都给每个系列一个数。")
        if not any(i["level"] == "fatal" for i in self.issues):
            for j in range(len(ser)): self._wf_balance(it, kinds, getv=lambda x, j=j: x["values"][j] if isinstance(x.get("values"), list) else None)
    def _lv(self, key, cap, nonneg=True, pct=False, lbl="label"):
        it = self.items(key, {lbl: "str", "value": "num"}, lo=2, hi=cap, ex=f'"{key}": [{{"{lbl}": "Online", "value": 57}}, {{"{lbl}": "Retail", "value": 24}}]')
        if it and nonneg and any(_num(x.get("value")) and x["value"] < 0 for x in it): self.fatal(f"{key} 里有负数，这种图画不了。", "去掉负值项或改用条形图。")
        if it and pct: self.pct_sum([[x.get("value") for x in it]], "各项")
        return it
    def c_pie(self):
        it = self._lv("segments", None, pct=True)
        if it and len(it) > LIMITS["pie"]: self.warn(f"饼图有 {len(it)} 块，超过 {LIMITS['pie']} 块就很难读。", "合并小块为“Other”，或改用 bar_sorted。"); self.alt("bar_sorted", "块太多，条形更好比较"); self.compromise.append("把最小的几块合并为 Other")
    c_doughnut = c_pie
    def c_waffle(self):
        it = self._lv("items", 5, pct=True)
        if it:
            s = sum(x["value"] for x in it if _num(x.get("value")))
            if not 90 <= s <= 110: self.warn(f"华夫图表示 100 格，各项加和是 {s:g}，会按比例换算成格数。", "最好直接给百分比（加和 100）。")
    def c_proportional_area(self): self._lv("items", 6)
    def c_funnel(self):
        it = self._lv("stages", LIMITS["funnel"])
        if it:
            v = [x["value"] for x in it if _num(x.get("value"))]
            if any(b > a for a, b in zip(v, v[1:])): self.warn("漏斗中后一阶段比前一阶段大，不符合漏斗逐级减少的逻辑。", "检查阶段顺序；如果不是逐级转化，改用 bar。"); self.alt("bar", "数值不是逐级递减")
    def c_tam_sam_som(self):
        it = self._lv("levels", 3)
        if it:
            if len(it) != 3: self.warn(f"TAM/SAM/SOM 通常是 3 层，现在是 {len(it)} 层。")
            v = [x["value"] for x in it]
            if any(b > a for a, b in zip(v, v[1:])): self.fatal("TAM ≥ SAM ≥ SOM 不成立：内层比外层大。", "检查顺序：第 1 个是 TAM（最大），最后是 SOM（最小）。")
    def c_scatter(self, bubble=False):
        f = {"label": "str", "x": "num", "y": "num"}
        if bubble: f["size"] = "num"
        p = self.items("points", f, lo=3, hi=30, ex='"points": [{"label":"A","x":12,"y":60' + (',"size":10' if bubble else '') + '}]')
        if bubble and p and any(_num(x.get("size")) and x["size"] <= 0 for x in p): self.fatal("气泡大小 size 必须大于 0。")
        if not self.d.get("x_title") or not self.d.get("y_title"): self.warn("没有坐标轴名称 x_title / y_title，读者不知道横纵轴是什么。", '加 "x_title": "Price ($)", "y_title": "CSAT"。')
    def c_bubble(self): self.c_scatter(True)
    def c_matrix_2x2(self):
        q = self.need("quadrants", "list", '"quadrants": ["Partner", "Invest", "Deprioritise", "Harvest"]')
        if q and len(q) != 4: self.fatal(f"quadrants 要刚好 4 个名字，现在 {len(q)} 个。")
        p = self.items("points", {"label": "str", "x": "num", "y": "num"}, lo=1, hi=15, ex='"points": [{"label":"Cloud","x":0.8,"y":0.8,"size":3}]')
        xr, yr = self.d.get("x_range", [0, 1]), self.d.get("y_range", [0, 1])
        if p:
            out = [x["label"] for x in p if _num(x.get("x")) and _num(x.get("y")) and not (xr[0] <= x["x"] <= xr[1] and yr[0] <= x["y"] <= yr[1])]
            if out: self.fatal(f"这些点超出坐标范围 x {xr} / y {yr}：{out}。", '把 x、y 换算成 0–1 的得分，或在 data 里写 "x_range": [最小, 最大], "y_range": [...]。')
    def c_heatmap(self):
        r = self.need("rows", "list", '"rows": ["Software", "Services"]'); c = self.need("cols", "list", '"cols": ["North", "South"]'); v = self.need("values", "list", '"values": [[32, 28], [22, 18]]')
        if r and c and v:
            if len(v) != len(r): self.fatal(f"values 有 {len(v)} 行，rows 有 {len(r)} 个名字。", "每个行名对应一行数字。"); return
            for i, row in enumerate(v): self.nums(row, f"data.values[{i}]", len(c))
            if len(r) > 12 or len(c) > 10: self.warn("热力图格子太多，数字会太小。", "控制在 12 行 × 10 列以内。")
    def c_pareto(self):
        c = self.cats(cap=12); v = self.need("values", "list", '"values": [120, 85, 60]')
        if c and v: self.nums(v, "data.values", len(c), nonneg=True)
        if c and len(c) < 4: self.warn("帕累托图类别少于 4 个，看不出“少数原因占大头”。", "用 bar_sorted。"); self.alt("bar_sorted", "类别少")
    def c_tornado(self):
        self.need("base", "num", '"base": 120')
        it = self.items("items", {"label": "str", "low": "num", "high": "num"}, lo=2, hi=10, ex='"items": [{"label":"Price ±10%","low":78,"high":162}]')
        b = self.d.get("base")
        if it and _num(b):
            out = [x["label"] for x in it if _num(x.get("low")) and _num(x.get("high")) and not (min(x["low"], x["high"]) <= b <= max(x["low"], x["high"]))]
            if out: self.warn(f"这些项的区间没有包含基准值 {b:g}：{out}，条会整段落在一侧。", "确认 low/high 是“该因素变化后的结果值”，而不是变化量。")
    def c_tree(self):
        r = self.need("root", "dict", '"root": {"label":"ROCE","value":"14%","children":[{"label":"EBIT margin","value":"9%"}]}')
        def walk(n, depth, path):
            if not isinstance(n, dict) or not n.get("label"): self.fatal(f"树节点 {path} 缺少 label。"); return 0
            ch = n.get("children") or []
            if depth > 3: self.warn("驱动树超过 4 层，一页放不下。", "只展开关键分支。")
            return 1 + sum(walk(c, depth+1, f"{path}>{c.get('label') if isinstance(c, dict) else '?'}") for c in ch)
        if r:
            n = walk(r, 0, r.get("label", "root"))
            if not r.get("children"): self.fatal("根节点没有 children，画不成树。", ex='"children": [{"label":"EBIT margin","value":"9%"}]')
            if n > 15: self.warn(f"节点有 {n} 个，太多。", "控制在 15 个以内。")
    def c_kpi_cards(self):
        cs = self.items("cards", {"label": "str", "value": "str"}, lo=1, hi=LIMITS["kpi"], ex='"cards": [{"label":"Revenue","value":"$125M","delta":"+14.7% YoY","spark":[75,84,96]}]')
        for i, c in enumerate(cs or []):
            if "spark" in c: self.nums(c["spark"], f"cards[{i}].spark")
    def c_bullet(self):
        it = self.items("items", {"label": "str", "value": "num", "target": "num", "ranges": "list"}, lo=1, hi=6, ex='"items": [{"label":"Revenue","value":125,"target":118,"ranges":[90,110,140]}]')
        for i, x in enumerate(it or []):
            r = x.get("ranges")
            if isinstance(r, list) and (not all(_num(a) for a in r) or r != sorted(r)): self.fatal(f"items[{i}].ranges 应该是从小到大的数字（差/中/好的分界）。", ex='"ranges": [90, 110, 140]')
    def c_progress_bars(self):
        it = self.items("items", {"label": "str", "value": "num", "target": "num"}, lo=1, hi=8, ex='"items": [{"label":"Procurement","value":4.1,"target":12}]')
        for i, x in enumerate(it or []):
            if _num(x.get("target")) and x["target"] <= 0: self.fatal(f"items[{i}].target 必须大于 0（要算完成率）。")
    def c_radar(self):
        a = self.need("axes", "list", '"axes": ["Product", "Price", "Service"]')
        if a:
            if len(a) < 3: self.fatal("雷达图至少要 3 个维度。", "维度少时用 clustered 或 dumbbell。"); self.alt("clustered", "维度少")
            self.series(len(a), lo=1, hi=3, nonneg=True)
    def c_slope(self):
        for k in ("left_label", "right_label"): self.need(k, "str", f'"{k}": "2020"')
        self.items("items", {"label": "str", "a": "num", "b": "num"}, lo=2, hi=10, ex='"items": [{"label":"Stores","a":52,"b":31}]')
    def c_small_multiples(self):
        c = self.cats(cap=12)
        p = self.items("panels", {"title": "str", "values": "list"}, lo=2, hi=9, ex='"panels": [{"title":"Asia","values":[20,26,33]}]')
        for i, x in enumerate(p or []):
            if c: self.nums(x.get("values"), f"panels[{i}].values", len(c), nonneg=True)
    def _gantt(self, prog=False, swim=False):
        s = self.need("start", "date", '"start": "2026-05-04"'); e = self.need("end", "date", '"end": "2026-08-01"')
        if s and e and s >= e: self.fatal(f"整体开始日期 {s} 不早于结束日期 {e}。")
        t = self.items("tasks", {"name": "str"}, lo=1, hi=15, ex='"tasks": [{"name":"Send teaser","start":"2026-05-04","end":"2026-05-15"}]')
        miss = []
        for i, x in enumerate(t or []):
            if x.get("header"): continue
            if "milestone" in x:
                if not _date(x["milestone"]): self.fatal(f"tasks[{i}].milestone 应该是日期 YYYY-MM-DD。")
                continue
            if "start" not in x or "end" not in x: miss.append(x.get("name", f"#{i}")); continue
            if not (_date(x["start"]) and _date(x["end"])): self.fatal(f"任务“{x.get('name')}”的日期格式不对：{x.get('start')} ~ {x.get('end')}。", '日期写成 "YYYY-MM-DD"，例如 "2026-05-04"。'); continue
            if x["start"] > x["end"]: self.fatal(f"任务“{x.get('name')}”开始 {x['start']} 晚于结束 {x['end']}。")
            if s and e and _date(s) and _date(e) and (x["start"] < s or x["end"] > e): self.warn(f"任务“{x.get('name')}”超出了整体时间范围 {s} ~ {e}，超出部分会画到图外。", "把 data.start / data.end 放宽。")
            if prog and not (_num(x.get("progress")) and 0 <= x["progress"] <= 1): self.fatal(f"任务“{x.get('name')}”缺少完成度 progress（0–1 之间的小数）。", ex='"progress": 0.35')
        if miss:
            self.fatal(f"这些任务没有开始/结束日期：{miss}。甘特图必须知道每个任务从哪天到哪天。",
                       "给每个任务补 start 和 end；只有一个时间点的事件写成里程碑 milestone。",
                       '{"name": "Due diligence", "start": "2026-07-01", "end": "2026-07-24"}  或  {"name": "Signing", "milestone": "2026-07-31"}')
            self.alt("timeline", "如果只有阶段名和大致月份，可以用时间轴 timeline（也要日期，但更粗）")
            self.alt("table_harvey", "完全没有日期时，只能先做任务清单表")
            self.compromise.append("先把缺日期的任务删掉或写成 milestone，其余照常画")
    def c_gantt(self): self._gantt()
    def c_gantt_progress(self): self._gantt(prog=True)
    def c_gantt_swimlane(self): self._gantt(swim=True)
    def c_timeline(self):
        self.need("start", "date", '"start": "2026-01-01"'); self.need("end", "date", '"end": "2027-12-31"')
        self.items("phases", {"name": "str", "start": "date", "end": "date"}, lo=1, hi=6, ex='"phases": [{"name":"Diagnose","start":"2026-01-01","end":"2026-04-30"}]')
        if "milestones" in self.d: self.items("milestones", {"date": "date", "label": "str"}, lo=0, hi=8)
    def c_table_harvey(self):
        c = self.need("columns", "list", '"columns": ["Vendor A", "Vendor B"]')
        r = self.items("rows", {"name": "str", "values": "list"}, lo=1, hi=10, ex='"rows": [{"name":"Coverage","values":[{"harvey":3},{"harvey":4}]}]')
        for i, x in enumerate(r or []):
            if c and isinstance(x.get("values"), list) and len(x["values"]) != len(c): self.fatal(f"第 {i+1} 行“{x.get('name')}”有 {len(x['values'])} 格，但有 {len(c)} 列。")
            for v in x.get("values") or []:
                if isinstance(v, dict) and "harvey" in v and not (_num(v["harvey"]) and 0 <= v["harvey"] <= 4): self.fatal(f"哈维球取值要在 0–4 之间（0=空，4=满），“{x.get('name')}”里有 {v['harvey']}。")
    def generic(self): pass
    # ---- 多图拼版 ----
    def _mini(self, kind, d, where):
        KINDS = ("area_stack", "lines", "column_stack", "bars_pair")
        if kind not in KINDS: self.fatal(f"{where} 的 chart.kind=\"{kind}\" 不认识，只能是 {' / '.join(KINDS)}。"); return 0
        if not isinstance(d, dict): self.fatal(f"{where} 缺少 data。", ex='"data": {"categories": ["Q1","Q2"], "series": [{"name":"Team A","values":[1,2]}]}'); return 0
        if kind == "bars_pair":
            rows = d["rows"] if "rows" in d else [d]
            for r in rows:
                if r is None: continue
                if not any(k in r for k in ("value", "compare")): self.fatal(f"{where} 成对条形缺少 value / compare。", ex='{"value": 54.1, "compare": 56.1}')
                for k in ("value", "compare"):
                    if k in r and r[k] is not None and not _num(r[k]): self.fatal(f"{where}.{k} 应该是数字（百分比写成 54.1，不要带 %）。")
            return 1
        c = d.get("categories"); S = d.get("series")
        if not isinstance(c, list) or not c: self.fatal(f"{where} 缺少 categories（横轴）。", ex='"categories": ["25-Q1", "25-Q2"]'); return 0
        if not isinstance(S, list) or not S: self.fatal(f"{where} 缺少 series。", ex='"series": [{"name":"Team A","values":[1,2]}]'); return 0
        for k, s in enumerate(S):
            if not isinstance(s, dict) or "values" not in s: self.fatal(f"{where}.series[{k}] 缺少 values。"); continue
            self.nums(s["values"], f"{where}.series[{k}].values", len(c), nonneg=kind != "lines", allow_none=kind == "lines")
            if kind == "column_stack" and s.get("point_colors") is not None and len(s["point_colors"]) != len(c): self.fatal(f"{where}.series[{k}].point_colors 长度要等于类别数 {len(c)}。")
        if len(c) > 24: self.warn(f"{where} 横轴有 {len(c)} 个点，拼版里会很挤。", "用 x_label_every 隔点显示标签，或缩短区间。")
        if kind != "lines" and len(S) > 6: self.warn(f"{where} 有 {len(S)} 个堆叠系列，小图里难以区分。", "合并为 Others。")
        return len(c)
    def _deco(self, ch, n, where, names):
        segs = ch.get("segments", [])
        for s in segs:
            if not (isinstance(s, dict) and isinstance(s.get("from"), int) and isinstance(s.get("to"), int) and 0 <= s["from"] <= s["to"] < max(n, 1)):
                self.fatal(f"{where} 的分段 segments 写错：{json.dumps(s, ensure_ascii=False)}；from/to 是类别序号（0 开始），不能超过 {n-1}。", ex='{"from": 0, "to": 2, "label": "By Q"}')
        for a in ch.get("annotations", []):
            t = a.get("type")
            if t not in ("circle", "arrow", "note", "channel", "text"): self.fatal(f"{where} 有不认识的标注类型 {t}（可用 circle / arrow / note / channel / text）。"); continue
            if a.get("series") is not None and a["series"] not in names: self.fatal(f"{where} 的标注引用了不存在的系列“{a['series']}”。", f"系列名要和 series.name 一字不差：{names}")
            pts = a.get("points", []) + ([a["point"]] if "point" in a else [])
            if any(not isinstance(i, int) or not 0 <= i < n for i in pts): self.fatal(f"{where} 的标注点序号超出范围 0–{n-1}：{pts}。")
            if t == "arrow" and not (isinstance(a.get("from"), list) and isinstance(a.get("to"), list)): self.fatal(f"{where} 的箭头需要 from/to（面板内 0–1 比例坐标）。", ex='{"type":"arrow","from":[0.6,0.1],"to":[0.7,0.3]}')
            if t == "note" and "point" not in a and "at" not in a: self.fatal(f"{where} 的批注需要 point（挂在某个数据点）或 at（比例坐标）。")
            if t == "channel" and a.get("series") is None: self.fatal(f"{where} 的趋势通道需要指定 series。")
    def c_dashboard(self):
        P = self.spec.get("panels")
        if not isinstance(P, list) or not P: self.fatal("拼版缺少 panels（子图列表）。", ex='"panels": [{"box":[0,0,0.5,1], "title":"Daily Revenue", "chart":{"kind":"area_stack","data":{...}}}]'); return
        if len(P) > 9: self.warn(f"一页放了 {len(P)} 个子图，太密。", "控制在 6 个以内，或拆成两页。")
        g = self.spec.get("grid")
        for k, p in enumerate(P):
            w = f"panels[{k}]"
            if "box" in p:
                b = p["box"]
                if not (isinstance(b, list) and len(b) == 4 and all(_num(x) for x in b) and b[0] >= 0 and b[1] >= 0 and b[0]+b[2] <= 1.001 and b[1]+b[3] <= 1.001): self.fatal(f"{w}.box 应为 [x, y, 宽, 高]（内容区的 0–1 比例），且不能超出边界：{b}。")
            elif "cell" in p:
                if not g: self.fatal(f"{w} 用了 cell，但页面没有 grid。", ex='"grid": {"rows": 2, "cols": 3}')
                else:
                    r, c = p["cell"]; rs, cs = p.get("span", [1, 1])
                    if r+rs > g["rows"] or c+cs > g["cols"]: self.fatal(f"{w} 的 cell/span 超出网格 {g['rows']}×{g['cols']}。")
            ch = p.get("chart") or {}
            n = self._mini(ch.get("kind"), ch.get("data"), w)
            if n: self._deco(ch, n, w, [s.get("name") for s in (ch.get("data") or {}).get("series", [])])
        boxes = [p["box"] for p in P if isinstance(p.get("box"), list) and len(p["box"]) == 4]
        for i in range(len(boxes)):
            for j in range(i+1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if a[0] < b[0]+b[2]-0.01 and b[0] < a[0]+a[2]-0.01 and a[1] < b[1]+b[3]-0.01 and b[1] < a[1]+a[3]-0.01: self.warn(f"panels[{i}] 和 panels[{j}] 的区域重叠，子图会压在一起。", "调整 box。")
    def c_facet(self):
        rows, cols, cells = self.spec.get("rows"), self.spec.get("cols"), self.spec.get("cells")
        if not isinstance(rows, list) or not rows: self.fatal("分面缺少 rows（行：指标或分组）。", ex='"rows": [{"label":"Daily Rev","chart":{"kind":"area_stack"}}]'); return
        if not isinstance(cols, list) or not cols: self.fatal("分面缺少 cols（列名）。", ex='"cols": ["Country 1", "Country 2"]'); return
        if not isinstance(cells, list) or len(cells) != len(rows): self.fatal(f"cells 要有 {len(rows)} 行（和 rows 一样多），每行 {len(cols)} 格。"); return
        if len(rows)*len(cols) > 60: self.warn(f"分面有 {len(rows)}×{len(cols)} = {len(rows)*len(cols)} 格，数字会小到看不清。", "减少行或列。")
        for i, (r, row) in enumerate(zip(rows, cells)):
            kind = (r.get("chart") or {}).get("kind")
            if not isinstance(row, list) or len(row) != len(cols): self.fatal(f"cells[{i}] 有 {len(row) if isinstance(row, list) else '?'} 格，但有 {len(cols)} 列。", "没有数据的格子写 null。"); continue
            if kind == "bars_pair":
                rule = r["chart"].get("rule", {})
                if rule.get("threshold") is not None and not _num(rule["threshold"]): self.fatal(f"rows[{i}] 的 rule.threshold（时间进度）应该是数字。")
            for j, d in enumerate(row):
                if d is None: continue
                self._mini(kind, d, f"cells[{i}][{j}]")

def validate(spec):
    v = V(spec)
    try: v.run()
    except Exception as e: v.fatal(f"数据结构无法解析（{type(e).__name__}: {e}）。", "对照 examples/<type>.json 检查字段。")
    lv = [i["level"] for i in v.issues]
    st = FAIL if "fatal" in lv else WARN if "warn" in lv else OK
    return dict(type=v.t, id=spec.get("id"), status=st, issues=v.issues, alternatives=v.alts, compromise=v.compromise)

def report(r):
    L = [f"【数据校验】图表类型：{r['type']}{'（'+r['id']+'）' if r.get('id') else ''}", f"结论：{r['status']}"]
    f = [i for i in r["issues"] if i["level"] == "fatal"]; w = [i for i in r["issues"] if i["level"] == "warn"]
    if f:
        L.append("必须先解决的问题（不解决画不出来或会画错）：")
        for k, i in enumerate(f, 1):
            L.append(f"  {k}. {i['msg']}")
            if i.get("fix"): L.append(f"     怎么补：{i['fix']}")
            if i.get("example"): L.append(f"     示例格式：{i['example']}")
    if w:
        L.append("可以画，但建议注意：")
        for k, i in enumerate(w, 1):
            L.append(f"  {k}. {i['msg']}" + (f" 建议：{i['fix']}" if i.get("fix") else ""))
            if i.get("example"): L.append(f"     示例格式：{i['example']}")
    if r["compromise"]: L.append("如果一定要现在出图，折中办法：" + "；".join(dict.fromkeys(r["compromise"])) + "。")
    if r["alternatives"]: L.append("也可以考虑换图：" + "；".join(f"{a['type']}（{a['why']}）" for a in r["alternatives"]) + "。")
    if r["status"] == OK: L.append("数据完整，可以直接渲染。")
    return "\n".join(L)

def main():
    import argparse, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(); ap.add_argument("specs", nargs="+"); ap.add_argument("--json", action="store_true"); a = ap.parse_args()
    out = []; worst = 0
    for f in a.specs:
        j = json.load(open(f, encoding="utf-8"))
        if isinstance(j, list) or ("slides" not in j and "type" not in j): continue
        for s in (j["slides"] if "slides" in j else [j]):
            r = validate(s); out.append(r); worst = max(worst, [OK, WARN, FAIL].index(r["status"]))
            if not a.json: print(report(r)); print()
    if a.json: print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(2 if worst == 2 else 0)

if __name__ == "__main__":
    import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); main()
