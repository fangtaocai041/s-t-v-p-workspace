#!/usr/bin/env python3
"""
回补刘凯课题组文献到 f项目知识库
从 刘凯老师课题组/01_文献数据库/ 提取所有文献信息
"""

import yaml, os, datetime

KB = r'D:\Reasonix\fish-ecology-assistant\config\fish_species_kb.yaml'

# 课题组核心物种映射
SPECIES_KEYWORDS = {
    'coilia_nasus': ['刀鲚', 'Coilia nasus', 'coilia_nasus'],
    'coilia_brachygnathus': ['短颌鲚', 'Coilia brachygnathus', 'coilia_brachygnathus'],
    'neophocaena_asiaeorientalis': ['江豚', 'finless porpoise', 'Neophocaena'],
    'parabramis_pekinensis': ['鳊', 'Parabramis pekinensis'],
    'culter_alburnus': ['翘嘴鲌', 'Culter alburnus'],
    'chanodichthys_dabryi': ['达氏鲌', 'Chanodichthys dabryi'],
    'hemiculter_leucisculus': ['䱗', 'Hemiculter'],
    'siniperca_chuatsi': ['鳜', 'Siniperca'],
    'elopichthys_bambusa': ['鳡', 'Elopichthys bambusa'],
}

# 主要文献列表 (从课题组数据库提取)
papers_en = [
    # 2026
    {"doi":"10.1002/ece3.72775","title":"Evaluating Fishing Ban Effectiveness Through Spatiotemporal Changes in Genetic Diversity of Parabramis pekinensis","year":2026,"journal":"Ecol Evol","species":["parabramis_pekinensis"],"category":"genetics","authors":["Wang Z","Yin D","Liu J","Liu K"]},
    {"doi":"10.3390/ani16050840","title":"Gut Microbiome Signatures Across Migratory, Sedentary, and Aquaculture Ecotypes of Coilia nasus","year":2026,"journal":"Animals","species":["coilia_nasus"],"category":"microbiome","authors":["Liu X","Ying C","Ma F","Liu K"]},
    {"doi":"10.3390/biom16010083","title":"Telomere-to-Telomere Genome Assembly of Two Hemiculter Species","year":2026,"journal":"Biomolecules","species":["hemiculter_leucisculus"],"category":"genomics","authors":["Liu J","Yin D","Ma F","Liu K"]},
    # 2025
    {"doi":"10.1002/ece3.72815","title":"Population Genomics Provides Novel Insights Into Evolutionary Relationships of Two Ecotypes Coilia nasus","year":2025,"journal":"Ecol Evol","species":["coilia_nasus"],"category":"genomics","authors":["Ma F","Liu K"]},
    {"doi":"10.3390/ani15233434","title":"Otolith Sr Isotope Reveals Mixed Life Histories of Coilia brachygnathus","year":2025,"journal":"Animals","species":["coilia_brachygnathus"],"category":"ecology","authors":["Xuan Z","Liu K"]},
    {"doi":"10.3390/ani15172603","title":"Tetranucleotide Repeat Microsatellite Markers in Yangtze Finless Porpoise","year":2025,"journal":"Animals","species":["neophocaena_asiaeorientalis"],"category":"genetics","authors":["Tang M","Yin D","Liu K"]},
    {"doi":"10.3390/ani15131838","title":"Genetic Diversity of Yangtze Finless Porpoise in Poyang Lake","year":2025,"journal":"Animals","species":["neophocaena_asiaeorientalis"],"category":"genetics","authors":["Zhang H","Yin D","Liu K"]},
    {"doi":"10.3390/biology14091211","title":"Spatial and Sex-Specific Growth Variations of Migratory Coilia nasus","year":2025,"journal":"Biology","species":["coilia_nasus"],"category":"ecology","authors":["Guo H","Liu K"]},
    # 2024
    {"doi":"10.1093/gigascience/giae067","title":"T2T Gap-free Genome of Endangered Yangtze Finless Porpoise","year":2024,"journal":"Gigascience","species":["neophocaena_asiaeorientalis"],"category":"genomics","authors":["Yin D","Liu K"]},
    {"doi":"10.3390/biology13010056","title":"Recruitment Patterns and Environmental Sensitivity of Glass Eels in Yangtze Estuary","year":2024,"journal":"Biology","species":[],"category":"ecology","authors":["Guo H","Liu K"]},
    {"doi":"10.1016/j.cbd.2024.101261","title":"Hepatic Immune Response of Coilia nasus Infected with Anisakidae","year":2024,"journal":"Comp Biochem Physiol D","species":["coilia_nasus"],"category":"immunology","authors":["Ying C","Liu K"]},
    # 2023
    {"doi":"10.3390/ani14020199","title":"Comparative Blood Transcriptome of Yangtze Finless Porpoise","year":2023,"journal":"Animals","species":["neophocaena_asiaeorientalis"],"category":"transcriptomics","authors":["Liu W","Yin D","Liu K"]},
    {"doi":"10.1099/ijsem.0.006117","title":"Vibrio chanodichtyis from Intestine of Chanodichthys dabryi","year":2023,"journal":"Int J Syst Evol Microbiol","species":["chanodichthys_dabryi"],"category":"microbiology","authors":["Wu N","Liu K"]},
    # 2022
    {"doi":"10.3389/fmicb.2022.1006251","title":"Bacteria of Yangtze Finless Porpoise Are Site-Specific","year":2022,"journal":"Front Microbiol","species":["neophocaena_asiaeorientalis"],"category":"microbiome","authors":["Zhang X","Ying C","Liu K"]},
    {"doi":"10.1016/j.cbd.2022.100995","title":"A Proteomics Approach Reveals Digestive Responses in Coilia nasus","year":2022,"journal":"Comp Biochem Physiol D","species":["coilia_nasus"],"category":"proteomics","authors":["Ma F","Liu K"]},
    {"doi":"10.1111/jfb.15027","title":"Anisakidae Parasitism Activated Immune Response in Coilia nasus","year":2022,"journal":"J Fish Biol","species":["coilia_nasus"],"category":"immunology","authors":["Ying C","Liu K"]},
    # 2021
    {"doi":"10.1016/j.cbpb.2021.110635","title":"Integrated Analysis of Blood mRNAs and microRNAs in Yangtze Finless Porpoise","year":2021,"journal":"Comp Biochem Physiol B","species":["neophocaena_asiaeorientalis"],"category":"transcriptomics","authors":["Yin D","Liu K"]},
    {"doi":"10.1007/s00284-020-02088-y","title":"Variations of Gut Prokaryotic Microbiome During Spawning Migration in Coilia nasus","year":2021,"journal":"Curr Microbiol","species":["coilia_nasus"],"category":"microbiome","authors":["Ying C","Liu K"]},
    # 2020
    {"doi":"10.1016/j.ygeno.2020.05.027","title":"Metabolic Mechanisms of Coilia nasus in Food Intake During Migration","year":2020,"journal":"Genomics","species":["coilia_nasus"],"category":"metabolism","authors":["Yin D","Liu K"]},
    # 2019
    {"doi":"10.1002/mbo3.874","title":"The Intestinal Microbiota of Lake Anchovy in Taihu Lake","year":2019,"journal":"MicrobiologyOpen","species":["coilia_brachygnathus"],"category":"microbiome","authors":["Jiang M","Liu K"]},
    {"doi":"10.1371/journal.pone.0221120","title":"Investigating Distribution of Yangtze Finless Porpoise Using eDNA","year":2019,"journal":"PLoS One","species":["neophocaena_asiaeorientalis"],"category":"ecology","authors":["Ma X","Liu K"]},
    # 2017
    {"doi":"10.1093/gigascience/giw012","title":"Whole genome sequencing of Chinese clearhead icefish","year":2017,"journal":"Gigascience","species":[],"category":"genomics","authors":["Liu K"]},
]

