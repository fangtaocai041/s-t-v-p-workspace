#!/usr/bin/env python3
"""
为刘凯课题组生成 Zotero 导入用 BibTeX 文件
包含所有英文/中文论文 + 已下载全文的文件路径
"""

import os, re

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
BIB_FILE = os.path.join(OUTPUT_DIR, "课题组_刘凯_全部文献.bib")
PDF_DIR_EN = os.path.join(OUTPUT_DIR, "02_文献PDF", "英文论文")
PDF_DIR_CN = os.path.join(OUTPUT_DIR, "02_文献PDF", "中文论文")

def safe_title(t):
    t = re.sub(r'[{}&%#$]', '', t)
    t = t.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
    return t.strip()

def safe_author(authors):
    """Zotero BibTeX author format: Last, First and Last, First"""
    result = []
    for a in authors:
        parts = a.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            first = ' '.join(parts[:-1])
            result.append(f"{last}, {first}")
        else:
            result.append(a.strip())
    return ' and '.join(result)

entries = []

# ========================================
# 英文论文 (40篇)
# ========================================
en_papers = [
    {
        "citekey": "LiuK_E01_2026",
        "title": "Evaluating Fishing Ban Effectiveness Through Spatiotemporal Changes in Genetic Diversity of Parabramis pekinensis",
        "author": ["Wang, Zhiwen", "Yin, Denghua", "Liu, Jie", "Wang, Pan", "Liu, Silei", "Huang, Zhongjia", "Li, Wenwen", "Cao, Mingxue", "Liu, Kai"],
        "journal": "Ecology and Evolution",
        "year": 2026, "volume": "16", "number": "4", "pages": "e72775",
        "doi": "10.1002/ece3.72775", "pmcid": "PMC13054008",
        "file": "E01_Evaluating_Fishing_Ban_Effectiveness_Parabramis_pekinensis.md"
    },
    {
        "citekey": "LiuK_E02_2026",
        "title": "Gut Microbiome Signatures Across Migratory, Sedentary, and Aquaculture Ecotypes of Coilia nasus",
        "author": ["Liu, Xiao", "Ying, Congping", "Ma, Fengjiao", "Yang, Yanping", "Liu, Kai"],
        "journal": "Animals",
        "year": 2026, "volume": "16", "number": "5", "pages": "840",
        "doi": "10.3390/ani16050840", "pmcid": "PMC13145378",
        "file": "E02_Gut_Microbiome_Signatures_Across_Migratory,_Sedentary,_and_Aquaculture_Ecotypes_of_Coilia_nasus.txt"
    },
    {
        "citekey": "LiuK_E03_2026",
        "title": "Telomere-to-Telomere Genome Assembly of Two Hemiculter Species Provide Insights into Genomic and Morphometric Bases of Adaptation to Flow Velocity",
        "author": ["Liu, Jie", "Yin, Denghua", "Ma, Fengjiao", "Jiang, Min", "Wang, Xinyue", "Wang, Pan", "Liu, Kai"],
        "journal": "Biomolecules",
        "year": 2026, "volume": "16", "number": "1", "pages": "83",
        "doi": "10.3390/biom16010083", "pmcid": "PMC12838669",
        "file": "E03_T2T_Genome_Hemiculter.md"
    },
    {
        "citekey": "LiuK_E04_2026",
        "title": "Telomere-to-telomere gap-free genome assembly of Opsariichthys evolans",
        "author": ["Wang, Pan", "Wang, Xinyue", "Yin, Denghua", "Liu, Jie", "Jiang, Min", "Liu, Kai"],
        "journal": "Scientific Data",
        "year": 2026, "volume": "13", "number": "1", "pages": "263",
        "doi": "10.1038/s41597-026-06588-7", "pmcid": "PMC12917274",
        "file": "E04_T2T_Opsariichthys_evolans.md"
    },
    {
        "citekey": "LiuK_E05_2025",
        "title": "Population Genomics Provides Novel Insights Into Evolutionary Relationships and Local Adaptation of Two Ecotypes Coilia nasus",
        "author": ["Ma, Fengjiao", "Wang, Sheng", "Ma, Wenzhi", "Wang, Hui", "Jin, Haotian", "Peng, Legen", "Yin, Guojun", "Liu, Kai"],
        "journal": "Ecology and Evolution",
        "year": 2025, "volume": "15", "number": "12", "pages": "e72815",
        "doi": "10.1002/ece3.72815", "pmcid": "PMC12723445",
        "file": "E05_Population_Genomics_Coilia_nasus.md"
    },
    {
        "citekey": "LiuK_E06_2025",
        "title": "Otolith Sr Isotope Reveals Mixed Life Histories of Coilia brachygnathus in the Middle-Lower Yangtze River Floodplain",
        "author": ["Xuan, Z", "Wang, Y", "Wang, S", "Yang, Y", "Wang, C", "Liu, S", "Liu, Kai"],
        "journal": "Animals",
        "year": 2025, "volume": "15", "number": "23", "pages": "3434",
        "doi": "10.3390/ani15233434", "pmcid": "PMC12691453",
        "file": "E06_Otolith_Sr_Isotope_Reveals_Mixed_Life_Histories_of_Coilia_brachygnathus.txt"
    },
    {
        "citekey": "LiuK_E07_2025",
        "title": "Key lncRNA-mRNA Networks Regulated by Polyascus sp. Infection in Eriocheir sinensis",
        "author": ["Xie, Jing", "Ying, Congping", "Tang, Zhen", "Yang, Yanping", "Liu, Kai"],
        "journal": "Comp Biochem Physiol D",
        "year": 2025, "volume": "57", "pages": "101693",
        "doi": "10.1016/j.cbd.2025.101693",
        "file": None
    },
    {
        "citekey": "LiuK_E08_2025",
        "title": "Eyestalk Transcriptome: Sexually Dimorphic Host-Parasite Interactions of Polyascus sp. in Eriocheir sinensis",
        "author": ["Xie, Jing", "Ying, Congping", "Tang, Zhen", "Yang, Yanping", "Liu, Kai"],
        "journal": "PeerJ",
        "year": 2025, "volume": "13", "pages": "e20089",
        "doi": "10.7717/peerj.20089", "pmcid": "PMC12510255",
        "file": None
    },
    {
        "citekey": "LiuK_E09_2025",
        "title": "Spatial and Sex-Specific Growth Variations of Migratory Coilia nasus",
        "author": ["Guo, Hongyi", "Zhang, Xuguang", "Tang, Wenqiao", "Liu, Kai"],
        "journal": "Biology",
        "year": 2025, "volume": "14", "number": "9", "pages": "1211",
        "doi": "10.3390/biology14091211", "pmcid": "PMC12467153",
        "file": None
    },
    {
        "citekey": "LiuK_E10_2025",
        "title": "Tetranucleotide Repeat Microsatellite Markers in Yangtze Finless Porpoise",
        "author": ["Tang, Mengting", "Yin, Denghua", "Que, Jianglong", "Lin, Danqing", "Ying, Congping", "Liu, Jie", "Liu, Fangning", "Wang, Pan", "Li, Wenwen", "Yu, Jinxiang", "Liu, Kai"],
        "journal": "Animals",
        "year": 2025, "volume": "15", "number": "17", "pages": "2603",
        "doi": "10.3390/ani15172603", "pmcid": "PMC12427282",
        "file": None
    },
    {
        "citekey": "LiuK_E11_2025",
        "title": "Genome Survey and Evolutionary Analysis of 8 Lamprotula Species",
        "author": ["Jiang, Min", "Liu, Qi", "Jiang, Chao", "Zhan, Mingfei", "Wen, Haibo", "Shu, Fengyue", "Xie, Lingli", "Liu, Tengteng", "Ren, Chenliang", "Tang, Wenqiao", "Liu, Kai"],
        "journal": "DNA Research",
        "year": 2025, "volume": "32", "number": "5", "pages": "dsaf020",
        "doi": "10.1093/dnares/dsaf020", "pmcid": "PMC12454935",
        "file": None
    },
    {
        "citekey": "LiuK_E12_2025",
        "title": "Multi-Omics: Gut Microbiota, Fatty Acid Metabolism, and Immune in Coilia nasus",
        "author": ["Yang, C", "Liu, Kai", "Deng, Y", "Wang, Q", "Cao, S", "Zhou, Q"],
        "journal": "Microorganisms",
        "year": 2025, "volume": "13", "number": "7", "pages": "1711",
        "doi": "10.3390/microorganisms13071711",
        "file": None
    },
    {
        "citekey": "LiuK_E13_2025",
        "title": "Gut Microbiota Contribute to Heterosis in Hybrid Largemouth Bass",
        "author": ["Hua, J", "Wang, Q", "Tao, Y", "Sun, H", "Lu, S", "Zhuge, Y", "Chen, W", "Liu, Kai", "He, J", "Qiang, J"],
        "journal": "Microorganisms",
        "year": 2025, "volume": "13", "number": "7", "pages": "1449",
        "doi": "10.3390/microorganisms13071449", "pmcid": "PMC12298284",
        "file": "E13_Gut_Microbiota_Contribute_to_Heterosis_in_Hybrid_Largemouth_Bass.txt"
    },
    {
        "citekey": "LiuK_E14_2025",
        "title": "T2T Gap-free Reference Genome and Taxonomic Reassessment of Siniperca roulei",
        "author": ["Jiang, M", "Zhao, C", "Ma, F", "Yin, D", "Wang, C", "Jian, J", "Liu, Kai"],
        "journal": "Gigascience",
        "year": 2025, "volume": "14", "pages": "giaf068",
        "doi": "10.1093/gigascience/giaf068",
        "file": None
    },
    {
        "citekey": "LiuK_E15_2025",
        "title": "GWAS and RNA-Seq: Growth Traits in Red Tilapia Under Hyperosmotic Stress",
        "author": ["Jiang, B", "Tao, Y", "Tao, W", "Lu, S", "Badran, MF", "Xu, P", "Qiang, J", "Liu, Kai"],
        "journal": "Int J Mol Sci",
        "year": 2025, "volume": "26", "number": "13", "pages": "6492",
        "doi": "10.3390/ijms26136492",
        "file": None
    },
    {
        "citekey": "LiuK_E16_2025",
        "title": "Genetic Diversity of Yangtze Finless Porpoise in Poyang Lake",
        "author": ["Zhang, H", "Yin, D", "Que, J", "Zhu, X", "Lin, D", "Ying, C", "Yu, J", "Liu, Kai"],
        "journal": "Animals",
        "year": 2025, "volume": "15", "number": "13", "pages": "1838",
        "doi": "10.3390/ani15131838",
        "file": None
    },
    {
        "citekey": "LiuK_E17_2024",
        "title": "T2T Gap-free Genome of Endangered Yangtze Finless Porpoise and East Asian Finless Porpoise",
        "author": ["Yin, D", "Chen, C", "Lin, D", "Hua, Z", "Ying, C", "Zhang, J", "Zhao, C", "Liu, Y", "Cao, Z", "Zhang, H", "Wang, C", "Liang, L", "Xu, P", "Jian, J", "Liu, Kai"],
        "journal": "Gigascience",
        "year": 2024, "volume": "13", "pages": "giae067",
        "doi": "10.1093/gigascience/giae067",
        "file": None
    },
    {
        "citekey": "LiuK_E18_2024",
        "title": "Effects of Season and Water Quality on Planktonic Eukaryotes in Chaohu Lake",
        "author": ["Zhang, Y", "Han, M", "Wu, L", "Ding, G", "Liu, Kai", "He, K", "Zhao, J", "Liao, Y", "Gao, Y", "Zhang, C"],
        "journal": "Front Microbiol",
        "year": 2024, "volume": "15", "pages": "1424277",
        "doi": "10.3389/fmicb.2024.1424277",
        "file": None
    },
    {
        "citekey": "LiuK_E19_2024",
        "title": "Evaluating eDNA and eRNA Metabarcoding for Aquatic Biodiversity Assessment",
        "author": ["Zhang, Y", "Qiu, Y", "Liu, Kai", "Zhong, W", "Yang, J", "Altermatt, F", "Zhang, X"],
        "journal": "Environ Sci Ecotechnol",
        "year": 2024, "volume": "21", "pages": "100441",
        "doi": "10.1016/j.ese.2024.100441",
        "file": None
    },
    {
        "citekey": "LiuK_E20_2024",
        "title": "Hepatic Immune Response of Coilia nasus Infected with Anisakidae During Ovarian Development",
        "author": ["Ying, C", "Hua, Z", "Ma, F", "Yang, Y", "Wang, Y", "Liu, Kai", "Yin, G"],
        "journal": "Comp Biochem Physiol D",
        "year": 2024, "volume": "52", "pages": "101261",
        "doi": "10.1016/j.cbd.2024.101261",
        "file": None
    },
    {
        "citekey": "LiuK_E21_2024",
        "title": "Recruitment Patterns and Environmental Sensitivity of Glass Eels (Anguilla japonica) in the Yangtze Estuary",
        "author": ["Guo, H", "Zhang, X", "Zhang, Y", "Tang, W", "Liu, Kai"],
        "journal": "Biology",
        "year": 2024, "volume": "13", "number": "1", "pages": "56",
        "doi": "10.3390/biology13010056",
        "file": None
    },
    {
        "citekey": "LiuK_E22_2023",
        "title": "Comparative Blood Transcriptome of Yangtze Finless Porpoise",
        "author": ["Liu, W", "Yin, D", "Li, Z", "Zhu, X", "Zhang, S", "Zhang, P", "Lin, D", "Hua, Z", "Cao, Z", "Zhang, H", "Zhang, J", "Ying, C", "Xu, P", "Dong, G", "Liu, Kai"],
        "journal": "Animals",
        "year": 2023, "volume": "14", "number": "2", "pages": "199",
        "doi": "10.3390/ani14020199",
        "file": None
    },
    {
        "citekey": "LiuK_E23_2023",
        "title": "Vibrio chanodichtyis sp. nov. from Intestine of Chanodichthys dabryi",
        "author": ["Wu, N", "Liu, L", "Liu, Kai", "Shao, J", "Nie, Z", "He, J", "Shen, Q"],
        "journal": "Int J Syst Evol Microbiol",
        "year": 2023, "volume": "73", "number": "11", "pages": "006117",
        "doi": "10.1099/ijsem.0.006117",
        "file": None
    },
    {
        "citekey": "LiuK_E24_2023",
        "title": "In Vitro Antibiofilm Activity of Resveratrol against Aeromonas hydrophila",
        "author": ["Qin, T", "Chen, K", "Xi, B", "Pan, L", "Xie, J", "Lu, L", "Liu, Kai"],
        "journal": "Antibiotics",
        "year": 2023, "volume": "12", "number": "4", "pages": "686",
        "doi": "10.3390/antibiotics12040686",
        "file": None
    },
    {
        "citekey": "LiuK_E25_2022",
        "title": "Bacteria of Yangtze Finless Porpoise Are Site-Specific",
        "author": ["Zhang, X", "Ying, C", "Jiang, M", "Lin, D", "You, L", "Yin, D", "Zhang, J", "Liu, Kai", "Xu, P"],
        "journal": "Front Microbiol",
        "year": 2022, "volume": "13", "pages": "1006251",
        "doi": "10.3389/fmicb.2022.1006251", "pmcid": "PMC12492875",
        "file": "E25_Bacteria_of_Yangtze_Finless_Porpoise_Are_Site-Specific.txt"
    },
    {
        "citekey": "LiuK_E26_2022",
        "title": "A Proteomics Approach Reveals Digestive and Nutritional Responses in Anadromous Coilia nasus",
        "author": ["Ma, F", "Yang, Y", "Wang, Y", "Yin, D", "Liu, Kai", "Yin, G"],
        "journal": "Comp Biochem Physiol D",
        "year": 2022, "volume": "43", "pages": "100995",
        "doi": "10.1016/j.cbd.2022.100995",
        "file": None
    },
    {
        "citekey": "LiuK_E27_2022",
        "title": "Anisakidae Parasitism Activated Immune Response in Coilia nasus",
        "author": ["Ying, C", "Fang, X", "Wang, H", "Yang, Y", "Xu, P", "Liu, Kai", "Yin, G"],
        "journal": "J Fish Biol",
        "year": 2022, "volume": "100", "number": "4", "pages": "958-969",
        "doi": "10.1111/jfb.15027",
        "file": None
    },
    {
        "citekey": "LiuK_E28_2022",
        "title": "Metabolic Mechanisms of Coilia nasus in Food Intake During Migration",
        "author": ["Yin, D", "Lin, D", "Ying, C", "Ma, F", "Yang, Y", "Wang, Y", "Tan, J", "Liu, Kai"],
        "journal": "Genomics",
        "year": 2022, "volume": "112", "number": "5", "pages": "3294-3305",
        "doi": "10.1016/j.ygeno.2020.05.027",
        "file": None
    },
    {
        "citekey": "LiuK_E29_2021",
        "title": "Integrated Analysis of Blood mRNAs and microRNAs in Yangtze Finless Porpoise",
        "author": ["Yin, D", "Lin, D", "Guo, H", "Gu, H", "Ying, C", "Zhang, Y", "Zhang, J", "Liu, Kai", "Tang, W"],
        "journal": "Comp Biochem Physiol B",
        "year": 2021, "volume": "256", "pages": "110635",
        "doi": "10.1016/j.cbpb.2021.110635", "pmcid": "PMC12547954",
        "file": "E29_Integrated_Analysis_of_Blood_mRNAs_and_microRNAs_in_Yangtze_Finless_Porpoise.txt"
    },
    {
        "citekey": "LiuK_E30_2021",
        "title": "Changes in Fecal Microbiome of Yangtze Finless Porpoise",
        "author": ["You, L", "Ying, C", "Liu, Kai", "Zhang, X", "Lin, D", "Yin, D", "Zhang, J", "Xu, P"],
        "journal": "Open Life Sci",
        "year": 2021, "volume": "15", "number": "1", "pages": "296-310",
        "doi": "10.1515/biol-2020-0032",
        "file": None
    },
    {
        "citekey": "LiuK_E31_2021",
        "title": "Variations of Gut Prokaryotic Microbiome During Spawning Migration in Coilia nasus",
        "author": ["Ying, CP", "Jiang, M", "You, L", "Tan, JH", "Yang, YP", "Wang, YP", "Liu, Kai"],
        "journal": "Curr Microbiol",
        "year": 2021, "volume": "77", "number": "10", "pages": "2802-2812",
        "doi": "10.1007/s00284-020-02088-y",
        "file": None
    },
    {
        "citekey": "LiuK_E32_2017",
        "title": "Whole genome sequencing of Chinese clearhead icefish, Protosalanx hyalocranius",
        "author": ["Liu, Kai", "Xu, D", "Li, J", "Bian, C", "Duan, J", "Zhou, Y", "Zhang, M", "You, X", "You, Y", "Chen, J", "Yu, H", "Xu, G", "Fang, DA", "Qiang, J", "Jiang, S", "He, J", "Xu, J", "Shi, Q", "Zhang, Z", "Xu, P"],
        "journal": "Gigascience",
        "year": 2017, "volume": "6", "number": "4", "pages": "1-6",
        "doi": "10.1093/gigascience/giw012", "pmcid": "PMC12266836",
        "file": "E32_Whole_genome_sequencing_of_Chinese_clearhead_icefish,_Protosalanx_hyalocranius.txt"
    },
    {
        "citekey": "LiuK_E33_2020",
        "title": "Genome and Population Sequencing of Coilia nasus — Chromosome-level Assembly",
        "author": ["Xu, G", "Bian, C", "Nie, Z", "Liu, Kai", "Xu, P"],
        "journal": "Gigascience",
        "year": 2020, "volume": "9", "number": "1", "pages": "giz157",
        "doi": "10.1093/gigascience/giz157",
        "file": None
    },
    {
        "citekey": "LiuK_E34_2019",
        "title": "The Intestinal Microbiota of Lake Anchovy in Taihu Lake",
        "author": ["Jiang, M", "Xu, M", "Ying, C", "Yin, D", "Dai, P", "Yang, Y", "Ye, K", "Liu, Kai"],
        "journal": "MicrobiologyOpen",
        "year": 2019, "volume": "8", "number": "11", "pages": "e874",
        "doi": "10.1002/mbo3.874", "pmcid": "PMC11433935",
        "file": "E34_The_Intestinal_Microbiota_of_Lake_Anchovy_in_Taihu_Lake.txt"
    },
    {
        "citekey": "LiuK_E35_2019",
        "title": "Investigating Distribution of Yangtze Finless Porpoise Using eDNA",
        "author": ["Ma, X", "Liu, Kai", "Ying, C", "Lin, D", "Yin, D", "Zhang, J", "Xu, P"],
        "journal": "PLoS One",
        "year": 2019, "volume": "14", "number": "8", "pages": "e0221120",
        "doi": "10.1371/journal.pone.0221120",
        "file": None
    },
    {
        "citekey": "LiuK_E36_2019",
        "title": "A Proteomics Approach to Liver Starvation Stress in Coilia nasus",
        "author": ["Ma, F", "Liu, Kai", "Yin, D", "Yang, Y", "Wang, Y", "Xu, P", "Yin, G"],
        "journal": "Comp Biochem Physiol D",
        "year": 2019, "volume": "30", "pages": "133-143",
        "doi": "10.1016/j.cbd.2019.02.005", "pmcid": "PMC11547106",
        "file": "E36_Proteomics_Approach_to_Liver_Starvation_Stress_in_Coilia_nasus.txt"
    },
    # 数据论文
    {
        "citekey": "LiuK_D1_2023",
        "title": "Gap-free genome assembly of anadromous Coilia nasus",
        "author": ["Liu, Kai"],
        "journal": "Scientific Data",
        "year": 2023, "volume": "10", "number": "1", "pages": "360",
        "doi": "10.1038/s41597-023-02278-w",
        "file": None
    },
    {
        "citekey": "LiuK_D2_2022",
        "title": "Gapless genome assembly of East Asian finless porpoise",
        "author": ["Liu, Kai"],
        "journal": "Scientific Data",
        "year": 2022, "volume": "9", "number": "1", "pages": "765",
        "doi": "10.1038/s41597-022-01868-4",
        "file": None
    },
    {
        "citekey": "LiuK_D3_2025",
        "title": "Chromosome-level genome assembly of Anodonta woodiana",
        "author": ["Liu, Kai"],
        "journal": "Scientific Data",
        "year": 2025, "volume": "12", "number": "1", "pages": "731",
        "doi": "10.1038/s41597-025-05078-6",
        "file": None
    },
    {
        "citekey": "LiuK_D4_2025",
        "title": "Chromosome-level genome assembly of Pseudorasbora elongata",
        "author": ["Liu, Kai"],
        "journal": "Scientific Data",
        "year": 2025, "volume": "12", "number": "1", "pages": "554",
        "doi": "10.1038/s41597-025-04890-4",
        "file": None
    },
]

