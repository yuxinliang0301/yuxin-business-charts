# 图表选择规则（数据形态 × 表达意图 → 图表）

`scripts/tc_advise.py` 按本表打分。每条规则给一个基础分；用户说出的意图命中时再加分：一般 +12，表达“构成/占比”时占比类图表 +36。得分最高的 3 种不同图表作为 1 个首选 + 2 个备选，并为首选生成 spec 草稿，再交给 `tc_validate.py` 校验。
规则只是起点。Agent 必须结合用户的语境做最终判断，见 SKILL.md 的“工作流程”。

## 1. 先识别的数据形态
| 形态 | 怎么判断 |
|---|---|
| 维度 / 度量 | 非数字列 = 维度（文本或时间）；≥80% 能解析成数字的列 = 度量（去掉 `$ ¥ , % pp x 亿 万`，`(12)` 视为 -12） |
| 时间序列 | 类别像年份、季度、月份、FY24、2024Q1、1月等；度量列名是年份时视为**宽表**，自动转置 |
| 两层分类 | 2 个维度列 + 1 个度量列 → 自动透视成 类别 × 系列 |
| 构成 / 加总 | 每个类别的各系列之和 ≈ 100 → 100% 构成；单列各项之和 ≈ 100 → 整体构成；同单位、量级接近、列名不是比率 → 可加总 |
| 正负增量 / 起止桥 | 单列有正有负；**首项 + 中间各项 ≈ 末项**（容差 1%），或首末项名字像“期初/期末、2024/2025、合计”。中间的“毛利 / EBIT / 营业利润”等若等于累计值，识别为小计 |
| 成本拆解 | 首项为正、其后全为负，且不平 |
| 两个时点 | 正好 2 个系列，系列名是两个时期，或 before/after、plan/actual、去年/今年 |
| 目标 | 有名为 target / plan / budget / 目标 / 预算的数值列 |
| 区间 | 有 low/high（下限/上限）列；另有 base（基准）列 → 敏感性分析 |
| 宽度 | 有 size / market / 规模 / 权重 等数值列 → 可做 Mekko、变宽柱 |
| 日程 | 有 2 个日期列（start/end）→ 甘特图 |
| 转化阶段 | 类别名像 访问/加购/下单/visit/cart/purchase，且数值逐级递减 |
| 极值差异 | 最大值 / 第二大值 ≥ 3 → 需要数值轴破断（column 加 `axis_break`） |
| 类别名长度、类别数 | 最长名 > 10 字符或类别 > 6 个 → 倾向横向条形；超过各图可读上限时提示合并为 Other |

