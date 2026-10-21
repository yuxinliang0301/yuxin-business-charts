"""yuxin-business-charts 核心：用 python-pptx 画 think-cell 风格图表（全部为可编辑 PPT 形状）。
规范与依据见 ../docs/STYLE_SPEC.md；颜色见 PALETTES。"""
import math, datetime as dt
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn
from lxml import etree

def H(h): h=h.lstrip('#'); return RGBColor(int(h[:2],16),int(h[2:4],16),int(h[4:],16))
# 取色来源：think-cell 手册 introductioncharting 页 applying_color.jpg 的填充下拉菜单色块（逐像素取色，见 docs/COLORS.md）
TC = dict(accent1="#6DA600", accent2="#4C7400", accent3="#0070AF", accent4="#00507C", accent5="#C0C0C0", accent6="#777777",
          text2="#005082", tc_red="#C10D3B", tc_gray="#D4D7D9", tc_green="#027673",
          smoke10="#DEE5F0", smoke20="#C4CEE0", smoke40="#9DB0D0", smoke60="#6D8EB9", smoke80="#4E6A9C", smoke90="#344E6A",
          light_gray="#C0C0C0", med_gray="#969596", dark_gray="#808080", black="#000000", white="#FFFFFF")
# ---------------- 主题（语义角色色）----------------
# consulting_navy：取色自用户提供的两张咨询参考图（见 docs/COLORS.md）；thinkcell_green：旧版 think-cell 手册取色
def _th(palette, pos, accent5, accent6, neg, neg2, neg3, shade, target="#000000", callout=None, wf_pos=None,
        wf_neg=None, muted=None, bullet=None, tam=None, likert=None, **meta):
    callout = callout or neg
    return dict(palette=palette, accent1=pos, accent5=accent5, accent6=accent6, tc_red=callout, tc_gray=shade,
                pos=pos, wf_pos=wf_pos or pos, wf_neg=wf_neg or neg, neg=neg, neg2=neg2, neg3=neg3,
                target=target, callout=callout, good=pos, bad=neg, muted=muted or accent5, bullet=bullet or pos,
                tam=tam or [palette[6] if len(palette) > 6 else accent5, palette[1], pos],
                likert=likert or [pos, palette[6] if len(palette) > 6 else accent5, accent5, neg], meta=meta)
# 每套主题的色值出处见 docs/PALETTES.md 与 references/palettes/SOURCES.csv
THEMES = {
  # 本地用户偏好：吸收图表模板的分析结构，以低饱和蓝灰重构视觉层级。
  "restrained_navy": _th(["#24465C", "#7391A4", "#B7C6D0", "#DCE3E8", "#536773", "#94A3AE", "#C9D0D5", "#3C5666"],
      pos="#24465C", accent5="#C9D0D5", accent6="#687782", neg="#A0525A", neg2="#85434B", neg3="#69363D", shade="#EEF2F5",
      target="#414D57", callout="#24465C",
      tam=["#DCE3E8", "#7391A4", "#24465C"], likert=["#24465C", "#B7C6D0", "#E6EAED", "#A0525A"],
      zh="克制蓝灰", restrained=True),
  # 海军蓝咨询风（默认）：用户提供的两张参考图取色
  "consulting_navy": _th(["#00507D", "#6C89B4", "#F8BA00", "#E87722", "#5E9C42", "#787675", "#98ADC9", "#344B6B"],
      pos="#00507D", accent5="#C6C0C0", accent6="#787675", neg="#A20603", neg2="#85100B", neg3="#691413", shade="#E3E8F0",
      tam=["#98ADC9", "#6C89B4", "#00507D"], likert=["#00507D", "#98ADC9", "#C6C0C0", "#A20603"],
      zh="海军蓝咨询风"),
  # think-cell 手册经典绿灰：手册 applying_color.jpg 菜单色块取色
  "thinkcell_green": _th(["#6DA600", "#777777", "#C0C0C0", "#4C7400", "#0070AF", "#00507C"],
      pos="#6DA600", accent5="#C0C0C0", accent6="#777777", neg="#C10D3B", neg2="#9E0B30", neg3="#7A0825", shade="#D4D7D9",
      target="#C10D3B", wf_pos="#C0C0C0", wf_neg="#777777", muted="#777777", bullet="#000000",
      tam=["#C0C0C0", "#777777", "#6DA600"], likert=["#6DA600", "#B5D47F", "#C0C0C0", "#C10D3B"], zh="think-cell 经典绿灰"),
  # think-cell 官网蓝阶风：think-cell 官网产品页图表截图取色
  "thinkcell_blue": _th(["#1736B5", "#2972FF", "#8EC1FF", "#1BBC9B", "#3D3D3D", "#BEBEBE", "#BCD8FF", "#599DFE"],
      pos="#1736B5", accent5="#DBDBDB", accent6="#707070", neg="#E8163B", neg2="#BA1230", neg3="#8C0D24", shade="#E8E8F0",
      tam=["#BCD8FF", "#599DFE", "#1736B5"], likert=["#1736B5", "#8EC1FF", "#DBDBDB", "#E8163B"], zh="think-cell 官网蓝阶风"),
  # 青绿+黑 现代风：think-cell 官网瀑布图截图（青绿 + 黑 + 蓝）取色
  "teal_modern": _th(["#18A98C", "#3D3D3D", "#8ED4C5", "#1B57F5", "#BEBEBE", "#0E6B58", "#BCD8FF", "#707070"],
      pos="#18A98C", accent5="#DBDBDB", accent6="#707070", neg="#E8163B", neg2="#BA1230", neg3="#8C0D24", shade="#E8F8F8",
      tam=["#8ED4C5", "#18A98C", "#0E6B58"], likert=["#0E6B58", "#8ED4C5", "#DBDBDB", "#E8163B"], zh="青绿现代风"),
  # 投行深蓝金：深海军蓝 + 金色；取色自用户参考图 B 的深灰蓝 #344B6B / 金 #F8BA00，其余为推导
  "banking_navy_gold": _th(["#1F2E44", "#344B6B", "#F8BA00", "#98ADC9", "#787675", "#C9A227", "#C6C0C0", "#6C89B4"],
      pos="#1F2E44", accent5="#C6C0C0", accent6="#787675", neg="#A20603", neg2="#85100B", neg3="#691413", shade="#EEF1F5",
      tam=["#98ADC9", "#344B6B", "#1F2E44"], likert=["#1F2E44", "#98ADC9", "#C6C0C0", "#A20603"], zh="投行深蓝金"),
  # Office 默认主题：PowerPoint 2023+ 默认 Accent1-6（think-cell 默认跟随主题色，KB0105）
  "office": _th(["#156082", "#E97132", "#196B24", "#0F9ED5", "#A02B93", "#4EA72E", "#7F7F7F", "#BFBFBF"],
      pos="#156082", accent5="#BFBFBF", accent6="#7F7F7F", neg="#C00000", neg2="#A00000", neg3="#7F0000", shade="#E8E8E8",
      tam=["#9DC3D6", "#0F9ED5", "#156082"], likert=["#156082", "#0F9ED5", "#BFBFBF", "#C00000"], zh="Office 默认主题"),
  # 单色渐变（Smoke 蓝灰）：think-cell 手册填充菜单 Smoke 10-90% 色块取色
  "mono_smoke": _th(["#344E6A", "#6D8EB9", "#C4CEE0", "#4E6A9C", "#9DB0D0", "#DEE5F0", "#808080", "#C0C0C0"],
      pos="#344E6A", accent5="#C4CEE0", accent6="#808080", neg="#C10D3B", neg2="#9E0B30", neg3="#7A0825", shade="#DEE5F0",
      tam=["#C4CEE0", "#6D8EB9", "#344E6A"], likert=["#344E6A", "#9DB0D0", "#DEE5F0", "#C10D3B"], zh="单色渐变（Smoke 蓝灰）"),
  # 灰阶 + 单一强调红：think-cell 手册灰阶（Light/Med/Dark Gray）+ tc Red
  "gray_accent": _th(["#4D4D4D", "#969596", "#C0C0C0", "#C10D3B", "#777777", "#DEDEDE", "#B0B0B0", "#2B2B2B"],
      pos="#4D4D4D", accent5="#C0C0C0", accent6="#777777", neg="#C10D3B", neg2="#9E0B30", neg3="#7A0825", shade="#EDEDED",
      wf_pos="#969596", tam=["#DEDEDE", "#969596", "#4D4D4D"], likert=["#4D4D4D", "#969596", "#DEDEDE", "#C10D3B"],
      zh="灰阶+强调红"),
}
FORCE_THEME = None   # CLI --theme 设置后覆盖 spec 里的 theme
DEFAULT_THEME = "restrained_navy"
def set_theme(name):
    th = THEMES.get(name, THEMES[DEFAULT_THEME])
    for k, v in th.items():
        if k not in ("palette", "meta"): TC[k] = v
    return th