# 中文论文精简版
cn_papers = [
    {"citekey": "LiuK_R1_2024", "title": "长江江豚保护进展与工作展望", "author": ["徐跑", "刘凯", "应聪萍", "尹登花", "蔺丹清", "张家路"], "journal": "水生生物学报", "year": 2024, "volume": "48", "number": "6", "pages": "1077-1084", "doi": "10.7541/2024.2024.0027"},
    {"citekey": "LiuK_C01_2025", "title": "安庆西江长江江豚迁地群体分布格局及影响因子", "author": ["梁海英", "蔺丹清", "严燕", "陈宇宽", "张四刚", "应聪萍", "王炜祺", "李凡", "刘凯"], "journal": "水生生物学报", "year": 2025, "volume": "49", "number": "7", "pages": "1-12"},
    {"citekey": "LiuK_C02_2025", "title": "禁捕初期鄱阳湖江湖通道鱼类早期资源时空特征", "author": ["沈英东", "刘凯"], "journal": "湖泊科学", "year": 2025},
    {"citekey": "LiuK_C03_2025", "title": "禁捕初期鄱阳湖刀鲚出入湖时序特征及环境影响因子", "author": ["刘凯"], "journal": "中国水产科学", "year": 2025},
    {"citekey": "LiuK_C04_2026", "title": "长江口及邻近海域刀鲚的季节性时空分布特征", "author": ["郭弘艺", "张旭光", "刘守海", "唐文乔", "刘凯"], "journal": "水产学报", "year": 2026, "volume": "50", "number": "4", "pages": "049318"},
    {"citekey": "LiuK_C05_2023", "title": "禁捕初期长江下游鱼类群落现状分析及禁渔效果初步评估", "author": ["王银平", "邓艳敏", "刘思磊", "李佩杰", "刘凯"], "journal": "水产学报", "year": 2023, "volume": "47", "number": "2", "pages": "029315", "doi": "10.11964/jfc.20220913698"},
    {"citekey": "LiuK_C06_2023", "title": "长江刀鲚生殖洄游期间脂肪酸组成及含量变化分析", "author": ["马凤娇", "郭文君", "应聪萍", "杨彦平", "徐跑", "刘凯", "殷国俊"], "journal": "水生生物学报", "year": 2023, "volume": "47", "number": "1", "pages": "156-167", "doi": "10.7541/2023.2022.0047"},
    {"citekey": "LiuK_C07_2022", "title": "长江禁捕后长江口刀鲚资源特征", "author": ["马凤娇", "杨彦平", "方弟安", "应聪萍", "徐跑", "刘凯", "殷国俊"], "journal": "水生生物学报", "year": 2022, "volume": "46", "number": "10", "pages": "1580-1590", "doi": "10.7541/2023.2022.0070"},
    {"citekey": "LiuK_C08_2021", "title": "长江近口段近岸段鱼类群落多样性现状", "author": ["田佳丽", "王银平", "李佩杰", "代培", "刘思磊", "胡敏琦", "刘凯"], "journal": "上海海洋大学学报", "year": 2021, "volume": "30", "number": "2", "pages": "320-330", "doi": "10.12024/jsou.20200202921"},
    {"citekey": "LiuK_C09_2021", "title": "长江下游及鄱阳湖长江江豚体内元素累积特征比较", "author": ["阚雪洋", "尹登花", "方昕", "蔺丹清", "应聪萍", "徐跑", "刘凯"], "journal": "大连海洋大学学报", "year": 2021},
]