def match_species(title, text_species):
    """Match paper to KB species by title keywords"""
    title_lower = title.lower()
    for kb_id, keywords in SPECIES_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return kb_id
    if text_species:
        return text_species[0]
    return None

def main():
    with open(KB, encoding='utf-8') as f:
        kb = yaml.safe_load(f)
    
    species_list = kb.setdefault('species', [])
    added = 0
    today = datetime.date.today().isoformat()
    
    for paper in papers_en:
        # Match to species
        sp_id = match_species(paper['title'], paper.get('species', []))
        if not sp_id:
            continue
        
        # Find species entry
        entry = None
        for s in species_list:
            if (s.get('id','') == sp_id or 
                sp_id.lower() in (s.get('scientific','')+s.get('name','')).lower()):
                entry = s
                break
        
        if not entry:
            continue
        
        # Add literature
        lit = entry.setdefault('literature', [])
        existing = [l.get('doi','') for l in lit]
        if paper['doi'] in existing:
            continue
        
        lit.append({
            'doi': paper['doi'],
            'title': paper['title'],
            'year': paper['year'],
            'journal': paper['journal'],
            'category': paper['category'],
            'authors': paper['authors'][:5],
            'group': '刘凯课题组',
            'added_at': today,
        })
        added += 1
    
    # Save
    with open(KB, 'w', encoding='utf-8') as f:
        yaml.dump(kb, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
    
    print(f'✅ Added {added} papers to KB')
    print(f'   Species affected:')
    paper_counts = {}
    for paper in papers_en:
        sp = match_species(paper['title'], paper.get('species',[]))
        if sp:
            paper_counts[sp] = paper_counts.get(sp, 0) + 1
    for sp, n in sorted(paper_counts.items()):
        name = next((s.get('name','?') for s in species_list if s.get('id','') == sp), sp)
        print(f'   {name} ({sp}): +{n} papers')

if __name__ == '__main__':
    main()
