# 版面与样式规范（逐条注明依据）

> 参考图都在 `references/img/`，文件名格式是"手册页名--图名.jpg"。每张图的原始 URL 和来源页见 `references/SOURCES.csv`。
> 手册根地址：https://www.think-cell.com/en/resources/manual/ 。标注 **[约定]** 的条目，think-cell 官方没有规定，是本 skill 的约定，不冒充官方依据。

## 本地默认审美

新图默认 `restrained_navy`；结构参考 [professional-patterns.md](../references/professional-patterns.md)。下文保留历史来源与旧主题规范，涉及酒红通用圈注、红色斜体下划线标题、绿好红坏或固定高密度字号时，以本节为准：普通注释深蓝、负差酒红；标题正体深色左对齐；同指标同尺度；必要刻度保留；没有真实例外无需圈注。旧模板的显式颜色/样式不由主题自动覆盖，Agent 改写旧 spec 时需检查。

全部标题、数字、图例、批注和脚注使用楷体（`Kaiti SC` / 楷体-简）；默认输出 PNG + 原生形状可编辑 PPTX。PPT 中文字体属性必须显式写入，不能依赖 Arial 的系统回退。

## 1. 版面分区（13.33×7.5 in，16:9）
| 区域 | 位置 (in) | 规则 | 依据 |
|---|---|---|---|
| 标题区 | x0.5 y0.35 w12.3 h0.8 | 24pt 粗体，结论式一句话 | **[约定]** think-cell 手册只管图表元素，不规定幻灯片标题；它用 PowerPoint 母版字体（https://www.think-cell.com/en/resources/manual/textlabels："The options in Font reflect the fonts… in the slide master"） |
| 副标题/单位区 | y1.2 h0.35 | 14pt 灰 #777777，单位放在括号里 | **[约定]**；单位写法参考 `quantitative-charts--bar-chart.jpg`（"Units sold" 放在图左上） |
| 图表区 (chart area) | x0.7 y1.75 w11.9 h4.95 | 包含绘图区、类别标签、系列标签和装饰 | 图表区与绘图区的划分见 https://www.think-cell.com/en/resources/manual/chart-area-plot-area，`chart-area-plot-area--chart-area-plot-area.jpg` |
| 标记区（绘图区上方/右侧预留） | 柱形图有 CAGR/总差时顶部预留 0.9in，有系列标签时右侧预留 1.6in | CAGR、总差箭头在柱顶上方；差值箭头和系列标签在最后一列右侧 | `chartdecorations--cagr_formula.jpg`、`differencearrow_abs2.jpg`（箭头在柱上方）、`differencearrow_abs1.jpg`（在右侧）、`column-line-area-charts--sample_stacked.jpg`（系列名在右侧） |
| 重点强调区 | 叠加在图表区上 | 酒红 #A20603 椭圆圈、callout 框加引线 | **[约定]**；颜色取自用户参考图 A 的费用色（见 COLORS.md） |
| 脚注来源区 | 底部 y≈6.65–7.05 | 10pt 灰，"Source: …"，脚注在前 | **[约定]**（think-cell 手册没有涉及） |

## 2. 图表元素规则
1. **减少非必要网格与轴**（柱、堆叠、瀑布有直接读数时可省数值轴；精确比较、散点与范围图需保留必要尺度），数值直接标在段内。依据：`sample_stacked.jpg`、`sample_waterfall.jpg`、`sample_chart2.jpg`、`sample_mekko.jpg`。
2. **段内标签居中**，段太小放不下时不显示（瀑布图改放到柱外）。依据：https://www.think-cell.com/en/resources/manual/waterfall 的 sample_waterfall3（"3"标在小柱上）；think-cell 对放不下的标签会自动处理（https://www.think-cell.com/en/resources/manual/textlabels）。
3. **堆叠柱顶部显示总计**。依据：`sample_stacked.jpg`（22/38/27）、`sample_100perc.jpg`（23/45/30 显示在 100% 柱上方）。
4. **系列标签放在最后一列右侧，与段垂直居中**，不用图例框。依据：`sample_stacked.jpg`、`sample_100perc.jpg`、`mekko--sample_mekko.jpg`。簇状柱、组合图例外，用图例（`sample_clustered.jpg` 没有段可以对齐）。
5. **类别标签在基线下方居中**；基线是一条细黑线。依据：所有柱形示例。
6. **字号统一**：段内标签、总计、类别标签、系列标签同字号（默认 14pt），因为 think-cell 对所有图表标签用同一默认字号。依据：`sample_chart2.jpg`、`sample_waterfall.jpg`（目测所有标签同号）。
7. **无阴影、无渐变**：所有形状去掉主题样式（删除 p:style）。依据：手册所有示例图都是平面填充。
8. **线宽**：轴和箭头 0.75pt；连接线 0.5pt。依据：目测 `sample_waterfall_connectors.jpg`、`stacked_with_connectors.jpg`。