# 学位论文
thesis_papers = [
    {"citekey": "LiuK_T01_2021", "title": "刀鲚肠道微生物群落特征及其对异尖线虫感染的免疫响应", "author": ["应聪萍"], "school": "南京农业大学", "year": 2021, "type": "master"},
    {"citekey": "LiuK_T02_2022", "title": "长江江豚转录组及基因组学研究", "author": ["尹登花"], "school": "南京农业大学", "year": 2022, "type": "master"},
    {"citekey": "LiuK_T03_2021", "title": "长江近口段近岸段鱼类群落多样性现状研究", "author": ["田佳丽"], "school": "上海海洋大学", "year": 2021, "type": "master"},
    {"citekey": "LiuK_T04_2023", "title": "禁捕初期长江下游鱼类群落现状分析及禁渔效果评估", "author": ["王银平"], "school": "上海海洋大学", "year": 2023, "type": "master"},
    {"citekey": "LiuK_T05_2022", "title": "长江下游及鄱阳湖长江江豚体内元素累积特征比较研究", "author": ["阚雪洋"], "school": "南京农业大学", "year": 2022, "type": "master"},
    {"citekey": "LiuK_T06_2023", "title": "长江下游鱼类群落时空分布特征研究", "author": ["刘思磊"], "school": "上海海洋大学", "year": 2023, "type": "master"},
    {"citekey": "LiuK_T07_2023", "title": "长江近口段鱼类群落多样性及禁捕初期变化", "author": ["李佩杰"], "school": "上海海洋大学", "year": 2023, "type": "master"},
    {"citekey": "LiuK_T08_2022", "title": "长江下游渔业资源时空变化研究", "author": ["代培"], "school": "上海海洋大学", "year": 2022, "type": "master"},
    {"citekey": "LiuK_T09_2022", "title": "长江口鱼类群落粒径结构及稳定性研究", "author": ["胡敏琦"], "school": "上海海洋大学", "year": 2022, "type": "master"},
    {"citekey": "LiuK_T10_2021", "title": "长江安庆段死亡长江江豚元素含量分析", "author": ["许萌原"], "school": "南京农业大学", "year": 2021, "type": "master"},
    {"citekey": "LiuK_T11_2025", "title": "禁捕初期鄱阳湖江湖通道鱼类早期资源时空特征", "author": ["沈英东"], "school": "南京农业大学", "year": 2025, "type": "master"},
    {"citekey": "LiuK_T12_2024", "title": "长江安庆段长江江豚分布特征及其影响因子探究", "author": ["陈宇宽"], "school": "南京农业大学", "year": 2024, "type": "master"},
]

