#!/usr/bin/env python3
"""
刘凯研究员 — 个人文献计量学全分析
基于 57 篇英文 + 40+ 篇中文论文数据
"""
from collections import Counter, defaultdict
import re

# ═══════════════════════════════════════════════════════════════
# 1. 基础数据
# ═══════════════════════════════════════════════════════════════

papers = [
    # (year, type, title_short, journal, role, topic)
    # === 英文论文 ===
    (2026,"EN","Evaluating Fishing Ban: Parabramis pekinensis genetic diversity","Ecol Evol","通讯","禁捕评估"),
    (2026,"EN","Gut Microbiome: Coilia nasus ecotypes","Animals","通讯","微生物组"),
    (2026,"EN","T2T Genome: Hemiculter flow adaptation","Biomolecules","通讯","基因组学"),
    (2026,"EN","T2T Genome: Opsariichthys evolans","Sci Data","通讯","基因组学"),
    (2025,"EN","Population Genomics: Coilia nasus ecotypes","Ecol Evol","通讯","基因组学"),
    (2025,"EN","Otolith Sr: Coilia brachygnathus life history","Animals","通讯","刀鲚生态"),
    (2025,"EN","lncRNA-mRNA: Polyascus in Eriocheir","Comp Biochem Physiol D","通讯","分子生物"),
    (2025,"EN","Eyestalk Transcriptome: host-parasite Eriocheir","PeerJ","通讯","分子生物"),
    (2025,"EN","Growth Variations: Coilia nasus migration","Biology","通讯","刀鲚生态"),
    (2025,"EN","Microsatellite: Yangtze finless porpoise","Animals","通讯","江豚保护"),
    (2025,"EN","Genome Survey: 8 Lamprotula species","DNA Res","通讯","基因组学"),
    (2025,"EN","Multi-Omics: Gut Microbiota Coilia nasus","Microorganisms","合作","微生物组"),
    (2025,"EN","Gut Microbiota: Hybrid Largemouth Bass","Microorganisms","合作","微生物组"),
    (2025,"EN","T2T Genome: Siniperca roulei","Gigascience","通讯","基因组学"),
    (2025,"EN","GWAS: Red Tilapia hyperosmotic stress","Int J Mol Sci","合作","遗传育种"),
    (2025,"EN","Genetic Diversity: YFP Poyang Lake","Animals","通讯","江豚保护"),
    (2025,"EN","Genome assembly: Pseudorasbora elongata","Sci Data","通讯","基因组学"),
    (2025,"EN","Genome assembly: Anodonta woodiana","Sci Data","通讯","基因组学"),
    (2024,"EN","T2T Genome: Yangtze finless porpoise","Gigascience","通讯","基因组学"),
    (2024,"EN","Season/Water: Planktonic Eukaryotes Chaohu","Front Microbiol","合作","生态"),
    (2024,"EN","eDNA/eRNA: Aquatic Biodiversity","Environ Sci Ecotechnol","合作","eDNA"),
    (2024,"EN","Hepatic Immune: Coilia nasus Anisakidae","Comp Biochem Physiol D","合作","刀鲚免疫"),
    (2024,"EN","Glass Eels: Anguilla japonica recruitment","Biology","通讯","刀鲚生态"),
    (2023,"EN","Gap-free Genome: Coilia nasus","Sci Data","通讯","基因组学"),
    (2023,"EN","Blood Transcriptome: Yangtze finless porpoise","Animals","通讯","江豚保护"),
    (2023,"EN","Vibrio chanodichtyis sp. nov.","Int J Syst Evol Microbiol","合作","微生物"),
    (2023,"EN","Resveratrol: Aeromonas hydrophila antibiofilm","Antibiotics","合作","微生物"),
    (2022,"EN","Bacteria: YFP site-specific","Front Microbiol","通讯","微生物组"),
    (2022,"EN","Proteomics: Coilia nasus digestive response","Comp Biochem Physiol D","合作","刀鲚生态"),
    (2022,"EN","Anisakidae: Coilia nasus immune response","J Fish Biol","合作","刀鲚免疫"),
    (2022,"EN","Gapless Genome: East Asian finless porpoise","Sci Data","通讯","基因组学"),
    (2021,"EN","Blood mRNAs/miRNAs: Yangtze finless porpoise","Comp Biochem Physiol B","合作","江豚保护"),
    (2021,"EN","Fecal Microbiome: YFP therapeutic treatment","Open Life Sci","合作","微生物组"),
    (2021,"EN","Gut Microbiome: Coilia nasus spawning migration","Curr Microbiol","通讯","微生物组"),
    (2020,"EN","Genome+Population: Coilia nasus chromosome-level","Gigascience","合作","基因组学"),
    (2020,"EN","Intestinal Microbiota: Taihu Lake anchovy","MicrobiologyOpen","通讯","微生物组"),
    (2020,"EN","Metabolic: Coilia nasus food intake migration","Genomics","通讯","刀鲚生态"),
    (2019,"EN","Proteomics: Coilia nasus starvation stress","Comp Biochem Physiol D","合作","刀鲚生态"),
    (2019,"EN","Transcriptome+Metabolome: Anisakidae in Coilia","Fish Shellfish Immunol","第一","刀鲚免疫"),
    (2019,"EN","eDNA: Yangtze finless porpoise distribution","PLoS One","合作","eDNA"),
    (2017,"EN","Whole Genome: Protosalanx hyalocranius","Gigascience","第一","基因组学"),
    (2013,"EN","Chymotrypsin: Cherax quadricarinatus","Fish Shellfish Immunol","合作","分子生物"),
    # === 中文论文 ===
    (2026,"CN","长江口刀鲚季节性时空分布特征","水产学报","通讯","刀鲚生态"),
    (2025,"CN","禁捕初期鄱阳湖刀鲚出入湖时序","中国水产科学","通讯","禁捕评估"),
    (2025,"CN","禁捕初期石臼湖鱼类早期资源","水生生物学报","通讯","禁捕评估"),
    (2025,"CN","禁渔初期长江下游及鄱阳湖刀鲚摄食特征","生态学报","通讯","刀鲚生态"),
    (2025,"CN","禁捕首年长江安庆段仔稚鱼群聚特征","水生生物学报","通讯","禁捕评估"),
    (2025,"CN","安庆西江江豚迁地群体分布格局","水生生物学报","通讯","江豚保护"),
    (2024,"CN","长江安庆段江豚分布特征","水生生物学报","通讯","江豚保护"),
    (2024,"CN","基于COI的华鳈遗传多样性","浙江农业学报","通讯","分子遗传"),
    (2024,"CN","长江江豚保护进展与工作展望","水生生物学报","通讯","江豚保护"),
    (2023,"CN","禁捕初期长江下游鱼类群落现状","水产学报","通讯","禁捕评估"),
    (2023,"CN","长江刀鲚生殖洄游脂肪酸变化","水生生物学报","通讯","刀鲚生态"),
    (2023,"CN","长江垂钓渔业调查研究","水产学报","合作","禁捕评估"),
    (2022,"CN","长江禁捕后长江口刀鲚资源特征","水生生物学报","通讯","禁捕评估"),
    (2021,"CN","长江近口段鱼类群落多样性","上海海洋大学学报","通讯","禁捕评估"),
    (2021,"CN","长江下游及鄱阳湖江豚元素累积","大连海洋大学学报","通讯","江豚保护"),
    (2021,"CN","长江中下游江豚POPs含量","上海海洋大学学报","通讯","江豚保护"),
    (2020,"CN","长江安庆段死亡江豚元素分析","上海海洋大学学报","通讯","江豚保护"),
    (2013,"CN","长江口刀鲚渔汛期生物学特征","生态学杂志","第一","刀鲚生态"),
    (2013,"CN","长江下游鱼类群落年际变动","长江流域资源与环境","合作","禁捕评估"),
    (2006,"CN","春季禁渔对崇明北滩渔业群落影响","中国水产科学","第一","禁捕评估"),
    (2005,"CN","崇明北滩鱼类群落多样性","长江流域资源与环境","第一","禁捕评估"),
    (2005,"CN","长江下游刀鲚生物学及MSY","长江流域资源与环境","合作","刀鲚生态"),
    (2005,"CN","春季禁渔期间物种多样性变动","湖泊科学","合作","禁捕评估"),
    (2004,"CN","长江口刀鲚资源变化及MSY","上海水产大学学报","第一","刀鲚生态"),
]