## 3. 瀑布图
- 连接线是**细虚线**，连接相邻柱的累计水平位置。依据：`waterfall--sample_waterfall_connectors.jpg`；手册原文："In a basic waterfall chart, every two columns are connected by precisely one horizontal connector."
- 段标签默认**显示正值（不带符号）**。手册原文："By default, the segment labels in waterfall charts show the extent of the segment which is always a positive value." 可选 `signed_labels`。
- 起止柱用系列 1 的颜色（绿）。依据：`sample_waterfall.jpg`（41/47/41 是绿柱）。
- build-down 水平版依据 `sample_waterfall2.jpg`、`quantitative-charts--waterfall-chart-example.jpg`。

## 4. 装饰（标记区）
| 装饰 | 画法 | 依据 |
|---|---|---|
| CAGR 箭头 | 从起点柱顶上方竖线升起，水平线跨到终点柱，向下箭头；中间是白底黑边椭圆，标 "+x.x%" | `chartdecorations--cagr_formula.jpg`（+10% p.a.）、手册："only one CAGR is inserted that stretches from the selected category to the last category" |
| 总差箭头 | 与 CAGR 同形，标签是 % 或绝对差 | `chartdecorations--differencearrow_abs2.jpg`（+22%） |
| 差值箭头（level difference） | 两柱顶用虚线引到右侧，双向竖箭头加椭圆 | `chartdecorations--differencearrow_abs1.jpg`（+127%）、`differencearrow_bigbubble.jpg`；手册："If the arrow is so small that the bubble would cover it up, the bubble is automatically placed next to the arrow"（本 skill 一律把椭圆放在箭头旁边） |
| 数值线 | 虚线横穿全部柱，右端标值 | `chartdecorations--averageline.jpg` |
| 轴破断 | 在超高柱中段画两条白色斜平行线，被截掉的区间压缩到 8% | `axes--break_wiggle.jpg`、`axes--break_y1.jpg`；手册："Use a value axis break to shrink a particularly large segment" |

## 5. Mekko
- 百分比 Mekko：左侧刻度 0–100%，柱顶标宽度值（市场规模），右上角标 "100% ="，系列名放在最后一列右侧。依据：`quantitative-charts--mekko-percent-axis-example.jpg`、`sample_mekko.jpg`。
- 单位 Mekko：左侧是绝对值刻度，柱顶标总计。依据：`mekko--sample_olympic.jpg`、`quantitative-charts--mekko-unit-axis-example.jpg`。

## 6. 其他图
- 100% 堆叠：`sample_100perc.jpg`。簇状：`sample_clustered.jpg`。组合/双轴：`sample_combi.jpg`、`secondary_axis.jpg`。
- 折线：`line-chart-example.jpg`（系列名标在线尾）。面积/100% 面积：`sample_area.jpg`、`sample_area100perc.jpg`。
- 蝴蝶：`sample_butterfly.jpg`。区间（足球场）：`football.jpg`。哑铃图在手册中没有，是 **[约定]**。
- 散点/气泡：`sample_scatter.jpg`、`sample_bubble.jpg`、`partition.jpg`（分区线）。
- 饼/环：`sample_pie.jpg`、`sample_doughnut.jpg`（百分比在扇区内，类别名在外）。
- 甘特：`gantt--gantt-chart-project-timeline-provisional.jpg`（左侧 Activity 列，顶部月/周刻度，右侧负责人列）、`gantt-timeline-bars`、`milestones`（黑色菱形）、`shade`（灰色阴影期）、`brackets`（底部括号）。
- Harvey ball 表格：手册 https://www.think-cell.com/en/resources/manual/harvey-balls-and-checkboxes（该页图片未能抓取，按文字说明实现 0–4 档）；表格条纹依据 https://www.think-cell.com/en/resources/manual/table。