# 写入BibTeX
lines = []
lines.append("% BibTeX 导入文件 — 刘凯课题组全部文献")
lines.append(f"% 生成日期: 2025-06-13")
lines.append(f"% 收录: {len(en_papers)} 篇英文 + {len(cn_papers)} 篇中文 + {len(thesis_papers)} 篇学位论文")
lines.append(f"% 已下载全文路径指向: 02_文献PDF/")
lines.append("")

PDF_DIR_EN_ABS = os.path.abspath(PDF_DIR_EN).replace('\\', '/')

# 英文论文
for p in en_papers:
    lines.append(f"@article{{{p['citekey']},")
    lines.append(f"  title = {{{p['title']}}},")
    lines.append(f"  author = {{{safe_author(p['author'])}}},")
    lines.append(f"  journal = {{{p['journal']}}},")
    lines.append(f"  year = {{{p['year']}}},")
    if 'volume' in p and p['volume']:
        lines.append(f"  volume = {{{p['volume']}}},")
    if 'number' in p and p['number']:
        lines.append(f"  number = {{{p['number']}}},")
    if 'pages' in p and p['pages']:
        lines.append(f"  pages = {{{p['pages']}}},")
    if 'doi' in p and p['doi']:
        lines.append(f"  doi = {{{p['doi']}}},")
    if p.get('file'):
        fpath = f"{PDF_DIR_EN_ABS}/{p['file']}"
        lines.append(f"  file = {{{fpath}}},")
    lines.append("}")
    lines.append("")