PALETTES = {
  # 系列顺序 = 数据表顺序（第 1 个系列画在最上面），与手册示例图一致：顶=绿 Accent1、中=深灰 Accent6、底=浅灰 Accent5
  "thinkcell": [TC["accent1"], TC["accent6"], TC["accent5"], TC["accent2"], TC["accent3"], TC["accent4"]],
  **{k: v["palette"] for k, v in THEMES.items()},
  # 新版 Office 默认主题（think-cell 默认跟随 PowerPoint 主题 Accent1-6，见 KB0105）
}
SW, SH = 13.333, 7.5
FONT = "Kaiti SC"

def set_run_font(run, family=FONT):
    """Set Latin, East Asian and complex-script fonts explicitly in editable PPTX."""
    run.font.name = family
    props = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        node = props.find(qn(tag))
        if node is None:
            node = etree.SubElement(props, qn(tag))
        node.set("typeface", family)

FS = 14            # 图内所有文字同一字号（手册示例：段内标签/总计/类别标签同字号）
FS_TITLE, FS_SUB, FS_FOOT = 24, 14, 10
LINE_W = 0.75
DARK = {"#6DA600","#777777","#4C7400","#0070AF","#00507C","#027673","#C10D3B","#344E6A","#4E6A9C","#156082","#196B24","#A02B93","#808080","#000000"}

def _lum(h):
    h = h.lstrip("#"); c = [int(h[i:i+2],16)/255 for i in (0,2,4)]
    c = [x/12.92 if x <= 0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]
def ink(fill):
    """按 WCAG 对比度选白字或黑字（取对比度更高者）"""
    L = _lum(fill); return RGBColor(255,255,255) if (1.05)/(L+0.05) >= (L+0.05)/0.05 else RGBColor(0,0,0)

def fmt(v, f=None):
    if f: return f.format(v)
    if isinstance(v,float) and not v.is_integer(): return f"{v:.1f}"
    return f"{v:,.0f}" if abs(v)>=10000 else f"{v:g}"

class Slide:
    def __init__(self, prs, spec):
        self.s = prs.slides.add_slide(prs.slide_layouts[6]); self.spec = spec
        th = set_theme(FORCE_THEME or spec.get("theme", DEFAULT_THEME)); self.theme = th
        pal = spec.get("palette"); self.pal = pal if isinstance(pal, list) else PALETTES.get(pal, th["palette"])
        self.font = spec.get("font_family", FONT)
        self.fs = spec.get("font_size", FS); self._boxes = []; self._marks = []
        # Optional chart bounds leave room for dense captions without scaling text.
        if "chart_box" in spec:
            box = spec["chart_box"]
            if (not isinstance(box, (list, tuple)) or len(box) != 4 or
                any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in box) or
                min(box[:2]) < 0 or min(box[2:]) <= 0 or box[0]+box[2] > SW or box[1]+box[3] > SH):
                raise ValueError("chart_box must be [x, y, width, height] in inches within the slide")
            self.CHART = tuple(box)
    def col(self, i): return self.pal[i % len(self.pal)]
    # ---------- primitives (全部去掉主题 style -> 无阴影、无主题描边) ----------
    def _nostyle(self, shp):
        st = shp._element.find(qn('p:style'))
        if st is not None: shp._element.remove(st)
        return shp
    def _tf(self, tf, s, size=None, color="#000000", bold=False, align="c", anchor="m", wrap=False, italic=False):
        tf.margin_left = tf.margin_right = Inches(0.02); tf.margin_top = tf.margin_bottom = 0
        tf.word_wrap = wrap; tf.vertical_anchor = {"m":MSO_ANCHOR.MIDDLE,"t":MSO_ANCHOR.TOP,"b":MSO_ANCHOR.BOTTOM}[anchor]
        lines = str(s).split("\n")
        for k,ln in enumerate(lines):
            p = tf.paragraphs[0] if k==0 else tf.add_paragraph()
            p.alignment = {"c":PP_ALIGN.CENTER,"l":PP_ALIGN.LEFT,"r":PP_ALIGN.RIGHT}[align]
            r = p.add_run(); r.text = ln; f = r.font
            set_run_font(r, self.font)
            f.size = Pt(size or self.fs); f.bold = bold; f.italic = italic
            f.color.rgb = H(color) if isinstance(color,str) else color
    def rect(self, x, y, w, h, fill, label=None, outline=None, lw=LINE_W, shape=MSO_SHAPE.RECTANGLE, size=None, dash=None):
        if h < 0: y, h = y+h, -h
        if w < 0: x, w = x+w, -w
        s = self._nostyle(self.s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(max(w,0.001)), Inches(max(h,0.001))))
        if fill is None: s.fill.background()
        else: s.fill.solid(); s.fill.fore_color.rgb = H(fill)
        if outline: s.line.color.rgb = H(outline); s.line.width = Pt(lw)
        else: s.line.fill.background()
        if dash: s.line.dash_style = dash
        if label is not None: self.mark(label, x+w/2, y+h/2)
        if label is not None and h >= (size or self.fs)/72*1.05 and w >= 0.25:
            self._tf(s.text_frame, label, size=size, color=ink(fill) if fill else RGBColor(0,0,0))
        return s
    def _est(self, s, size):
        lines = str(s).split("\n"); fs = (size or self.fs)/72
        wd = max(sum(1.0 if ord(ch) > 0x2E80 else 0.56 for ch in ln) for ln in lines) * fs
        return wd, len(lines)*fs*1.2
    def text(self, x, y, s, w=1.2, h=None, align="c", anchor="m", size=None, color="#000000", bold=False, wrap=False, italic=False, avoid=True):
        h = h or (size or self.fs)/72*1.5
        # 标签自动防重叠：估算文字实际外框，与已放置标签相交时上下交替微移（最多 4 次）
        if avoid and not wrap and anchor == "m":
            tw, th = self._est(s, size); tw = min(tw, w)
            bx = lambda yy: ((x - tw/2) if align=="c" else (x - tw if align=="r" else x), yy - th/2, tw, th)
            hit = lambda b: any(b[0] < o[0]+o[2] and o[0] < b[0]+b[2] and b[1] < o[1]+o[3] and o[1] < b[1]+b[3] for o in self._boxes)
            y_try = y
            for k in range(9):
                if not hit(bx(y_try)): break
                y_try = y + ((k//2)+1)*th*0.9*(-1 if k%2==0 else 1)
            else: y_try = y
            y = y_try; self._boxes.append(bx(y))
        x0 = x - w/2 if align=="c" else (x - w if align=="r" else x)
        y0 = y - h/2 if anchor=="m" else (y - h if anchor=="b" else y)
        tw_, th_ = self._est(s, size)
        self.mark(s, x if align=="c" else (x - min(tw_,w)/2 if align=="r" else x + min(tw_,w)/2), y if anchor=="m" else (y - h/2 if anchor=="b" else y + h/2), min(tw_,w), th_)
        t = self.s.shapes.add_textbox(Inches(x0), Inches(y0), Inches(w), Inches(h))
        self._tf(t.text_frame, s, size=size, color=color, bold=bold, align=align, anchor=anchor, wrap=wrap, italic=italic); return t
    def mark(self, s, x, y, w=0.0, h=0.0):
        """登记一个可被 callout/highlight 引用的锚点（任何标签文字都会自动登记，含文字外框）"""
        self._marks.append((str(s), x, y, w, h))
    def find(self, key, nth=0, box=False):
        hits = [m[1:] for m in self._marks if m[0] == str(key)]
        if not hits: hits = [m[1:] for m in self._marks if str(key) in m[0]]
        if hits and not box: hits = [h[:2] for h in hits]
        if not hits: raise KeyError(f"anchor not found: {key!r}")
        return hits[min(nth, len(hits)-1)]
    def line(self, x1, y1, x2, y2, w=LINE_W, color="#000000", dash=None, head=None, tail=None):
        c = self._nostyle(self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)))
        c.line.color.rgb = H(color); c.line.width = Pt(w)
        if dash: c.line.dash_style = dash
        ln = c.line._get_or_add_ln()
        for tag,val in (("a:headEnd",head),("a:tailEnd",tail)):
            if val: e = etree.SubElement(ln, qn(tag)); e.set("type", val); e.set("w","med"); e.set("len","med")
        return c
    def poly(self, pts, fill=None, outline=None, lw=1.5, closed=True):
        fb = self.s.shapes.build_freeform(Inches(pts[0][0]), Inches(pts[0][1]), scale=1.0)
        fb.add_line_segments([(Inches(x),Inches(y)) for x,y in pts[1:]], close=closed)
        s = self._nostyle(fb.convert_to_shape())
        if fill: s.fill.solid(); s.fill.fore_color.rgb = H(fill)
        else: s.fill.background()
        if outline: s.line.color.rgb = H(outline); s.line.width = Pt(lw)
        else: s.line.fill.background()
        return s
    def bubble(self, cx, cy, s, w=None):
        """think-cell 差值/CAGR 标签：白底黑边椭圆（手册 chartdecorations: differencearrow_abs1 / cagr_formula）"""
        w = w or max(0.9, 0.11*len(s)+0.35); h = self.fs/72*1.7
        e = self.rect(cx-w/2, cy-h/2, w, h, "#FFFFFF", outline="#000000", shape=MSO_SHAPE.OVAL)
        self._tf(e.text_frame, s, bold=True); return e
    # ---------- 版面分区（见 docs/STYLE_SPEC.md §1） ----------
    def frame(self):
        sp = self.spec
        if sp.get("title"): self.text(0.5, 0.35, sp["title"], w=12.3, h=0.8, align="l", anchor="t", size=FS_TITLE, bold=True, wrap=True)
        sub = " ".join(x for x in [sp.get("subtitle",""), (sp.get("unit") and f"({sp['unit']})") or ""] if x)
        if sub: self.text(0.5, 1.2, sub, w=12.3, h=0.35, align="l", size=FS_SUB, color="#777777")
        foot = []
        if sp.get("footnote"): foot.append(sp["footnote"])
        foot.append("Source: " + (sp.get("source") or "[missing – add source]"))
        if foot: self.text(0.5, 7.05, "\n".join(foot), w=12.3, h=0.4, align="l", anchor="b", size=FS_FOOT, color="#555555", wrap=True)
    CHART = (0.7, 1.75, 11.9, 4.95)   # x, y, w, h 图表区

