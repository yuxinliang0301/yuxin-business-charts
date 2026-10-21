"""HTML CLI 的交付隔离与兼容性回归；无需 LibreOffice 或浏览器。"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "tc_render.py"
SPEC = ROOT / "examples" / "waterfall.json"


class HtmlExportCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def run_cli(self, *args):
        # 空 PATH 证明 HTML 导出不调用 soffice、pdftoppm 或其他外部命令。
        return subprocess.run(
            [sys.executable, str(CLI), *map(str, args)], cwd=self.folder,
            env=dict(os.environ, PATH=""), capture_output=True, text=True,
        )

    def test_html_only_preserves_existing_deliverables(self):
        pptx = self.folder / "report.pptx"
        png = self.folder / "report.png"
        pptx.write_bytes(b"existing PowerPoint")
        png.write_bytes(b"existing PNG")
        before_spec = SPEC.read_bytes()
        output = self.folder / "report.html"
        result = self.run_cli(SPEC, "--html", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.is_file())
        self.assertNotIn("PPTX:", result.stdout)
        self.assertEqual(pptx.read_bytes(), b"existing PowerPoint")
        self.assertEqual(png.read_bytes(), b"existing PNG")
        self.assertEqual(SPEC.read_bytes(), before_spec)
        self.assertEqual({p.name for p in self.folder.iterdir()},
                         {"report.pptx", "report.png", "report.html"})

    def test_adding_html_keeps_all_pptx_parts_identical(self):
        before = self.folder / "before.pptx"
        after = self.folder / "after.pptx"
        for args in ((SPEC, "-o", before),
                     (SPEC, "-o", after, "--html", self.folder / "after.html")):
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(before) as a, zipfile.ZipFile(after) as b:
            self.assertEqual(set(a.namelist()), set(b.namelist()))
            for name in a.namelist():
                self.assertEqual(a.read(name), b.read(name), name)

    def test_multiple_inputs_and_slides_wrapper(self):
        waterfall = json.loads(SPEC.read_text())
        wrapped = self.folder / "deck.json"
        wrapped.write_text(json.dumps({"slides": [waterfall, waterfall]}))
        output = self.folder / "deck.html"
        result = self.run_cli(wrapped, ROOT / "examples" / "doughnut.json",
                              "--html", output, "--theme", "mono_smoke")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_text().count("<svg "), 3)

    def test_rejects_ambiguous_outputs_before_writing(self):
        cases = [
            (SPEC,),
            (SPEC, "--html", "out.html", "--png", "previews"),
            (SPEC, "--html", "out.pptx"),
            (SPEC, "-o", "same.html", "--html", "same.html"),
        ]
        for args in cases:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(list(self.folder.iterdir()), [])

    def test_rejects_alias_of_input(self):
        output = self.folder / "alias.html"
        output.symlink_to(SPEC)
        before = SPEC.read_bytes()
        result = self.run_cli(SPEC, "--html", output)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(SPEC.read_bytes(), before)

    def test_validation_failure_writes_no_outputs(self):
        result = self.run_cli(ROOT / "tests" / "specs" / "v01_waterfall_unbalanced.json",
                              "--html", "bad.html", "-o", "bad.pptx")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("瀑布不平", result.stderr)
        self.assertEqual(list(self.folder.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