# 中文论文
for p in cn_papers:
    lines.append(f"@article{{{p['citekey']},")
    lines.append(f"  title = {{{p['title']}}},")
    lines.append(f"  author = {{{safe_author(p['author'])}}},")
    lines.append(f"  journal = {{{p['journal']}}},")
    lines.append(f"  year = {{{p['year']}}},")
    if 'volume' in p and p.get('volume'):
        lines.append(f"  volume = {{{p['volume']}}},")
    if 'number' in p and p.get('number'):
        lines.append(f"  number = {{{p['number']}}},")
    if 'pages' in p and p.get('pages'):
        lines.append(f"  pages = {{{p['pages']}}},")
    if 'doi' in p and p.get('doi'):
        lines.append(f"  doi = {{{p['doi']}}},")
    lines.append("}")
    lines.append("")

# 学位论文
for p in thesis_papers:
    lines.append(f"@mastersthesis{{{p['citekey']},")
    lines.append(f"  title = {{{p['title']}}},")
    lines.append(f"  author = {{{safe_author(p['author'])}}},")
    lines.append(f"  school = {{{p['school']}}},")
    lines.append(f"  year = {{{p['year']}}},")
    lines.append("}")
    lines.append("")

with open(BIB_FILE, "w", encoding="utf-8") as f:
    f.write('\n'.join(lines))

print(f"[OK] BibTeX 文件已生成: {BIB_FILE}")
print(f"     共 {len(en_papers)} 篇英文 + {len(cn_papers)} 篇中文 + {len(thesis_papers)} 篇学位论文")
print(f"     已下载全文自动链接到 BibTeX 的 file 字段")
