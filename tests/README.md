# 测试与验证

## 原有图表、推荐与校验回归

在技能根目录运行：

```bash
.venv/bin/python tests/run_tests.py
```

- `data/`：**20 份推荐数据集**，覆盖 CSV、TSV、Markdown 表、多空格对齐文本、JSON 和 Excel；包括时间序列、宽表、起止桥、小计利润表、构成、调研量表、同比、目标、区间、敏感性、甘特、漏斗、正负、Mekko、散点、两层分类长表、离群值、量与率，以及多个指标 × 多个团队的 `facet` 推荐。
- `specs/`：**16 份校验用例**，包括瀑布不平、比例问题、缺宽度/日期/目标、长度不一致、上下限颠倒、系列数不对、文本数字、类别过密、未知类型，以及错误 `dashboard` / `facet` 的结构问题。
- 脚本检查推荐首选/备选、意图偏好、草稿能否渲染、校验结论、61 个基础示例和 5 个拼版示例，并检查自动拦截和 `--force` 行为。它不递归扫描 `examples/ops-report/`；经营对账例子由下方 HTML 导出套件一起覆盖。

## SVG 与可编辑 HTML 回归

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

- `test_svg.py`：全部 72 个示例的 SVG 覆盖与只读性；检查几何、扇区与圆环、箭头方向、文字格式和安全转义，以及未知形状应明确报错。
- `test_html_document.py`：单文件封装、内联页面、用户文本/标题/文件名转义、只读导出和空文档保护；实际编辑交互由浏览器回归检查。
- `test_html_export.py`：CLI 的 HTML 单独/附加输出、多输入与 `slides` 封装、主题和输出参数约束；检查既有 PPTX / PNG 与源 JSON 保持不变，以及校验失败不写文件。

示例覆盖范围是 **72 个图表 spec**：`examples/` 的 61 个基础单图、`examples/dashboards/` 的 5 个拼版、`examples/ops-report/` 的 6 个经营对账示例。`examples/catalog.json` 是索引，不计入图表；原有分类 PPTX 的「72 页」指 61 个单图加 11 张分类页，与这里的 72 个 spec 不是同一统计。

HTML 只编辑显示文字，不重新计算数据，也不回写 JSON / PPTX / PNG。仅 HTML 导出和相应回归不需要 LibreOffice 或 Poppler；PNG 渲染仍需要两者。测试数量以运行结果为准，不把断言数和样例数混用。

## 可选浏览器回归

`check_html_browser.cjs` 使用 Node.js 和 Playwright 驱动浏览器，检查离线矢量显示、中文换行、纯文本粘贴、图形保持不变、下载重开、再次编辑与还原，以及小屏幕横向滚动。它是开发验证工具；生成和使用 HTML 本身不依赖 Node.js 或 Playwright。

需先让当前 Node.js 能加载 `playwright`，并具备可用的 Chromium 浏览器；也可用 `TC_BROWSER_PATH` 指向本机 Chrome 可执行文件。

```bash
# 默认在临时目录生成瀑布图和环形图 HTML，结束后清理临时文件
node tests/check_html_browser.cjs

# 使用现成 HTML 验证
node tests/check_html_browser.cjs gallery/editable-demo.html
```

可选环境变量：

| 变量 | 用途 |
| --- | --- |
| `TC_BROWSER_PATH` | Chrome 可执行文件路径；省略时使用 Playwright 的 Chromium |
| `TC_PYTHON` | 生成临时示例所用 Python；默认使用本技能的 `.venv/bin/python`，传入现成 HTML 时无需生成 |

## 浏览器目检

自动化交互通过后，仍需对实际交付文件目检。交付可编辑 HTML 前，在浏览器中完成：

1. 离线打开 HTML，检查图形、文字、颜色与 SVG 是否正常显示。
2. 开启编辑，分别修改标题、说明、数据标签、脚注和批注；检查长文字有无重叠或遮挡。
3. 保存 HTML，重新打开保存的文件，确认修改保留，且仍可继续编辑。
4. 确认修改显示数字不会被误认为已更新图形或源数据；检查原 JSON / PPTX / PNG 未被 HTML 编辑过程改写。

`gallery/editable-demo.html` 用于演示和人工验收；`gallery/index.html` 是原有 PNG 静态画廊。二者用途不同。
