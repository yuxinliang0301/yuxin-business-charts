"""独立 HTML 交付物：复用已布局的图形，并内联离线文字编辑器。"""
from html import escape
from pathlib import Path
import re

from tc_svg import presentation_to_svg


def export_html(prs, output_path, title="图表报告"):
    """只读取 Presentation，返回写入的 Path；不保存或修改 PPTX、PNG。"""
    destination = Path(output_path)
    slides = presentation_to_svg(prs)
    if not slides:
        raise ValueError("HTML 至少需要一页图表")
    template = (Path(__file__).resolve().parent.parent / "assets" / "html-editor.html").read_text(encoding="utf-8")
    sections = []
    for index, svg in enumerate(slides, 1):
        sections.append(
            f'<section class="tc-slide" aria-label="第 {index} 页">'
            f'<div class="tc-page-label"><span>第 {index} 页</span><span>{index} / {len(slides)}</span></div>'
            f'<div class="tc-slide-scroll"><div class="tc-slide-canvas">{svg}</div></div>'
            '</section>'
        )
    # 单次替换，避免用户标题中的占位符被再次解释成模板语法。
    values = {
        "TITLE": escape(str(title), quote=True),
        "FILENAME": escape(destination.name, quote=True),
        "SLIDES": "\n".join(sections),
        "COUNT": str(len(slides)),
    }
    document = re.sub(r"\{\{(TITLE|FILENAME|SLIDES|COUNT)\}\}", lambda match: values[match.group(1)], template)
    destination.write_text(document, encoding="utf-8")
    return destination
