"""生成 examples/*.json（每种图一份），分类信息写入 examples/catalog.json"""
import json, os
D = os.path.join(os.path.dirname(__file__), "..", "examples")
Y5 = ["2021","2022","2023","2024","2025"]
SEG = [{"name":"Seg C","values":[10,12,15,19,25]},{"name":"Seg B","values":[25,28,33,38,43]},{"name":"Seg A","values":[40,44,48,52,57]}]
SRC = "Illustrative data"
E = []
def add(cat, id, type, title, data, use, unit=None, deco=None, sub=None, foot=None):
    s = {"id":id, "type":type, "title":title, "subtitle":sub or "", "unit":unit or "", "source":SRC, "data":data}
    if foot: s["footnote"]=foot
    if deco: s["decorations"]=deco
    E.append((cat, use, s))
# 1 柱形族
add("柱形图","column","column","Revenue has grown every year since 2021",{"categories":Y5,"series":[{"name":"Revenue","values":[75,84,96,109,125]}]},"单一指标随时间/类别变化","$M",[{"type":"cagr","from":0,"to":4}])
add("柱形图","stacked","stacked","Growth driven by all three segments, Seg C fastest",{"categories":Y5,"series":SEG},"总量+构成随时间变化（带总计和 CAGR）","$M",[{"type":"cagr","from":0,"to":4}])
add("柱形图","percent","percent","Seg C share rose from 13% to 20%",{"categories":Y5,"series":SEG},"构成占比变化（100% 堆叠）","% of revenue")
add("柱形图","clustered","clustered","Region North outperforms in every year",{"categories":["2023","2024","2025"],"series":[{"name":"North","values":[42,48,55]},{"name":"South","values":[35,37,40]},{"name":"West","values":[20,24,26]}]},"少量系列跨类别直接比较","$M")
add("柱形图","column_axis_break","column","One outlier year dwarfs the rest – axis break keeps detail readable",{"categories":["2021","2022","2023","2024","2025"],"series":[{"name":"Deals","values":[14,18,391,22,27]}],"axis_break":{"from":40,"to":360}},"有个别极大值时用轴破断","# deals")
add("柱形图","stacked_diff","stacked","2025 revenue is 67% above 2021",{"categories":Y5,"series":SEG},"突出两点之间的差值（差值箭头）","$M",[{"type":"diff","from":0,"to":4}])
add("柱形图","stacked_highlight","stacked","2024 was the inflection point",{"categories":Y5,"series":SEG},"强调某一列 + callout 说明","$M",[{"type":"highlight","category":"2024"},{"type":"callout","category":"2024","text":"New pricing launched","dx":-2.6,"dy":0.3}])
# 2 瀑布
add("瀑布图","waterfall","waterfall","Volume and price more than offset FX and other headwinds",{"items":[{"label":"2024","value":100,"kind":"start"},{"label":"Price","value":15},{"label":"Volume","value":22},{"label":"FX","value":-8},{"label":"Other","value":-4},{"label":"2025","value":125,"kind":"total"}]},"起点→驱动因素→终点的桥（收入桥、利润桥）","$M",[{"type":"total_diff","from":0,"to":5}])
add("瀑布图","waterfall_signed","waterfall","EBIT bridge with signed labels and sign colors",{"items":[{"label":"EBIT 2024","value":40,"kind":"start"},{"label":"Price","value":9},{"label":"Mix","value":4},{"label":"Input cost","value":-11},{"label":"Opex","value":-3},{"label":"EBIT 2025","value":39,"kind":"total"}],"signed_labels":True,"color_by_sign":True},"需要一眼看出正负方向时","$M")
add("瀑布图","waterfall_h","waterfall_h","Where the revenue goes: cost build-down",{"items":[{"label":"Revenue","value":125,"kind":"start"},{"label":"COGS","value":-55},{"label":"SG&A","value":-28},{"label":"R&D","value":-12},{"label":"D&A","value":-6},{"label":"EBIT","value":24,"kind":"total"}]},"总额向下分解（build-down，条目名较长时用水平版）","$M")
# 3 Mekko
MK = {"categories":["China","US","EU"],"widths":[50,30,20],"series":[{"name":"Brand A","values":[40,25,30]},{"name":"Brand B","values":[30,35,20]},{"name":"Brand C","values":[20,25,30]},{"name":"Others","values":[10,15,20]}]}
add("Mekko 图","mekko_percent","mekko_percent","Brand A leads in the largest market, China",MK,"市场规模（宽度）× 份额（高度），看结构","$B / %")
add("Mekko 图","mekko_unit","mekko_unit","US is smaller, with Brand B ahead of Brand A",{"categories":["China","US","EU"],"series":[{"name":"Brand A","values":[20,7.5,6]},{"name":"Brand B","values":[15,10.5,4]},{"name":"Others","values":[15,12,10]}]},"宽度和高度都是绝对值（单位 Mekko）","$B")
# 4 条形
CO = ["Keyboards","Headphones","Mice","Webcams","Monitors","Docks"]
add("条形图","bar","bar","Keyboards are the best-selling accessory",{"categories":CO,"series":[{"name":"Units","values":[515,420,310,280,190,120]}]},"类别名较长/类别较多时的排名","k units")
add("条形图","bar_sorted","bar_sorted","Sorted: Mice overtook Webcams in Q3",{"categories":["Webcams","Mice","Docks","Keyboards","Monitors"],"series":[{"name":"Units","values":[280,310,120,515,190]}],"highlight":["Mice"]},"自动降序 + 高亮重点项","k units")
add("条形图","bar_stacked","bar_stacked","Online now exceeds in-store in every region",{"categories":["North","South","East","West"],"series":[{"name":"Online","values":[58,49,55,42]},{"name":"In-store","values":[42,36,40,33]}]},"水平堆叠，类别名长时用","$M")
add("对比图","butterfly","butterfly","Men and women value different features",{"categories":["Price","Battery","Camera","Design","Brand"],"series":[{"name":"Men","values":[62,55,40,28,35]},{"name":"Women","values":[58,49,61,52,30]}]},"两组人群/两个时期左右对照（蝴蝶图）","% respondents")
add("对比图","dumbbell","dumbbell","NPS improved in all channels, most in App",{"categories":["App","Web","Store","Call center"],"series":[{"name":"2024","values":[22,30,41,12]},{"name":"2025","values":[45,38,46,20]}],"min":0},"两个时点的前后对比（哑铃图）","NPS")
add("对比图","football","football","Valuation range: DCF supports the offer price",{"categories":["52-week range","Trading comps","Precedent deals","DCF","LBO"],"series":[{"name":"Low","values":[18,20,23,22,19]},{"name":"High","values":[27,26,31,30,25]}],"min":15,"marker":{"value":25,"label":"Offer $25"}},"估值区间（足球场图）","$ per share")
# 5 折线/面积/组合
M12 = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug"]
add("折线/面积图","line","line","Online traffic overtook stores in May",{"categories":M12,"series":[{"name":"Online","values":[20,24,27,31,38,42,45,49]},{"name":"Store","values":[40,39,38,37,36,35,34,33]}]},"连续时间趋势","k visits")
add("折线/面积图","area","area","Total visits grew 90%, paid ads drove most",{"categories":M12,"series":[{"name":"Organic","values":[10,11,12,12,13,14,15,16]},{"name":"Paid ads","values":[6,7,8,10,11,12,13,14]},{"name":"Social","values":[4,4,5,5,6,6,7,8]}]},"总量趋势 + 构成","k visits")
add("折线/面积图","area_percent","area_percent","Paid ads share rising",{"categories":M12,"series":[{"name":"Organic","values":[10,11,12,12,13,14,15,16]},{"name":"Paid ads","values":[6,7,8,10,11,12,13,14]},{"name":"Social","values":[4,4,5,5,6,6,7,8]}]},"构成占比的连续变化","%")
add("折线/面积图","combo","combo","Revenue grows while margin expands",{"categories":Y5,"columns":[{"name":"Services","values":[20,24,28,33,40]},{"name":"Products","values":[55,60,68,76,85]}],"line":{"name":"EBIT margin","values":[8,9.5,11,12,14],"suffix":"%"}},"量 + 率（双轴组合）","$M / %")
# 6 散点/气泡
add("散点/气泡图","scatter","scatter","Higher price does not mean higher satisfaction",{"points":[{"x":x,"y":y,"label":l} for x,y,l in [(12,60,"A"),(15,72,"B"),(18,55,"C"),(22,80,"D"),(25,66,"E"),(30,70,"F"),(34,58,"G")]],"x_title":"Price ($)","y_title":"CSAT","partition":{"x":23,"y":65}},"两个指标的相关/四象限","")
add("散点/气泡图","bubble","bubble","Business segment: large and profitable",{"points":[{"x":2,"y":12,"size":25,"label":"Business"},{"x":4,"y":5,"size":8,"label":"Budget"},{"x":1,"y":18,"size":5,"label":"Power users"},{"x":5,"y":9,"size":15,"label":"Mid-range"},{"x":3,"y":15,"size":3,"label":"Early adopters"}],"x_title":"Purchase frequency (years)","y_title":"Margin (%)"},"三个维度（x、y、规模）的组合定位","")
# 7 饼/环
add("饼/环图","pie","pie","Heating dominates household energy use",{"segments":[{"label":"Heating","value":57},{"label":"Cooling","value":24},{"label":"Other","value":19}]},"少数（≤5）部分占整体","%")
add("饼/环图","doughnut","doughnut","Three channels make up the mix",{"segments":[{"label":"Online","value":57},{"label":"Retail","value":24},{"label":"Partners","value":19}],"center":"$125M"},"占比 + 中心放总量","%")
# 8 甘特/时间线
add("甘特/时间线","gantt","gantt","Project plan: deal closes end of July",{"start":"2026-05-04","end":"2026-08-01","weeks":True,"tasks":[
  {"name":"Send teaser","start":"2026-05-04","end":"2026-05-15","owner":"Bank"},{"name":"Sign NDA","milestone":"2026-05-20","milestone_label":"NDA signed","owner":"Legal"},
  {"name":"Management calls","start":"2026-05-18","end":"2026-06-12","owner":"CEO"},{"name":"Data room access","start":"2026-06-01","end":"2026-07-10","owner":"CFO"},
  {"name":"Final due diligence","start":"2026-06-29","end":"2026-07-24","owner":"Buyer"},{"name":"Signing","milestone":"2026-07-29","milestone_label":"SPA signed","owner":"All"}],
  "shades":[{"start":"2026-06-29","end":"2026-07-10","label":"Exclusivity"}],"brackets":[{"start":"2026-05-04","end":"2026-06-12","label":"Buyer outreach"}],"today":"2026-06-08"},"项目计划、里程碑、负责人")
