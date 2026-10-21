"""将本技能的 PPT 形状树只读转为 SVG；不改动图表布局或 Presentation。

只解析引擎实际使用的 DrawingML 子集。未知形状或绘制属性会明确报错，
避免 HTML 看似导出成功却缺失图形。SVG 的一个用户单位对应一个 point。
"""
from html import escape
import math
import re

from pptx.oxml.ns import qn

EMU_PER_POINT = 12700
SVG_NS = "http://www.w3.org/2000/svg"
XHTML_NS = "http://www.w3.org/1999/xhtml"


class UnsupportedShapeError(ValueError):
    """输入包含当前 HTML 导出器不支持的形状或样式。"""


def _num(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("SVG coordinates must be finite")
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def _tag(element):
    return element.tag.rsplit("}", 1)[-1]


def _find(element, path):
    if element is None:
        return None
    node = element
    for part in path.split("/"):
        node = node.find(qn(part))
        if node is None:
            return None
    return node


def _attr(element, name, default=None):
    return element.get(name, default) if element is not None else default


def _color(fill, default="none"):
    if fill is None:
        return default
    children = list(fill)
    if len(children) != 1 or _tag(children[0]) not in {"srgbClr", "sysClr"}:
        raise UnsupportedShapeError("HTML export requires an explicit RGB color")
    color = children[0]
    value = color.get("val") if _tag(color) == "srgbClr" else color.get("lastClr")
    if not value or not re.fullmatch(r"[0-9a-fA-F]{6}", value):
        raise UnsupportedShapeError("Invalid RGB color in DrawingML")
    if len(color):
        raise UnsupportedShapeError("HTML export does not support color transforms")
    return "#" + value.upper()


def _fill(element, default="none"):
    if element is None:
        return default
    for child in element:
        tag = _tag(child)
        if tag == "noFill":
            return "none"
        if tag == "solidFill":
            return _color(child)
        if tag in {"gradFill", "blipFill", "pattFill", "grpFill"}:
            raise UnsupportedShapeError(f"Unsupported fill: {tag}")
    return default


def _adjustments(geometry):
    values = {}
    av_list = _find(geometry, "a:avLst")
    for node in av_list if av_list is not None else ():
        formula = node.get("fmla", "").split()
        if len(formula) != 2 or formula[0] != "val":
            raise UnsupportedShapeError("Only literal shape adjustments are supported")
        values[node.get("name")] = float(formula[1])
    return values


def _point(cx, cy, rx, ry, angle):
    angle = math.radians(angle)
    # DrawingML 的角度表示中心射线角，转换为椭圆参数角。
    param = math.atan2(rx * math.sin(angle), ry * math.cos(angle))
    return cx + rx * math.cos(param), cy + ry * math.sin(param)


def _arc(cx, cy, rx, ry, start, sweep):
    """输出一段/两段 SVG 弧；整圆必须拆成两段。"""
    if rx <= 0 or ry <= 0:
        return f"L {_num(cx)} {_num(cy)}"
    segments = 2 if abs(sweep) >= 359.999999 else 1
    result = []
    for i in range(1, segments + 1):
        x, y = _point(cx, cy, rx, ry, start + sweep * i / segments)
        result.append(f"A {_num(rx)} {_num(ry)} 0 {int(abs(sweep / segments) > 180)} {int(sweep >= 0)} {_num(x)} {_num(y)}")
    return " ".join(result)


def _preset(geometry, width, height):
    preset = geometry.get("prst")
    w, h = width, height
    a = _adjustments(geometry)
    if preset == "rect":
        return f'<rect width="{_num(w)}" height="{_num(h)}"/>'
    if preset == "roundRect":
        radius = min(w, h) * min(max(a.get("adj", 16667), 0), 50000) / 100000
        return f'<rect width="{_num(w)}" height="{_num(h)}" rx="{_num(radius)}"/>'
    if preset == "ellipse":
        return f'<ellipse cx="{_num(w / 2)}" cy="{_num(h / 2)}" rx="{_num(w / 2)}" ry="{_num(h / 2)}"/>'
    if preset == "diamond":
        points = [(w / 2, 0), (w, h / 2), (w / 2, h), (0, h / 2)]
    elif preset == "chevron":
        inset = min(w, max(0, min(w, h) * a.get("adj", 50000) / 100000))
        points = [(0, 0), (w - inset, 0), (w, h / 2), (w - inset, h), (0, h), (inset, h / 2)]
    elif preset == "line":
        return f'<line x1="0" y1="0" x2="{_num(w)}" y2="{_num(h)}"/>'
    elif preset in {"pie", "blockArc"}:
        start = a.get("adj1", 0 if preset == "pie" else 10800000) / 60000
        end = a.get("adj2", 16200000 if preset == "pie" else 0) / 60000
        sweep = (end - start) % 360 or 360
        cx, cy, rx, ry = w / 2, h / 2, w / 2, h / 2
        sx, sy = _point(cx, cy, rx, ry, start)
        path = f"M {_num(sx)} {_num(sy)} " + _arc(cx, cy, rx, ry, start, sweep)
        if preset == "pie":
            path += f" L {_num(cx)} {_num(cy)} Z"
        else:
            thickness = min(w, h) * min(max(a.get("adj3", 25000), 0), 50000) / 100000
            inner_x, inner_y = max(0, rx - thickness), max(0, ry - thickness)
            ix, iy = _point(cx, cy, inner_x, inner_y, end)
            path += f" L {_num(ix)} {_num(iy)} " + _arc(cx, cy, inner_x, inner_y, end, -sweep) + " Z"
        return f'<path d="{path}"/>'
    else:
        raise UnsupportedShapeError(f"Unsupported preset geometry: {preset}")
    return '<polygon points="' + " ".join(f"{_num(x)},{_num(y)}" for x, y in points) + '"/>'


def _custom(geometry, width, height):
    paths = _find(geometry, "a:pathLst")
    if paths is None:
        raise UnsupportedShapeError("Custom geometry has no paths")
    result = []
    for path in paths:
        # 当前自由形状以 EMU 写入路径坐标；有宽高时先缩放到形状矩形。
        pw, ph = float(path.get("w", width * EMU_PER_POINT)), float(path.get("h", height * EMU_PER_POINT))
        sx, sy = width / pw if pw else 0, height / ph if ph else 0
        commands = []
        for cmd in path:
            kind = _tag(cmd)
            if kind in {"moveTo", "lnTo", "quadBezTo", "cubicBezTo"}:
                letter, count = {"moveTo": ("M", 1), "lnTo": ("L", 1), "quadBezTo": ("Q", 2), "cubicBezTo": ("C", 3)}[kind]
                points = list(cmd)
                if len(points) != count:
                    raise UnsupportedShapeError(f"Malformed {kind} path command")
                coords = " ".join(f"{_num(float(p.get('x')) * sx)} {_num(float(p.get('y')) * sy)}" for p in points)
                commands.append(f"{letter} {coords}")
            elif kind == "close":
                commands.append("Z")
            else:
                raise UnsupportedShapeError(f"Unsupported custom path command: {kind}")
        overrides = ''
        fill = path.get("fill", "norm")
        if fill == "none":
            overrides += ' fill="none"'
        elif fill != "norm":
            raise UnsupportedShapeError(f"Unsupported custom path fill: {fill}")
        if path.get("stroke") in {"0", "false"}:
            overrides += ' stroke="none"'
        result.append(f'<path d="{" ".join(commands)}"{overrides}/>')
    return "".join(result)


def _marker(node, ident, color, start):
    kind = node.get("type", "none")
    if kind == "none":
        return "", ""
    sizes = {"sm": 2, "med": 3, "lg": 5}
    width = sizes.get(node.get("w", "med"), 3)
    length = sizes.get(node.get("len", "med"), 3)
    if kind in {"triangle", "stealth"}:
        path = 'M 0 0 L 10 5 L 0 10' + (' L 3 5' if kind == "stealth" else '') + ' Z'
        glyph = f'<path d="{path}" fill="{color}"/>'
    elif kind == "arrow":
        glyph = f'<path d="M 0 0 L 10 5 L 0 10" fill="none" stroke="{color}" stroke-width="1.5"/>'
    elif kind == "diamond":
        glyph = f'<path d="M 0 5 L 5 0 L 10 5 L 5 10 Z" fill="{color}"/>'
    elif kind == "oval":
        glyph = f'<ellipse cx="5" cy="5" rx="5" ry="5" fill="{color}"/>'
    else:
        raise UnsupportedShapeError(f"Unsupported line ending: {kind}")
    marker = f'<marker id="{ident}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="{length}" markerHeight="{width}" orient="auto-start-reverse" markerUnits="strokeWidth" overflow="visible">{glyph}</marker>'
    return marker, f' marker-{"start" if start else "end"}="url(#{ident})"'


def _paint(properties, ident):
    fill = _fill(properties)
    line = _find(properties, "a:ln")
    stroke = _fill(line)
    width = float(_attr(line, "w", 9525)) / EMU_PER_POINT
    attrs = f' fill="{fill}" stroke="{stroke}" stroke-width="{_num(width)}"'
    defs = []
    if line is not None:
        if line.get("cmpd", "sng") != "sng":
            raise UnsupportedShapeError("Compound line styles are unsupported")
        cap = {"flat": "butt", "rnd": "round", "sq": "square"}.get(line.get("cap", "flat"), "butt")
        attrs += f' stroke-linecap="{cap}"'
        dash = _find(line, "a:prstDash")
        patterns = {"solid": [], "dot": [1, 3], "dash": [4, 3], "lgDash": [8, 3], "dashDot": [4, 3, 1, 3], "lgDashDot": [8, 3, 1, 3], "lgDashDotDot": [8, 3, 1, 3, 1, 3], "sysDash": [3, 1], "sysDot": [1, 1], "sysDashDot": [3, 1, 1, 1], "sysDashDotDot": [3, 1, 1, 1, 1, 1]}
        if dash is not None:
            pattern = dash.get("val")
            if pattern not in patterns:
                raise UnsupportedShapeError(f"Unsupported dash pattern: {pattern}")
            if patterns[pattern]:
                attrs += ' stroke-dasharray="' + " ".join(_num(v * width) for v in patterns[pattern]) + '"'
        if _find(line, "a:custDash") is not None:
            raise UnsupportedShapeError("Custom line dash is unsupported")
        for tag, start in (("headEnd", True), ("tailEnd", False)):
            ending = _find(line, f"a:{tag}")
            if ending is not None:
                definition, ending_attr = _marker(ending, ident + "-" + tag, stroke, start)
                defs.append(definition)
                attrs += ending_attr
    return "".join(defs), attrs


def _font(properties, base=None):
    style = dict(base or {"font-family": '"Kaiti SC", "STKaiti", "KaiTi", "楷体", serif', "font-size": "14px", "font-weight": "400", "font-style": "normal", "color": "#000000", "text-decoration": "none"})
    if properties is None:
        return style
    latin = _find(properties, "a:latin")
    if latin is not None:
        family = latin.get("typeface", "Kaiti SC").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")
        style["font-family"] = f'"{family}", "STKaiti", "KaiTi", "楷体", serif'
    if properties.get("sz"):
        style["font-size"] = _num(float(properties.get("sz")) / 100) + "px"
    for key, name, yes, no in (("b", "font-weight", "700", "400"), ("i", "font-style", "italic", "normal")):
        if properties.get(key) is not None:
            style[name] = yes if properties.get(key) in {"1", "true"} else no
    if properties.get("u") is not None:
        style["text-decoration"] = "none" if properties.get("u") == "none" else "underline"
    color = _find(properties, "a:solidFill")
    if color is not None:
        style["color"] = _color(color)
    return style


def _css(style):
    return escape(";".join(f"{key}:{value}" for key, value in style.items()), quote=True)


def _text(text_body, width, height, ident):
    if text_body is None or not any(el.text for el in text_body.iter(qn("a:t"))):
        return ""
    body = _find(text_body, "a:bodyPr")
    if _attr(body, "vert", "horz") != "horz" or float(_attr(body, "rot", 0)):
        raise UnsupportedShapeError("Vertical or rotated text is unsupported")
    wrap = _attr(body, "wrap", "square") != "none"
    paragraphs = []
    first_font = None
    first_align = None
    for paragraph in text_body.findall(qn("a:p")):
        properties = _find(paragraph, "a:pPr")
        default = _font(_find(properties, "a:defRPr"))
        runs = []
        pfont = None
        for node in paragraph:
            kind = _tag(node)
            if kind in {"r", "fld"}:
                font = _font(_find(node, "a:rPr"), default)
                pfont = pfont or font
                content = escape("".join(el.text or "" for el in node.findall(qn("a:t"))), quote=False)
                runs.append(f'<span style="{_css(font)}">{content}</span>')
            elif kind == "br":
                runs.append("<br/>")
            elif kind not in {"pPr", "endParaRPr"}:
                raise UnsupportedShapeError(f"Unsupported text node: {kind}")
        pfont = pfont or default
        first_font = first_font or pfont
        align = {"l": "left", "ctr": "center", "r": "right", "just": "justify"}.get(_attr(properties, "algn", "l"))
        first_align = first_align or align
        if align is None:
            raise UnsupportedShapeError("Unsupported paragraph alignment")
        pstyle = dict(pfont, margin="0", padding="0", **{"text-align": align, "line-height": "1.15", "flex": "0 0 auto", "min-height": "1.15em"})
        paragraphs.append(f'<p style="{_css(pstyle)}">{"".join(runs) or "<br/>"}</p>')
    margins = [float(_attr(body, key, default)) / EMU_PER_POINT for key, default in (("tIns", 45720), ("rIns", 91440), ("bIns", 45720), ("lIns", 91440))]
    anchor = {"t": "flex-start", "ctr": "center", "b": "flex-end"}.get(_attr(body, "anchor", "t"))
    if anchor is None:
        raise UnsupportedShapeError("Unsupported vertical text anchor")
    style = dict(first_font or _font(None), width="100%", height="100%", display="flex", **{"box-sizing": "border-box", "text-align": first_align or "left", "line-height": "1.15", "flex-direction": "column", "justify-content": anchor, "white-space": "pre-wrap" if wrap else "pre", "overflow-wrap": "break-word" if wrap else "normal", "overflow": "visible", "padding": " ".join(_num(v) + "px" for v in margins)})
    return f'<foreignObject width="{_num(width)}" height="{_num(height)}" overflow="visible"><div xmlns="{XHTML_NS}" class="tc-editable" data-edit-id="{ident}" contenteditable="false" tabindex="-1" spellcheck="false" style="{_css(style)}">{"".join(paragraphs)}</div></foreignObject>'


def _shape(element, slide_index):
    kind = _tag(element)
    if kind not in {"sp", "cxnSp"}:
        raise UnsupportedShapeError(f"Unsupported shape element: {kind}")
    nonvisual = _find(element, "p:nvSpPr/p:cNvPr" if kind == "sp" else "p:nvCxnSpPr/p:cNvPr")
    shape_id = _attr(nonvisual, "id", "")
    if not re.fullmatch(r"[0-9]+", shape_id):
        raise UnsupportedShapeError("Shape has no valid numeric identifier")
    ident = f"s{slide_index}-shape{shape_id}"
    properties = _find(element, "p:spPr")
    if properties is None:
        raise UnsupportedShapeError(f"{ident}: missing shape properties")
    for node in properties:
        if _tag(node) in {"effectLst", "effectDag", "scene3d", "sp3d"} and len(node):
            raise UnsupportedShapeError(f"{ident}: unsupported effect {_tag(node)}")
    transform = _find(properties, "a:xfrm")
    offset, extent = _find(transform, "a:off"), _find(transform, "a:ext")
    if offset is None or extent is None:
        raise UnsupportedShapeError(f"{ident}: missing shape transform")
    x, y = float(offset.get("x")) / EMU_PER_POINT, float(offset.get("y")) / EMU_PER_POINT
    w, h = float(extent.get("cx")) / EMU_PER_POINT, float(extent.get("cy")) / EMU_PER_POINT
    transforms = [f"translate({_num(x)} {_num(y)})"]
    angle = float(transform.get("rot", 0)) / 60000
    if angle:
        transforms.append(f"rotate({_num(angle)} {_num(w / 2)} {_num(h / 2)})")
    flip_h, flip_v = transform.get("flipH") in {"1", "true"}, transform.get("flipV") in {"1", "true"}
    if flip_h or flip_v:
        transforms.extend([f"translate({_num(w if flip_h else 0)} {_num(h if flip_v else 0)})", f"scale({-1 if flip_h else 1} {-1 if flip_v else 1})"])
    geometry = _find(properties, "a:prstGeom")
    custom = _find(properties, "a:custGeom")
    if geometry is not None:
        drawing = _preset(geometry, w, h)
    elif custom is not None:
        drawing = _custom(custom, w, h)
    else:
        raise UnsupportedShapeError(f"{ident}: missing shape geometry")
    definitions, paint = _paint(properties, ident)
    text = _text(_find(element, "p:txBody"), w, h, ident)
    return (f'<defs>{definitions}</defs>' if definitions else '') + f'<g data-shape-id="{ident}" transform="{" ".join(transforms)}"><g{paint}>{drawing}</g>{text}</g>'


def presentation_to_svg(prs):
    """返回每页原生 SVG 字符串；只读取 XML，不访问会隐式写入的形状 API。"""
    width, height = prs.slide_width / EMU_PER_POINT, prs.slide_height / EMU_PER_POINT
    slides = []
    for index, slide in enumerate(prs.slides):
        tree = _find(slide._element, "p:cSld/p:spTree")
        if tree is None:
            raise UnsupportedShapeError(f"Slide {index + 1} has no shape tree")
        background = _find(slide._element, "p:cSld/p:bg")
        if _find(background, "p:bgRef") is not None:
            raise UnsupportedShapeError("Theme slide backgrounds are unsupported")
        color = _fill(_find(background, "p:bgPr"), "#FFFFFF")
        shapes = []
        for element in tree:
            if _tag(element) in {"nvGrpSpPr", "grpSpPr"}:
                continue
            shapes.append(_shape(element, index))
        slides.append(f'<svg xmlns="{SVG_NS}" viewBox="0 0 {_num(width)} {_num(height)}" width="100%" role="img" aria-label="Chart {index + 1}" style="display:block;height:auto;overflow:visible"><rect width="{_num(width)}" height="{_num(height)}" fill="{color}"/>{"".join(shapes)}</svg>')
    return slides