## 7. 第二批图表的依据
| 类型 | 依据 |
|---|---|
| stacked_clustered | 手册 column-line-area-charts：`sample_stacked_clustered.jpg` |
| column_error | 手册 column-line-area-charts：`errorbars.jpg`（黑色误差线，两端短横） |
| column_grouped | 手册 axes：`category_gap.jpg`（类别间隔）；组名放在第二行，**[约定]** |
| column_xbreak | 手册 axes：`break_x.jpg`（类别轴上的双斜线破断） |
| value_line / line_target 的目标线 | 手册 chartdecorations：`averageline.jpg`（虚线加右端标签）；目标区间带 **[约定]**（tc Gray） |
| waterfall_stacked | 手册 waterfall：瀑布柱可由多段组成（`sample_waterfall_signed_sum.jpg`） |
| waterfall_subtotal | 手册 waterfall："Remove a connector… to start a new summation"，equals 列（`sample_waterfall3.jpg`）；本 skill 用 kind=subtotal 自动计算 |
| waterfall_percent、负终点瀑布 | **[约定]**，画法同普通瀑布 |
| variwide | 手册 quantitative-charts：`mekko-unit-axis-example.jpg`（单系列单位 Mekko） |
| bar_percent | `sample_100perc.jpg` 的条形版；李克特配色 **[约定]**（海军蓝 #00507D、浅灰蓝 #98ADC9、浅灰 #C6C0C0、酒红 #A20603） |
| bar_yoy、bar_diverging、slope、small_multiples、proportional_area | **[约定]**；沿用手册条形图语言（`quantitative-charts--bar-chart.jpg`：值标在条尾、类别名在左） |
| gantt_progress、gantt_swimlane | 手册 gantt：`gantt-timeline-bars`、`gantt-timeline-shade`；完成度和泳道标题行 **[约定]** |
| funnel、heatmap、matrix_2x2、pareto、tornado、tree、kpi_cards、bullet、progress_bars、radar、tam_sam_som、waffle | think-cell 没有这些图（手册 think-cell-charts 页列出的图表类型里没有），全部是 **[约定]**；统一用 think-cell 视觉语言：平面填充、无阴影、细黑线、海军蓝表示重点或正向，酒红表示负向，黑色表示目标，灰阶表示其他 |

## 8. 标签防重叠（第二批新增）
`Slide.text()` 会估算每个文字标签的外框，与已放置的标签相交时，上下交替微移（最多 8 次）。坐标轴类别标签设 `avoid=False` 固定不动。段内标签放在形状内部，不参与避让。依据：think-cell 会自动摆放标签（手册 textlabels 页 `dragging_labels*.jpg`）；具体算法是 **[约定]**。

## 9. 四区规范（所有图表类型通用，由引擎 `frame()` + `annotate()` 实现）
| 区 | JSON 字段 | 规则 | 依据 |
|---|---|---|---|
| ① 标题区 | `title`（必填，结论式一句话）、`subtitle`、`unit`（必填） | 标题 24pt 粗体左对齐，最多 2 行；副标题和单位在同一行，14pt #777777，单位放在括号里 | **[约定]**（见 §1） |
| ② 数据标签区 | 由各图生成；`format` / `delta_format` 控制数字格式 | 图内统一 14pt；段内标签放不下时隐藏或移到柱外；自动防重叠（§8）；单位只写在副标题行，标签里不重复单位（% / pp 除外） | §2 第 2–6 条（手册 sample_stacked、sample_waterfall 等） |
| ③ 重点强调区 | `highlight`: `[{category｜anchor｜at, "shape":"circle｜box｜arrow", w,h,ox,oy,dx,dy}]`；另有数据内高亮（如 `bar_sorted.highlight`、`matrix_2x2.focus`） | 一律用酒红 #A20603（`thinkcell_green` 主题下为 tc Red #C10D3B）：圆圈 2pt、虚线圆角框 1.5pt、箭头 2.25pt；每页建议 ≤ 2 处 | 颜色取自用户参考图 A（COLORS.md）；圈和框本身是 **[约定]** |
| ④ 备注说明区 | `callouts`: `[{text, category｜anchor｜at, dx,dy,w,h,nth}]`；`footnote`；`source`（必填，缺失时显示红字提醒） | 引申气泡：白底 + 酒红 1pt 圆角边框 + 酒红粗体 13pt 文字 + 0.75pt 引线 + 锚点小圆点；气泡自动限制在图表区内，锚点贴在被引用标签外框的边缘。脚注 10pt 灰，顺序为脚注在前、"Source:" 在后，放在幻灯片底部 | **[约定]**（think-cell 手册没有 callout 组件；视觉沿用 difference arrow 的"线 + 标签框"语言，`chartdecorations--differencearrow_abs1.jpg`） |