def label_h(fs): return fs/72*1.05

# ======================= 类别型图（柱/堆叠/100%/簇状/堆叠簇状） =======================
def _cat_layout(sl, n, groups=1, gap=0.5, right_legend=1.6, top_room=0.0, left=0.0):
    X,Y,W,Hh = sl.CHART
    pw = W - right_legend - left; px = X + left
    slot = pw / n
    return px, Y+top_room, pw, Hh-top_room, slot

def column_family(sl, d, mode="stacked"):
    """mode: stacked | percent | clustered | stacked_clustered | column"""
    cats = d["categories"]; series = d["series"]; n = len(cats)
    vals = [[s["values"][i] for s in series] for i in range(n)]
    deco = sl.spec.get("decorations", [])
    top_room = 0.9 if any(k.get("type") in ("cagr","total_diff") for k in deco) else 0.35
    px, py, pw, ph, slot = _cat_layout(sl, n, top_room=top_room, right_legend=1.6 if len(series)>1 and mode!="clustered" else 0.3)
    y0 = py + ph - 0.35   # baseline，留出类别标签
    geo = {"x":[], "w":[], "top":[], "bot":[], "tot":[], "seg":[]}
    brk = d.get("axis_break")  # {"from":a,"to":b}
    def scale_fn(vmax, vmin=0):
        hspan = y0 - py - 0.35
        cut = (brk["to"]-brk["from"]) if brk else 0
        sc = hspan / ((vmax - vmin) - cut*0.92)
        def yy(v):
            if brk and v > brk["to"]: v = v - cut*0.92
            elif brk and v > brk["from"]: v = brk["from"] + (v-brk["from"])*0.08
            return y0 - (v - vmin)*sc
        return yy
    if mode == "percent":
        tots = [sum(v) for v in vals]
        hspan = y0 - py - 0.35
        yy = lambda p: y0 - p/100*hspan
    elif mode == "clustered":
        vmax = max(max(v) for v in vals); vmin = min(0, min(min(v) for v in vals)); yy = scale_fn(vmax, vmin)
    else:
        pos = [sum(x for x in v if x>0) for v in vals]; neg = [sum(x for x in v if x<0) for v in vals]
        vmax = max(pos); vmin = min(0, min(neg)); yy = scale_fn(vmax, vmin)
    base = yy(0)
    sl.line(px, base, px+pw, base, LINE_W)
    gw = d.get("gap_width", 0.6 if mode!="clustered" else 0.75)
    for i, c in enumerate(cats):
        cx = px + slot*(i+0.5); bw = slot*gw
        sl.text(cx, y0+0.22 if mode!="clustered" or vmin>=0 else y0+0.22, c, w=slot)
        segs = []
        if mode == "clustered":
            k = len(series); w1 = bw/k
            for j,s in enumerate(series):
                v = vals[i][j]; x = cx - bw/2 + j*w1
                sl.rect(x, yy(max(v,0)), w1, abs(yy(v)-base), sl.col(j))
                sl.text(x+w1/2, (yy(v)-0.15) if v>=0 else (yy(v)+0.15), fmt(v,d.get("format")), w=w1+0.3)
                segs.append((x, yy(max(v,0)), w1, yy(min(v,0))))
            geo["top"].append(min(yy(max(v,0)) for v in vals[i])); geo["tot"].append(max(vals[i]))
        else:
            up = 0; dn = 0
            order = list(range(len(series)))[::-1]   # 第 1 个系列画在最上面
            for j in order:
                v = vals[i][j]
                if mode == "percent":
                    p = v / tots[i] * 100; a, b = up, up+p; up = b; lab = f"{p:.0f}%"
                else:
                    if v >= 0: a, b = up, up+v; up = b
                    else: a, b = dn+v, dn; dn = a
                    lab = fmt(v, d.get("format"))
                ytop, ybot = yy(b), yy(a)
                sl.rect(cx-bw/2, ytop, bw, ybot-ytop, sl.col(j), None if mode=="column" else lab)
                segs.append((cx-bw/2, ytop, bw, ybot, j))
            top = yy(up) if mode!="percent" else yy(100)
            geo["top"].append(top); geo["tot"].append(sum(vals[i]) if mode!="percent" else 100)
            if mode in ("stacked","stacked_clustered") and len(series)>1 and d.get("show_totals", True):
                sl.text(cx, top-0.18, fmt(sum(vals[i]), d.get("format")), w=slot)
            if mode == "percent" and d.get("show_totals", True):
                sl.text(cx, top-0.18, fmt(tots[i], d.get("format")), w=slot)
            if mode == "column":
                sl.text(cx, top-0.18, fmt(sum(vals[i]), d.get("format")), w=slot)
        geo["x"].append(cx); geo["w"].append(bw); geo["seg"].append(segs); geo["bot"].append(base)
    if mode == "percent":
        for t in (0, 50, 100): sl.text(px-0.1, yy(t), f"{t}%", w=0.7, align="r")
    # 系列标签：放在最后一列右侧（手册 sample_stacked / sample_100perc）
    diff_last = any(k.get("type")=="diff" and k.get("to") in (n-1, cats[-1]) for k in deco)
    if len(series) > 1 and diff_last:
        _legend(sl, [s["name"] for s in series])
    elif len(series) > 1 and mode != "clustered":
        last = geo["seg"][-1]
        for (x, yt, w, yb, j) in last:
            sl.text(x+w+0.12, (yt+yb)/2, series[j]["name"], w=1.5, align="l")
    elif mode == "clustered":
        _legend(sl, [s["name"] for s in series])
    if brk: _axis_break_marks(sl, geo, yy, brk)
    geo["yy"] = yy; geo["base"] = base; geo["slot"] = slot
    return geo

def _legend(sl, names, y=None):
    X,Y,W,Hh = sl.CHART; y = y or Y+0.05; x = X
    for j, nm in enumerate(names):
        sl.rect(x, y-0.08, 0.16, 0.16, sl.col(j)); sl.text(x+0.22, y, nm, w=1.8, align="l"); x += 0.3 + 0.1*len(nm) + 0.3

def _axis_break_marks(sl, geo, yy, brk):
    """轴破断：在被截断的柱子上画两条白色斜平行线（手册 axes: break_wiggle / break_y1）"""
    ym = yy((brk["from"]+brk["to"])/2)
    for x, w, t in zip(geo["x"], geo["w"], geo["tot"]):
        if t > brk["to"]:
            for dy in (-0.05, 0.05):
                sl.poly([(x-w/2-0.06, ym+dy+0.05), (x+w/2+0.06, ym+dy-0.05), (x+w/2+0.06, ym+dy-0.02), (x-w/2-0.06, ym+dy+0.08)], fill="#FFFFFF")