add("甘特/时间线","timeline","timeline","Transformation roadmap 2026–2027",{"start":"2026-01-01","end":"2027-12-31","phases":[{"name":"Diagnose","start":"2026-01-01","end":"2026-04-30","color":2},{"name":"Design","start":"2026-05-01","end":"2026-10-31","color":1},{"name":"Roll-out","start":"2026-11-01","end":"2027-12-31","color":0}],"milestones":[{"date":"2026-03-15","label":"Baseline done"},{"date":"2026-07-01","label":"Target model"},{"date":"2026-11-15","label":"Pilot live"},{"date":"2027-06-30","label":"50% sites"},{"date":"2027-12-01","label":"Full scale"}]},"高层路线图/阶段 + 里程碑")
# 9 表格
H = lambda q:{"harvey":q}
add("表格","table_harvey","table_harvey","Vendor B is the strongest overall fit",{"columns":["Vendor A","Vendor B","Vendor C","Vendor D"],"rows":[
  {"name":"Functional coverage","values":[H(3),H(4),H(2),H(1)]},{"name":"Integration effort","values":[H(2),H(3),H(3),H(1)]},
  {"name":"Total cost (5y, $M)","values":["4.2","5.1","3.6","2.9"]},{"name":"Local support","values":[{"check":True},{"check":True},{"check":False},{"check":True}]},
  {"name":"References in industry","values":[H(1),H(4),H(2),H(0)]}]},"多维度定性评估（Harvey ball / 勾叉）")

