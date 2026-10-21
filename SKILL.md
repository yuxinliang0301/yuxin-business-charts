---
name: yuxin-business-charts
description: 基于给定数据生成商业图片与表格：楷体、咨询风配色、堆叠与分面、差值标注、热力表、Excel条件格式、数据条和迷你图。保留先确认新设计及必要处理口径的流程，已有方案直接沿用。支持55种图型的PPTX形状、PNG与可改字HTML；丰富数据表按载体实现。用于汇报配图、表格可视化、选型和现有图表优化，不承担VOC分析验证、策略评价或完整报告写作，不提供Excel自动联动。
---

# Yuxin 商业图表助手

用一份 JSON 描述图表，生成**可编辑 PPTX**（全部是 PowerPoint 原生形状，每个都能单独选中、改色、改字）、**PNG 预览**，以及**可编辑 HTML**（原生 SVG 图形，标题、数据标签与说明可在浏览器改字并保存）。支持单图与 dashboard / facet 拼版；视觉风格参考 think-cell 示例并包含本项目的扩展约定。

## 按当前任务使用

| 当前需求 | 执行范围与必读参考 |
|---|---|
| 只画图、改图 | 按已确认目的与口径选型；不扩展为完整报告 |
| 做重点表、条件格式或迷你图 | 读 [管理层表格](references/management-tables.md)；原生Excel实现另读 [Excel条件格式](references/excel-conditional-formatting.md) |
| 差值、同比标注、嵌套柱、断轴、合计或均值线 | 读 [高阶比较配方](references/advanced-comparison-patterns.md)，先核对真实数据关系与现有实现能力 |
| 已有报告需要配图/做表 | 使用报告中已确认的数据、结论和口径设计图表；不重新分析原声、不重写整份报告 |
| 仅改图表文字或格式 | 修改标题、标签、脚注、字体、颜色与布局；不启动完整复盘或扩大取数范围 |

本技能只负责图片和表格的制作。`tc_render.py` 仍是图表页渲染器，不因这些方法说明而自动新增通用Excel条件格式、Word排版或数据绑定能力。使用哪种载体就调用其真实可用工具；无相应能力时说明限制，不虚构spec字段。

## 制作范围与必要检查

- 接收已有数据、指标定义与表达目标，完成选型、版式、标注、表格条件格式和文件导出。不默认启动VOC分类/验证、策略效果判断、SQL取数或完整报告写作。
- 检查仅限绘制所需：数值与标签一致、总分可加、比例分母明确、缺失与零分开、时间粒度/尺度一致。若给定口径冲突，只指出影响该图表的具体问题，不扩展成业务审计。
- 图表标题可以把已有发现写清楚，但不得新增材料外的业务结论。上游分析已确定的主题、分类与口径作为输入，不重新判断用户表达或客服话术。
- 制作所需的日均、CPO、占比或差值按已确认公式计算；未知公式/分母先补缺项，不猜口径。已确认的风格、图数、处理方式和交付形式直接沿用。

## 本次复盘沉淀的图表与表格约定

- **总量与子集**：关键词并集＋其余工单＝计价规则总量；堆叠顶部是总量，段内显示分项，底部/相邻列显示关键词占比。不能把总量和关键词再次相加。
- **逐日与阶段**：逐日解释冲击时点，阶段表解释日均、CPO与缓解。没有每日总量就不画每日总量堆叠；没有每日完单不均摊伪造逐日CPO。
- **变化标注**：选重点加细括号、箭头、基期虚线和直接数值；明确比较对象、基期与单位，%与百分点分开。参考圆圈只在确有帮助时轻量使用，不满图加粗圈。
- **嵌套窗口**：当天、3日内、第1周、后14天互相包含，不作为可加总的堆叠构成。可改为日均/CPO的独立摘要或互斥时间段。
- **重点表**：策略组汇总后紧跟组内城市；量、率与变化分列，精简到支持结论的指标。数据条看规模，色阶看强弱，图标看已定义的方向/状态，迷你图看轨迹，仍保留精确读数。
- **话题热力表**：先核对是否多标签、分母与样本量；行内独立色阶只能作行内比较，必须标明。多标签不能直接画100%堆叠或饼图。
- **最终载体**：用户要Word时保持正常纵向页面和原生表格，宽表拆分而不强行缩字或改横向；图表渲染器固定16:9不决定报告纸张方向。原生Excel规则、HTML/CSS视觉模拟和静态PNG分别说明，不能混称动态条件格式。