## 2. 决策表
| 数据形态 | 表达意图 | 首选 | 常见备选 | 建议强调 / 标记 |
|---|---|---|---|---|
| 首项+增量=末项 | 变化原因、拆解 | waterfall（95） | waterfall_h、bar_diverging | 最大正/负驱动；总差箭头 |
| 起止桥 + 中间小计 | 利润表、逐级落地 | waterfall_subtotal（97） | waterfall、waterfall_h | 最大扣减项；总差箭头 |
| 总额后全是扣减 | 成本构成 | waterfall_h（88） | waterfall_subtotal | 最大成本项 |
| 单列有正有负（不成桥） | 谁升谁降 | bar_diverging（88） | waterfall、bar_sorted | 最大正、最大负 |
| 开始/结束日期 | 计划、进度 | gantt（92）；有完成度时 gantt_progress（96） | timeline、gantt_swimlane | today 线、里程碑、关键路径 |
| 低/高 + 基准 | 敏感性 | tornado（95） | football、dumbbell | 影响最大的因素 |
| 低/高 | 估值、区间 | football（90） | dumbbell、table_harvey | 报价竖线 |
| 实际 + 目标 | 达成情况 | column_target（90）；时间序列单指标时可选 line_target（80） | progress_bars、bullet | 未达标项、差值 |
| 宽度 + 各段占比 | 市场规模 × 份额 | mekko_percent（92） | percent、heatmap | 最大市场里的领先者 |
| 宽度 + 单指标 | 规模 × 盈利 | variwide（88） | — | 又大又高的类别 |
| 两个时点 × 类别 | 同比、前后 | bar_yoy（88） | dumbbell（82）、slope（78） | 变化最大项；Δ% 列 |
| 时间 × 单指标 | 增长 | column（88）+ CAGR | line（期数 > 8 时优先）、kpi_cards | CAGR 箭头；末期高亮 |
| 时间 × 单指标，有离群值 | 增长 / 异常 | column + axis_break（92） | line | 离群值 |
| 时间 × 多系列，可加总 | 总量增长 + 构成 | stacked（90） | percent、area、line、small_multiples（系列 ≥ 5） | 总量 CAGR；增长最快的部分 |
| 时间 × 多系列，各期加和 100 | 结构变化 | percent（92） | area_percent | 占比变化最大的部分 |
| 时间 × 两个量级不同的指标（或一个是比率） | 量与率一起看 | combo（89） | line、clustered | 右轴折线 |
| 时间 × 系列本身是年份（如 2024/2025 × Q1–Q4） | 两年逐期比较 | clustered（88） | line、column_grouped | 增幅最大的一期 |
| 类别 × 单指标 | 排名、比较 | bar_sorted（80–86） | column（类别少、名字短）、pareto（≥ 5 类） | 第一名 / 讨论对象 |
| 类别 × 单指标，加和 100 | 构成 | pie（≤ 5 块，84） | doughnut、waffle（≤ 3 块）、bar_sorted | 最大的一块 |
| 转化阶段逐级递减 | 转化 | funnel（94） | bar_sorted、pareto | 流失最大的一步；整体转化率 |
| 类别 × 多系列，各类别加和 100 | 调研量表、结构 | bar_percent（名字长或类别 > 5，90）/ percent（90） | heatmap | 最好/最差的类别 |
| 类别 × 多系列，可加总 | 总量 + 构成 | bar_stacked（80） | stacked、mekko_unit、clustered、butterfly（2 组） | — |
| 类别 × 2 个数值指标，≥ 6 个个体 | 相关关系 | scatter（82） | matrix_2x2、bar_sorted | 离群点；均值分割线 |
| 类别 × 3 个数值指标，≥ 5 个个体 | 相关 + 规模 | bubble（84） | scatter | 右上角 |
| 行 × 列矩阵（评分等） | 高低分布 | heatmap（78） | radar（少数对象 × 多维评分） | 最低/最高格 |

意图关键词（中英文都识别）：趋势/增长 → trend；构成/占比/份额 → composition；排名/最大 → ranking；拆解/驱动/从…到… → bridge；目标/达成/预算 → target；相关/关系 → correlation；区间/敏感/估值 → range；同比/前后/两年 → change；进度/里程碑 → schedule；二八/帕累托 → concentration。

## 3. 结论候选（用户没说时）
根据形态自动算出：首末增长率和 CAGR、增长最快的系列及其占比变化、峰值、离群值、最大正/负驱动、最大占比、前 3 项集中度、领先倍数、达标数、相关系数、整体转化率和流失最大的一步、敏感性最大的因素、区间重叠段。建议标题取第一条，Agent 应改成用户认可的结论。

## 4. 指定图表时的数据充分性校验
用户点名图表时，或渲染前（`tc_render.py` 自动调用），用 `tc_validate.py` 检查。结论分三档：**能做 / 能做但有问题 / 不能做**。对每个问题都说明缺什么、怎么补、示例格式；还会给出能凑合出图的折中办法，以及更合适的替代图。覆盖全部 55 种图表，主要检查：

- **字段**：必填字段是否齐全、类型是否正确；数字里是否混了 % 或单位等文字；各列表长度是否一致。
- **数值关系**：百分比是否加和 100；瀑布图起点 + 增量是否等于小计/终点（堆叠瀑布逐系列检查）；football 的下限是否 ≤ 上限；TAM ≥ SAM ≥ SOM；漏斗是否逐级递减；子弹图 ranges 是否递增。
- **图表专属字段**：百分比 Mekko 是否有 widths；甘特图每个任务是否有日期、格式是否正确、开始是否早于结束；line_target 是否有目标值；butterfly 和 dumbbell 是否正好 2 个系列；radar 是否 ≥ 3 个维度；2×2 矩阵的点是否在坐标范围内。
- **可读性**：类别数是否超出上限（如饼图 6 块、柱形 12 个、条形 15 个）；类别名是否过长；是否需要轴破断。
- **通用**：source 是否填写、是否有标题。