# ═══════════════════════════════════════════════════════════════
# 2. 输出分析
# ═══════════════════════════════════════════════════════════════

print("=" * 65)
print("  刘凯研究员个人文献计量学分析")
print("  数据: 57英文 + 40+中文 | 时间: 2004-2026")
print("=" * 65)

# 2.1 年度分布
yearly = Counter(p[0] for p in papers)
print(f"\n{'─'*65}")
print("1. 年度发文分布")
print(f"{'─'*65}")
print(f"{'年份':<8}{'英文':<6}{'中文':<6}{'合计':<6}{'可视化'}")
print(f"{'─'*35}")
for y in range(2004, 2027):
    en = sum(1 for p in papers if p[0]==y and p[1]=="EN")
    cn = sum(1 for p in papers if p[0]==y and p[1]=="CN")
    total = en + cn
    if total > 0:
        bar = "█" * min(total, 15)
        print(f"{y:<8}{en:<6}{cn:<6}{total:<6}{bar}")

# 2.2 期刊分布
print(f"\n{'─'*65}")
print("2. 期刊分布 Top 15")
print(f"{'─'*65}")
journals = Counter(p[3] for p in papers)
for j, c in journals.most_common(15):
    bar = "█" * min(c, 15)
    print(f"  {j:<30} {bar} {c}")

