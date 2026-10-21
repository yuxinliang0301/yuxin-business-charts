"""按分类生成 gallery/thinkcell-gallery.pptx（每类前一张分类页）+ 渲染 PNG 到 examples/"""
import json, os, sys, subprocess, tempfile, glob, shutil
sys.path.insert(0, os.path.dirname(__file__)); import tc_core, tc_more
R = os.path.join(os.path.dirname(__file__), "..")
cat = json.load(open(f"{R}/examples/catalog.json")); prs = tc_core.new_prs(); cur = None; pages = []
for c in cat:
    if c["category"] != cur:
        cur = c["category"]; sl = tc_core.Slide(prs, {})
        n = sum(1 for x in cat if x["category"]==cur)
        sl.text(0.8, 3.2, cur, w=11, h=1, align="l", size=40, bold=True); sl.text(0.8, 4.1, f"{n} 个示例", w=6, align="l", size=18, color="#777777")
        sl.rect(0.8, 2.5, 1.2, 0.08, tc_core.TC["accent1"]); pages.append(None)
    tc_core.render(prs, json.load(open(f"{R}/examples/{c['id']}.json"))); pages.append(c["id"])
out = f"{R}/gallery/thinkcell-gallery.pptx"; prs.save(out)
tmp = tempfile.mkdtemp(); subprocess.run(["soffice","--headless","--convert-to","pdf","--outdir",tmp,out], check=True, capture_output=True)
shutil.copy(glob.glob(tmp+"/*.pdf")[0], f"{R}/gallery/thinkcell-gallery.pdf")
subprocess.run(["pdftoppm","-png","-r","110",glob.glob(tmp+"/*.pdf")[0],tmp+"/p"], check=True)
for pid, p in zip(pages, sorted(glob.glob(tmp+"/p-*.png"))):
    if pid: shutil.move(p, f"{R}/examples/{pid}.png")
print(out, len(pages), "slides")