## 5. 经营汇报高频意图 → 图型（通用，不绑具体业务）

以下意图来自真实经营复盘/周会/月度复盘类材料的归纳，给 Agent 覆盖 `tc_advise` 规则推荐时用。表述保持通用。

| 表达意图（用户原话或语境） | 首选 | 常见备选 | 必须带的标注 |
|---|---|---|---|
| 相对时间进度 / 目标是否达标；开场对账 | `dashboard` 含 `bars_pair` + `rule.threshold`，或 `column_target` / `progress_bars` / `kpi_cards` | `bullet`、表格式 scorecard | 优先同期分期目标，线性时间进度只作已说明的辅助基准；对比期灰、缺口按主题强调，不默认红绿 |
| 谁解释了增速差额 / 贡献度归因 | `waterfall` 或 `column_stack`（贡献拆解）+ Explain 表（可用旁侧 `callouts`/脚注） | `bar_diverging`、`pareto` | 标最大正/负贡献；总差箭头 |
| 大促 vs 日常（节点膨胀） | `clustered` / `column_grouped`（本期高峰 vs 日常，或今年 vs 去年） | `bar_yoy`、`dumbbell` | 写倍率（×）与 **pp** 差（百分点，不是%） |
| 量、增速、效率是否同向 | `facet` 或 `dashboard`：`area_stack`（量）+ `lines`（YoY）+ `lines`（效率/费率） | `combo`、`small_multiples` | 三行共用时间轴；需要解释的异常才加注释 |
| 换切维找结构差异（团队/层级/市场） | `facet`（列=切维，行=指标） | `dashboard` 网格 | 同行同尺度，核对所选 kind 是否支持 `shared_y`；有业务依据的差异才强调 |
| 漏斗渗透 / 各层定义 | `funnel`；定义卡可用表或并排 KPI | `bar_sorted`、概念信息图（非数据时说明） | 写清时间窗与互斥规则；流失最大一步 |
| 场景×产品×指标选型 / 增效证明 | `heatmap` 或矩阵表 | `matrix_2x2`、案例拼版 `dashboard` | 高亮最优格；脚注度量口径 |
| 预算是否触顶 / 边际递减 | `scatter`（花费×回报）+ 饱和趋势 | `bubble`、`line` | 分区（还可加 / 临界 / 过饱和）；离群点 callout |
| 机制/方案讲解（少小数点） | 概念漏斗或对比示意图（可用 `funnel`/`bars_pair` 示意） | 深色背景示意页 | 标题讲逻辑；数字用示意并标注 |

意图关键词补充（中英文）：时间进度/attainment/pacing → target；贡献度/CTG/explain/归因 → bridge；膨胀/大促/高峰/promo/peak → change；量速效/费率/效率背离 → trend+composition；分面/按团队/按市场 → facet；渗透/漏斗层 → funnel；饱和/加预算 → correlation。


## 6. 参考模板的结构覆盖规则（Agent 判断层）

经营复盘、同比/目标/累计/多指标组合时读 [professional-patterns.md](../references/professional-patterns.md)，按其 14 类配方选择和简化。该参考覆盖 Agent 决策，不改变 `tc_advise.py` 的规则评分。

- 多于两个不同量纲的指标优先共轴独立面板；不能为分层显示给数据加偏移量。
- 极值先考虑直接标注、分面或改图；轴破断会影响长度比较，仅在明确标出断点并不会误导时使用。
- 同比/环比、累计/当期、率/量分清；月季年汇总中的率从分子分母重算。
- 模板里叫“瀑布”不等于实际是贡献桥；必须满足起点+净增量=终点。
- 优先推荐 restrained_navy；新任务先按 SKILL.md 确认配色，已有选择不重复询问。参考图的亮色、三维和全点装饰不继承。

## 7. Thinkcell 经营教程的补充判断

遇到差异箭头、复合增速、收入成本面积、应收桥或规模×结构时，读 [thinkcell-operating-analysis.md](../references/thinkcell-operating-analysis.md)。重点：总量差异与分项差异分开；月度复合增长不自动叫年化；面积顶部是各分项之和；Mekko 的百分比轴和单位轴不能混为一谈。该参考改变 Agent 的选型与计算判断，不改变推荐器打分或渲染器能力。