# ======================= 装饰：CAGR / 差值箭头 / 总差括号 / 强调 =======================
def decorations(sl, geo, deco, cats):
    idx = lambda k: cats.index(k) if isinstance(k, str) else k
    for dd in deco:
        t = dd["type"]
        if t in ("cagr", "total_diff"):
            # 手册 chartdecorations cagr_formula / differencearrow_abs2：从 A 柱顶上方竖线 -> 水平线 -> 箭头指向 B 柱顶，中间椭圆标签
            a, b = idx(dd["from"]), idx(dd["to"])
            xa, xb = geo["x"][a], geo["x"][b]; ya, yb = geo["top"][a]-0.38, geo["top"][b]-0.38
            yl = min(geo["top"][a:b+1]) - 0.38 - 0.45 - 0.25*dd.get("level",0)
            sl.line(xa, ya, xa, yl); sl.line(xa, yl, xb, yl); sl.line(xb, yl, xb, yb, tail="triangle")
            va, vb = geo["tot"][a], geo["tot"][b]
            if t == "cagr":
                r = (vb/va)**(1/(b-a)) - 1; s = dd.get("label", f"{r*100:+.1f}%")
            else:
                s = dd.get("label", f"{(vb/va-1)*100:+.0f}%" if dd.get("percent", True) else fmt(vb-va))
            sl.bubble((xa+xb)/2, yl, s)
        elif t == "diff":
            # 手册 differencearrow_abs1：A 顶虚线水平引出到 B 右侧，双向竖箭头 + 椭圆标签
            a, b = idx(dd["from"]), idx(dd["to"])
            ya, yb = geo["top"][a], geo["top"][b]; xr = geo["x"][b] + geo["w"][b]/2 + 0.25
            sl.line(geo["x"][a]+geo["w"][a]/2, ya, xr+0.08, ya, dash=MSO_LINE_DASH_STYLE.DASH)
            sl.line(geo["x"][b]+geo["w"][b]/2, yb, xr+0.08, yb, dash=MSO_LINE_DASH_STYLE.DASH)
            sl.line(xr, ya, xr, yb, head="triangle", tail="triangle")
            va, vb = geo["tot"][a], geo["tot"][b]
            s = dd.get("label", f"{(vb/va-1)*100:+.0f}%" if dd.get("percent", True) else f"{vb-va:+g}")
            sl.bubble(xr+0.55, (ya+yb)/2, s)
        elif t == "value_line":
            v = dd["value"]; y = geo["yy"](v); X,Y,W,Hh = sl.CHART
            sl.line(geo["x"][0]-geo["slot"]/2, y, geo["x"][-1]+geo["slot"]/2, y, dash=MSO_LINE_DASH_STYLE.DASH)
            sl.text(geo["x"][-1]+geo["slot"]/2+0.05, y, dd.get("label", fmt(v)), w=1.4, align="l")
        elif t == "highlight":
            # 强调：圆圈/椭圆圈住目标柱（tc Red 描边）
            a = idx(dd["category"]); x, w = geo["x"][a], geo["w"][a]
            yt = geo["top"][a]-0.35; yb = geo["base"]+0.45
            sl.rect(x-w/2-0.2, yt, w+0.4, yb-yt, None, outline=TC["tc_red"], lw=2, shape=MSO_SHAPE.OVAL)
        elif t == "callout":
            a = idx(dd["category"]); x = geo["x"][a]; y = geo["top"][a]
            tx, ty = x + dd.get("dx", 1.4), y - dd.get("dy", 0.6)
            sl.line(x, y-0.05, tx-0.05, ty+0.2, color=TC["tc_red"])
            b = sl.rect(tx-0.05, ty-0.25, dd.get("w", 2.2), 0.5, "#FFFFFF", outline=TC["tc_red"], lw=1)
            sl._tf(b.text_frame, dd["text"], color=TC["tc_red"], bold=True)

# ======================= 瀑布 =======================
def _resolve_subtotals(items):
    out = []; run = 0
    for it in items:
        it = dict(it); k = it.get("kind","delta")
        if k == "subtotal": it["kind"] = "total"; k = "total"
        if k in ("total",) and "value" not in it: it["value"] = run
        if k == "start": run = it["value"]
        elif k == "delta": run += it["value"]
        out.append(it)
    return out

def waterfall(sl, d):
    items = _resolve_subtotals(d["items"])   # kind: start|delta|subtotal|total（subtotal/total 不给 value 时自动计算）
    run = 0; bars = []
    for it in items:
        v = it["value"]; k = it.get("kind","delta")
        if k in ("start","total"): bars.append((0, v)); run = v if k=="start" else run
        else: bars.append((run, run+v)); run += v
        if k == "total" and abs(run - v) > 1e-6 and d.get("check", True): pass
    n = len(items); X,Y,W,Hh = sl.CHART
    vmax = max(max(a,b) for a,b in bars); vmin = min(0, min(min(a,b) for a,b in bars))
    py = Y+0.4; y0 = Y+Hh-0.4; sc = (y0-py)/(vmax-vmin); yy = lambda v: y0-(v-vmin)*sc
    slot = W/n; bw = slot*d.get("gap_width",0.6); base = yy(0)
    sl.line(X, base, X+W, base)
    geo = {"x":[], "w":[], "top":[], "tot":[], "base":base, "yy":yy, "slot":slot}
    for i, (it, (a, b)) in enumerate(zip(items, bars)):
        k = it.get("kind","delta"); v = it["value"]; cx = X+slot*(i+0.5)
        fill = it.get("color") or ((sl.col(0) if v>=0 else TC["neg3"]) if k in ("start","total") else (TC["wf_pos"] if v>=0 else TC["wf_neg"]))
        if d.get("color_by_sign") and k=="delta": fill = TC["good"] if v>=0 else TC["bad"]
        top, bot = yy(max(a,b)), yy(min(a,b))
        lab = fmt(abs(v) if (k=="delta" and not d.get("signed_labels")) else v, d.get("delta_format") if k=="delta" and d.get("delta_format") else d.get("format"))
        if k == "delta" and d.get("signed_labels") and not d.get("delta_format"): lab = ("+" if v>0 else "") + lab
        r = sl.rect(cx-bw/2, top, bw, bot-top, fill, lab)
        if bot-top < label_h(sl.fs):   # 放不下：标签放在柱外（上方/下方）
            sl.text(cx, top-0.16 if v>=0 else bot+0.16, lab, w=slot)
        sl.text(cx, y0+0.22, it["label"], w=slot, wrap=True, h=0.45, anchor="t") if False else sl.text(cx, max(base, y0)+0.22, it["label"], w=slot)
        if i < n-1:   # 连接线：细虚线（手册 sample_waterfall_connectors）
            lvl = b if k in ("start","total") or v>=0 else a
            if k=="delta" and v<0: lvl = b+v if False else a
            lvl = run_level(bars, items, i)
            sl.line(cx+bw/2, yy(lvl), cx+slot-bw/2, yy(lvl), w=0.5, dash=MSO_LINE_DASH_STYLE.DASH)
        geo["x"].append(cx); geo["w"].append(bw); geo["top"].append(top); geo["tot"].append(max(a,b)); geo.setdefault("bot", []).append(float(bot)); geo["wf"] = True
    return geo

def run_level(bars, items, i):
    a, b = bars[i]; k = items[i].get("kind","delta"); v = items[i]["value"]
    if k in ("start","total"): return b
    return b   # 增量后累计值 = b（负值时 b=run+v 低于 a）

def waterfall_h(sl, d):
    """水平瀑布（build-down 分解：总额 -> 各项）"""
    items = d["items"]; n = len(items); X,Y,W,Hh = sl.CHART
    run = 0; bars = []
    for it in items:
        v = it["value"]; k = it.get("kind","delta")
        if k in ("start","total"): bars.append((0, v)); run = v
        else: bars.append((run, run+v) if v>=0 else (run+v, run)); run += v
    vmax = max(b for a,b in bars); lx = X+2.4; pw = W-2.4-0.8; sc = pw/vmax; xx = lambda v: lx+v*sc
    slot = Hh/n; bh = slot*0.6
    sl.line(lx, Y, lx, Y+Hh)
    for i,(it,(a,b)) in enumerate(zip(items,bars)):
        cy = Y+slot*(i+0.5); k = it.get("kind","delta"); v = it["value"]
        fill = (sl.col(0) if v>=0 else TC["neg3"]) if k in ("start","total") else (TC["wf_pos"] if v>=0 else TC["wf_neg"])
        r = sl.rect(xx(a), cy-bh/2, xx(b)-xx(a), bh, fill)
        lab = fmt(abs(v) if k=="delta" else v, d.get("format"))
        if xx(b)-xx(a) > 0.5: sl._tf(r.text_frame, lab, color=ink(fill))
        else: sl.text(xx(b)+0.3, cy, lab, w=0.6)
        sl.text(lx-0.1, cy, it["label"], w=2.3, align="r")
        if i < n-1:
            lvl = run_after(bars, items, i)
            sl.line(xx(lvl), cy+bh/2, xx(lvl), cy+slot-bh/2, w=0.5, dash=MSO_LINE_DASH_STYLE.DASH)

