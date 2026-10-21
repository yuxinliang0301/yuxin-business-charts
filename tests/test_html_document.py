"""验证独立 HTML 的封装、注入边界与只读导出约定。"""
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tc_core
from tc_html import export_html


class DocumentProbe(HTMLParser):
    def __init__(self, document):
        super().__init__()
        self.tags = []
        self.title = ""
        self.in_title = False
        self.feed(document)

    def handle_starttag(self, tag, attributes):
        self.tags.append((tag, dict(attributes)))
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, value):
        if self.in_title:
            self.title += value


class HtmlDocumentTests(unittest.TestCase):
    def make_presentation(self, text):
        presentation = tc_core.new_prs()
        slide = tc_core.Slide(presentation, {})
        slide.text(.5, .5, text, w=10, h=1, size=24, wrap=True)
        return presentation

    def test_text_title_and_filename_cannot_create_active_markup(self):
        title = '</title><script>alert("title")</script> {{SLIDES}} & 中文'
        text = '<img src=x onerror="alert(1)"> {{TITLE}} & 中文'
        presentation = self.make_presentation(text)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'test" data-injected="yes.html'
            self.assertEqual(export_html(presentation, path, title=title), path)
            document = path.read_text(encoding="utf-8")
        probe = DocumentProbe(document)
        self.assertEqual(probe.title, title)
        scripts = [attrs for tag, attrs in probe.tags if tag == "script"]
        self.assertEqual(len(scripts), 1)
        self.assertNotIn("src", scripts[0])
        self.assertFalse(any(tag == "img" for tag, _ in probe.tags))
        body = next(attrs for tag, attrs in probe.tags if tag == "body")
        self.assertEqual(body["data-filename"], path.name)
        self.assertNotIn("data-injected", body)
        self.assertIn('&lt;img src=x onerror="alert(1)"&gt;', document)

    def test_all_pages_are_inline_and_presentation_is_unchanged(self):
        presentation = self.make_presentation("第一页")
        tc_core.Slide(presentation, {}).text(.5, .5, "第二页", w=10, h=1)
        before = [slide._element.xml for slide in presentation.slides]
        with tempfile.TemporaryDirectory() as temp:
            path = export_html(presentation, Path(temp) / "report.html")
            probe = DocumentProbe(path.read_text(encoding="utf-8"))
        self.assertEqual(before, [slide._element.xml for slide in presentation.slides])
        self.assertEqual(sum(tag == "svg" for tag, _ in probe.tags), 2)
        self.assertEqual(sum(tag == "section" for tag, _ in probe.tags), 2)
        self.assertFalse(any(tag in {"link", "iframe", "image"} for tag, _ in probe.tags))
        edit_boxes = [attrs for _, attrs in probe.tags if attrs.get("class") == "tc-editable"]
        self.assertEqual(len(edit_boxes), 2)
        self.assertEqual(len({attrs["data-edit-id"] for attrs in edit_boxes}), 2)
        self.assertTrue(all(attrs["contenteditable"] == "false" for attrs in edit_boxes))

    def test_empty_document_does_not_overwrite_an_existing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "existing.html"
            path.write_text("existing document", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "至少需要一页"):
                export_html(tc_core.new_prs(), path)
            self.assertEqual(path.read_text(encoding="utf-8"), "existing document")


if __name__ == "__main__":
    unittest.main()
