# Yuxin 商业图表助手

> Local workflow: confirm palette, delivery format, chart count and per-chart plan before requesting data; agree on substantive transformations before applying them. `restrained_navy` is the recommended palette. It uses navy/gray semantic colors and plain panel headings. Eight additional single-page examples and a 24-page atlas live in `examples/restrained/`; historical galleries retain their original styling. See [structure recipes](references/professional-patterns.md).

[简体中文](README.md) · **English**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](scripts/requirements.txt) [![Chart types](https://img.shields.io/badge/Chart_types-55-00507D)](docs/CATALOG.md) [![Examples](https://img.shields.io/badge/Example_specs-81-6C89B4)](#gallery) [![Themes](https://img.shields.io/badge/Themes-9-18A98C)](docs/PALETTES.md) [![Output](https://img.shields.io/badge/Output-PPTX_%2B_PNG_%2B_HTML-E87722)](#quickstart) [![GitHub stars](https://img.shields.io/github/stars/ZeroxZhang/zerox-skills?style=flat&label=Suite%20stars)](https://github.com/ZeroxZhang/zerox-skills)

**Turn tabular data into consulting charts: recommend a chart, validate its data, and generate editable PowerPoint shapes, PNG previews, and HTML with offline text editing.**

The skill also documents focused table design: data bars, color scales, icon sets, sparklines, grouped rows, and exact numerical labels. It consumes supplied data and definitions; it does not initiate VOC analysis, strategy evaluation, or full report writing. See [management tables](references/management-tables.md), [Excel conditional formatting](references/excel-conditional-formatting.md), and [advanced comparison recipes](references/advanced-comparison-patterns.md).

These recipes do not add new CLI chart types. Native XLSX rules require a spreadsheet tool; native Word tables use a document tool. Static images, editable PowerPoint shapes, HTML styling, and data-responsive Excel rules are distinct outputs. Reuse choices already confirmed in the task.

This edition is customized by Yuxin, based on `zerox-thinkcell-charts` from the [zerox-skills](https://github.com/ZeroxZhang/zerox-skills) suite. It includes **55 single-chart types, 11 categories, 61 single-chart examples, and 9 color themes**, plus **dashboard / facet multi-panel layouts** (shared x-axis, segment labels, conditional coloring, circles and notes). A JSON specification can reproduce everything from waterfall bridges, Mekko charts, and stacked columns to project schedules, sensitivity charts, KPI cards, and ops dashboards. Another 5 dashboard examples and 6 ops review examples form the original **72 chart specs**; 8 local single-page examples and a 24-page atlas bring the current total to **81 spec files / 104 pages**. See the [atlas](gallery/chart-atlas.html).

Bars, lines, text, arrows, and annotations can be selected and edited individually in PowerPoint. The output consists of **editable shapes**, not native chart objects with embedded data sheets. To change the underlying data, update the specification and render again.

This is an independent open-source implementation, with no affiliation, authorization, or endorsement from think-cell. The name describes a visual influence; the renderer does not depend on the think-cell add-in.

[Quick start](#quickstart) · [Editable HTML](#editable-html) · [How to use & write prompts](#how-to-use) · [Capabilities](#capabilities) · [Multi-panel](#multipanel) · [Ops review recipes](#ops-report) · [Inputs and outputs](#data-contract) · [Themes](#themes) · [All examples](#gallery) · [CLI](#cli) · [Maintenance](#maintenance) · [Limitations](#limitations) · [License](#license)

<a id="quickstart"></a>
## Quick start

### 1. Install this edition and its Python dependencies

Clone this customized edition into the Codex skills directory (back up any existing installation first):

```bash
git clone https://github.com/yuxinliang0301/yuxin-business-charts.git ~/.codex/skills/yuxin-business-charts
```

Alternatively, download the repository ZIP and place its complete contents in `~/.codex/skills/yuxin-business-charts/`. Reload the session to discover the skill.

```bash
cd ~/.codex/skills/yuxin-business-charts
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
```

| Dependency | Purpose | When required |
| --- | --- | --- |
| Python 3.9+ | Run the scripts | Required |
| `python-pptx>=1.0` | Create PPTX shapes, text, and connectors | Required; included in requirements |
| `openpyxl>=3.1` | Read `.xlsx` / `.xlsm` tables | Excel recommendation input; included in requirements |
| LibreOffice (`soffice`) | Render PPTX to an intermediate PDF | PNG export and gallery rebuilds |
| Poppler (`pdftoppm`) | Convert PDF pages to PNG | PNG export and gallery rebuilds |
| Kaiti SC / 楷体-简 | Keep text layout consistent | Default font for all text; the rendering host must have it installed. PPTX does not embed fonts. |

LibreOffice and Poppler are unnecessary for PPTX-only or HTML-only output. Install the preview tools for your platform:

```bash
# macOS
brew install --cask libreoffice
brew install poppler

# Ubuntu / Debian
sudo apt install libreoffice-impress poppler-utils fonts-liberation
```

Both commands must be available on `PATH`. Text layout can differ between LibreOffice, PowerPoint, and font environments.

### 2. Render your first chart

Run these commands from the skill directory:

```bash
# Editable PPTX and PNG preview
.venv/bin/python scripts/tc_render.py examples/waterfall.json \
  -o out.pptx --png out_png/

# Combine multiple JSON files into a deck in the supplied order
.venv/bin/python scripts/tc_render.py examples/waterfall.json examples/mekko_percent.json \
  -o deck.pptx --png deck_png/ --theme consulting_navy
```

The first command produces `out.pptx` and `out_png/waterfall.png`. Edit individual shapes in PowerPoint, and use the PNG for visual inspection or documents. Ready-made outputs are also available: [full example PPTX](gallery/thinkcell-gallery.pptx), [PDF](gallery/thinkcell-gallery.pdf), and an [static PNG gallery](gallery/index.html) to open locally after downloading the repository.

### 3. Use the skill in an agent

Codex discovers `~/.codex/skills/yuxin-business-charts/SKILL.md`. Other hosts should import the complete directory using their supported installation method. Reload the session if its skill inventory still shows the old name.

Example request to an Agent Skills-compatible host:

> Use yuxin-business-charts to turn this revenue breakdown into a waterfall chart. Use consulting_navy, preserve the real data source, and deliver editable PPTX plus PNG.

<a id="editable-html"></a>
## Editable HTML: view offline, edit text, and save

`--html` creates a single HTML file that opens directly in a browser. Charts use **native SVG and editable text**, covering all 55 single-chart types and `dashboard` / `facet` layouts. Styles and editing scripts are embedded: no CDN or network service is required, and HTML generation needs neither LibreOffice nor Poppler.

```bash
# Write HTML only; do not generate or overwrite existing PPTX / PNG files
.venv/bin/python scripts/tc_render.py examples/waterfall.json --html report.html

# Request PPTX, PNG, and an independent HTML output together
.venv/bin/python scripts/tc_render.py examples/waterfall.json \
  -o report.pptx --png report_png/ --html report.html

# Multi-panel layouts can also be exported as HTML alone
.venv/bin/python scripts/tc_render.py examples/dashboards/dash_three_column.json \
  --html dashboard.html
```

To use it:

1. Download and open the HTML in a browser, then click the toolbar’s “编辑文字” (Edit text) button.
2. Click a title, explanation, data label, footnote, or annotation to change its displayed text.
3. Click “保存 HTML” (Save HTML), or press Ctrl / Cmd + S, to download `*-edited.html`. Reopen it to keep viewing or editing; share that one file.

The toolbar also provides font-size controls, text-box fitting, and overflow notices. “还原本次修改” (Reset this session) restores the content as it was when the current file opened. Small screens can scroll horizontally while editing. JavaScript is needed for editing and saving; charts remain viewable with scripts disabled.

Start with the [editable demo](gallery/editable-demo.html). If GitHub shows source code, download the file and open it in a browser. The existing [PNG example index](gallery/index.html) is a static image gallery for browsing chart types, distinct from the editable export.

HTML edits change text in that document only: **they do not recalculate values, resize chart marks, or write changes back to JSON, PPTX, or PNG**. Changing a label from `100` to `120`, for example, leaves the bar height unchanged. For data changes, update the source spec and render again. Longer text and browser / PowerPoint font differences can affect layout, so inspect the document before saving. Shape dragging, hover data tooltips, and linked-data updates are not provided.

Existing CLI commands do not generate HTML automatically. Deliver the confirmed formats only; editable PPTX plus page PNGs in Kaiti SC is a recommended option for chart tasks. HTML is optional. For image-only delivery, PPTX can remain a rendering intermediate. Rendering requires at least `-o` or `--html`; `--png` still requires `-o`.

<a id="capabilities"></a>
## Capabilities and workflow

| Capability | Behavior |
| --- | --- |
| Data profiling | Identifies dimensions, measures, time series, wide tables, nested categories, bridges, targets, ranges, market widths, and project dates |
| Chart recommendations | Combines data shape with Chinese or English intent to propose a preferred chart and up to two alternatives, including reasons, candidate conclusions, emphasis, and a draft spec |
| Validation | Covers all 55 types; checks structure, numeric types, list lengths, bridge arithmetic, proportions, dates, ranges, and readability, with suggested fixes and alternatives |
| PPTX generation | One 16:9 slide per spec; multiple files or a `slides` array can form one deck |
| Editable HTML | Native SVG and editable text in an offline, single-file document; export independently, edit text, save, and reopen for further editing |
| Chart presentation | Totals, segment labels, series labels, change rates, targets, dual axes, error bars, category gaps, and value/category axis breaks, depending on chart type |
| Annotations | Action titles, units, circles, boxes, arrows, callouts, footnotes, and sources; CAGR, total difference, level difference, and value-line decorations |
| Color themes | Nine semantic themes for positive, negative, target, emphasis, and background roles; custom series palettes are supported |
| Preview and reuse | PNG previews, categorized PPTX/PDF galleries, a static PNG index, editable HTML, individual JSON examples, and a generated chart catalog |

The workflow is **confirm palette, outputs and per-chart plan → request data → agree on required transformations → process and validate → render → inspect → deliver**.

- **No chart selected:** run `tc_advise.py`. The agent should interpret the business context and confirm the chart and intended conclusion before completing the draft. Rules cannot substitute for business judgment.
- **Chart already selected:** adapt its example spec and run `tc_validate.py`. Supply real missing data or agree on an alternative; do not invent values.
- **Chart, conclusion, or colors already specified:** retain those choices. For missing choices, offer professional palettes and a concrete chart plan, then await confirmation. See [drawing intake](references/drawing-intake.md).
- **After rendering:** inspect the requested outputs for labels, annotation placement, color semantics, and sources. Use previews for PPTX / PNG; when delivering HTML, also check enabling editing, changing text, saving, reopening, and continuing to edit.

The recommender temporarily fills some missing draft values with `0`, and the `source` must be completed. A draft is a starting point: placeholder values and inferred conclusions must not be treated as verified facts.

```bash
# Recommend a chart and write both a draft and a machine-readable report
.venv/bin/python scripts/tc_advise.py tests/data/03_ebit_bridge.csv \
  --intent "Explain the drivers of profit change" -o draft.json --json advice.json

# Validate one or more specs
.venv/bin/python scripts/tc_validate.py examples/waterfall.json examples/mekko_percent.json

# JSON validation output for automation
.venv/bin/python scripts/tc_validate.py examples/waterfall.json --json
```

Validation has three outcomes: ready, usable with issues, and insufficient data. `tc_validate.py` exits with `2` for fatal findings and `0` for warnings. The renderer validates automatically: warnings are reported and rendering continues; fatal findings stop rendering. `--force` only attempts to bypass fatal validation; it does not fix data or guarantee rendering. `--no-validate` skips this validation layer entirely.

<a id="data-contract"></a>
## Inputs, outputs, and JSON structure

### Raw tables and chart specifications are different inputs

| Entry point | Accepted input | Output |
| --- | --- | --- |
| `tc_advise.py` | CSV, TSV, semicolon-separated text, Markdown tables, text aligned with multiple spaces; active sheets in `.xlsx` / `.xlsm`; tabular JSON; `-` for text from standard input | A Chinese explanatory report, optional full report JSON, and an optional draft spec for the preferred chart |
| `tc_validate.py` | One chart object, `{"slides":[...]}`, or multiple spec files | Human-readable or JSON validation results |
| `tc_render.py` | A chart or multi-panel object, `{"slides":[...]}`, or multiple spec files | Requested PPTX, PNG per slide, or independent editable HTML; HTML-only output is supported |

Tabular JSON can be a list of records, an object mapping column names to arrays, a two-dimensional array with a header, or `{"columns":[...],"rows":[...]}`. Excel input uses saved formula-cache values and does not calculate formulas; recalculate and save in spreadsheet software first. Legacy binary `.xls` files are unsupported.

Save the following complete example as `revenue.json`. Its data is illustrative, as stated in `source`:

```json
{
  "id": "revenue",
  "type": "column",
  "title": "Revenue grew 25% from 2024 to 2025",
  "unit": "$M",
  "source": "Illustrative data",
  "theme": "consulting_navy",
  "data": {
    "categories": ["2024", "2025"],
    "series": [{"name": "Revenue", "values": [100, 125]}]
  },
  "decorations": [{"type": "total_diff", "from": 0, "to": 1}],
  "highlight": [{"category": "2025", "shape": "circle"}],
  "footnote": "Example only; replace with verified business data"
}
```

```bash
.venv/bin/python scripts/tc_render.py revenue.json -o revenue.pptx --png revenue_png/
```

| Field | Location and meaning |
| --- | --- |
| `type`, `data` | Core fields in each chart object; `data` varies by type, so `categories + series` is not universal |
| `id` | Chart identifier and PNG basename; falls back to the input JSON filename, not an automatically unique page number |
| `title`, `subtitle`, `unit` | Top-level headline, context, and units; delivery should include a clear action title and units |
| `source`, `footnote` | Top-level source and footnote; missing sources produce a reminder in the chart and should be replaced with real provenance |
| `theme`, `palette` | Top-level theme; `palette` accepts a preset name or a list of hex colors to override series colors |
| `font_size` | Top-level chart-label size, default 14 pt; titles and footnotes have their own sizes |
| `highlight`, `callouts` | Top-level emphasis and explanatory bubbles, positioned by labels or coordinates |
| `decorations` | Top-level calculated markers for supported chart types, listed below |
| `format`, `delta_format` | Usually inside `data`; supported renderers accept Python format strings such as `"{:.1f}"` and `"{:+.1f}pp"` |

For several charts, use `{"slides":[spec1,spec2]}`. Theme, title, and other settings belong inside each chart object; CLI `--theme` overrides the theme for the entire run. Give each slide a unique `id` when exporting PNGs, or duplicate filenames may overwrite one another. The CLI does not accept chart specs as a top-level JSON array.

### Data shapes at a glance

| Chart family | Main data shape | Runnable example |
| --- | --- | --- |
| Columns, bars, lines, areas | `categories` + `series[].values` | [stacked.json](examples/stacked.json) |
| Waterfalls | `items[]` with `label`, `value`, and `kind` for opening, contribution, and total | [waterfall.json](examples/waterfall.json) |
| Mekko | `categories` + `series`; percentage Mekko also requires market `widths` | [mekko_percent.json](examples/mekko_percent.json) |
| Scatter and bubble | `points[]` with `x`, `y`, and `size` for bubbles | [bubble.json](examples/bubble.json) |
| Pie and doughnut | `segments[]` with `label` and `value` | [doughnut.json](examples/doughnut.json) |
| Gantt and timeline | Date range plus `tasks` or `phases` / `milestones` | [gantt.json](examples/gantt.json) |
| Tables and heatmaps | Rows, columns, and values; special objects for Harvey balls and check marks | [table_harvey.json](examples/table_harvey.json), [heatmap.json](examples/heatmap.json) |
| Other consulting charts | Dedicated structures such as `cards`, `root`, `levels`, or `stages` | [Complete types and schemas](docs/CATALOG.md) |

### Decorations and slide layout

Slides use four zones: title and units, data labels, visual emphasis, and explanatory notes with sources. The default canvas is 16:9, approximately 13.333 × 7.5 inches, with flat fills, thin lines, and direct labels.

| Decoration | JSON example | Purpose |
| --- | --- | --- |
| CAGR | `{"type":"cagr","from":0,"to":4}` | Calculate growth from endpoint values and the number of category intervals |
| Total difference | `{"type":"total_diff","from":0,"to":4,"percent":false}` | Show absolute change across columns; relative change is the default |
| Level difference | `{"type":"diff","from":0,"to":2}` | Connect two heights and label relative or absolute change |
| Value line | `{"type":"value_line","value":100,"label":"Target"}` | Draw a reference line at a supplied value |

These `decorations` apply to `column`, `stacked`, `percent`, `clustered`, `waterfall`, `waterfall_subtotal`, and `waterfall_percent`. `from` / `to` accept zero-based indices or category names. CAGR uses the count of category intervals, so supply evenly spaced periods rather than treating irregular dates as annual periods.

`highlight` supports `circle`, `box`, and `arrow`; `callouts` adds a bubble and leader line. Position them using a supported chart's `category`, an existing text `anchor` (`nth` disambiguates repeated labels), or chart-relative `at: [x,y]` coordinates. See the [style specification](docs/STYLE_SPEC.md) and [highlight example](examples/stacked_highlight.json) for exact fields.

<a id="multipanel"></a>
## Multi-panel layouts (dashboard / facet)

Put several small charts on one slide, as in ops dashboards and weekly reviews. Full field reference: [docs/DASHBOARD.md](docs/DASHBOARD.md) (Chinese). Layout conventions: [docs/STYLE_SPEC.md](docs/STYLE_SPEC.md) §10.

### Two layout modes

| Type | When to use | How to lay out |
| --- | --- | --- |
| `dashboard` | Mix chart kinds on one page (area left, lines middle, YoY right), or use unequal panel sizes | Free `box: [x, y, w, h]` in content-area fractions, or `grid` + `cell` / `span` |
| `facet` | Repeat the same chart kind as rows = metrics × columns = countries / teams for side-by-side comparison | Write `rows`, `cols`, and `cells[row][col]`; use `null` for empty cells |

### Multi-panel features

| Feature | What it does |
| --- | --- |
| Shared x-axis | `x_labels` can be multi-layer (week / month / year); panels share the same tick marks |
| Segment labels | `segments` draws vertical dashed dividers with names (By Q / By M / year); style via `segment_style` |
| Conditional coloring | Paired-bar `rule`: green if ≥ time progress, red if below, gray for comparison period; page shows `▲ 60%` progress line |
| Annotations | Red circles (`circle`), red diagonal arrows (`arrow`), sign-colored "VS … ±pp" notes (`note`), trend channels (`channel`) |
| Page chrome | Yellow tag block before the title (`title_tag`); plain dark panel subtitles in the local default theme; shared `source` and `footnotes` |
| Panel kinds | Four today: `area_stack`, `lines`, `column_stack`, `bars_pair` (smooth lines, in-band "value (share%)", right-side series names) |
| Palette | Spec-local `ops_bright` (blue / orange / green / gray, [convention]); does not change the 9 themes |

When data has time + group + ≥2 measures, `tc_advise.py` recommends `facet` first and drafts a renderable spec. `tc_validate.py` checks multi-panel specs (kinds, lengths, segment bounds, series names, overlapping boxes, and more).

| | |
|---|---|
| ![](examples/dashboards/dash_three_column.png) | ![](examples/dashboards/facet_country_metric.png) |
| ![](examples/dashboards/facet_target_bars.png) | ![](examples/dashboards/dash_shared_axis_layers.png) |

```bash
.venv/bin/python scripts/make_dashboards.py
.venv/bin/python scripts/tc_render.py examples/dashboards/*.json -o dashboards.pptx --png examples/dashboards
```


<a id="ops-report"></a>
### Ops review page recipes (scorecard / volume–speed–efficiency / facet)

Three common one-page skeletons for weekly and monthly business reviews. Fields: [docs/DASHBOARD.md](docs/DASHBOARD.md) §7 (Chinese). Conclusion-page checklist and misread guards: [docs/STYLE_SPEC.md](docs/STYLE_SPEC.md) §11–§12. Intent → chart additions: [docs/CHART_SELECTION.md](docs/CHART_SELECTION.md) §5.


| Recipe | Use when | Example spec | Preview |
| --- | --- | --- | --- |
| Scorecard | Attainment vs time progress; red behind, green ahead | [scorecard.json](examples/ops-report/scorecard.json) | below |
| Volume–speed–efficiency | Absolute volume + YoY + efficiency move together? | [volume-speed-efficiency.json](examples/ops-report/volume-speed-efficiency.json) | below |
| Facet by cut | Same metrics, swap group / team columns | [facet-by-tier.json](examples/ops-report/facet-by-tier.json) | below |
| Peak vs Base | Peak-period lift vs normal baseline | [promo-vs-bau.json](examples/ops-report/promo-vs-bau.json) | [img](gallery/ops-report/promo-vs-bau.png) |
| CTG waterfall | Who explains the growth delta | [ctg-waterfall.json](examples/ops-report/ctg-waterfall.json) | [img](gallery/ops-report/ctg-waterfall.png) |
| Saturation scatter | Is spend hitting diminishing returns | [saturation-scatter.json](examples/ops-report/saturation-scatter.json) | [img](gallery/ops-report/saturation-scatter.png) |

All figures below use **illustrative data**, metric/group names and numbers are placeholders.

| | |
|---|---|
| ![Scorecard](gallery/ops-report/scorecard.png) | ![Volume–speed–efficiency](gallery/ops-report/volume-speed-efficiency.png) |
| ![Facet by group](gallery/ops-report/facet-by-tier.png) | ![Peak vs Base](gallery/ops-report/promo-vs-bau.png) |

```bash
.venv/bin/python scripts/tc_render.py examples/ops-report/*.json \
  -o ops-report.pptx --png gallery/ops-report/
```

<a id="how-to-use"></a>
## How to use and how to write prompts

This section is for **people who actually use the skill**: what to say to the agent, what data to provide, and what you get back. Agent-side steps live in [SKILL.md](SKILL.md) (Chinese).

### When to use it

- You have a table and want a consulting-style column / line / waterfall / Mekko / Gantt chart.
- You have several related small charts and want them on **one dashboard page** or a **facet grid**.
- You need an **ops review page** (scorecard, volume–speed–efficiency, facet-by-cut) → see [Ops review recipes](#ops-report).
- You already have a JSON spec and want validation first, or a re-render with a new theme.
- You need an offline HTML chart whose titles and explanatory text can be edited and saved in the browser.

### How to provide data

Any of these works:

1. Hand the agent a CSV / TSV / Excel file or a pasted table (or put it in the skill folder and name the path).
2. Give a chart JSON (see `examples/` or `examples/dashboards/`).
3. Attach a reference screenshot and say "match this layout, use my numbers" — **do not ask the agent to copy real business figures from the reference**.

Every chart needs a **source** (`source`). Without one, the footer shows a red reminder. Do not invent a source.

### If you have not chosen a chart type

Give the table and say what conclusion you want. The agent runs the recommender, offers 1 primary + 2 alternatives, and waits for your confirmation before rendering.

### If you have chosen a chart type

Name the type (waterfall, percent Mekko, target column, Gantt, …) and attach the data. The agent writes a spec from `docs/CATALOG.md`, validates, then renders. If data is incomplete it tells you what is missing — **it will not invent numbers**.

### If you want a multi-panel page

- "Make a one-page ops / weekly dashboard" → usually `dashboard` (mix area, lines, YoY).
- "Columns = countries (or teams), rows = metrics" → usually `facet`.
- Mention segments, time-progress lines, circles, or VS notes in the prompt when you need them (see examples below).

### Choosing a theme

- Single chart: name a theme, or say "your call" → default `restrained_navy`. See [docs/PALETTES.md](docs/PALETTES.md).
- Dashboard: say "use the ops blue / orange / green / gray set" → `ops_bright`.

### What you get back

Choose the formats required by the task; they are not all delivered by default.

- **Editable PPTX**: bars, lines, text, and arrows are PowerPoint shapes you can restyle; changing data means re-running the script.
- **PNG preview**: for checking overlaps and arrow placement.
- **Editable HTML**: optional and can be delivered alone when requested. Edit text in a browser, save, and reopen for further edits without writing back to other files.
- Optional: validation report and recommendation JSON.

### Copy-paste prompt examples

Swap paths and business words for yours.

**1. Single chart — let the skill recommend**

```text
Use yuxin-business-charts. Data is in ./revenue.csv.
I want to explain "how revenue mix changed over three years".
Recommend a chart and a conclusion first; wait for my OK before rendering.
Default theme is fine. Source: "Finance system · 2024".
Deliver editable PPTX + PNG.
```

**2. Named waterfall**

```text
Use yuxin-business-charts. Draw a waterfall that explains the profit bridge.
Data: start 120, price +18, volume +9, cost -11, opex -6, end 130 (Mn).
Conclusion-style title; positive = primary color, negative = wine red;
footnote source "Management report · Q3". PPTX + PNG.
```

**3. Multi-panel dashboard**

```text
Use yuxin-business-charts for a one-page ops dashboard (type: dashboard).
Left: stacked area of Metric A by team; middle-top: Metric C share lines with a red diagonal arrow;
middle-bottom: Metric B stacked area; right: smooth YoY lines.
Segment the x-axis with By Q / By M dashed lines; yellow tag "Region A" before the title;
palette ops_bright. Use my attached table (Team A/B/C is fine); do not copy real figures from any reference image.
Deliver PPTX + PNG.
```

**4. Facet grid**

```text
Use yuxin-business-charts for a facet chart (type: facet).
Columns = 6 groups; rows = Metric A / Metric A share / Metric D / Metric E;
shared y-axis within each row. Metric A = stacked area with "value (share%)" labels; bottom two rows = lines.
Data: ./by_group.csv. Source: "Illustrative data". PPTX + PNG.
```

**5. Validate first, then render**

```text
Use yuxin-business-charts. I edited a waterfall spec at ./my_bridge.json.
Run validation first and tell me in plain language whether it can render and what is missing.
Only render after status is "能做" / OK, or after I accept a workaround.
```

**6. Re-theme without changing data**

```text
Re-render ./draft.json with theme banking_navy_gold.
Do not change chart type, data, or conclusion. Deliver new PPTX + PNG.
```

**7. HTML only, with offline text editing**

```text
Use yuxin-business-charts to export ./draft.json as editable HTML.
Create only ./report.html; do not modify the existing PPTX or PNG files.
I need to edit titles, data labels, and notes in the browser, save, and reopen for further edits.
Keep chart types and source data unchanged. Check editing, saving, and reopening before delivery.
```

**8. Keep the original outputs and add HTML**

```text
Use yuxin-business-charts with ./draft.json and deliver three outputs:
editable PPTX, PNG previews, and editable HTML.
The HTML must open offline, allow text editing and saving, and remain editable when reopened.
Keep the existing PPTX / PNG generation unchanged; HTML is an additional independent file.
```

<a id="themes"></a>
## Eight color themes

Themes change semantic colors. The local default also simplifies dashboard headings and notes while preserving chart geometry. The default is `restrained_navy`; CLI `--theme` takes precedence over each slide's `theme`. A slide with an explicit `palette` still retains its custom series palette.

| Name | Visual character | Typical use |
| --- | --- | --- |
| `consulting_navy` | Navy, burgundy for negatives, gold/orange/green accents | Strategy and business reviews |
| `thinkcell_green` | Classic green with dark and light gray | Green-and-gray consulting charts |
| `thinkcell_blue` | Blue scale, teal, and bright red | Product, technology, and financial analysis |
| `teal_modern` | Teal, charcoal, and red emphasis | Clean, modern reports |
| `banking_navy_gold` | Deep navy and gold | Financing, valuation, and M&A |
| `office` | Preset Office-style series colors | Familiar Office presentation styling |
| `mono_smoke` | Shades of blue-gray | Restrained multi-series charts |
| `gray_accent` | Grayscale with red emphasis | A single focused message |

![Eight themes rendered by this project](gallery/palettes/all-palettes.png)

```bash
.venv/bin/python scripts/tc_render.py --list-themes
.venv/bin/python scripts/tc_render.py examples/waterfall.json \
  -o teal.pptx --png teal_png/ --theme teal_modern
```

See [PALETTES.md](docs/PALETTES.md) and [COLORS.md](docs/COLORS.md) for color values, semantic roles, and provenance. Theme names describe visual directions and do not imply brand certification.

<a id="gallery"></a>
## All chart examples

The gallery below contains all **61 PNGs generated by this project**, covering all **55 `type` values**. Some types have extra examples for axis breaks, differences, emphasis, or signed labels; these variants do not count as additional chart types. Click an image for the original PNG, or its JSON link for the complete reusable configuration. All example data is illustrative.

[Columns](#gallery-columns) · [Waterfalls](#gallery-waterfalls) · [Mekko and proportional charts](#gallery-mekko) · [Bars](#gallery-bars) · [Comparisons](#gallery-comparisons) · [Lines and areas](#gallery-trends) · [Scatter and bubble charts](#gallery-scatter) · [Pie and doughnut charts](#gallery-shares) · [Gantt charts and timelines](#gallery-schedules) · [Assessment tables](#gallery-tables) · [Consulting charts](#gallery-consulting)

<a id="gallery-columns"></a>
### Columns · 13 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Column</strong><br>
<a href="examples/column.png"><img src="examples/column.png" alt="Column — Compare a single metric across periods or categories." width="100%"></a><br>
Compare a single metric across periods or categories.<br>
<code>column</code> · <a href="examples/column.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Stacked columns + CAGR</strong><br>
<a href="examples/stacked.png"><img src="examples/stacked.png" alt="Stacked columns + CAGR — Show total growth and the contribution of each segment." width="100%"></a><br>
Show total growth and the contribution of each segment.<br>
<code>stacked</code> · <a href="examples/stacked.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>100% stacked columns</strong><br>
<a href="examples/percent.png"><img src="examples/percent.png" alt="100% stacked columns — Compare composition across periods." width="100%"></a><br>
Compare composition across periods.<br>
<code>percent</code> · <a href="examples/percent.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Clustered columns</strong><br>
<a href="examples/clustered.png"><img src="examples/clustered.png" alt="Clustered columns — Compare a small number of series across categories." width="100%"></a><br>
Compare a small number of series across categories.<br>
<code>clustered</code> · <a href="examples/clustered.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Value-axis break</strong><br>
<a href="examples/column_axis_break.png"><img src="examples/column_axis_break.png" alt="Value-axis break — Keep smaller columns readable alongside an exceptionally large value." width="100%"></a><br>
Keep smaller columns readable alongside an exceptionally large value.<br>
<code>column</code> · <a href="examples/column_axis_break.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Stacked columns + difference arrow</strong><br>
<a href="examples/stacked_diff.png"><img src="examples/stacked_diff.png" alt="Stacked columns + difference arrow — Emphasize the difference between two totals." width="100%"></a><br>
Emphasize the difference between two totals.<br>
<code>stacked</code> · <a href="examples/stacked_diff.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Stacked columns + highlight</strong><br>
<a href="examples/stacked_highlight.png"><img src="examples/stacked_highlight.png" alt="Stacked columns + highlight — Focus attention on one column with an explanatory callout." width="100%"></a><br>
Focus attention on one column with an explanatory callout.<br>
<code>stacked</code> · <a href="examples/stacked_highlight.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Stacked clustered columns</strong><br>
<a href="examples/stacked_clustered.png"><img src="examples/stacked_clustered.png" alt="Stacked clustered columns — Compare multiple stacks per category, such as plan versus actual." width="100%"></a><br>
Compare multiple stacks per category, such as plan versus actual.<br>
<code>stacked_clustered</code> · <a href="examples/stacked_clustered.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Columns with error bars</strong><br>
<a href="examples/column_error.png"><img src="examples/column_error.png" alt="Columns with error bars — Compare means with supplied uncertainty or variability ranges." width="100%"></a><br>
Compare means with supplied uncertainty or variability ranges.<br>
<code>column_error</code> · <a href="examples/column_error.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Grouped category columns</strong><br>
<a href="examples/column_grouped.png"><img src="examples/column_grouped.png" alt="Grouped category columns — Separate nested categories, such as quarters within years." width="100%"></a><br>
Separate nested categories, such as quarters within years.<br>
<code>column_grouped</code> · <a href="examples/column_grouped.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Actual versus target columns</strong><br>
<a href="examples/column_target.png"><img src="examples/column_target.png" alt="Actual versus target columns — Show target markers and attainment for each category." width="100%"></a><br>
Show target markers and attainment for each category.<br>
<code>column_target</code> · <a href="examples/column_target.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Category-axis break</strong><br>
<a href="examples/column_xbreak.png"><img src="examples/column_xbreak.png" alt="Category-axis break — Mark a discontinuity, such as omitted years." width="100%"></a><br>
Mark a discontinuity, such as omitted years.<br>
<code>column_xbreak</code> · <a href="examples/column_xbreak.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Stacked columns + value line</strong><br>
<a href="examples/stacked_value_line.png"><img src="examples/stacked_value_line.png" alt="Stacked columns + value line — Add a supplied reference or average value across columns." width="100%"></a><br>
Add a supplied reference or average value across columns.<br>
<code>stacked</code> · <a href="examples/stacked_value_line.json">JSON</a>
</td>
<td width="50%"></td>
</tr>
</table>

<a id="gallery-waterfalls"></a>
### Waterfalls · 7 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Waterfall bridge</strong><br>
<a href="examples/waterfall.png"><img src="examples/waterfall.png" alt="Waterfall bridge — Explain the drivers between an opening and closing total." width="100%"></a><br>
Explain the drivers between an opening and closing total.<br>
<code>waterfall</code> · <a href="examples/waterfall.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Waterfall with signed labels</strong><br>
<a href="examples/waterfall_signed.png"><img src="examples/waterfall_signed.png" alt="Waterfall with signed labels — Make the direction of each contribution explicit." width="100%"></a><br>
Make the direction of each contribution explicit.<br>
<code>waterfall</code> · <a href="examples/waterfall_signed.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Horizontal waterfall</strong><br>
<a href="examples/waterfall_h.png"><img src="examples/waterfall_h.png" alt="Horizontal waterfall — Build down a total, with space for long item labels." width="100%"></a><br>
Build down a total, with space for long item labels.<br>
<code>waterfall_h</code> · <a href="examples/waterfall_h.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Stacked waterfall</strong><br>
<a href="examples/waterfall_stacked.png"><img src="examples/waterfall_stacked.png" alt="Stacked waterfall — Split each bridge contribution by product or region." width="100%"></a><br>
Split each bridge contribution by product or region.<br>
<code>waterfall_stacked</code> · <a href="examples/waterfall_stacked.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Waterfall with subtotals</strong><br>
<a href="examples/waterfall_subtotal.png"><img src="examples/waterfall_subtotal.png" alt="Waterfall with subtotals — Build a multistage profit bridge with calculated subtotals." width="100%"></a><br>
Build a multistage profit bridge with calculated subtotals.<br>
<code>waterfall_subtotal</code> · <a href="examples/waterfall_subtotal.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Percentage waterfall</strong><br>
<a href="examples/waterfall_percent.png"><img src="examples/waterfall_percent.png" alt="Percentage waterfall — Explain margin changes in percentage points." width="100%"></a><br>
Explain margin changes in percentage points.<br>
<code>waterfall_percent</code> · <a href="examples/waterfall_percent.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Waterfall ending below zero</strong><br>
<a href="examples/waterfall_negative_end.png"><img src="examples/waterfall_negative_end.png" alt="Waterfall ending below zero — Show a bridge whose closing total is negative." width="100%"></a><br>
Show a bridge whose closing total is negative.<br>
<code>waterfall</code> · <a href="examples/waterfall_negative_end.json">JSON</a>
</td>
<td width="50%"></td>
</tr>
</table>

<a id="gallery-mekko"></a>
### Mekko and proportional charts · 4 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Percentage Mekko</strong><br>
<a href="examples/mekko_percent.png"><img src="examples/mekko_percent.png" alt="Percentage Mekko — Combine market size as width with segment share as height." width="100%"></a><br>
Combine market size as width with segment share as height.<br>
<code>mekko_percent</code> · <a href="examples/mekko_percent.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Unit Mekko</strong><br>
<a href="examples/mekko_unit.png"><img src="examples/mekko_unit.png" alt="Unit Mekko — Compare variable-width columns with absolute segment values." width="100%"></a><br>
Compare variable-width columns with absolute segment values.<br>
<code>mekko_unit</code> · <a href="examples/mekko_unit.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Variwide columns</strong><br>
<a href="examples/variwide.png"><img src="examples/variwide.png" alt="Variwide columns — Encode size by width and a separate metric by height." width="100%"></a><br>
Encode size by width and a separate metric by height.<br>
<code>variwide</code> · <a href="examples/variwide.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Proportional area</strong><br>
<a href="examples/proportional_area.png"><img src="examples/proportional_area.png" alt="Proportional area — Compare magnitudes using proportional areas." width="100%"></a><br>
Compare magnitudes using proportional areas.<br>
<code>proportional_area</code> · <a href="examples/proportional_area.json">JSON</a>
</td>
</tr>
</table>

<a id="gallery-bars"></a>
### Bars · 6 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Horizontal bars</strong><br>
<a href="examples/bar.png"><img src="examples/bar.png" alt="Horizontal bars — Compare categories with longer names." width="100%"></a><br>
Compare categories with longer names.<br>
<code>bar</code> · <a href="examples/bar.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Sorted bars</strong><br>
<a href="examples/bar_sorted.png"><img src="examples/bar_sorted.png" alt="Sorted bars — Rank categories in descending order and highlight selected items." width="100%"></a><br>
Rank categories in descending order and highlight selected items.<br>
<code>bar_sorted</code> · <a href="examples/bar_sorted.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Stacked bars</strong><br>
<a href="examples/bar_stacked.png"><img src="examples/bar_stacked.png" alt="Stacked bars — Compare totals and composition with long category labels." width="100%"></a><br>
Compare totals and composition with long category labels.<br>
<code>bar_stacked</code> · <a href="examples/bar_stacked.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Year-over-year bars</strong><br>
<a href="examples/bar_yoy.png"><img src="examples/bar_yoy.png" alt="Year-over-year bars — Compare two periods with a separate change-rate column." width="100%"></a><br>
Compare two periods with a separate change-rate column.<br>
<code>bar_yoy</code> · <a href="examples/bar_yoy.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Diverging bars</strong><br>
<a href="examples/bar_diverging.png"><img src="examples/bar_diverging.png" alt="Diverging bars — Show positive and negative changes around a zero baseline." width="100%"></a><br>
Show positive and negative changes around a zero baseline.<br>
<code>bar_diverging</code> · <a href="examples/bar_diverging.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>100% stacked bars</strong><br>
<a href="examples/bar_percent.png"><img src="examples/bar_percent.png" alt="100% stacked bars — Compare survey responses or composition across categories." width="100%"></a><br>
Compare survey responses or composition across categories.<br>
<code>bar_percent</code> · <a href="examples/bar_percent.json">JSON</a>
</td>
</tr>
</table>

<a id="gallery-comparisons"></a>
### Comparisons · 3 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Butterfly chart</strong><br>
<a href="examples/butterfly.png"><img src="examples/butterfly.png" alt="Butterfly chart — Place two populations or periods on opposite sides." width="100%"></a><br>
Place two populations or periods on opposite sides.<br>
<code>butterfly</code> · <a href="examples/butterfly.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Dumbbell chart</strong><br>
<a href="examples/dumbbell.png"><img src="examples/dumbbell.png" alt="Dumbbell chart — Compare two observations for each category." width="100%"></a><br>
Compare two observations for each category.<br>
<code>dumbbell</code> · <a href="examples/dumbbell.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Football field chart</strong><br>
<a href="examples/football.png"><img src="examples/football.png" alt="Football field chart — Compare valuation ranges with an optional reference marker." width="100%"></a><br>
Compare valuation ranges with an optional reference marker.<br>
<code>football</code> · <a href="examples/football.json">JSON</a>
</td>
<td width="50%"></td>
</tr>
</table>

<a id="gallery-trends"></a>
### Lines and areas · 7 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Line chart</strong><br>
<a href="examples/line.png"><img src="examples/line.png" alt="Line chart — Show a trend across ordered periods." width="100%"></a><br>
Show a trend across ordered periods.<br>
<code>line</code> · <a href="examples/line.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Stacked area</strong><br>
<a href="examples/area.png"><img src="examples/area.png" alt="Stacked area — Show a total trend and its composition." width="100%"></a><br>
Show a total trend and its composition.<br>
<code>area</code> · <a href="examples/area.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>100% stacked area</strong><br>
<a href="examples/area_percent.png"><img src="examples/area_percent.png" alt="100% stacked area — Show how shares evolve over time." width="100%"></a><br>
Show how shares evolve over time.<br>
<code>area_percent</code> · <a href="examples/area_percent.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Dual-axis combination</strong><br>
<a href="examples/combo.png"><img src="examples/combo.png" alt="Dual-axis combination — Compare a quantity and a rate on separate axes." width="100%"></a><br>
Compare a quantity and a rate on separate axes.<br>
<code>combo</code> · <a href="examples/combo.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Line with target</strong><br>
<a href="examples/line_target.png"><img src="examples/line_target.png" alt="Line with target — Compare a trend against a target line or band." width="100%"></a><br>
Compare a trend against a target line or band.<br>
<code>line_target</code> · <a href="examples/line_target.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Slope chart</strong><br>
<a href="examples/slope.png"><img src="examples/slope.png" alt="Slope chart — Show change between two periods for several categories." width="100%"></a><br>
Show change between two periods for several categories.<br>
<code>slope</code> · <a href="examples/slope.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Small multiples</strong><br>
<a href="examples/small_multiples.png"><img src="examples/small_multiples.png" alt="Small multiples — Compare several panels on a shared scale." width="100%"></a><br>
Compare several panels on a shared scale.<br>
<code>small_multiples</code> · <a href="examples/small_multiples.json">JSON</a>
</td>
<td width="50%"></td>
</tr>
</table>

<a id="gallery-scatter"></a>
### Scatter and bubble charts · 2 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Scatter plot</strong><br>
<a href="examples/scatter.png"><img src="examples/scatter.png" alt="Scatter plot — Explore the relationship between two metrics and optional quadrants." width="100%"></a><br>
Explore the relationship between two metrics and optional quadrants.<br>
<code>scatter</code> · <a href="examples/scatter.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Bubble chart</strong><br>
<a href="examples/bubble.png"><img src="examples/bubble.png" alt="Bubble chart — Position items by two metrics and encode a third with size." width="100%"></a><br>
Position items by two metrics and encode a third with size.<br>
<code>bubble</code> · <a href="examples/bubble.json">JSON</a>
</td>
</tr>
</table>

<a id="gallery-shares"></a>
### Pie and doughnut charts · 2 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Pie chart</strong><br>
<a href="examples/pie.png"><img src="examples/pie.png" alt="Pie chart — Show a small number of parts of a whole." width="100%"></a><br>
Show a small number of parts of a whole.<br>
<code>pie</code> · <a href="examples/pie.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Doughnut chart</strong><br>
<a href="examples/doughnut.png"><img src="examples/doughnut.png" alt="Doughnut chart — Show shares with a central total or label." width="100%"></a><br>
Show shares with a central total or label.<br>
<code>doughnut</code> · <a href="examples/doughnut.json">JSON</a>
</td>
</tr>
</table>

<a id="gallery-schedules"></a>
### Gantt charts and timelines · 4 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Gantt chart</strong><br>
<a href="examples/gantt.png"><img src="examples/gantt.png" alt="Gantt chart — Show tasks, dates, milestones, and owners." width="100%"></a><br>
Show tasks, dates, milestones, and owners.<br>
<code>gantt</code> · <a href="examples/gantt.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Timeline</strong><br>
<a href="examples/timeline.png"><img src="examples/timeline.png" alt="Timeline — Summarize a roadmap with phases and milestones." width="100%"></a><br>
Summarize a roadmap with phases and milestones.<br>
<code>timeline</code> · <a href="examples/timeline.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Gantt with progress</strong><br>
<a href="examples/gantt_progress.png"><img src="examples/gantt_progress.png" alt="Gantt with progress — Add completion percentages to a project plan." width="100%"></a><br>
Add completion percentages to a project plan.<br>
<code>gantt_progress</code> · <a href="examples/gantt_progress.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Swimlane Gantt</strong><br>
<a href="examples/gantt_swimlane.png"><img src="examples/gantt_swimlane.png" alt="Swimlane Gantt — Group tasks by workstream." width="100%"></a><br>
Group tasks by workstream.<br>
<code>gantt_swimlane</code> · <a href="examples/gantt_swimlane.json">JSON</a>
</td>
</tr>
</table>

<a id="gallery-tables"></a>
### Assessment tables · 1 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Harvey-ball table</strong><br>
<a href="examples/table_harvey.png"><img src="examples/table_harvey.png" alt="Harvey-ball table — Compare qualitative assessments with Harvey balls and check marks." width="100%"></a><br>
Compare qualitative assessments with Harvey balls and check marks.<br>
<code>table_harvey</code> · <a href="examples/table_harvey.json">JSON</a>
</td>
<td width="50%"></td>
</tr>
</table>

<a id="gallery-consulting"></a>
### Consulting charts · 12 examples

<table>
<tr>
<td width="50%" valign="top">
<strong>Funnel</strong><br>
<a href="examples/funnel.png"><img src="examples/funnel.png" alt="Funnel — Show stage volumes and conversion rates." width="100%"></a><br>
Show stage volumes and conversion rates.<br>
<code>funnel</code> · <a href="examples/funnel.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Heatmap</strong><br>
<a href="examples/heatmap.png"><img src="examples/heatmap.png" alt="Heatmap — Compare intensity across rows and columns." width="100%"></a><br>
Compare intensity across rows and columns.<br>
<code>heatmap</code> · <a href="examples/heatmap.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>2×2 matrix</strong><br>
<a href="examples/matrix_2x2.png"><img src="examples/matrix_2x2.png" alt="2×2 matrix — Position initiatives or businesses in a strategic matrix." width="100%"></a><br>
Position initiatives or businesses in a strategic matrix.<br>
<code>matrix_2x2</code> · <a href="examples/matrix_2x2.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Pareto chart</strong><br>
<a href="examples/pareto.png"><img src="examples/pareto.png" alt="Pareto chart — Rank contributions and show their cumulative share." width="100%"></a><br>
Rank contributions and show their cumulative share.<br>
<code>pareto</code> · <a href="examples/pareto.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Tornado chart</strong><br>
<a href="examples/tornado.png"><img src="examples/tornado.png" alt="Tornado chart — Compare supplied low/high sensitivity outcomes against a baseline." width="100%"></a><br>
Compare supplied low/high sensitivity outcomes against a baseline.<br>
<code>tornado</code> · <a href="examples/tornado.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Driver tree</strong><br>
<a href="examples/tree.png"><img src="examples/tree.png" alt="Driver tree — Display a supplied hierarchy of metrics and drivers." width="100%"></a><br>
Display a supplied hierarchy of metrics and drivers.<br>
<code>tree</code> · <a href="examples/tree.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>KPI cards</strong><br>
<a href="examples/kpi_cards.png"><img src="examples/kpi_cards.png" alt="KPI cards — Summarize metrics, deltas, and optional sparklines." width="100%"></a><br>
Summarize metrics, deltas, and optional sparklines.<br>
<code>kpi_cards</code> · <a href="examples/kpi_cards.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Bullet chart</strong><br>
<a href="examples/bullet.png"><img src="examples/bullet.png" alt="Bullet chart — Compare actual performance with a target and qualitative ranges." width="100%"></a><br>
Compare actual performance with a target and qualitative ranges.<br>
<code>bullet</code> · <a href="examples/bullet.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>Progress bars</strong><br>
<a href="examples/progress_bars.png"><img src="examples/progress_bars.png" alt="Progress bars — Show completion against a target and optional expected progress." width="100%"></a><br>
Show completion against a target and optional expected progress.<br>
<code>progress_bars</code> · <a href="examples/progress_bars.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Radar chart</strong><br>
<a href="examples/radar.png"><img src="examples/radar.png" alt="Radar chart — Compare a small number of profiles across several dimensions." width="100%"></a><br>
Compare a small number of profiles across several dimensions.<br>
<code>radar</code> · <a href="examples/radar.json">JSON</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<strong>TAM / SAM / SOM</strong><br>
<a href="examples/tam_sam_som.png"><img src="examples/tam_sam_som.png" alt="TAM / SAM / SOM — Show nested levels of market size." width="100%"></a><br>
Show nested levels of market size.<br>
<code>tam_sam_som</code> · <a href="examples/tam_sam_som.json">JSON</a>
</td>
<td width="50%" valign="top">
<strong>Waffle chart</strong><br>
<a href="examples/waffle.png"><img src="examples/waffle.png" alt="Waffle chart — Communicate a percentage through a grid of cells." width="100%"></a><br>
Communicate a percentage through a grid of cells.<br>
<code>waffle</code> · <a href="examples/waffle.json">JSON</a>
</td>
</tr>
</table>

<a id="cli"></a>
## CLI reference

### `tc_render.py`: rendering

```text
python scripts/tc_render.py SPEC.json [MORE.json ...] [-o OUTPUT.pptx] [--png DIR] [--html OUTPUT.html] [OPTIONS]
```

| Argument | Meaning |
| --- | --- |
| `specs` | One or more JSON files, read in order; `examples/*.json` renders the examples and skips the non-chart `catalog.json` index |
| `-o` / `--out` | Output PPTX path; provide at least this or `--html`; the output parent directory should already exist |
| `--png DIR` | Requires `-o`; exports each page as PNG, creates the directory, and uses LibreOffice → PDF → Poppler |
| `--html FILE` | Export all input pages as one independent editable `.html` / `.htm` file; combine with PPTX / PNG or omit `-o` for HTML-only output |
| `--dpi N` | PNG resolution, default `110` |
| `--theme NAME` | Set the theme for all slides in this run |
| `--list-themes` | List themes and exit; requires neither specs nor `-o` |
| `--force` | Report validation findings and still attempt rendering |
| `--no-validate` | Skip pre-render validation |

```bash
# Render the 61 base examples; dashboard and ops examples are in subdirectories
.venv/bin/python scripts/tc_render.py examples/*.json \
  -o all-examples.pptx --png all-examples_png/ --dpi 150
```

### `tc_advise.py`: recommendations

```text
python scripts/tc_advise.py DATA [--intent TEXT] [-o DRAFT.json] [--json REPORT.json]
```

- `DATA`: data file, or `-` for standard input.
- `--intent`: the intended message or comparison, with Chinese and English keyword support.
- `-o` / `--out`: save a draft spec when automatic generation is available for the preferred chart; some data shapes still require a handwritten spec.
- `--json`: path for the full recommendation result. `-` appends JSON after the text report, so it **does not produce JSON-only stdout**. Use a file path for automation.

### `tc_validate.py`: validation

```text
python scripts/tc_validate.py SPEC.json [MORE.json ...] [--json]
```

`--json` writes all validation results as a JSON array. See [chart selection and data sufficiency](docs/CHART_SELECTION.md) for the rules.

<a id="maintenance"></a>
## Structure, maintenance, and verification

```text
yuxin-business-charts/
├── SKILL.md                 # Agent entry point and workflow
├── README.md / README_EN.md  # Bilingual guides and complete galleries
├── LICENSE                  # Apache-2.0
├── NOTICE                   # External reference rights and provenance
├── scripts/
│   ├── tc_core.py           # Layout, base charts, themes, and annotations
│   ├── tc_more.py           # Additional chart implementations
│   ├── tc_dash.py           # dashboard / facet layouts
│   ├── tc_render.py         # PPTX / PNG / HTML CLI
│   ├── tc_svg.py            # Convert chart shapes to native SVG
│   ├── tc_html.py           # Single-file editable HTML export
│   ├── tc_advise.py         # Rule-based recommendations and draft specs
│   ├── tc_validate.py       # Data sufficiency and readability checks
│   ├── make_examples.py     # Example JSON generation
│   ├── build_gallery.py     # Categorized PPTX / PDF and example PNGs
│   ├── build_docs.py        # Chart catalog and HTML gallery generation
│   ├── audit.py             # Historical comparison; requires old examples
│   └── requirements.txt
├── assets/html-editor.html  # Embedded editing and save interface
├── examples/                # 61 single-chart + 5 dashboard + 6 ops specs
├── docs/                    # Catalog, selection, style, colors, and audits
├── gallery/                 # PPTX, PDF, static gallery, editable demo, and themes
├── references/              # Public source lists; original images stay local
└── tests/                   # Recommendation fixtures and validation tests
```

| Document | Contents |
| --- | --- |
| [SKILL.md](SKILL.md) | Agent decisions, missing data, color selection, and delivery |
| [CATALOG.md](docs/CATALOG.md) | Per-type `data` structures, full JSON examples, and previews |
| [CHART_SELECTION.md](docs/CHART_SELECTION.md) | Data shape × intent rules and validation coverage |
| [STYLE_SPEC.md](docs/STYLE_SPEC.md) | Layout, labels, arrows, anchors, and the four-zone convention |
| [PALETTES.md](docs/PALETTES.md) / [COLORS.md](docs/COLORS.md) | Theme roles, values, and color provenance |
| [AUDIT.md](docs/AUDIT.md) | Presence of four-zone elements in the examples |
| [tests/README.md](tests/README.md) | Test datasets and checks |

```bash
# Regression checks for recommendations, validation, examples, and PPTX rendering
.venv/bin/python tests/run_tests.py

# Regression checks for SVG, the HTML editor, and HTML export
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'

# Rebuild the five-page editable demo without rewriting its PPTX / PNG outputs
.venv/bin/python scripts/tc_render.py examples/waterfall.json examples/doughnut.json \
  examples/timeline.json examples/dashboards/dash_three_column.json \
  examples/ops-report/scorecard.json --html gallery/editable-demo.html

# Rebuild the chart catalog and static PNG HTML index
.venv/bin/python scripts/build_docs.py

# Rebuild 61 example PNGs and a 72-page PPTX / PDF with 11 category dividers
.venv/bin/python scripts/build_gallery.py

# Historical audit: first supply a real directory of previous example JSONs
# .venv/bin/python scripts/audit.py /absolute/path/to/previous-examples
```

`run_tests.py` uses 20 recommendation datasets and 16 validation cases, covering intent preferences, draft rendering, validation of the 61 base examples, 5 dashboard examples, and rejection / `--force` behavior. The `test_*.py` suite additionally covers SVG, HTML documents, and CLI export, including all 72 example specs. See the [test guide](tests/README.md) for scope; automated checks do not replace visual review and in-browser editing, saving, and reopening checks. `audit.py` is a historical before/after comparison tool and requires an explicit directory of previous examples; its default directory is not distributed, so it is not a general test command. Build scripts overwrite their generated artifacts; `make_examples.py` rewrites example JSON files, so decide whether the generator or a manually edited spec is authoritative before rebuilding.

<a id="limitations"></a>
## Known limitations

- **Shape editing, not data-bound charts:** no PowerPoint “Edit Data” sheet, automatic Excel link, or think-cell-style interactive rearrangement.
- **HTML edits displayed text only:** it does not recalculate data, write back to JSON / PPTX / PNG, or provide shape dragging or linked-data updates. Inspect for overlaps after adding long text.
- **Fixed canvas and layout:** default 16:9; no CLI for template import, arbitrary slide dimensions, or logarithmic axes.
- **Heuristic label placement:** estimated bounds and small position adjustments can still leave overlaps; tiny segments may hide labels. Long titles, dense categories, and multiple annotations require inspection.
- **Rules, not business verification:** recommendation and validation cannot verify sources, establish causality, or decide a business conclusion. Field checks are not a comprehensive JSON Schema validator.
- **Project-specific extensions:** funnels, heatmaps, driver trees, KPI cards, radar charts, and others use this project's visual conventions; the catalog is not a feature-equivalence claim about commercial think-cell.
- **Environment-dependent previews:** fonts and differences between browsers, Office, and LibreOffice can change wrapping and alignment. Python dependencies alone support PPTX / HTML output, but not PNG rendering.
- **Language scope:** both README versions are available; recommendation and validation reports are primarily Chinese, while chart titles and labels use your supplied text. Other reference documents currently remain in Chinese.

<a id="license"></a>
## License and reference material

This skill's original code, documentation, and generated examples are released under the [Apache License 2.0](LICENSE). This directory's license does not change the licensing of other suite members.

Original external or user-provided reference images remain local in `references/img/` and `references/palettes/` and are excluded from public Git distribution. The runtime does not depend on them; only source and provenance indexes are published. Rights remain with their respective owners; **the project's Apache-2.0 license does not automatically cover those materials**. See the [chart source list](references/SOURCES.csv), [palette source list](references/palettes/SOURCES.csv), and [third-party notices](NOTICE) for scope and provenance. The README gallery displays charts and theme previews generated by this project, not third-party reference screenshots.


## Customized edition on GitHub

Install this edition from https://github.com/yuxinliang0301/yuxin-business-charts.
See the [Chinese usage guide](gallery/intro/usage-guide.png) and [chart and table examples](gallery/intro/chart-and-table-examples.png).