def run_after(bars, items, i):
    k = items[i].get("kind","delta"); v = items[i]["value"]; a,b = bars[i]
    if k in ("start","total"): return b
    return a if v<0 else b if False else (b if v>=0 else a)

# ======================= Mekko =======================
def mekko(sl, d, unit=False):
    cats = d["categories"]; series = d["series"]; n = len(cats)
    vals = [[s["values"][i] for s in series] for i in range(n)]
    widths = d.get("widths") or [sum(v) for v in vals]
    X,Y,W,Hh = sl.CHART; lx = X+0.7; pw = W-0.7-1.7; py = Y+0.45; y0 = Y+Hh-0.4; ph = y0-py
    tw = sum(widths); x = lx
    vmax = max(sum(v) for v in vals) if unit else None
    if not unit:
        for t in (0, 20, 40, 60, 80, 100): sl.text(lx-0.08, y0-ph*t/100, f"{t}%", w=0.6, align="r")
        sl.text(lx+pw+0.1, py-0.25, d.get("total_label","100% ="), w=1.5, align="l")
    else:
        for t in _ticks(vmax): sl.text(lx-0.08, y0-ph*t/vmax, fmt(t), w=0.6, align="r")
        sl.line(lx, py, lx, y0)
    sl.line(lx, y0, lx+pw, y0)
    lastsegs = []
    for i, c in enumerate(cats):
        w = pw*widths[i]/tw; tot = sum(vals[i]); up = 0; segs = []
        for j in range(len(series)-1, -1, -1):
            v = vals[i][j]; h = (ph*v/tot) if not unit else ph*v/vmax
            yt = y0-up-h; lab = (f"{v/tot*100:.0f}%" if not unit else fmt(v)) if d.get("labels","auto") else None
            sl.rect(x, yt, w, h, sl.col(j), lab if (w>0.45) else None, outline="#FFFFFF", lw=1)
            segs.append((x, yt, w, yt+h, j)); up += h
        ttop = y0-up
        sl.text(x+w/2, ttop-0.2, fmt(widths[i] if not unit else tot, d.get("format")), w=max(w,0.6))
        sl.text(x+w/2, y0+0.22, c, w=max(w,0.6))
        x += w; lastsegs = segs
    for (sx, yt, w, yb, j) in lastsegs:
        sl.text(sx+w+0.1, (yt+yb)/2, series[j]["name"], w=1.6, align="l")