# ===== 第二批 =====
add("柱形图","stacked_clustered","stacked_clustered","Actuals beat plan in every year across all segments",{"categories":["2023","2024","2025"],"groups":[{"name":"Plan","series":[{"name":"Seg C","values":[12,15,20]},{"name":"Seg B","values":[30,33,38]},{"name":"Seg A","values":[45,48,52]}]},{"name":"Actual","series":[{"name":"Seg C","values":[15,19,25]},{"name":"Seg B","values":[33,38,43]},{"name":"Seg A","values":[48,52,57]}]}]},"计划 vs 实际等「每类多根堆叠柱」","$M")
add("柱形图","column_error","column_error","Pilot stores lift sales by 12–18%",{"categories":["Control","Pilot A","Pilot B","Pilot C"],"values":[100,112,118,115],"errors":[4,5,6,3]},"带置信区间/波动范围的均值比较（误差线）","Index",foot="Error bars show 95% confidence interval")
add("柱形图","column_grouped","column_grouped","Q4 is the strongest quarter in both years",{"groups":[{"name":"2024","categories":["Q1","Q2","Q3","Q4"],"values":[22,25,24,31]},{"name":"2025","categories":["Q1","Q2","Q3","Q4"],"values":[26,29,28,37]}]},"两级类别（年-季度）分组 + 组间间隔","$M")
add("柱形图","column_target","column_target","Three of five regions hit their target",{"categories":["North","South","East","West","Central"],"actual":[52,38,47,29,41],"target":[48,42,45,35,40]},"实际 vs 目标（目标标记线 + 达成率）","$M")
add("柱形图","column_xbreak","column_xbreak","Revenue doubled from 2010 to 2025",{"categories":["2010","2022","2023","2024","2025"],"values":[50,78,86,94,101],"break_after":0},"类别轴不连续（跳过年份）时用横轴破断","$M")
add("柱形图","stacked_value_line","stacked","Revenue exceeds the 5-year average from 2024",{"categories":Y5,"series":SEG},"数值线/平均线（value line）","$M",[{"type":"value_line","value":97.8,"label":"Avg 97.8"}])
add("瀑布图","waterfall_stacked","waterfall_stacked","Both products contributed to growth; B more from price",{"series":["Product A","Product B"],"items":[{"label":"2024","values":[60,40],"kind":"start"},{"label":"Price","values":[5,10]},{"label":"Volume","values":[14,8]},{"label":"FX","values":[-5,-3]},{"label":"2025","values":[74,55],"kind":"total"}]},"每个驱动再按产品/区域拆分（堆叠瀑布）","$M")
add("瀑布图","waterfall_subtotal","waterfall_subtotal","From revenue to net income with two subtotals",{"items":[{"label":"Revenue","value":125,"kind":"start"},{"label":"COGS","value":-55},{"label":"Gross profit","kind":"subtotal"},{"label":"SG&A","value":-28},{"label":"R&D","value":-12},{"label":"EBIT","kind":"subtotal"},{"label":"Interest","value":-4},{"label":"Tax","value":-6},{"label":"Net income","kind":"total"}]},"多级小计的损益桥（subtotal 自动计算）","$M")
add("瀑布图","waterfall_percent","waterfall_percent","Margin expanded 2.6 pp, mostly from mix",{"items":[{"label":"Margin 2024","value":18.4,"kind":"start"},{"label":"Price","value":1.2},{"label":"Mix","value":2.1},{"label":"Input cost","value":-1.5},{"label":"Scale","value":0.8},{"label":"Margin 2025","value":21.0,"kind":"total"}],"format":"{:.1f}%","delta_format":"{:+.1f}pp","signed_labels":True},"百分比/利润率桥（pp 变化）","% / pp")
add("瀑布图","waterfall_negative_end","waterfall","Cash bridge: free cash flow turns negative",{"items":[{"label":"EBITDA","value":30,"kind":"start"},{"label":"Capex","value":-22},{"label":"Working cap.","value":-9},{"label":"Tax","value":-5},{"label":"FCF","value":-6,"kind":"total"}],"color_by_sign":True,"signed_labels":True},"终点为负的桥（零线以下）","$M")
add("Mekko 图","variwide","variwide","Large segments have the lowest margins",{"categories":["Retail","Wholesale","Online","B2B","Export"],"widths":[40,25,15,12,8],"values":[8,11,18,22,15],"suffix":"%","highlight":["Online","B2B"]},"宽=规模、高=指标的变宽柱（单系列 Mekko）","Margin %; width = revenue $M")
add("Mekko 图","proportional_area","proportional_area","Global market dwarfs our core region",{"items":[{"label":"Global","value":400},{"label":"Asia","value":160},{"label":"China","value":90},{"label":"Our sales","value":12}]},"量级差距很大时用面积比例","$B")
add("条形图","bar_yoy","bar_yoy","All categories grew except Mice",{"categories":["Keyboards","Headphones","Mice","Webcams","Monitors"],"previous":{"name":"2024","values":[480,350,330,220,160]},"current":{"name":"2025","values":[515,420,310,280,190]}},"两年逐项对比 + 变化率列","k units")
add("条形图","bar_diverging","bar_diverging","Margin change by business unit",{"categories":["Cloud","Devices","Services","Ads","Hardware","Licensing"],"values":[4.2,2.1,0.8,-1.5,-2.7,-3.4],"suffix":"pp"},"有正有负的变化（正负条形）","pp")
add("条形图","bar_percent","bar_percent","Two-thirds of customers are satisfied with service",{"categories":["Service","Price","Delivery","Product range","App"],"series":[{"name":"Very satisfied","values":[30,15,25,20,12]},{"name":"Satisfied","values":[36,30,35,40,28]},{"name":"Neutral","values":[20,30,22,25,30]},{"name":"Dissatisfied","values":[14,25,18,15,30]}],"colors":"likert"},"调研量表（李克特）/ 100% 构成条形","% respondents")
add("折线/面积图","line_target","line_target","Churn back inside target range since May",{"categories":M12,"series":[{"name":"Churn","values":[3.8,3.6,3.1,2.9,2.4,2.2,2.3,2.0]}],"band":[1.5,2.5],"label_last":False,"target":2.0,"target_label":"Target 2.0%"},"趋势 + 目标线 / 目标区间","% monthly churn")
add("折线/面积图","slope","slope","Online and App gained share, Stores lost most",{"left_label":"2020","right_label":"2025","items":[{"label":"Stores","a":52,"b":31},{"label":"Online","a":24,"b":36},{"label":"App","a":8,"b":21},{"label":"Phone","a":16,"b":12}],"highlight":["Online","App"],"red_down":True},"两个时点的排名/份额变化（斜率图）","% share")
add("折线/面积图","small_multiples","small_multiples","Every region grew, Asia fastest",{"categories":Y5,"cols":3,"panels":[{"title":"Asia","values":[20,26,33,41,52]},{"title":"Europe","values":[40,42,44,45,47]},{"title":"N. America","values":[50,53,55,58,60]},{"title":"LatAm","values":[10,11,13,14,16]},{"title":"Africa","values":[5,6,6,7,9]},{"title":"Oceania","values":[8,8,9,9,10]}]},"多个对象同刻度并排比较（小倍数）","$M")
add("甘特/时间线","gantt_progress","gantt_progress","Programme status: design 90% complete, build 35%",{"start":"2026-01-05","end":"2026-07-31","tasks":[{"name":"Discovery","start":"2026-01-05","end":"2026-02-13","progress":1.0},{"name":"Design","start":"2026-02-02","end":"2026-04-03","progress":0.9},{"name":"Build","start":"2026-03-16","end":"2026-06-12","progress":0.35},{"name":"Test","start":"2026-05-18","end":"2026-07-03","progress":0.05},{"name":"Go-live","milestone":"2026-07-15","milestone_label":"Go-live"}],"today":"2026-04-20"},"甘特 + 完成百分比（项目状态汇报）")
add("甘特/时间线","gantt_swimlane","gantt_swimlane","Three workstreams converge on the October launch",{"start":"2026-06-01","end":"2026-10-31","tasks":[{"name":"Commercial","header":True},{"name":"Pricing redesign","start":"2026-06-01","end":"2026-07-31","indent":True},{"name":"Sales training","start":"2026-08-03","end":"2026-09-25","indent":True},{"name":"Operations","header":True},{"name":"Supplier onboarding","start":"2026-06-15","end":"2026-08-28","indent":True,"color":1},{"name":"Warehouse set-up","start":"2026-07-20","end":"2026-09-30","indent":True,"color":1},{"name":"IT","header":True},{"name":"ERP changes","start":"2026-06-08","end":"2026-09-11","indent":True,"color":2},{"name":"Launch","milestone":"2026-10-05","milestone_label":"Launch"}]},"按工作流分组（泳道）的甘特")
add("咨询常用图","funnel","funnel","Only 2.4% of visitors convert to purchases",{"stages":[{"label":"Visitors","value":100000},{"label":"Product views","value":42000},{"label":"Add to cart","value":9800},{"label":"Checkout","value":4100},{"label":"Purchase","value":2400}]},"转化漏斗（逐级转化率）","#")
add("咨询常用图","heatmap","heatmap","Margin pressure concentrated in South / Hardware",{"rows":["Software","Services","Hardware","Devices"],"cols":["North","South","East","West","Central"],"values":[[32,28,30,31,29],[22,18,21,20,19],[12,4,10,9,8],[15,9,14,13,12]]},"两维交叉的强弱分布（热力矩阵）","EBIT margin %")
add("咨询常用图","matrix_2x2","matrix_2x2","Prioritise Cloud and Analytics: attractive and winnable",{"x_title":"Ability to win","y_title":"Market attractiveness","quadrants":["Partner / build","Invest to grow","Deprioritise","Harvest"],"points":[{"x":0.78,"y":0.82,"size":30,"label":"Cloud","focus":True},{"x":0.66,"y":0.68,"size":18,"label":"Analytics","focus":True},{"x":0.3,"y":0.75,"size":22,"label":"AI platforms"},{"x":0.75,"y":0.3,"size":25,"label":"On-prem"},{"x":0.22,"y":0.22,"size":8,"label":"Legacy HW"}]},"战略矩阵 / 二乘二优先级","Bubble size = revenue")
add("咨询常用图","pareto","pareto","Three causes explain 83% of defects",{"categories":["Solder","Alignment","Paint","Packaging","Label","Screws","Other"],"values":[120,85,60,22,15,10,8]},"找出 80/20 主因（帕累托）","# defects")
add("咨询常用图","tornado","tornado","NPV is most sensitive to price and volume",{"base":120,"items":[{"label":"Price ±10%","low":78,"high":162},{"label":"Volume ±15%","low":92,"high":150},{"label":"Input cost ±10%","low":135,"high":104},{"label":"WACC ±1pp","low":138,"high":105},{"label":"Capex ±20%","low":131,"high":110}]},"敏感性分析（龙卷风图）","NPV $M")
add("咨询常用图","tree","tree","ROCE driver tree: asset turnover is the gap",{"root":{"label":"ROCE","value":"14%","children":[{"label":"EBIT margin","value":"9%","op":"×","children":[{"label":"Gross margin","value":"38%"},{"label":"Opex ratio","value":"29%","op":"−"}]},{"label":"Asset turnover","value":"1.6x","op":"","highlight":True,"children":[{"label":"Revenue","value":"$125M"},{"label":"Capital employed","value":"$78M","op":"÷"}]}]}},"指标拆解树 / 驱动树")
add("咨询常用图","kpi_cards","kpi_cards","Q3 at a glance",{"cols":4,"cards":[{"label":"Revenue","value":"$125M","delta":"+14.7% YoY","spark":[75,84,96,109,125]},{"label":"EBIT margin","value":"21.0%","delta":"+2.6 pp","spark":[16,17,18.4,19,21]},{"label":"NPS","value":"45","delta":"+23 pts","spark":[10,15,22,30,45]},{"label":"Churn","value":"2.0%","delta":"+0.3 pp","good":False,"spark":[1.6,1.7,1.7,1.8,2.0]}]},"KPI 仪表板卡片")
add("咨询常用图","bullet","bullet","Revenue and NPS ahead of target, margin behind",{"items":[{"label":"Revenue","unit":"$M","value":125,"target":118,"ranges":[90,110,140]},{"label":"EBIT margin","unit":"%","value":19,"target":21,"ranges":[15,20,25]},{"label":"NPS","unit":"pts","value":45,"target":40,"ranges":[20,35,60]},{"label":"New customers","unit":"k","value":8.2,"target":9,"ranges":[5,8,12]}]},"实际 vs 目标 vs 区间（子弹图）")
add("咨询常用图","progress_bars","progress_bars","Initiatives behind plan: procurement and pricing",{"expected":0.6,"items":[{"label":"Procurement savings","value":4.1,"target":12},{"label":"Pricing uplift","value":3.2,"target":8},{"label":"SG&A reduction","value":6.5,"target":10},{"label":"Footprint","value":2.8,"target":4},{"label":"Working capital","value":15,"target":20}]},"举措/目标完成进度（对照时间进度）","$M")
add("咨询常用图","radar","radar","We lead on product, lag on service",{"axes":["Product","Price","Service","Brand","Distribution","Innovation"],"max":5,"series":[{"name":"Us","values":[4.6,3.2,2.5,3.8,3.5,4.2]},{"name":"Competitor","values":[3.8,3.9,4.1,4.0,3.0,3.1]}]},"多维能力画像对比（雷达）","Score 1–5")
add("咨询常用图","tam_sam_som","tam_sam_som","A $1.2B obtainable market within a $40B TAM",{"levels":[{"label":"TAM","value":40,"display":"$40B","desc":"Global B2B payments software"},{"label":"SAM","value":9,"display":"$9B","desc":"Mid-market, Europe + NA"},{"label":"SOM","value":1.2,"display":"$1.2B","desc":"5-year obtainable at 13% share"}]},"潜在市场规模分层（TAM/SAM/SOM）")
add("咨询常用图","waffle","waffle","Almost two-thirds of spend is addressable",{"items":[{"label":"Addressable","value":64},{"label":"Partly addressable","value":21},{"label":"Locked-in contracts","value":15}]},"直观的百分比（华夫图）","% of spend")

