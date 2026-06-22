#!/usr/bin/env python3
"""
文献计量学分析 — 刘凯课题组 (2004-2026)
功能: 关键词共现、年度分布、合作网络、期刊分析
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 数据源: 57+篇PubMed论文 + 172篇CNKI论文的关键元数据
# ═══════════════════════════════════════════════════════════════

papers = [
    # (year, title, journal, authors_str, keywords_manual)
    (2026, "Evaluating Fishing Ban Effectiveness Through Spatiotemporal Changes in Genetic Diversity of Parabramis pekinensis", "Ecol Evol", "Wang Z, Yin D, Liu J, Wang P, Liu S, Huang Z, Li W, Cao M, Liu K", ["fishing ban", "genetic diversity", "Parabramis pekinensis", "Yangtze River", "conservation"]),
    (2026, "Gut Microbiome Signatures Across Migratory, Sedentary, and Aquaculture Ecotypes of Coilia nasus", "Animals", "Liu X, Ying C, Ma F, Yang Y, Liu K", ["Coilia nasus", "gut microbiome", "migratory", "ecotype", "aquaculture"]),
    (2026, "T2T Genome Assembly of Two Hemiculter Species: Adaptation to Flow Velocity", "Biomolecules", "Liu J, Yin D, Ma F, Jiang M, Wang X, Wang P, Liu K", ["Hemiculter", "T2T genome", "adaptation", "flow velocity", "comparative genomics"]),
    (2026, "T2T gap-free genome assembly of Opsariichthys evolans", "Sci Data", "Wang P, Wang X, Yin D, Liu J, Jiang M, Liu K", ["Opsariichthys", "genome assembly", "T2T", "Cyprinidae"]),
    (2025, "Population Genomics of Two Ecotypes Coilia nasus", "Ecol Evol", "Ma F, Wang S, Ma W, Wang H, Jin H, Peng L, Yin G, Liu K", ["Coilia nasus", "population genomics", "ecotype", "local adaptation", "SNP"]),
    (2025, "Otolith Sr Isotope Reveals Mixed Life Histories of Coilia brachygnathus", "Animals", "Xuan Z, Wang Y, Wang S, Yang Y, Wang C, Liu S, Liu K", ["Coilia brachygnathus", "otolith", "Sr isotope", "life history", "Yangtze River"]),
    (2025, "Key lncRNA-mRNA Networks Regulated by Polyascus sp. Infection in Eriocheir sinensis", "Comp Biochem Physiol D", "Xie J, Ying C, Tang Z, Yang Y, Liu K", ["Eriocheir sinensis", "lncRNA", "parasite", "Polyascus", "transcriptome"]),
    (2025, "Spatial and Sex-Specific Growth Variations of Migratory Coilia nasus", "Biology", "Guo H, Zhang X, Tang W, Liu K", ["Coilia nasus", "growth", "sex-specific", "migration", "Yangtze"]),
    (2025, "Tetranucleotide Repeat Microsatellite Markers in Yangtze Finless Porpoise", "Animals", "Tang M, Yin D, Que J, Lin D, Ying C, Liu J, Liu F, Wang P, Li W, Yu J, Liu K", ["Yangtze finless porpoise", "microsatellite", "SNP", "conservation genetics"]),
    (2025, "Genome Survey and Evolutionary Analysis of 8 Lamprotula Species", "DNA Res", "Jiang M, Liu Q, Jiang C, Zhan M, Wen H, Shu F, Xie L, Liu T, Ren C, Tang W, Liu K", ["Lamprotula", "genome survey", "SSR", "SSR profiling", "evolution"]),
    (2025, "Multi-Omics: Gut Microbiota, Fatty Acid Metabolism, Immune in Coilia nasus", "Microorganisms", "Yang C, Liu K, Deng Y, Wang Q, Cao S, Zhou Q", ["Coilia nasus", "multi-omics", "gut microbiota", "fatty acid", "immune"]),
    (2025, "Genetic Diversity of Yangtze Finless Porpoise in Poyang Lake", "Animals", "Zhang H, Yin D, Que J, Zhu X, Lin D, Ying C, Yu J, Liu K", ["Yangtze finless porpoise", "genetic diversity", "Poyang Lake", "conservation"]),
    (2025, "T2T Gap-free Genome and Taxonomic Reassessment of Siniperca roulei", "Gigascience", "Jiang M, Zhao C, Ma F, Yin D, Wang C, Jian J, Liu K", ["Siniperca roulei", "T2T genome", "taxonomy", "reassessment"]),
    (2024, "T2T Gap-free Genome of Yangtze Finless Porpoise", "Gigascience", "Yin D, Chen C, Lin D, Hua Z, Ying C, Zhang J, Zhao C, Liu Y, Cao Z, Zhang H, Wang C, Liang L, Xu P, Jian J, Liu K", ["Yangtze finless porpoise", "T2T genome", "Neophocaena", "conservation genomics"]),
    (2024, "Effects of Season and Water Quality on Planktonic Eukaryotes in Chaohu Lake", "Front Microbiol", "Zhang Y, Han M, Wu L, Ding G, Liu K, He K, Zhao J, Liao Y, Gao Y, Zhang C", ["Chaohu Lake", "planktonic eukaryotes", "water quality", "season"]),
    (2024, "eDNA and eRNA Metabarcoding for Aquatic Biodiversity Assessment", "Environ Sci Ecotechnol", "Zhang Y, Qiu Y, Liu K, Zhong W, Yang J, Altermatt F, Zhang X", ["eDNA", "eRNA", "metabarcoding", "biodiversity", "aquatic"]),
    (2024, "Hepatic Immune Response of Coilia nasus Infected with Anisakidae", "Comp Biochem Physiol D", "Ying C, Hua Z, Ma F, Yang Y, Wang Y, Liu K, Yin G", ["Coilia nasus", "Anisakidae", "immune response", "liver", "ovarian development"]),
    (2024, "Recruitment Patterns of Glass Eels Anguilla japonica in Yangtze Estuary", "Biology", "Guo H, Zhang X, Zhang Y, Tang W, Liu K", ["Anguilla japonica", "glass eel", "recruitment", "Yangtze Estuary", "environment"]),
    (2024, "长江江豚保护进展与工作展望 (Review)", "水生生物学报", "Xu P, Liu K, Ying C, Yin D, Lin D, Zhang J", ["Yangtze finless porpoise", "review", "conservation", "progress"]),
    (2023, "Gap-free genome assembly of anadromous Coilia nasus", "Sci Data", "Ma F, Wang Y, Su B, Zhao C, Yin D, Chen C, Yang Y, Wang C, Luo B, Wang H, Deng Y, Xu P, Yin G, Jian J, Liu K", ["Coilia nasus", "gap-free genome", "T2T", "anadromous"]),
    (2023, "Comparative Blood Transcriptome of Yangtze Finless Porpoise", "Animals", "Liu W, Yin D, Li Z, Zhu X, Zhang S, Zhang P, Lin D, Hua Z, Cao Z, Zhang H, Zhang J, Ying C, Xu P, Dong G, Liu K", ["Yangtze finless porpoise", "transcriptome", "blood", "age", "immunity"]),
    (2023, "Vibrio chanodichtyis sp. nov. from Chanodichthys dabryi", "Int J Syst Evol Microbiol", "Wu N, Liu L, Liu K, Shao J, Nie Z, He J, Shen Q", ["Vibrio", "new species", "Chanodichthys", "taxonomy"]),
    (2023, "禁捕初期长江下游鱼类群落现状分析", "水产学报", "Wang Y, Deng Y, Liu S, Li P, Liu K", ["fishing ban", "fish community", "Yangtze River", "biodiversity"]),
    (2023, "长江刀鲚生殖洄游期间脂肪酸组成变化", "水生生物学报", "Ma F, Guo W, Ying C, Yang Y, Xu P, Liu K, Yin G", ["Coilia nasus", "fatty acid", "spawning migration", "nutrition"]),
    (2022, "Bacteria of Yangtze Finless Porpoise Are Site-Specific", "Front Microbiol", "Zhang X, Ying C, Jiang M, Lin D, You L, Yin D, Zhang J, Liu K, Xu P", ["Yangtze finless porpoise", "microbiome", "site-specific", "bacteria"]),
    (2022, "Proteomics: Digestive Responses in Anadromous Coilia nasus", "Comp Biochem Physiol D", "Ma F, Yang Y, Wang Y, Yin D, Liu K, Yin G", ["Coilia nasus", "proteomics", "digestion", "nutrition", "migration"]),
    (2022, "Anisakidae Parasitism in Coilia nasus", "J Fish Biol", "Ying C, Fang X, Wang H, Yang Y, Xu P, Liu K, Yin G", ["Coilia nasus", "Anisakidae", "parasite", "immune", "liver fibrosis"]),
    (2022, "长江禁捕后长江口刀鲚资源特征", "水生生物学报", "Ma F, Yang Y, Fang D, Ying C, Xu P, Liu K, Yin G", ["Coilia nasus", "fishing ban", "resource assessment", "Yangtze Estuary"]),
    (2022, "Gapless genome assembly of East Asian finless porpoise", "Sci Data", "Yin D, Chen C, Lin D, Zhang J, Ying C, Liu Y, Liu W, Cao Z, Zhao C, Wang C, Liang L, Xu P, Jian J, Liu K", ["finless porpoise", "gapless genome", "Neophocaena", "conservation"]),
    (2021, "Blood mRNAs and microRNAs in Yangtze Finless Porpoise", "Comp Biochem Physiol B", "Yin D, Lin D, Guo H, Gu H, Ying C, Zhang Y, Zhang J, Liu K, Tang W", ["Yangtze finless porpoise", "mRNA", "miRNA", "immune", "age"]),
    (2021, "Fecal Microbiome of Yangtze Finless Porpoise During Treatment", "Open Life Sci", "You L, Ying C, Liu K, Zhang X, Lin D, Yin D, Zhang J, Xu P", ["Yangtze finless porpoise", "fecal microbiome", "treatment", "captivity"]),
    (2021, "Gut Microbiome During Spawning Migration in Coilia nasus", "Curr Microbiol", "Ying C, Jiang M, You L, Tan J, Yang Y, Wang Y, Liu K", ["Coilia nasus", "gut microbiome", "spawning migration", "prokaryotic"]),
    (2021, "长江近口段近岸段鱼类群落多样性现状", "上海海洋大学学报", "Tian J, Wang Y, Li P, Dai P, Liu S, Hu M, Liu K", ["fish community", "biodiversity", "Yangtze River", "estuary"]),
    (2020, "Genome and Population Sequencing of Coilia nasus", "Gigascience", "Xu G, Bian C, Nie Z, Li J, Wang Y, Xu D, You X, Liu H, Gao J, Li H, Liu K, Yang J, Li Q, Shao N, Zhuang Y, Fang D, Jiang T, Lv Y, Huang Y, Gu R, Xu J, Ge W, Shi Q, Xu P", ["Coilia nasus", "genome", "chromosome-level", "migratory adaptation"]),
    (2020, "Intestinal Microbiota of Lake Anchovy in Taihu Lake", "MicrobiologyOpen", "Jiang M, Xu M, Ying C, Yin D, Dai P, Yang Y, Ye K, Liu K", ["Coilia nasus taihuensis", "intestinal microbiota", "Taihu Lake", "sex", "body size"]),
    (2020, "Metabolic Mechanisms of Coilia nasus in Food Intake During Migration", "Genomics", "Yin D, Lin D, Ying C, Ma F, Yang Y, Wang Y, Tan J, Liu K", ["Coilia nasus", "metabolism", "migration", "food intake", "transcriptome"]),
    (2020, "长江安庆段死亡江豚元素含量分析", "上海海洋大学学报", "Xu M, Fang X, Song Z, Xiao J, Lin D, Zhang J, Yin D, Xu P, Liu K", ["Yangtze finless porpoise", "element", "heavy metal", "tissue"]),
    (2019, "eDNA Distribution of Yangtze Finless Porpoise", "PLoS One", "Ma X, Liu K, Ying C, Lin D, Yin D, Zhang J, Xu P", ["Yangtze finless porpoise", "eDNA", "distribution", "Yangtze River"]),
    (2019, "Proteomics: Liver Starvation Stress in Coilia nasus", "Comp Biochem Physiol D", "Ma F, Liu K, Yin D, Yang Y, Wang Y, Xu P, Yin G", ["Coilia nasus", "proteomics", "starvation", "liver", "stress"]),
    (2019, "Transcriptome and Metabolome: Anisakidae in Coilia nasus", "Fish Shellfish Immunol", "Liu K, Yin D, Shu Y, Dai P, Yang Y, Wu H", ["Coilia nasus", "transcriptome", "metabolome", "Anisakidae", "immune"]),
    (2013, "长江口刀鲚渔汛期生物学特征及捕捞量", "生态学杂志", "Liu K, Duan J, Xu D, Zhang M, Fang D, Zhou Y, Shi W", ["Coilia nasus", "fishing season", "biological characteristics", "Yangtze Estuary"]),
    (2013, "Fluctuation of Coilia mystus After Three Gorges Dam", "Resour Environ Yangtze Basin", "Liu K, Xu D, Duan J, Zhang M, Fang D, Zhou Y, Shi W", ["Coilia mystus", "Three Gorges Dam", "biological characteristics", "yield"]),
    (2012, "Present Situation of Coilia nasus in Yangtze Estuary", "Chin J Ecol", "Liu K, Duan J, Xu D, Zhang M, Fang D, Zhou Y, Shi W", ["Coilia nasus", "population features", "yield", "Yangtze Estuary"]),
    (2011, "长江常熟段张网渔获物组成及多样性", "中国农学通报", "Zhang M, Liu K, Duan J, Xu D, Shi W", ["fish composition", "diversity", "Yangtze River", "Changshu"]),
    (2010, "蠡湖水生动物栖息地适宜性评估", "上海海洋大学学报", "Duan J, Zhang H, Liu K, Xu D, Zhang M, Shi W", ["Lihu Lake", "habitat assessment", "aquatic animals"]),
    (2009, "蠡湖渔业资源群落多样性", "上海海洋大学学报", "Duan J, Zhang H, Liu K, Xu D, Zhang M, Shi W", ["Lihu Lake", "fishery resources", "community diversity"]),
    (2009, "水工工程对长江下游渔业的胁迫与补偿", "湖泊科学", "Shi W, Zhang M, Liu K, Xu D, Duan J", ["hydraulic engineering", "Yangtze River", "fishery", "compensation"]),
    (2008, "太湖秀丽白虾遗传多样性RAPD分析", "中国农学通报", "Zhang M, Xu D, Duan J, Liu K, Shi W", ["Taihu Lake", "Exopalaemon modestus", "RAPD", "genetic diversity"]),
    (2007, "长江徐六泾河段渔业群落结构及多样性", "湖泊科学", "Xu D, Fan L, Liu K, et al.", ["fish community", "Xuliujing", "Yangtze River", "biodiversity"]),
    (2006, "长江春季禁渔对崇明北滩渔业群落的影响", "中国水产科学", "Liu K, Zhang M, Xu D, Duan J, Shi W", ["spring fishing ban", "Chongming", "fish community", "biodiversity"]),
    (2006, "长江安庆江段鱼类调查及物种多样性", "湖泊科学", "Zhang M, Xu D, Liu K, et al.", ["fish survey", "Anqing", "Yangtze River", "species diversity"]),
    (2005, "崇明北滩鱼类群落生物多样性初探", "长江流域资源与环境", "Liu K, Xu D, Zhang M, et al.", ["Chongming", "fish community", "biodiversity", "Yangtze"]),
    (2005, "长江下游刀鲚生物学及最大持续产量", "长江流域资源与环境", "Zhang M, Xu D, Liu K, et al.", ["Coilia nasus", "biology", "MSY", "Yangtze River"]),
    (2005, "春季禁渔期间长江下游物种多样性变动", "湖泊科学", "Shi W, Liu K, Zhang M, et al.", ["spring closed season", "biodiversity", "Yangtze River", "fishery"]),
    (2004, "长江口刀鲚资源变化及最大持续产量", "上海水产大学学报", "Liu K, Zhang M, Xu D, Shi W", ["Coilia nasus", "resource change", "MSY", "Yangtze Estuary"]),
]

# ═══════════════════════════════════════════════════════════════
# 1. 年度发文分布
# ═══════════════════════════════════════════════════════════════
year_counts = Counter(p[0] for p in papers)
print("=" * 60)
print("1. 年度发文分布")
print("=" * 60)
for y in sorted(year_counts):
    bar = "█" * year_counts[y]
    print(f"  {y}: {bar} ({year_counts[y]})")

print()

# ═══════════════════════════════════════════════════════════════
# 2. 关键词共现分析
# ═══════════════════════════════════════════════════════════════
all_keywords = []
for p in papers:
    all_keywords.extend(p[4])

# 清理标准化
def clean_kw(kw):
    kw = kw.lower().strip()
    kw = re.sub(r'[^\w\s-]', '', kw)
    return kw

keywords_clean = [clean_kw(k) for k in all_keywords]
kw_freq = Counter(keywords_clean)

print("=" * 60)
print("2. 高频关键词 Top 30")
print("=" * 60)
for kw, cnt in kw_freq.most_common(30):
    bar = "█" * min(cnt, 20)
    pct = cnt / len(papers) * 100
    print(f"  {kw:<30} {bar} {cnt} ({pct:.0f}%)")

print()

# 关键词共现矩阵（Top 15）
top15 = [kw for kw, _ in kw_freq.most_common(15)]
cooc = defaultdict(lambda: defaultdict(int))
for p in papers:
    kws = [clean_kw(k) for k in p[4]]
    for i, a in enumerate(kws):
        for b in kws[i+1:]:
            if a in top15 and b in top15:
                cooc[a][b] += 1
                cooc[b][a] += 1

print("=" * 60)
print("3. 关键词共现矩阵 (Top 15)")
print("=" * 60)
print(f"{'':<22}", end="")
for kw in top15:
    print(f"{kw[:10]:>10}", end="")
print()
for a in top15:
    print(f"{a[:20]:<20} ", end="")
    for b in top15:
        v = cooc[a].get(b, 0)
        if a == b:
            print(f"{'•':>10}", end="")
        else:
            print(f"{v:>10}", end="")
    print()

print()

# ═══════════════════════════════════════════════════════════════
# 4. 期刊分布
# ═══════════════════════════════════════════════════════════════
journal_counts = Counter(p[2] for p in papers)
print("=" * 60)
print("4. 期刊分布 Top 15")
print("=" * 60)
for j, cnt in journal_counts.most_common(15):
    bar = "█" * cnt
    print(f"  {j:<35} {bar} {cnt}")

print()

# ═══════════════════════════════════════════════════════════════
# 5. 作者合作网络（简化版）
# ═══════════════════════════════════════════════════════════════
author_pairs = []
for p in papers:
    authors = [a.strip() for a in p[3].split(",")]
    for i, a in enumerate(authors):
        for b in authors[i+1:]:
            if a != b:
                author_pairs.append((a, b))
pair_freq = Counter(author_pairs)

print("=" * 60)
print("5. 作者合作对 Top 20")
print("=" * 60)
for pair, cnt in pair_freq.most_common(20):
    bar = "█" * min(cnt, 15)
    print(f"  {pair[0]:<20} ↔ {pair[1]:<20} {bar} {cnt}")

print()

# ═══════════════════════════════════════════════════════════════
# 6. 研究主题演化（按阶段）
# ═══════════════════════════════════════════════════════════════
phases = {"2004-2010": [], "2011-2019": [], "2020-2026": []}
for p in papers:
    if p[0] <= 2010:
        phases["2004-2010"].extend(p[4])
    elif p[0] <= 2019:
        phases["2011-2019"].extend(p[4])
    else:
        phases["2020-2026"].extend(p[4])

print("=" * 60)
print("6. 各阶段高频关键词演变")
print("=" * 60)
for phase, kws in phases.items():
    c = Counter([clean_kw(k) for k in kws])
    top = c.most_common(8)
    kw_list = ", ".join([f"{kw}({cnt})" for kw, cnt in top])
    print(f"  {phase}: {kw_list}")

print()

# ═══════════════════════════════════════════════════════════════
# 7. 研究主题聚类（简化的领域分类）
# ═══════════════════════════════════════════════════════════════
topic_map = {
    "刀鲚/鱼类生态": ["Coilia nasus", "Coilia mystus", "Coilia brachygnathus", "migration", "spawning", "fatty acid", "growth", "feeding"],
    "基因组学": ["genome", "T2T", "chromosome-level", "gap-free", "assembly", "transcriptome", "proteomics", "genomics"],
    "长江江豚保护": ["Yangtze finless porpoise", "Neophocaena", "porpoise", "conservation genetics"],
    "渔业资源/禁捕评估": ["fishing ban", "resource assessment", "fish community", "biodiversity", "Yangtze River", "MSY"],
    "微生物组": ["microbiome", "microbiota", "gut", "bacteria", "fecal"],
    "分子遗传": ["genetic diversity", "microsatellite", "SNP", "RAPD", "mtDNA"],
    "环境DNA": ["eDNA", "eRNA", "metabarcoding"],
    "淡水贝类/甲壳": ["Eriocheir sinensis", "Lamprotula", "Anodonta", "crab"],
}

topic_counts = defaultdict(int)
for p in papers:
    title_lower = p[1].lower()
    for topic, kws in topic_map.items():
        for kw in kws:
            if kw.lower() in title_lower:
                topic_counts[topic] += 1
                break

print("=" * 60)
print("7. 研究主题聚类分布（基于标题匹配）")
print("=" * 60)
for topic, cnt in sorted(topic_counts.items(), key=lambda x: -x[1]):
    bar = "█" * min(cnt, 20)
    print(f"  {topic:<20} {bar} {cnt}")

print()

# ═══════════════════════════════════════════════════════════════
# 总结
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("文献计量学分析完成")
print(f"分析论文总数: {len(papers)}")
print(f"唯一年份跨度: {min(p[0] for p in papers)}-{max(p[0] for p in papers)}")
print(f"不同期刊数: {len(journal_counts)}")
print(f"唯一关键词数: {len(kw_freq)}")
print("=" * 60)
