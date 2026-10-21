# 多图拼版（dashboard / facet）

> 本地新图默认 `restrained_navy`：总标题左对齐、子标题深色正体、语义色随主题；以下旧示例的 `ops_bright`、红标题、显式系列色仍可兼容，但不会自动转成克制版。经营分层配方见 [professional-patterns.md](../references/professional-patterns.md)，可运行的新例子见 `../examples/restrained/aligned-metrics.json`。

一页放多张小图。两种类型都由 `scripts/tc_dash.py` 渲染，入口与单图相同：`tc_render.py spec.json -o out.pptx`，渲染前同样自动校验。

示例（全部为**示意数据**）：`examples/dashboards/*.json`、对应 PNG。重建方式：`python scripts/make_dashboards.py`。

## 1. 页面字段（两种类型通用）

| 字段 | 说明 |
|---|---|
| `title` | 总标题。可写成字符串，也可写成分段列表 `[{"text":"…","color":"red"}]` |
| `title_tag` | 标题前的标签块，例如 `{"text":"区域 A","fill":"yellow"}`（黄底标签），`title_sep` 是分隔符（默认 ` \| `） |
| `title_align` / `title_size` / `title_bold` | 对齐方式 `l`/`c`、字号、是否加粗 |
| `note` | 右上角小字说明（字符串或分段列表），标题区会自动下移 |
| `source` | 统一的页脚来源；缺省时显示红字提醒 |
| `footnotes` | 页脚更多行。每行可以是分段列表，用来给关键词标红或加粗 |
| `palette` | `ops_bright`（蓝 / 橙 / 绿 / 灰，取自运营看板参考图，[约定]）；不填就用当前 `--theme` |
| `series_colors` | 按系列名固定颜色，例如 `{"Team A":"#0070C0","Others":"#BFBFBF"}`，保证各子图里同一个名字颜色一致 |
| `font_size` | 子图里数据标签的字号，默认 7 |

颜色可以写 `#RRGGBB`，也可以用色名：`red`、`green`、`gray`、`yellow`、`blue`、`orange`、`black`。

## 2. dashboard：自由区域或网格

```json
{"type":"dashboard","title":"…","grid":{"rows":2,"cols":3,"gap":0.12},
 "panels":[{"box":[0,0,0.36,1],"title":"Daily Revenue ($Mn)","title_style":"red_underline","chart":{…}},
           {"cell":[0,1],"span":[1,2],"title":"…","chart":{…}}],
 "separators":[{"x":0.365}]}
```

- `box`：`[x, y, 宽, 高]`，按内容区的 0–1 比例写。也可以用 `cell` 加 `span`（需要先给 `grid`）。
- `title_style`：子图标题样式，可选 `red_underline`（红色、斜体、下划线）、`red`、`plain`。
- `separators`：页面级的虚线分隔，按内容区比例坐标写。

## 3. facet：行 × 列分面

```json
{"type":"facet","cols":["Country 1","Country 2"],
 "rows":[{"label":"指标 A","chart":{"kind":"area_stack","totals":true}}, …],
 "cells":[[{…data…},{…data…}], …],
 "shared_y":"row","row_header_style":"box","separators":"dash"}
```

- `cells[i][j]` 是第 i 行、第 j 列的数据；没有数据就写 `null`。
- `shared_y`：`row` 表示同一行的子图共用纵轴，`none` 表示各自独立。
- `row_header_style`：行表头样式，可选 `box`（方框）、`right`、`plain`。列表头用 `col_header_style`，可选 `red_underline` 或 `plain`。
- `separators`：设成 `dash` 时，行和列之间画虚线；设成 `null` 时不画。
- 某一行是 `bars_pair` 且带 `rule.threshold` 时，每一列都会画一条贯穿全部行的时间进度虚线，并在底部标出 `▲ 60%`。

## 4. 子图 `chart.kind`

| kind | data | 主要选项 |
|---|---|---|
| `area_stack` | `categories` + `series[{name, values}]` | `percent`（百分比面积）、`show_share`（显示 `值 (占比%)`）、`totals`、`smooth`、`min_label_h` |
| `lines` | 同上，值可为 `null` | `suffix`、`decimals`、`label_pos`（`above`/`below`/`auto`，或按系列名写成字典）、`smooth`、`markers`、`y_range` |
| `column_stack` | 同上；可加 `point_colors`（逐柱颜色） | `totals`、`bar_width` |
| `bars_pair` | `{value, compare}` 或 `{rows:[…]}` | `rule`：`{"threshold":60,"ge":"green","lt":"red","compare":"gray"}`，`x_max` |