**锚点写法**：
- `category`：仅柱形/瀑布类，指向该柱顶部。
- `anchor`：图上任意标签文字，如 `"515"`、`"Keyboards"`、`"Hardware|South"`（热力图单元格）、`"Asset turnover"`（树节点）；同名标签用 `nth` 选第几个。
- `at`：`[fx, fy]`，图表区比例坐标，左上角是 (0,0)。

## 10. 多图拼版规范 [约定]（`tc_dash.py`，依据用户提供的运营看板参考图归纳，不是 think-cell 官方规范）
- **总标题**：本地默认左对齐、深色加粗；`title_tag` 仅在有分组意义时使用，避免装饰性黄底。旧主题保留居中默认。
- **子图标题**：本地默认 `plain`，深色正体、左对齐；`red_underline` 留作显式兼容选项。
- **页脚**：页面左下角统一写来源。补充说明一行一条，关键词可以标红或加粗。不在每个子图下面重复写来源。
- **分隔**：子图之间、分面行列之间用灰色虚线分隔，不画实线边框。分面的行表头放在左侧方框里。
- **分段**：竖向灰色虚线分段，分段名（By Q / By M / 年份）写在该段顶部，用斜体小字。
- **颜色**：
  - `ops_bright` 配色：主序列蓝 #0070C0、橙 #EA6A06、绿 #4EA72E，其余归入灰色 #BFBFBF。
  - 同一个系列名在整页内颜色一致（`series_colors`）。
- **条件色**：达成值 ≥ 时间进度标绿 #3F9C1E，低于时间进度标红 #C00000，对比期标灰 #A6A6A6。时间进度画成黑色虚线，并在底部标 `▲ 数值`。
- **批注**：
  - “VS 基准 ±x.xpp”：正值标绿，负值标红。
  - 重点数值用红圈（`circle`）圈出。
  - 趋势变化用红色斜箭头（`arrow`）标示。
- **标签**：
  - 堆积面积在色块内写 `值 (占比%)`，色块太矮时隐藏。
  - 折线的系列名写在右端，用该系列的颜色；颜色太浅的文字自动加深。
- **字号**：子图数据标签 6–7pt，子图标题 9–10pt，总标题 18–20pt。

## 11. 结论页四件套（经营/咨询汇报默认检查清单）[约定]

出图前按分析任务自检：比较任务需基准，有例外才标注；来源与口径应明确。不要为凑齐要素编造异常或增加装饰。

| # | 必须项 | 对应字段 / 做法 |
|---|---|---|
| 1 | **标题是结论句** | `title` 写成「谁/什么 + 发生了什么 + 相对什么」，禁止「数据展示」「Overview」类空标题 |
| 2 | **有 baseline** | 至少一种：目标线、时间进度虚线、YoY/对比期、行业/组均值、日常（非高峰）对照 |
| 3 | **例外被标出** | `highlight` / `annotations`（circle、arrow、note）只标需要讨论的例外，每页建议 ≤ 2 处主圈 |
| 4 | **脚注可追溯** | `source` 必填；`footnote` 写口径 + **数据截止日期**（跨页对比先对齐日期） |

本地默认：主色=当期/重点，灰=对照/背景，酒红=负差/缺口；正负不自动等于业务好坏。旧主题可保留其明确说明的红绿语义。

## 12. 易误读护栏（生成标注时强制）[约定]

1. **达成率列要写清分母**：相对「目标」还是相对「预估/计划」；不要默认写成相对年度目标。
2. **百分点用 `pp`，百分比用 `%`**：差值写 `-9pp`，涨跌幅写 `-9%`；批注 `unit` 选错就改。
3. **红圈 = 讨论重点，不是数据本身**：`circle`/`arrow` 只标主讲人要讨论的点；不要把所有异常都圈满。
4. **跨页/跨文档对比先对齐截止日期**：脚注写清数据截止（as-of）日期；日期不一致时在 `note` 提醒不可直接比。
5. **结构占比下降 ≠ 一定变差**：总量被其他切片拉高时，原切片份额会被动下降——标题勿写「份额崩了」除非绝对量和效率也差。
