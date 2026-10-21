# 配色规范与出处

> 全部 8 套预设主题见 [PALETTES.md](PALETTES.md)。本文件记录默认主题与 think-cell 手册取色细节。

## 默认主题 `consulting_navy`（当前默认）
**色值来源：用户提供的两张参考图逐像素取色**（图 A：1038×520 瀑布/柱图，图 B：530×238 堆叠柱 + CAGR）。PNG 取大面积色块的众数像素。标 **[推导]** 的不是直接取色，是在取色值基础上插值或调浅得到的；标 **[约定]** 的是参考图里没有、按用户要求补充的辅助色。

| 角色 | 色值 | 来源 | skill 内用途 |
|---|---|---|---|
| 主色 海军蓝 | #00507D | 图 A 主柱 | 系列 1、瀑布起止/小计柱、正向增量、正向/重点（good、pos） |
| 中蓝（灰蓝） | #6C89B4 | 图 B Prod C | 系列 2 |
| 金色 | #F8BA00 | 图 B Prod B | 系列 3 |
| 橙色 | #E87722 | **[约定]** | 系列 4、组合图折线 |
| 绿色 | #5E9C42 | **[约定]** | 系列 5 |
| 灰色（深） | #787675 | 图 A Labor | 系列 6、次要 |
| 浅灰蓝 | #98ADC9 | 图 B Prod A | 系列 7 |
| 深灰蓝 | #344B6B | 图 B Prod D | 系列 8 |
| 浅灰 | #C6C0C0 | 图 A Material | 非重点柱/气泡、比较期（accent5） |
| 酒红 1 | #A20603 | 图 A Expenses 1/2 | 负向增量、费用、强调圈、callout 边框与文字（neg、bad、callout） |
| 酒红 2 | #85100B | **[推导]** 酒红 1 与酒红 3 之间插值 | 负向第二层级（neg2） |
| 酒红 3 | #691413 | 图 A Expenses 3 | 负向第三层级、负值总计柱（neg3） |
| 目标线 | #000000 | 图 A 目标虚线、图 B CAGR 箭头 | 目标线、计划线、today 线 |
| 阴影底色 | #E3E8F0 | **[推导]** #98ADC9 调浅 | 甘特阴影期、目标区间带 |

**系列顺序**：海军蓝 → 中蓝 → 金 → 橙 → 绿 → 灰。
**标签颜色**：按 WCAG 对比度自动选择。深色块（海军蓝、中蓝、酒红、深灰）用白字，浅色块（金、浅灰、浅灰蓝）用黑字。
**用法**：spec 里不写 `theme` 时用 `consulting_navy`；写 `"theme": "thinkcell_green"` 时切回旧的绿色主题。

---

## 可选主题 `thinkcell_green`（旧默认，保留）

## 结论
1. **think-cell 官方没有公布一套固定的"默认色值"**。官方说法：图表系列颜色用 PowerPoint 主题的 Accent 1–6，文字和装饰用 Text/Background Dark 1 / Light 1。
   - 出处：KB0105 https://www.think-cell.com/en/resources/kb/0105 ；手册 https://www.think-cell.com/en/resources/manual/default-theme
2. 所以`thinkcell_green` 主题（旧称 `thinkcell`）是**从官方手册截图逐像素取色**得到的，不是官方文档里写明的数值。取色依据是 think-cell 手册示例用的主题（手册页 https://www.think-cell.com/en/resources/manual/introductioncharting 的 `references/img/introductioncharting--applying_color.jpg`，图中是 think-cell 填充色下拉菜单的色块），用 `references/img/mekko--sample_mekko.jpg`、`pie--sample_pie.jpg`、`mekko--sample_olympic.jpg`、`waterfall--sample_waterfall.jpg` 的大面积色块做交叉核对。

## 取色结果（来源：applying_color.jpg 菜单色块中位数像素；JPEG 压缩，误差约 ±2）
| 名称（菜单原文） | 取色值 | skill 内用途 |
|---|---|---|
| Accent 1 | #6CA600（大面积色块众数 #6DA600，采用 **#6DA600**） | 系列 1（最上层）、瀑布起止柱、主强调色 |
| Accent 2 | #4C7400 | 系列 4 |
| Accent 3 | #0070AF | 系列 5 |
| Accent 4 | #00507C | 系列 6 |
| Accent 5 | #C1C0BE（色块众数 #C0C0C0，采用 **#C0C0C0**） | 系列 3、瀑布正增量 |
| Accent 6 | #787775（色块众数 #777777，采用 **#777777**） | 系列 2、瀑布负增量 |
| Text 2 | #005082 | — |
| tc Red | #C10D3B | 强调圈、callout、组合图折线、负向（color_by_sign） |
| tc Gray | #D4D7D9 | 甘特阴影期 |
| tc Green | #027673 | 备用 |
| Smoke 10/20/40/60/80/90% | #DEE5F0 / #C4CEE0 / #9DB0D0 / #6D8EB9 / #4E6A9C / #344E6A | 备用（可作单色系列） |
| Light / Med. / Dark Gray | #C0C0C0 / #969596 / #808080 | 网格、辅助线 |
| Text 1 / Black | #000000 | 所有文字、轴线、连接线、箭头 |

**系列顺序**：数据表第 1 个系列在最上面。参考 sample_stacked.jpg、sample_100perc.jpg 和 sample_mekko.jpg：最上层是绿，中间是深灰，最下层是浅灰。
**标签颜色**：深色填充（绿、深灰）上用白字，浅灰上用黑字，与 sample_chart2.jpg、sample_mekko.jpg 一致。

## 备选色板 `office`
新版 Office 默认主题：Accent1-6 = #156082 #E97132 #196B24 #0F9ED5 #A02B93 #4EA72E。
- 前三个色值用 think-cell 产品页图 `references/img/difference-arrow-100-v2.jpg` 取色核对过，结果是 #155F82 / #E97132 / #196B23。
- 后三个色值是我对 Office 主题的记忆值，没有官方文档核对，使用前请在 PowerPoint 的 Design › Colors 中确认。