公共选项：
- `x_labels`：多层共享横轴，例如 `[["W1","W2"],["Jan",""],["2026",""]]`，从上到下依次排列。
- `x_label_every`：每隔几个点显示一个横轴标签。
- `legend_right`：在右侧用系列颜色写系列名。

## 5. 分段与标注

- `segments`：`[{"from":0,"to":3,"label":"By Q"}]`。分段之间画竖向虚线，并在顶部写分段名。样式用 `segment_style` 调，可设 `color`、`italic`、`bold`、`size`、`dy`、`line_top`。
- `annotations`：
  - `{"type":"circle","series":"Team A","points":[6,7],"color":"red"}`：给数值画圈。
  - `{"type":"arrow","from":[0.6,0.1],"to":[0.7,0.3]}`：红色斜箭头，坐标用子图内的 0–1 比例。
  - `{"type":"note","series":"…","point":5,"text":"VS 基准","value":-1.5,"unit":"pp"}`：批注。按 `value` 的正负自动标绿或标红。
  - `{"type":"channel","series":"…","offset":0.08}`：画趋势通道，即线性拟合线上下各一条虚线。
  - `{"type":"text","at":[x,y],"text":"…"}`：在指定位置写文字。

## 6. 校验与推荐

- `tc_validate.py` 对拼版会检查：
  - 子图类型能不能识别；
  - 数据长度和类别数是否一致；
  - 分段和标注的序号有没有越界；
  - 标注引用的系列名是否存在；
  - box 有没有越界，各区域之间有没有重叠；
  - facet 的 `cells` 维度是否等于行数 × 列数；
  - 时间进度值是不是数字。
- `tc_advise.py`：如果是长表，并且同时有“时间维度、分组维度、≥2 个指标”，首选推荐 `facet`，备选是 `dashboard`，并直接生成可渲染的 facet 草稿（每行一个指标，每列一个分组，同一行共用纵轴）。

## 7. 经营对账页配方（可复用骨架，示意数据）

做周会/月度经营复盘一页多图时，优先套下面三种骨架，再填真实数据。字段写法见上文；示例数字一律示意。

### 7.1 Scorecard 开场条（相对时间进度）

- **何时用**：汇报第一屏；回答「哪些行低于时间进度」。
- **骨架**：`type: dashboard`，一行或多行 `bars_pair`；每行 `rule.threshold` = 当期时间进度（如 60）；`ge=green` / `lt=red` / `compare=gray`。
- **标题句式**：`「X 条业务线达成率低于时间进度 Y%」`（写清达成率相对计划还是目标）。
- **标注**：只圈低于阈值的行；脚注写 as-of 日期与口径。

### 7.2 量–速–效三联仪表盘

- **何时用**：判断盘子（量）、增速（YoY）、赚钱效率是否同向。
- **骨架**：`type: facet` 或 `dashboard` 三行：`area_stack`（绝对量，可 `show_share`）+ `lines`（YoY%）+ `lines`（效率/费率）；列可按市场/团队切。
- **标题句式**：`「量增速回落但效率升：变现变好 / 盘子承压」` 二选一，按三行是否同向写。
- **标注**：背离的拐点用 `circle`+`arrow`；不要三行各圈一遍。 **注意**：`facet` 里写在 `rows[].chart.annotations` 的圈会套到**该行每一列**；若只想圈某一列，改用 `dashboard` 分 panel，或先接受整行同构标注。

### 7.3 Facet 换维复用

- **何时用**：同一套指标换「团队 / 层级 / 品类 / 新老」找结构性差异。
- **骨架**：固定 `rows`（指标），只改 `cols` 与 `cells`；`shared_y: row`；`separators: dash`。
- **标题句式**：`「差异在列 C：…」`——先点出哪一列长得不一样。
- **复用纪律**：换维不换配色字典（`series_colors`），方便跨页扫读。 列专属圈注同 §7.2：facet 行级 annotations 会落到整行各列。

`column_stack` 支持 `segment_labels` 与 `totals`（默认均为 true）；单系列时可以关闭段内标签，只保留柱顶总数，避免重复读数。

## 8. 咨询案例式证据页

`exhibit: true` 在总标题下添加主题色细线，来源默认增至9pt；`footnote_size` 可调。顶层 `font_family` 默认 Kaiti SC，覆盖所有图内文字。

每个 dashboard panel 可加 `insight`（字符串或 rich text 段列表），在图下预留解释区；`insight_height` 默认0.75英寸，`insight_size` 默认12pt。解释建议1–2行，超长应缩写或拆页；空间不足会报错。facet 不支持逐格 insight。主图标题和图内数据保持原生可编辑。

结构与来源见 [Bainflix 图表论证配方](../references/bainflix-exhibit-patterns.md)，示例见 `examples/restrained/market-opportunity.json` 和 `coverage-productivity.json`。