# ===== 四区标注（标题区/数据标签区/强调区/备注说明区）=====
C = lambda text, **k: dict(text=text, **k)
ANN = {
 "column": dict(callouts=[C("Record year: +15% YoY", category="2025", dx=-7.6, dy=0.1)]),
 "stacked": dict(highlight=[{"category":"2025"}], callouts=[C("Seg C now 20% of revenue", category="2025", dx=-6.6, dy=0.0)]),
 "clustered": dict(callouts=[C("North +31% since 2023", anchor="55", dx=-2.6, dy=-0.1)]),
 "column_axis_break": dict(callouts=[C("One-off portfolio deal", category="2023", dx=2.4, dy=0.6)]),
 "stacked_highlight": dict(highlight=[{"category":"2024"}], callouts=[C("New pricing launched", category="2024", dx=-4.8, dy=-0.2)]),
 "waterfall": dict(highlight=[{"category":"Volume"}], callouts=[C("New customers in Asia", category="Volume", dx=0, dy=2.2)]),
 "waterfall_signed": dict(callouts=[C("Commodity spike in H1", category="Input cost", dx=0, dy=2.2)]),
 "waterfall_subtotal": dict(highlight=[{"category":"EBIT"}], callouts=[C("EBIT margin 24%", category="EBIT", dx=1.8, dy=-1.6)]),
 "waterfall_percent": dict(callouts=[C("Premium range +40% volume", category="Mix", dx=0, dy=2.2)]),
 "waterfall_negative_end": dict(callouts=[C("Capex peak: new plant", category="Capex", dx=3.0, dy=-0.6)]),
 "stacked_clustered": dict(callouts=[C("Actual +14% vs plan", anchor="125", dx=-2.6, dy=-0.1)]),
 "column_target": dict(highlight=[{"anchor":"-17%","shape":"circle","w":0.9,"h":0.45}], callouts=[C("Two key accounts lost", anchor="-17%", dx=1.6, dy=-1.15)]),
 "column_xbreak": dict(callouts=[C("Pre-merger baseline", anchor="50", dx=1.9, dy=-1.3)]),
 "bar": dict(highlight=[{"anchor":"515","shape":"circle","w":0.8,"h":0.45}], callouts=[C("Docks: review range", anchor="120", dx=2.6, dy=-0.5)]),
 "bar_sorted": dict(callouts=[C("Bundle with laptops lifted Mice", anchor="310", dx=3.0, dy=0.5)]),
 "butterfly": dict(highlight=[{"anchor":"Camera","shape":"box","w":2.4,"h":0.55}], callouts=[C("21 pp gap on camera", anchor="61", dx=0.6, dy=-0.75)]),
 "dumbbell": dict(callouts=[C("Biggest gain: +23 pts", anchor="45", dx=1.4, dy=0.6)]),
 "football": dict(callouts=[C("Offer inside DCF range", anchor="Offer $25", dx=3.0, dy=0.05)]),
 "line": dict(highlight=[{"at":[0.507,0.27],"shape":"circle","w":0.6,"h":0.6}], callouts=[C("Crossover in May", at=[0.507,0.27], dx=1.2, dy=1.6)]),
 "line_target": dict(callouts=[C("Retention programme launched", at=[0.507,0.378], dx=-2.4, dy=1.9)]),
 "combo": dict(callouts=[C("Margin +6 pp in 4 years", anchor="14%", dx=-5.0, dy=0.1)]),
 "scatter": dict(highlight=[{"anchor":"D","shape":"circle","w":0.6,"h":0.45}], callouts=[C("D: premium and loved", anchor="D", dx=-2.6, dy=0.5)]),
 "bubble": dict(callouts=[C("Largest profit pool", anchor="Business", dx=1.8, dy=1.0)]),
 "pie": dict(callouts=[C("Insulation could cut 30%", anchor="57%", dx=3.6, dy=1.0)]),
 "gantt": dict(callouts=[C("Critical path: DD → SPA", anchor="SPA signed", dx=-2.8, dy=1.25)]),
 "table_harvey": dict(highlight=[{"anchor":"Vendor B","shape":"box","w":1.9,"h":3.2,"oy":1.45}], callouts=[C("Premium justified by fit", anchor="5.1", dx=0.0, dy=2.1)]),
 "variwide": dict(callouts=[C("B2B: small but most profitable", anchor="22%", dx=-2.8, dy=-0.2)]),
 "funnel": dict(highlight=[{"anchor":"↓ 42%","nth":1,"shape":"circle","w":1.2,"h":0.45}], callouts=[C("Checkout UX fix: +0.8 pp", anchor="↓ 42%", nth=1, dx=-1.0, dy=0.9)]),
 "heatmap": dict(highlight=[{"anchor":"Hardware|South","shape":"circle","w":1.4,"h":0.8}], callouts=[C("Price war in South", anchor="Hardware|South", dx=1.0, dy=1.5)]),
 "matrix_2x2": dict(callouts=[C("Invest $40M over 3 years", anchor="Cloud", dx=-2.6, dy=-0.75)]),
 "pareto": dict(highlight=[{"anchor":"83%","shape":"circle","w":0.8,"h":0.42}], callouts=[C("Top 3 causes = 83% of defects", anchor="83%", dx=3.2, dy=0.8)]),
 "tornado": dict(callouts=[C("Pricing power is the key value lever", anchor="162", dx=1.2, dy=2.7)]),
 "tree": dict(callouts=[C("Peers at 2.1x", anchor="Asset turnover", dx=0.3, dy=1.1)]),
 "kpi_cards": dict(highlight=[{"anchor":"2.0%","shape":"circle","w":1.6,"h":0.75}], callouts=[C("Above 1.8% ceiling", anchor="+0.3 pp", dx=0.4, dy=0.9)]),
 "bullet": dict(callouts=[C("Mix headwind in Q3", anchor="19 / 21", dx=-1.6, dy=0.62)]),
 "progress_bars": dict(callouts=[C("Supplier renegotiation delayed", anchor="34%", dx=-2.6, dy=0.55)]),
 "radar": dict(callouts=[C("Service gap = top priority", anchor="Service", dx=1.3, dy=0.8)]),
 "slope": dict(callouts=[C("App share 2.6x", anchor="21  App", dx=0.9, dy=-0.55)]),
 "small_multiples": dict(callouts=[C("Asia: largest\ngrowth engine", anchor="52", dx=-2.1, dy=0.2, w=2.0)]),
 "bar_yoy": dict(highlight=[{"anchor":"-6%","shape":"circle","w":0.8,"h":0.42}], callouts=[C("Price war with private label", anchor="-6%", dx=-2.4, dy=0.55)]),
 "bar_diverging": dict(callouts=[C("Legacy contracts expiring", anchor="-3.4pp", dx=-1.6, dy=-1.1)]),
 "gantt_progress": dict(highlight=[{"anchor":"35%","shape":"circle","w":0.7,"h":0.4}], callouts=[C("Build 3 weeks behind", anchor="35%", dx=1.3, dy=0.8)]),
}
UNITS = {"scatter":"Price $ vs CSAT score","bubble":"Years between purchases vs margin %","gantt":"2026, ISO calendar weeks","gantt_progress":"2026, % complete","gantt_swimlane":"2026","timeline":"2026–2027","table_harvey":"Harvey ball 0–4; cost in $M","tree":"FY2025","kpi_cards":"Q3 2026 vs Q3 2025","bullet":"YTD actual vs target","tam_sam_som":"$B, 2026","pie":"% of household energy use","doughnut":"% of revenue, 2025"}
for c,u,s in E:
    a = ANN.get(s["id"], {})
    if s["id"] == "stacked_highlight": s["decorations"] = []
    s.update(a)
    if not s.get("unit"): s["unit"] = UNITS.get(s["id"], s.get("unit"))
    s.setdefault("footnote", "Figures rounded; illustrative example")
ORDER = []
[ORDER.append(c) for c,_,_ in E if c not in ORDER]
E.sort(key=lambda e: ORDER.index(e[0]))
os.makedirs(D, exist_ok=True); cat = []
for c,u,s in E:
    json.dump(s, open(f"{D}/{s['id']}.json","w"), ensure_ascii=False, indent=2); cat.append({"category":c,"id":s["id"],"type":s["type"],"use":u})
json.dump(cat, open(f"{D}/catalog.json","w"), ensure_ascii=False, indent=2); print(len(cat))