def _ticks(vmax, n=5):
    step = 10**math.floor(math.log10(vmax/n));
    for m in (1,2,2.5,5,10):
        if vmax/(step*m) <= n: step*=m; break
    return [step*k for k in range(int(vmax//step)+1)]

# ======================= 条形 =======================
def bar_family(sl, d, mode="bar"):
    """mode: bar | sorted | stacked_bar | butterfly | dumbbell | football"""
    cats = list(d["categories"]); series = d["series"]; n = len(cats)
    X,Y,W,Hh = sl.CHART
    if mode == "sorted":
        order = sorted(range(n), key=lambda i: -series[0]["values"][i])
        cats = [cats[i] for i in order]; series = [dict(s, values=[s["values"][i] for i in order]) for s in series]
    slot = Hh/n; bh = slot*0.6; lx = X+2.4
    hl = set(d.get("highlight", []))
    if mode in ("bar","sorted"):
        v = series[0]["values"]; vmax = max(v); pw = W-2.4-1.0; sc = pw/vmax
        sl.line(lx, Y, lx, Y+Hh)
        for i,c in enumerate(cats):
            cy = Y+slot*(i+0.5); f = TC["accent1"] if (c in hl or not hl) else TC["accent5"]
            if not hl: f = sl.col(0)
            sl.rect(lx, cy-bh/2, v[i]*sc, bh, f); sl.text(lx+v[i]*sc+0.08, cy, fmt(v[i], d.get("format")), w=1, align="l")
            sl.text(lx-0.1, cy, c, w=2.3, align="r")
    elif mode == "stacked_bar":
        tots = [sum(s["values"][i] for s in series) for i in range(n)]; pw = W-2.4-1.0; sc = pw/max(tots)
        sl.line(lx, Y+0.35, lx, Y+Hh); slot = (Hh-0.35)/n; bh = slot*0.6
        for i,c in enumerate(cats):
            cy = Y+0.35+slot*(i+0.5); x = lx
            for j,s in enumerate(series):
                w = s["values"][i]*sc; sl.rect(x, cy-bh/2, w, bh, sl.col(j), fmt(s["values"][i])); x += w
            sl.text(x+0.08, cy, fmt(tots[i]), w=1, align="l"); sl.text(lx-0.1, cy, c, w=2.3, align="r")
        _legend(sl, [s["name"] for s in series], y=Y+0.08)
    elif mode == "butterfly":
        L, R = series[0], series[1]; mid = X+W/2; half = (W-2.6)/2; vmax = max(L["values"]+R["values"]); sc = (half-0.6)/vmax
        top = Y+0.4; slot = (Hh-0.4)/n; bh = slot*0.6
        sl.text(mid-1.3-half/2, Y+0.1, L["name"], w=half, bold=True); sl.text(mid+1.3+half/2, Y+0.1, R["name"], w=half, bold=True)
        for i,c in enumerate(cats):
            cy = top+slot*(i+0.5); lv, rv = L["values"][i], R["values"][i]
            sl.rect(mid-1.3-lv*sc, cy-bh/2, lv*sc, bh, sl.col(0)); sl.text(mid-1.3-lv*sc-0.1, cy, fmt(lv), w=0.8, align="r")
            sl.rect(mid+1.3, cy-bh/2, rv*sc, bh, sl.col(1)); sl.text(mid+1.3+rv*sc+0.1, cy, fmt(rv), w=0.8, align="l")
            sl.text(mid, cy, c, w=2.5)
        sl.line(mid-1.3, top, mid-1.3, Y+Hh); sl.line(mid+1.3, top, mid+1.3, Y+Hh)
    elif mode in ("dumbbell", "football"):
        allv = [v for s in series for v in s["values"]]; vmin = d.get("min", min(allv)*0.9 if mode=="dumbbell" else min(allv)); vmax = max(allv)
        vmin = d.get("min", vmin); pw = W-2.4-1.2; sc = pw/(vmax-vmin); xx = lambda v: lx+(v-vmin)*sc
        top = Y+0.45; slot = (Hh-0.45)/n; bh = slot*0.5
        for t in _ticks(vmax-vmin):
            sl.text(xx(vmin+t), Y+Hh+0.2, fmt(vmin+t), w=0.8); sl.line(xx(vmin+t), top, xx(vmin+t), Y+Hh, w=0.25, color="#C0C0C0")
        for i,c in enumerate(cats):
            cy = top+slot*(i+0.5); a, b = series[0]["values"][i], series[1]["values"][i]
            sl.text(lx-0.1, cy, c, w=2.3, align="r")
            if mode == "dumbbell":
                sl.line(xx(a), cy, xx(b), cy, w=2, color="#C0C0C0")
                for j,v in ((0,a),(1,b)): sl.rect(xx(v)-0.09, cy-0.09, 0.18, 0.18, sl.col(j), shape=MSO_SHAPE.OVAL)
                sl.text(xx(a)+(-0.35 if a<b else 0.35), cy, fmt(a), w=0.6); sl.text(xx(b)+(0.35 if a<b else -0.35), cy, fmt(b), w=0.6)
            else:   # 手册 football.jpg：区间条 + 两端数值
                sl.rect(xx(a), cy-bh/2, xx(b)-xx(a), bh, sl.col(0))
                sl.text(xx(a)-0.08, cy, fmt(a), w=0.8, align="r"); sl.text(xx(b)+0.08, cy, fmt(b), w=0.8, align="l")
        if "marker" in d:
            m = d["marker"]; sl.line(xx(m["value"]), top-0.1, xx(m["value"]), Y+Hh, dash=MSO_LINE_DASH_STYLE.DASH, color=TC["target"])
            sl.text(xx(m["value"]), top-0.25, m.get("label", fmt(m["value"])), w=2, color=TC["target"])
        _legend(sl, [s["name"] for s in series], y=Y+0.08)

# ======================= 折线 / 面积 / 组合 =======================
def line_area(sl, d, mode="line"):
    cats = d["categories"]; series = d["series"]; n = len(cats)
    X,Y,W,Hh = sl.CHART; lx = X+0.6; pw = W-0.6-1.8; py = Y+0.3; y0 = Y+Hh-0.4
    if mode == "area100":
        tots = [sum(s["values"][i] for s in series) for i in range(n)]; vmax = 100
        get = lambda j,i: series[j]["values"][i]/tots[i]*100
    else:
        get = lambda j,i: series[j]["values"][i]
        vmax = max(sum(s["values"][i] for s in series) for i in range(n)) if mode=="area" else max(max(s["values"]) for s in series)
    ticks = _ticks(vmax); vtop = ticks[-1] if ticks[-1]>=vmax else vmax
    yy = lambda v: y0-(v/vtop)*(y0-py); step = pw/(n-1) if mode!="line_col" else pw/n
    xs = [lx+step*i for i in range(n)]
    for t in ticks: sl.text(lx-0.08, yy(t), fmt(t)+("%" if mode=="area100" else ""), w=0.7, align="r")
    sl.line(lx, y0, lx+pw, y0); sl.line(lx, py, lx, y0)
    for i,c in enumerate(cats): sl.text(xs[i], y0+0.22, c, w=max(step,0.8), avoid=False)
    if d.get("band"):   # 目标区间带（[约定]，tc Gray）
        lo, hi = d["band"]; sl.rect(lx, yy(hi), pw, yy(lo)-yy(hi), TC["tc_gray"]); sl.text(lx+pw-0.1, yy(lo)-0.15, d.get("band_label","Target range"), w=2.0, align="r", size=sl.fs-2, color="#777777")
    if d.get("target") is not None:   # 目标线（手册 averageline.jpg 的数值线画法）
        t = d["target"]; sl.line(lx, yy(t), lx+pw, yy(t), color=TC["target"], dash=MSO_LINE_DASH_STYLE.DASH, w=1)
        sl.text(lx+0.1, yy(t)-0.17, d.get("target_label", f"Target {fmt(t)}"), w=2.0, align="l", color=TC["target"], size=sl.fs-2)
    if mode == "line":
        for j,s in enumerate(series):
            pts = [(xs[i], yy(get(j,i))) for i in range(n)]
            sl.poly(pts, outline=sl.col(j), lw=2.25, closed=False)
            for (x,y) in pts: sl.rect(x-0.05, y-0.05, 0.1, 0.1, sl.col(j), shape=MSO_SHAPE.OVAL)
            sl.text(pts[-1][0]+0.12, pts[-1][1], s["name"], w=1.6, align="l", color=sl.col(j))
            if d.get("label_last", True): sl.text(pts[-1][0], pts[-1][1]-0.22, fmt(get(j,n-1)), w=0.8)
    else:
        cum = [0]*n; ends = []
        for j in range(len(series)-1, -1, -1):
            lo = cum[:]; hi = [cum[i]+get(j,i) for i in range(n)]
            pts = [(xs[i], yy(hi[i])) for i in range(n)] + [(xs[i], yy(lo[i])) for i in range(n-1,-1,-1)]
            sl.poly(pts, fill=sl.col(j), outline="#FFFFFF", lw=0.75)
            ends.append(((yy(hi[-1])+yy(lo[-1]))/2, j)); cum = hi
        for y,j in ends: sl.text(xs[-1]+0.12, y, series[j]["name"], w=1.6, align="l")

def combo(sl, d):
    """组合图：柱（左轴）+ 折线（右轴）——手册 sample_combi / secondary_axis"""
    cats = d["categories"]; cs = d["columns"]; ls = d["line"]; n = len(cats); LC = TC["neg"] if sl.theme is THEMES["thinkcell_green"] else sl.col(3)
    X,Y,W,Hh = sl.CHART; lx = X+0.6; pw = W-1.6-0.6; py = Y+0.4; y0 = Y+Hh-0.4
    cmax = max(sum(s["values"][i] for s in cs) for i in range(n)); lt = _ticks(max(ls["values"])); lmax = max(lt[-1], max(ls["values"]))
    ct = _ticks(cmax); cmx = max(ct[-1], cmax)
    yc = lambda v: y0-v/cmx*(y0-py); yl = lambda v: y0-v/lmax*(y0-py)
    slot = pw/n; bw = slot*0.55
    sl.line(lx, y0, lx+pw, y0)
    for t in ct: sl.text(lx-0.08, yc(t), fmt(t), w=0.7, align="r")
    for t in lt: sl.text(lx+pw+0.08, yl(t), fmt(t)+ls.get("suffix",""), w=0.7, align="l", color=LC)
    sl.line(lx, py, lx, y0); sl.line(lx+pw, py, lx+pw, y0, color=LC)
    for i,c in enumerate(cats):
        cx = lx+slot*(i+0.5); up = 0
        for j in range(len(cs)-1, -1, -1):
            v = cs[j]["values"][i]; sl.rect(cx-bw/2, yc(up+v), bw, yc(up)-yc(up+v), sl.col(j), fmt(v)); up += v
        sl.text(cx, y0+0.22, c, w=slot)
    pts = [(lx+slot*(i+0.5), yl(v)) for i,v in enumerate(ls["values"])]
    sl.poly(pts, outline=LC, lw=2.25, closed=False)
    for i,(x,y) in enumerate(pts):
        sl.rect(x-0.06, y-0.06, 0.12, 0.12, LC, shape=MSO_SHAPE.OVAL)
        sl.text(x, y-0.22, fmt(ls["values"][i])+ls.get("suffix",""), w=0.9, color=LC)
    _legend(sl, [s["name"] for s in cs], y=Y+0.08)
    sl.text(X+W-0.2, Y+0.08, "— "+ls["name"]+" (right axis)", w=3, align="r", color=LC)

# ======================= 散点 / 气泡 =======================
def scatter(sl, d, bubble=False):
    pts = d["points"]; X,Y,W,Hh = sl.CHART; lx = X+0.8; pw = W-0.8-0.6; py = Y+0.3; y0 = Y+Hh-0.5
    xs = [p["x"] for p in pts]; ys = [p["y"] for p in pts]
    xt = _ticks(max(xs)*1.05); yt = _ticks(max(ys)*1.05); xm, ym = xt[-1], yt[-1]
    if xm < max(xs): xm = max(xs)*1.1
    if ym < max(ys): ym = max(ys)*1.1
    xx = lambda v: lx+v/xm*pw; yy = lambda v: y0-v/ym*(y0-py)
    sl.line(lx, y0, lx+pw, y0); sl.line(lx, py, lx, y0)
    for t in xt: sl.text(xx(t), y0+0.2, fmt(t), w=0.8)
    for t in yt: sl.text(lx-0.08, yy(t), fmt(t), w=0.7, align="r")
    sl.text(lx+pw, y0+0.5, d.get("x_title",""), w=3, align="r"); sl.text(lx, py-0.25, d.get("y_title",""), w=3, align="l")
    smax = max((p.get("size",1) for p in pts), default=1); groups = []
    for p in pts:
        g = p.get("group", 0); gi = groups.index(g) if g in groups else (groups.append(g) or len(groups)-1)
        r = (0.08 if not bubble else 0.08+0.55*math.sqrt(p.get("size",1)/smax))
        sl.rect(xx(p["x"])-r, yy(p["y"])-r, 2*r, 2*r, sl.col(gi), shape=MSO_SHAPE.OVAL, outline="#FFFFFF" if bubble else None, lw=0.75)
        if p.get("label"):
            sl.text(xx(p["x"])+r+0.05, yy(p["y"]), p["label"], w=1.6, align="l")
    if "partition" in d:   # 象限分割线（手册 partition.jpg 的简化）
        q = d["partition"]; sl.line(xx(q["x"]), py, xx(q["x"]), y0, dash=MSO_LINE_DASH_STYLE.DASH); sl.line(lx, yy(q["y"]), lx+pw, yy(q["y"]), dash=MSO_LINE_DASH_STYLE.DASH)
    if len(groups) > 1 and not isinstance(groups[0], int): _legend(sl, groups, y=Y+0.05)

# ======================= 饼 / 环 =======================
def pie(sl, d, doughnut=False):
    segs = d["segments"]; tot = sum(s["value"] for s in segs); X,Y,W,Hh = sl.CHART
    r = min(Hh, W)/2 - 0.45; cx, cy = X+W/2-1.0, Y+Hh/2
    ang = -90.0
    for j,s in enumerate(segs):
        sweep = s["value"]/tot*360
        sh = sl.rect(cx-r, cy-r, 2*r, 2*r, s.get("color") or sl.col(j), shape=MSO_SHAPE.BLOCK_ARC if doughnut else MSO_SHAPE.PIE, outline="#FFFFFF", lw=1.5)
        a1, a2 = ang % 360, (ang+sweep) % 360
        sh.adjustments[0] = a1*0.6; sh.adjustments[1] = a2*0.6   # python-pptx 以 1/100000 存值，角度单位为 1/60000 度
        if doughnut: sh.adjustments[2] = 0.45/2 if False else 0.18
        mid = math.radians(ang+sweep/2); pct = f"{s['value']/tot*100:.0f}%"
        rr = r*0.68 if not doughnut else r*0.82
        sl.text(cx+rr*math.cos(mid), cy+rr*math.sin(mid), pct, w=0.8, color=ink(s.get("color") or sl.col(j)))
        lr = r+0.25; lxp = cx+lr*math.cos(mid)
        sl.text(lxp, cy+lr*math.sin(mid), s["label"], w=2.0, align="l" if math.cos(mid)>=0 else "r")
        ang += sweep
    if doughnut and d.get("center"): sl.text(cx, cy, d["center"], w=2, bold=True, size=sl.fs+4)

# ======================= 甘特 / 时间线 =======================
def _d(s): return dt.date.fromisoformat(s)
def gantt(sl, d, timeline=False):
    """手册 gantt：左侧活动列、顶部日历刻度（月/周）、条形、菱形里程碑、阴影期、括号"""
    tasks = d["tasks"]; start, end = _d(d["start"]), _d(d["end"]); days = (end-start).days
    X,Y,W,Hh = sl.CHART; lx = X+3.0; pw = W-3.0-(1.6 if any("owner" in t for t in tasks) else 0.1); hy = Y+0.6
    xx = lambda s: lx + (_d(s)-start).days/days*pw
    n = len(tasks); rowh = min(0.42, (Hh-0.7-(0.6 if d.get("brackets") else 0))/n)
    # 日历刻度：月份 + 分隔线
    m = dt.date(start.year, start.month, 1)
    while m <= end:
        nm = dt.date(m.year+(m.month==12), m.month%12+1, 1)
        a, b = max(m,start), min(nm,end)
        if (b-a).days > 0:
            x1 = lx+(a-start).days/days*pw; x2 = lx+(b-start).days/days*pw
            sl.text((x1+x2)/2, Y+0.15, m.strftime("%b %Y") if m.month==1 or m==dt.date(start.year,start.month,1) else m.strftime("%b"), w=x2-x1, bold=True)
            sl.line(x1, Y, x1, hy+n*rowh, w=0.5, color="#C0C0C0")
            if d.get("weeks"):
                w0 = a
                while w0 < b:
                    if w0.weekday()==0:
                        xw = lx+(w0-start).days/days*pw; sl.text(xw+0.12, Y+0.43, str(w0.isocalendar()[1]), w=0.4, size=sl.fs-3, color="#777777")
                    w0 += dt.timedelta(days=1)
        m = nm
    sl.line(lx+pw, Y, lx+pw, hy+n*rowh, w=0.5, color="#C0C0C0")
    sl.text(X, Y+0.43, d.get("activity_header","Activity"), w=2.8, align="l", bold=True)
    if any("owner" in t for t in tasks): sl.text(lx+pw+0.1, Y+0.43, d.get("owner_header","Owner"), w=1.5, align="l", bold=True)
    sl.line(X, hy, lx+pw+(1.5 if any("owner" in t for t in tasks) else 0), hy, w=0.75)
    for sh in d.get("shades", []):   # 阴影期（手册 gantt-timeline-shade）
        sl.rect(xx(sh["start"]), hy, xx(sh["end"])-xx(sh["start"]), n*rowh, TC["tc_gray"])
        if sh.get("label"): sl.text((xx(sh["start"])+xx(sh["end"]))/2, hy+n*rowh+0.2, sh["label"], w=2, size=sl.fs-2)
    for i,t in enumerate(tasks):
        cy = hy+rowh*(i+0.5)
        if not t.get("header"): sl.text(X+(0.25 if t.get("indent") else 0), cy, t["name"], w=2.8, align="l", bold=t.get("bold",False))
        if i: sl.line(X, hy+rowh*i, lx+pw, hy+rowh*i, w=0.25, color="#D9D9D9")
        if t.get("header"):
            sl.rect(X, hy+rowh*i, lx+pw-X, rowh, TC["tc_gray"]); sl.text(X, cy, t["name"], w=2.8, align="l", bold=True)
            continue
        if "progress" in t and "start" in t:
            x1, x2 = xx(t["start"]), xx(t["end"]); p = t["progress"]
            sl.rect(x1, cy-rowh*0.3, x2-x1, rowh*0.6, TC["accent5"]); sl.rect(x1, cy-rowh*0.3, (x2-x1)*p, rowh*0.6, sl.col(0))
            sl.text(x2+0.05, cy, f"{p*100:.0f}%", w=0.6, align="l", size=sl.fs-2)
        elif "start" in t and "end" in t:
            c = sl.col(t.get("color",0)) if isinstance(t.get("color",0),int) else t["color"]
            sl.rect(xx(t["start"]), cy-rowh*0.3, xx(t["end"])-xx(t["start"]), rowh*0.6, c)
        for ms in ([t["milestone"]] if "milestone" in t else []):
            x = xx(ms); s = rowh*0.55
            sl.rect(x-s/2, cy-s/2, s, s, "#000000", shape=MSO_SHAPE.DIAMOND)
            if t.get("milestone_label"):
                right = x < lx+pw*0.75
                sl.text(x+s/2+0.05 if right else x-s/2-0.05, cy, t["milestone_label"], w=2, align="l" if right else "r", size=sl.fs-2)
        if "owner" in t: sl.text(lx+pw+0.1, cy, t["owner"], w=1.5, align="l")
    for b in d.get("brackets", []):   # 括号（手册 gantt-timeline-brackets）
        yb = hy+n*rowh+0.12; x1, x2 = xx(b["start"]), xx(b["end"])
        sl.line(x1, yb, x1, yb+0.12); sl.line(x2, yb, x2, yb+0.12); sl.line(x1, yb+0.12, x2, yb+0.12)
        sl.line((x1+x2)/2, yb+0.12, (x1+x2)/2, yb+0.22); sl.text((x1+x2)/2, yb+0.38, b["label"], w=3)
    if d.get("today"):
        x = xx(d["today"]); sl.line(x, Y+0.3, x, hy+n*rowh, color=TC["callout"], dash=MSO_LINE_DASH_STYLE.DASH, w=1)
        sl.text(x, hy+n*rowh+0.2, d.get("today_label","Today"), w=1.2, color=TC["callout"])

def timeline(sl, d):
    """里程碑时间线：一条横轴 + 上下交错的里程碑"""
    X,Y,W,Hh = sl.CHART; start, end = _d(d["start"]), _d(d["end"]); days = (end-start).days
    yax = Y+Hh/2; xx = lambda s: X+0.3+(_d(s)-start).days/days*(W-0.6)
    for ph in d.get("phases", []):
        sl.rect(xx(ph["start"]), yax-0.15, xx(ph["end"])-xx(ph["start"]), 0.3, sl.col(ph.get("color",0)), ph["name"], outline="#FFFFFF", lw=1.5, shape=MSO_SHAPE.CHEVRON if ph.get("arrow",True) else MSO_SHAPE.RECTANGLE)
    for k, m in enumerate(d["milestones"]):
        x = xx(m["date"]); up = k%2==0; y1 = yax-(0.2 if up else -0.2); y2 = yax+(-1.3 if up else 1.3)
        sl.line(x, y1, x, y2, w=0.5); sl.rect(x-0.1, y2-0.1, 0.2, 0.2, "#000000", shape=MSO_SHAPE.DIAMOND)
        sl.text(x, y2+(-0.45 if up else 0.45), _d(m["date"]).strftime("%d %b %Y")+"\n"+m["label"], w=2.0, h=0.6, size=sl.fs-1)

# ======================= 表格 + Harvey ball =======================
def harvey(sl, cx, cy, r, q, color="#000000"):
    """Harvey ball：外圈 + 按 0..4 刻度填充扇形（手册 harvey-balls-and-checkboxes）"""
    sl.rect(cx-r, cy-r, 2*r, 2*r, "#FFFFFF", outline=color, lw=1, shape=MSO_SHAPE.OVAL)
    if q >= 4: sl.rect(cx-r, cy-r, 2*r, 2*r, color, outline=color, lw=1, shape=MSO_SHAPE.OVAL)
    elif q > 0:
        p = sl.rect(cx-r, cy-r, 2*r, 2*r, color, shape=MSO_SHAPE.PIE); p.adjustments[0] = 270*0.6; p.adjustments[1] = ((270+q*90) % 360)*0.6

def table(sl, d):
    cols = d["columns"]; rows = d["rows"]; X,Y,W,Hh = sl.CHART
    c0 = d.get("first_col_width", 3.2); cw = (W-c0)/len(cols); rh = min(0.55, (Hh-0.5)/len(rows))
    for j,c in enumerate(cols): sl.text(X+c0+cw*(j+0.5), Y+0.25, c, w=cw, bold=True, wrap=True, h=0.5)
    sl.line(X, Y+0.5, X+W, Y+0.5, w=1)
    for i,r in enumerate(rows):
        cy = Y+0.5+rh*(i+0.5)
        if d.get("stripes", True) and i%2==0: sl.rect(X, cy-rh/2, W, rh, "#F2F2F2")
        sl.text(X+0.1, cy, r["name"], w=c0-0.1, align="l")
        for j,v in enumerate(r["values"]):
            x = X+c0+cw*(j+0.5)
            if isinstance(v, dict) and "harvey" in v: harvey(sl, x, cy, rh*0.32, v["harvey"])
            elif isinstance(v, dict) and "check" in v:
                sl.text(x, cy, "✔" if v["check"] else "✘", w=0.5, color=TC["good"] if v["check"] else TC["bad"], bold=True)
            else: sl.text(x, cy, str(v), w=cw)
    sl.line(X, Y+0.5+rh*len(rows), X+W, Y+0.5+rh*len(rows), w=1)
    if d.get("legend", True) and any(isinstance(v,dict) and "harvey" in v for r in rows for v in r["values"]):
        x = X
        for q,lab in enumerate(d.get("harvey_legend", ["None","Low","Medium","High","Full"])):
            harvey(sl, x+0.15, Y+Hh-0.2, 0.1, q); sl.text(x+0.3, Y+Hh-0.2, lab, w=1, align="l", size=sl.fs-2); x += 1.2

# ======================= 分发 =======================
RENDER = {
  "column": lambda s,d: column_family(s,d,"column"), "stacked": lambda s,d: column_family(s,d,"stacked"),
  "percent": lambda s,d: column_family(s,d,"percent"), "clustered": lambda s,d: column_family(s,d,"clustered"),
  "waterfall": waterfall, "waterfall_h": waterfall_h,
  "mekko_percent": lambda s,d: mekko(s,d,False), "mekko_unit": lambda s,d: mekko(s,d,True),
  "bar": lambda s,d: bar_family(s,d,"bar"), "bar_sorted": lambda s,d: bar_family(s,d,"sorted"),
  "bar_stacked": lambda s,d: bar_family(s,d,"stacked_bar"), "butterfly": lambda s,d: bar_family(s,d,"butterfly"),
  "dumbbell": lambda s,d: bar_family(s,d,"dumbbell"), "football": lambda s,d: bar_family(s,d,"football"),
  "line": lambda s,d: line_area(s,d,"line"), "area": lambda s,d: line_area(s,d,"area"), "area_percent": lambda s,d: line_area(s,d,"area100"),
  "combo": combo, "scatter": lambda s,d: scatter(s,d,False), "bubble": lambda s,d: scatter(s,d,True),
  "pie": lambda s,d: pie(s,d,False), "doughnut": lambda s,d: pie(s,d,True),
  "gantt": lambda s,d: gantt(s,d), "timeline": timeline, "table_harvey": table,
}
CATEGORY_TYPES = {"column","stacked","percent","clustered","waterfall","waterfall_subtotal","waterfall_percent"}

# ======================= 通用四区：强调区 + 备注说明区（适用于所有图表类型） =======================
class _CC(str): pass
def _anchor(sl, a, geo, cats):
    """解析锚点：{"category":名/序号}（柱形/瀑布类，指向柱顶）| {"anchor":标签文字,"nth"?} | {"at":[fx,fy]}（图表区比例坐标）"""
    X,Y,W,Hh = sl.CHART
    if "category" in a and geo and "x" in geo and cats:
        i = cats.index(a["category"]) if isinstance(a["category"], str) else a["category"]
        return geo["x"][i], geo["top"][i]
    if "anchor" in a: return sl.find(a["anchor"], a.get("nth", 0))[:2]
    if "at" in a: return X + a["at"][0]*W, Y + a["at"][1]*Hh
    raise ValueError(f"callout/highlight needs category|anchor|at: {a}")

def annotate(sl, spec, geo):
    cats = spec["data"].get("categories") or [it.get("label") for it in spec["data"].get("items", [])] if isinstance(spec.get("data"), dict) else None
    X,Y,W,Hh = sl.CHART
    hls = spec.get("highlight", []); hls = [hls] if isinstance(hls, dict) else hls
    for h in hls:   # 重点强调区：圆圈 / 框 / 箭头（tc Red）
        x, y = _anchor(sl, h, geo, cats); kind = h.get("shape", "circle"); w, hh = h.get("w", 1.0), h.get("h", 0.6)
        x += h.get("ox", 0); y += h.get("oy", 0)
        if "category" in h and geo and "w" in geo and kind == "circle" and "w" not in h:
            i = cats.index(h["category"]) if isinstance(h["category"], str) else h["category"]
            bw = geo["w"][i]; yt = geo["top"][i]-0.35; yb = (geo["bot"][i]+0.3) if geo.get("bot") and isinstance(geo["bot"][i], float) and geo.get("wf") else geo.get("base", Y+Hh)+0.45
            sl.rect(x-bw/2-0.2, yt, bw+0.4, yb-yt, None, outline=TC["callout"], lw=2, shape=MSO_SHAPE.OVAL); continue
        if kind == "circle": sl.rect(x-w/2, y-hh/2, w, hh, None, outline=TC["callout"], lw=2, shape=MSO_SHAPE.OVAL)
        elif kind == "box": sl.rect(x-w/2, y-hh/2, w, hh, None, outline=TC["callout"], lw=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE, dash=MSO_LINE_DASH_STYLE.DASH)
        elif kind == "arrow":
            fx, fy = x + h.get("dx", -0.9), y + h.get("dy", -0.6); sl.line(fx, fy, x, y, w=2.25, color=TC["callout"], tail="triangle")
    for c in spec.get("callouts", []):   # 备注说明区：引申气泡（白底 tc Red 细边圆角框 + 引线 + 锚点圆点）
        ax, ay = _anchor(sl, c, geo, cats); lw_ = lh_ = 0
        if "anchor" in c: _, _, lw_, lh_ = sl.find(c["anchor"], c.get("nth", 0), box=True)
        bw = c.get("w") or min(3.6, max(1.6, sl._est(c["text"], sl.fs-1)[0] + 0.35)); bh = c.get("h") or 0.32 + 0.24*c["text"].count("\n") + 0.12
        bx = min(max(ax + c.get("dx", 1.2) - bw/2, X), X+W-bw); by = min(max(ay + c.get("dy", -0.8) - bh/2, Y-0.1), Y+Hh-bh)
        if lw_:   # 锚点落在标签文字外框边缘（朝气泡方向），不压住数字
            bcx, bcy = bx+bw/2, by+bh/2
            ax2 = min(max(bcx, ax-lw_/2-0.05), ax+lw_/2+0.05); ay2 = min(max(bcy, ay-lh_/2-0.03), ay+lh_/2+0.03)
            if (ax2, ay2) != (ax, ay) and not (abs(bcx-ax) < lw_/2 and abs(bcy-ay) < lh_/2): ax, ay = ax2, ay2
        ex = min(max(ax, bx), bx+bw); ey = by+bh if ay > by+bh else (by if ay < by else ay)
        if ex == ax and ey == ay: ex = bx
        sl.line(ax, ay, ex, ey, w=0.75, color=TC["callout"])
        sl.rect(ax-0.045, ay-0.045, 0.09, 0.09, TC["callout"], shape=MSO_SHAPE.OVAL)
        b = sl.rect(bx, by, bw, bh, "#FFFFFF", outline=TC["callout"], lw=1, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        b.adjustments[0] = 0.15; sl._tf(b.text_frame, c["text"], color=TC["callout"], bold=True, size=sl.fs-1)

def render(prs, spec):
    if spec.get("type") in ("dashboard", "facet"):   # 多图拼版，见 tc_dash.py
        import tc_dash; return tc_dash.render(prs, spec)
    sl = Slide(prs, spec); sl.frame()
    geo = RENDER[spec["type"]](sl, spec["data"])
    if spec["type"] in CATEGORY_TYPES and spec.get("decorations"):
        cats = spec["data"].get("categories") or [it["label"] for it in spec["data"]["items"]]
        decorations(sl, geo, spec["decorations"], cats)
    annotate(sl, spec, geo if isinstance(geo, dict) else None)
    return sl

def new_prs():
    p = Presentation(); p.slide_width = Inches(SW); p.slide_height = Inches(SH); return p