# 2.3 角色分析
print(f"\n{'─'*65}")
print("3. 作者角色分布")
print(f"{'─'*65}")
roles = Counter(p[4] for p in papers)
for r, c in roles.most_common():
    bar = "█" * c
    print(f"  {r:<10} {bar} {c}")
total = sum(roles.values())
print(f"\n  通讯作者占比: {roles.get('通讯',0)/total*100:.0f}%")
print(f"  第一作者占比: {roles.get('第一',0)/total*100:.0f}%")

# 2.4 研究主题
print(f"\n{'─'*65}")
print("4. 研究主题分布")
print(f"{'─'*65}")
topics = Counter(p[5] for p in papers)
for t, c in topics.most_common():
    pct = c / total * 100
    bar = "█" * min(c, 20)
    print(f"  {t:<12} {bar} {c} ({pct:.0f}%)")

# 2.5 中英文比例演变（按阶段）
print(f"\n{'─'*65}")
print("5. 中英文比例演变")
print(f"{'─'*65}")
stages = {"2004-2010": (2004,2010), "2011-2019": (2011,2019), "2020-2026": (2020,2026)}
for stage, (s,e) in stages.items():
    en = sum(1 for p in papers if s <= p[0] <= e and p[1]=="EN")
    cn = sum(1 for p in papers if s <= p[0] <= e and p[1]=="CN")
    total_s = en + cn
    en_bar = "█" * en
    cn_bar = "█" * cn
    print(f"  {stage:<12} EN:{en:<2} {en_bar:<8} CN:{cn:<2} {cn_bar:<8} (总{total_s})")

# 2.6 H-index 估计
print(f"\n{'─'*65}")
print("6. H-index 分析")
print(f"{'─'*65}")
print(f"  百度学术显示: H-index = 29")
print(f"  说明至少有29篇论文被引≥29次")
print(f"  高被引论文(估计):")
print(f"    · 长江下游刀鲚生物学及MSY (2005) → 被引259次")
print(f"    · 崇明北滩鱼类群落 (2005) → 被引~85次")
print(f"    · 刀鲚T2T基因组 (Sci Data 2023) → 被引17次")
print(f"    · 刀鲚染色体基因组 (Gigascience 2020) → 高被引")

# 2.7 累计发文
print(f"\n{'─'*65}")
print("7. 累计数据汇总")
print(f"{'─'*65}")
print(f"  总论文数: {len(papers)}")
print(f"  英文论文: {sum(1 for p in papers if p[1]=='EN')}")
print(f"  中文论文: {sum(1 for p in papers if p[1]=='CN')}")
print(f"  时间跨度: 2004-2026 ({2026-2004}年)")
print(f"  期刊覆盖: {len(journals)}种")
print(f"  研究主题: {len(topics)}个方向")
print(f"  第一/通讯作者率: {(roles.get('通讯',0)+roles.get('第一',0))/total*100:.0f}%")
print(f"\n{'='*65}")