## 快速使用
```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt   # 渲染 PNG 还需要 LibreOffice(soffice) + poppler(pdftoppm)
.venv/bin/python scripts/tc_render.py examples/waterfall.json -o out.pptx --png out_png/ --html out.html
.venv/bin/python scripts/tc_render.py a.json b.json c.json -o deck.pptx --png pngs/ --html deck.html   # 多张合成一个 deck
.venv/bin/python scripts/tc_render.py examples/waterfall.json --html report.html   # 只写 HTML
```
一个 JSON 可以是单个图表对象，也可以是 `{"slides":[...]}`。渲染至少提供 `-o` 或 `--html`；`--png` 仍要求 `-o`。HTML 为离线单文件，无 CDN，不需要 LibreOffice / Poppler；省略 `-o` 时只写 HTML，不改已有 PPTX / PNG。CLI 未指定 `--html` 时保持原有输出。建议交付逐页 PNG 图片和可编辑 PPTX，先由用户确认本次格式；HTML 是可选附加项。CLI 的输出能力与参数不代替对话中的需求确认。

给真正使用者的「什么时候用、怎么给数据、怎么写 prompt、交付物是什么」见 [README.md · 如何使用与怎么写 prompt](README.md#how-to-use)；多图拼版字段见 [docs/DASHBOARD.md](docs/DASHBOARD.md)。

## 新图、新表的工作流程（给 Agent）
**确认配色与交付形式 → 确认图数、各图目的与画法 → 索取所需数据 → 确认必要的处理口径 → 处理、校验、绘制 → 检查与交付**

这是用户指定的新图、新表协作流程；不用于技能维护或仅文字任务。首次绘图先读 [references/drawing-intake.md](references/drawing-intake.md)，使用其中的专业配色选项、简短确认话术和数据处理规则。尚未获得必要答复时，不先画正式图。用户已明确的选择和已同意的方案直接沿用，只补问缺项；“自行发挥”时先提出具体图数与逐图思路，获得确认后再绘制。若用户明确要求跳过某阶段，遵从该次指令，记录采用的假设，不杜撰数据。表格的方案包括关键列、行分组、排序、条件格式含义和载体，不强迫表格任务选择PPT。

1. **确认设计需求**：一次汇总配色（给专业方案及推荐理由）、交付形式（可编辑 PPT / PNG 图片 / 两者）和图数、每图想表达什么。用户没有思路时，按目的提出可审阅的方案：每图回答的问题、推荐图型、比较对象、布局与重点；可引用 24 种图谱中的对应样例。明确区分“图的数量”与“一页放几图”。等待用户选择或同意方案，不用默认值代替确认。
2. **按方案索取数据**：确认后给最小字段清单，写清单位、粒度、期间、比较基准及来源需求，支持 CSV、TSV、Excel、JSON 或粘贴表格。用户已给文件则先检查并只补缺项，不要求重复提交。方案在数据验证前只是拟回答的问题，不能预设结论。
3. **确认处理后再执行**：可先读取字段、样本行和数据质量来形成处理提案。需要筛选、去重、汇总、关联、计算指标、处理缺失/异常或调整时间口径时，先具体说明规则、公式、分母与影响，等用户确认后执行。已有明确口径直接按其执行；只涉及不改变数值意义的格式转换可直接完成。保留原始数据，处理后核对行数、合计与比例。发现数据不支持已定方案时，说明原因、提出替代并确认后再改图。无需数据的机制示意不索取无关数字；模拟数据只用于已同意的示例并明确标注。

以下技术步骤均在上述确认范围内执行：

本地审美偏好：专业来自比较关系、统一尺度和清楚的标注。默认白底、蓝灰主色、少量语义强调，避免为每个指标增加一种亮色。经营复盘或参考样图改造先读 [references/professional-patterns.md](references/professional-patterns.md)：它从用户提供的 106 页《384款图表模板样式图》中归纳结构配方，并说明采用、改造或舍弃的理由。**384 是参考文档的名称，现有渲染器仍支持 55 种单图，不代表新增了 384 种实现。**

涉及经营报告的重复更新、差异箭头/年化增长、应收余额桥、收入成本面积图、Mekko 或气泡分区时，读 [references/thinkcell-operating-analysis.md](references/thinkcell-operating-analysis.md)。它提炼用户提供的 Thinkcell 教程，并校正期间增长与年化、环比起止期、面积求和等误读。教程的插件功能不代表本 skill 已实现。

1. **准备已确认的数据**：保留原始文件，另存处理后的数据供渲染使用（粘贴内容可以传给 `tc_advise.py -`）。
2a. **用户没指定图表** → 运行
   `python scripts/tc_advise.py data.csv [--intent "用户想说明的结论"] -o draft.json --json advise.json`
   - 推荐器用于验证已沟通的画法。没有确定图型时，将推荐图型及理由补入方案并等用户确认；已确认的画法不重复询问。不能用推荐器结果跳过前置确认。
   - **结合自身判断**：规则引擎只看数据形态和关键词，不懂业务语境。下面几种情况要用自己的判断覆盖推荐：
     - 用户的原话、上下文或受众（董事会 / 运营周会）指向另一种图；
     - 数据其实不可加总（例如混了单位）；
     - 自动推断的结论不是用户真正想说的。
   - 覆盖推荐时，在 `docs/CHART_SELECTION.md` 里找对应行，说明理由。
   - 标题应能被数据支持；来源可写用户提供的文件和表页位置，未知则明确标注待补，不编来源。
   - 推荐器草稿可能把空值暂填为 0；渲染前与原数据核对，不能把缺失当真实零值。缺失影响结论时先补数据或缩小分析范围。
2b. **用户指定了图表** → 先按 `docs/CATALOG.md` 把数据写进 spec，再运行
   `python scripts/tc_validate.py spec.json`
   - **能做**：继续。
   - **能做但有问题**：把问题和建议告诉用户，由用户决定是否修正。
   - **不能做**：原样告诉用户缺什么、怎么补（含示例格式）、折中办法和替代图，**等用户补数据或同意折中**。不要自己编数据补齐。
3. **应用已确认的配色**：按用户选择的主题或品牌色写入 spec。`restrained_navy` 是推荐方案与底层渲染器的回退主题，不代表未确认即可直接使用。
4. **渲染**：常规使用 `tc_render.py spec.json -o out.pptx --png out/ [--theme 主题]`，按用户确认的格式交付；需要 HTML 时再加 `--html out.html`。只交付用户选择的格式；只要图片时 PPTX 可作为渲染中间文件保留在临时目录，不额外交付；至少提供 `-o` 或 `--html`，`--png` 需要 `-o`；只要 HTML 时不要加 `-o` / `--png`。渲染前会**自动校验**：遇到“不能做”会拒绝渲染并用大白话报错；只有用户明确接受折中时才加 `--force`。`--no-validate` 可以跳过校验。
   - 标题与单位、读数、来源与口径应清楚。`highlight` / `callouts` 只在解释异常或机制时添加，留出空间；不为凑齐元素硬加红圈。
   - 需要标记时加 decorations：CAGR、total_diff、diff、value_line。
4b. **多图拼版**：数据有多个指标 × 多个分组（推荐器会首选 `facet`），或者用户要“一页多图 / 看板 / 分面”时，按 `docs/DASHBOARD.md` 写 `type: dashboard`（自由区域或网格，子图类型可以混用）或 `type: facet`（行×列分面，可共用纵轴）。分段虚线、多层横轴、条件着色、圈注、箭头、“VS … ±pp”批注写在子图的 `segments` / `annotations` / `rule` 里；阈值须有依据，默认使用本地主题语义，不自动套用旧例的红绿色和满页圈注。用户给的参考图中如果有真实业务数字，示例一律换成示意数据。
5. **检查后交付用户要求的文件**：中文预览若漏字，先修正字体发现配置，参见结构配方末尾的字体检查；不能交付缺字图片。PPTX / PNG 通过预览检查标签、箭头、对齐和颜色语义。按已确认主题分配重点、对照、目标与负差的语义色；克制蓝灰方案中蓝色表示当期或重点、灰色表示对照、酒红表示负差/缺口。数值下降不自动等于业务变差。HTML 在浏览器目检，实际检查开启编辑 → 修改标题/说明/数据标签/脚注/批注 → 保存 HTML → 重新打开并继续编辑，不能仅凭文件生成就宣称可编辑。另按 `docs/STYLE_SPEC.md` §11–12 和参考配方检查分母、pp vs %、累计关系、共轴对齐与截止日期。

## 展示图表能力与选样式

用户要求“多展示几种图”“示例太单调”或挑选图型时，用 [24种图表图谱](examples/restrained/chart-atlas.json) 与 [图谱总览](gallery/chart-atlas-overview.html)（可筛选与放大）以及 [逐页可改字预览](gallery/chart-atlas.html)。图谱覆盖差异、构成、定位、决策和执行，使用模拟数据，展示现有 55 种类型中的 24 种，不增加图型数量。

展示多样性应改变信息编码与比较任务：长度、位置、区间、宽高、矩阵、流程关系、时间排期各有用途。不要把同一柱图换标题或颜色当成不同示例，也不要为实际分析凑齐图型。参考图谱中的副标题解释适用问题，脚注解释读法与限制；可推荐总览图片、逐页 PNG 和原生形状 PPTX，实际按用户确认的形式交付。

```bash
python scripts/tc_render.py examples/restrained/chart-atlas.json -o chart-atlas.pptx --png atlas_png/ --html chart-atlas.html
```

单图可选 `chart_box: [x, y, width, height]`，单位英寸，须在 13.333 × 7.5 页面内；图谱用 `[0.7, 1.75, 11.9, 4.6]` 为坐标标签与两行页脚留空间。它只调整图形区域，不缩小字体。每次重排后仍须渲染检查。

## 咨询案例式证据页

用户要求参照 Bainflix 案例、咨询图表页或“图表＋解释”时，读 [references/bainflix-exhibit-patterns.md](references/bainflix-exhibit-patterns.md)。按“结论标题 → 互补证据 → 图下解释”组织一页，不照搬密集红框、预测数字或极小字号。`dashboard` 可加 `exhibit: true`，panel 可加 `insight`、`insight_size`、`insight_height`；字段见 `docs/DASHBOARD.md`。只制作所需图表证据页；整本报告写作与排版不属于本技能职责，复杂策略图需单独设计实现。

## HTML 编辑边界

- 工具条切换文字编辑；点击文字改写，保存后的 HTML 可再次离线打开并继续编辑。使用说明与示例见 [README.md · 可编辑 HTML](README.md#editable-html) 和 `gallery/editable-demo.html`。
- 只改变当前 HTML 的显示文字，不重新计算数据、不改变柱高等几何信息，也不回写 JSON、PPTX 或 PNG。用户要求变更数值或数据关系时，修改真实源 spec 后重新渲染。
- HTML 是可选附加输出；建议 PNG + PPTX，实际按用户确认的格式交付。用户选择 HTML 时再生成。CLI 保持兼容，未加 `--html` 不自动生成。无需 LibreOffice 或 Poppler，不提供悬浮数据提示、图形拖拽或数据联动。
- 浏览器和 PowerPoint 的字体表现有微差；长文字可能挤压版面，编辑保存后需再次目检。

## 目录
- `references/management-tables.md`：管理层重点表、策略组与城市层级、条件格式组合与迷你图。
- `references/excel-conditional-formatting.md`：Excel原生条件格式、公式、规则范围/顺序、REPT和迷你图的使用与核验。
- `references/advanced-comparison-patterns.md`：差值/同比、嵌套柱、断轴、合计/均值线的适用条件与实现边界。
- `scripts/tc_core.py`：绘图引擎（版面分区、第一批 25 种图、装饰、标签防重叠）
- `scripts/tc_dash.py`：多图拼版（dashboard / facet，字段见 `docs/DASHBOARD.md`，示例见 `examples/dashboards/`）
- `scripts/tc_more.py`：第二批 30 种图（共 55 种类型、61 个示例、11 类）
- `scripts/tc_render.py`：PPTX / PNG / HTML CLI（渲染前自动调用 tc_validate；`--html`、`--theme`、`--list-themes`、`--force`、`--no-validate`）
- `scripts/tc_svg.py`、`scripts/tc_html.py`、`assets/html-editor.html`：原生 SVG 转换、单文件 HTML 导出与文字编辑保存界面
- `scripts/tc_advise.py`：数据分析 + 图表推荐（规则引擎，输出中文报告、JSON 和 spec 草稿）
- `scripts/tc_validate.py`：数据充分性校验（55 种图全覆盖）
- `docs/CHART_SELECTION.md`：数据形态 × 表达意图 → 图表 决策表，以及校验项清单（含 §5 经营汇报高频意图）
- `docs/DASHBOARD.md`：多图拼版字段；§7 为经营对账页配方（Scorecard / 量速效三联 / Facet 换维）
- `tests/`：20 个推荐数据集 + 16 个校验用例，`python tests/run_tests.py` 检查原有流程；`python -m unittest discover -s tests -p 'test_*.py'` 检查 SVG / HTML 与原有 72 个示例导出，范围见 `tests/README.md`
- `scripts/make_examples.py`：生成 `examples/*.json`
- `scripts/build_gallery.py`：分类 gallery PPTX/PDF，并重渲染示例 PNG
- `scripts/build_docs.py`：生成 CATALOG 和 HTML 总览
- `docs/CATALOG.md`：图表目录，每个图都有数据格式、样例、适合场景和示例图
- `docs/STYLE_SPEC.md`：版面分区和元素规则（§9 四区；§11 结论页四件套；§12 易误读护栏）
- `docs/AUDIT.md`：61 个示例的四区审核表
- `scripts/audit.py`：历史前后对照审核工具，需显式提供旧示例目录，不是通用测试入口
- `docs/COLORS.md`：配色和取色出处
- `references/SOURCES.csv`、`references/palettes/SOURCES.csv`：外部参考图来源索引；原始截图仅在本地 `references/img/` 与 `references/palettes/` 留存，不进入公开分发，也不是运行依赖。授权范围见 `NOTICE`。
- `examples/`：61 个基础单图（JSON / PNG，分类索引为 `catalog.json`）、5 个 `dashboards/` 拼版、6 个 `ops-report/` 经营对账 spec，上游原有 72 个图表 spec；本地另增 `restrained/` 中 8 个单页示例与 1 份含 24 页的图谱（合计 81 个 spec 文件、104 页）
- `gallery/`：`thinkcell-gallery.pptx` / `.pdf`（按分类排）、`index.html`（PNG 静态总览）、`editable-demo.html`（可离线改字的 HTML 示例）、`gallery-screenshot.png`

## 已知限制
- PPTX 输出是**形状**，不是 PowerPoint 原生图表对象：可以随意改样式，但改数据要重新生成（不能在 PowerPoint 里"编辑数据"）。
- 标签防重叠是启发式规则（估算文字宽度后上下微移），不能保证零重叠；段太小时直接隐藏标签。
- 第二批中咨询类图（漏斗、热力、矩阵、帕累托、龙卷风、树、KPI 卡、子弹、雷达、TAM、华夫等）think-cell 本身没有，样式属 [约定]。
- 拼版子图目前只支持 4 种 kind（area_stack / lines / column_stack / bars_pair），版面固定为 16:9。参考图如果更宽，会被等比压缩。
- 没有实现：think-cell 那种拖动重排、自动链接 Excel、对数轴。

## 字体与交付偏好

- 全部文字默认楷体：标题、正文、数字、图例、坐标、批注、来源和脚注统一使用 `Kaiti SC`（楷体-简）；PPT 同时写入 Latin / East Asian / Complex Script 字体属性。用户本次明确指定其他字体时可用顶层 `font_family` 覆盖。
- macOS 本机已有楷体；PNG 渲染时确保 fontconfig 包含实际字体目录。HTML 回退依次使用 STKaiti、KaiTi、楷体。不得无声用黑体代替楷体。
- 先确认交付形式，推荐逐页高清 PNG + 可编辑 PPTX；PPT 中保留文字、柱线、箭头等原生形状，不能把整张图片铺进 PPT 冒充可编辑。数字变化时修改源 spec 后重新生成。
- PPT 不嵌入本机字体；接收方需安装相应楷体才能保持相同排版，PNG 外观固定。交付检查实际字体和版面，不能只改文档约定。

## 配色与视觉层级
1. 首选推荐 `restrained_navy`（克制蓝灰），先与用户确认，其他方案见前置沟通参考：白底、深蓝 `#24465C`、钢蓝 `#7391A4`、对照灰 `#C9D0D5`；酒红 `#A0525A` 仅用于负差/缺口。已选定的配色不重复询问。普通注释用深蓝，拼版标题用正体深色，不默认红色斜体下划线。
2. 一页通常只有一个主色相，必要时加入一个语义强调色；多系列优先用深浅、直接标签、线型或分面。需要区分无序类别时可用少量低饱和异色，不能因强行单色而看不清；连续量用顺序色阶，正负偏离用有明确中心的发散色阶。
3. 同一实体跨页同色；当前与对照关系保持一致。新 spec 从旧例子改写时，逐项检查 `palette`、`series_colors`、`point_colors`、`rule`、显式文字颜色和 `title_style`。这些显式设置会保留，**单改 `theme` 不会自动清除彩色覆盖**。
4. 新 spec 显式写已确认的 `theme`，例如 `"theme": "restrained_navy"`。旧 8 套主题保留，可按用户品牌要求选择；`--theme` 优先于 spec 的主题，但不强改用户明确设置的系列色。
5. 图形平面化，不用装饰性渐变、立体、齿轮、阴影或彩虹刻度。通过留白、对齐、标注和合理图型建立层次。直接读数优先，精确比较时保留必要的数值刻度。

主题详情见 [docs/PALETTES.md](docs/PALETTES.md)；运行 `python scripts/tc_render.py --list-themes` 可查看全部 9 套。新的结构与配色示例见 `examples/restrained/`，旧画廊保留历史主题，不能当作本地默认审美。
