"""
批量下载课题组论文脚本
从 NCBI PMC API 批量获取论文全文
使用 urllib（Python 内置，无需额外安装）
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# === 配置 ===
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "英文论文")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 英文论文 DOI 列表（从文献数据库提取）
PAPERS = [
    # 2026年
    {"id": "E01", "doi": "10.1002/ece3.72775", "title": "Evaluating Fishing Ban Effectiveness Through Spatiotemporal Changes in Genetic Diversity of Parabramis pekinensis"},
    {"id": "E02", "doi": "10.3390/ani16050840", "title": "Gut Microbiome Signatures Across Migratory, Sedentary, and Aquaculture Ecotypes of Coilia nasus"},
    {"id": "E03", "doi": "10.3390/biom16010083", "title": "Telomere-to-Telomere Genome Assembly of Two Hemiculter Species"},
    {"id": "E04", "doi": "10.1038/s41597-026-06588-7", "title": "Telomere-to-telomere gap-free genome assembly of Opsariichthys evolans"},
    # 2025年
    {"id": "E05", "doi": "10.1002/ece3.72815", "title": "Population Genomics of Two Ecotypes Coilia nasus"},
    {"id": "E06", "doi": "10.3390/ani15233434", "title": "Otolith Sr Isotope Reveals Mixed Life Histories of Coilia brachygnathus"},
    {"id": "E07", "doi": "10.1016/j.cbd.2025.101693", "title": "Key lncRNA-mRNA Networks Regulated by Polyascus sp. Infection in Eriocheir sinensis"},
    {"id": "E08", "doi": "10.7717/peerj.20089", "title": "Eyestalk Transcriptome: Sexually Dimorphic Host-Parasite Interactions of Polyascus sp."},
    {"id": "E09", "doi": "10.3390/biology14091211", "title": "Spatial and Sex-Specific Growth Variations of Migratory Coilia nasus"},
    {"id": "E10", "doi": "10.3390/ani15172603", "title": "Tetranucleotide Repeat Microsatellite Markers in Yangtze Finless Porpoise"},
    {"id": "E11", "doi": "10.1093/dnares/dsaf020", "title": "Genome Survey and Evolutionary Analysis of 8 Lamprotula Species"},
    {"id": "E12", "doi": "10.3390/microorganisms13071711", "title": "Multi-Omics: Gut Microbiota, Fatty Acid Metabolism, and Immune in Coilia nasus"},
    {"id": "E13", "doi": "10.3390/microorganisms13071449", "title": "Gut Microbiota Contribute to Heterosis in Hybrid Largemouth Bass"},
    {"id": "E14", "doi": "10.1093/gigascience/giaf068", "title": "T2T Gap-free Reference Genome and Taxonomic Reassessment of Siniperca roulei"},
    {"id": "E15", "doi": "10.3390/ijms26136492", "title": "GWAS and RNA-Seq: Growth Traits in Red Tilapia Under Hyperosmotic Stress"},
    {"id": "E16", "doi": "10.3390/ani15131838", "title": "Genetic Diversity of Yangtze Finless Porpoise in Poyang Lake"},
    # 2024年
    {"id": "E17", "doi": "10.1093/gigascience/giae067", "title": "T2T Gap-free Genome of Endangered Yangtze Finless Porpoise"},
    {"id": "E18", "doi": "10.3389/fmicb.2024.1424277", "title": "Effects of Season and Water Quality on Planktonic Eukaryotes in Chaohu Lake"},
    {"id": "E19", "doi": "10.1016/j.ese.2024.100441", "title": "Evaluating eDNA and eRNA Metabarcoding for Aquatic Biodiversity Assessment"},
    {"id": "E20", "doi": "10.1016/j.cbd.2024.101261", "title": "Hepatic Immune Response of Coilia nasus Infected with Anisakidae"},
    {"id": "E21", "doi": "10.3390/biology13010056", "title": "Recruitment Patterns and Environmental Sensitivity of Glass Eels in Yangtze Estuary"},
    # 2023年
    {"id": "E22", "doi": "10.3390/ani14020199", "title": "Comparative Blood Transcriptome of Yangtze Finless Porpoise"},
    {"id": "E23", "doi": "10.1099/ijsem.0.006117", "title": "Vibrio chanodichtyis sp. nov. from Intestine of Chanodichthys dabryi"},
    {"id": "E24", "doi": "10.3390/antibiotics12040686", "title": "In Vitro Antibiofilm Activity of Resveratrol against Aeromonas hydrophila"},
    # 2022年
    {"id": "E25", "doi": "10.3389/fmicb.2022.1006251", "title": "Bacteria of Yangtze Finless Porpoise Are Site-Specific"},
    {"id": "E26", "doi": "10.1016/j.cbd.2022.100995", "title": "Proteomics Approach Reveals Digestive and Nutritional Responses in Coilia nasus"},
    {"id": "E27", "doi": "10.1111/jfb.15027", "title": "Anisakidae Parasitism Activated Immune Response in Coilia nasus"},
    {"id": "E28", "doi": "10.1016/j.ygeno.2020.05.027", "title": "Metabolic Mechanisms of Coilia nasus in Food Intake During Migration"},
    # 2021年
    {"id": "E29", "doi": "10.1016/j.cbpb.2021.110635", "title": "Integrated Analysis of Blood mRNAs and microRNAs in Yangtze Finless Porpoise"},
    {"id": "E30", "doi": "10.1515/biol-2020-0032", "title": "Changes in Fecal Microbiome of Yangtze Finless Porpoise"},
    {"id": "E31", "doi": "10.1007/s00284-020-02088-y", "title": "Variations of Gut Prokaryotic Microbiome During Spawning Migration in Coilia nasus"},
    # 2017年
    {"id": "E32", "doi": "10.1093/gigascience/giw012", "title": "Whole genome sequencing of Chinese clearhead icefish, Protosalanx hyalocranius"},
    # 2019-2020年
    {"id": "E33", "doi": "10.1093/gigascience/giz157", "title": "Genome and Population Sequencing of Coilia nasus"},
    {"id": "E34", "doi": "10.1002/mbo3.874", "title": "The Intestinal Microbiota of Lake Anchovy in Taihu Lake"},
    {"id": "E35", "doi": "10.1371/journal.pone.0221120", "title": "Investigating Distribution of Yangtze Finless Porpoise Using eDNA"},
    {"id": "E36", "doi": "10.1016/j.cbd.2019.02.005", "title": "Proteomics Approach to Liver Starvation Stress in Coilia nasus"},
    # 数据论文
    {"id": "D1", "doi": "10.1038/s41597-023-02278-w", "title": "Gap-free genome assembly of anadromous Coilia nasus"},
    {"id": "D2", "doi": "10.1038/s41597-022-01868-4", "title": "Gapless genome assembly of East Asian finless porpoise"},
    {"id": "D3", "doi": "10.1038/s41597-025-05078-6", "title": "Chromosome-level genome assembly of Anodonta woodiana"},
    {"id": "D4", "doi": "10.1038/s41597-025-04890-4", "title": "Chromosome-level genome assembly of Pseudorasbora elongata"},
]

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def safe_filename(title):
    """将标题转为安全的文件名"""
    name = re.sub(r'[<>:"/\\|?*]', '_', title)
    name = re.sub(r'\s+', '_', name)
    return name[:120]


def search_pubmed_by_doi(doi):
    """通过DOI查询PubMed，返回PMID和PMCID"""
    url = NCBI_BASE + "esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": f"{doi}[DOI]",
        "retmode": "json",
        "retmax": 1
    }
    try:
        req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params),
                                     headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        id_list = data.get("esearchresult", {}).get("idlist", [])
        if id_list:
            pmid = id_list[0]
            # 查询PMCID
            url2 = NCBI_BASE + "elink.fcgi"
            params2 = {
                "dbfrom": "pubmed",
                "db": "pmc",
                "id": pmid,
                "retmode": "json"
            }
            req2 = urllib.request.Request(url2 + "?" + urllib.parse.urlencode(params2),
                                          headers={"User-Agent": "Mozilla/5.0"})
            resp2 = urllib.request.urlopen(req2, timeout=15)
            data2 = json.loads(resp2.read().decode())
            linksets = data2.get("linksets", [])
            pmcid = None
            for ls in linksets:
                for link in ls.get("linksetdbs", []):
                    for item in link.get("links", []):
                        pmcid = f"PMC{item}"
                        break
            return pmid, pmcid
        return None, None
    except Exception as e:
        print(f"  ! 搜索DOI {doi} 失败: {e}")
        return None, None


def download_pmc_pdf(pmcid, output_path):
    """从PMC下载PDF"""
    # PMC PDF URL pattern
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        # 先检查是不是PDF
        resp = urllib.request.urlopen(req, timeout=30)
        content = resp.read()
        if content[:4] == b'%PDF':
            with open(output_path, 'wb') as f:
                f.write(content)
            return True, "PDF"
        else:
            # 尝试 main.pdf
            pdf_url2 = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/main.pdf"
            req2 = urllib.request.Request(pdf_url2, headers={"User-Agent": "Mozilla/5.0"})
            resp2 = urllib.request.urlopen(req2, timeout=30)
            content2 = resp2.read()
            if content2[:4] == b'%PDF':
                with open(output_path, 'wb') as f:
                    f.write(content2)
                return True, "PDF"
            return False, f"非PDF内容({len(content)} bytes)"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)


def fetch_pmc_text(pmcid):
    """从PMC获取全文XML并提取文本"""
    url = NCBI_BASE + "efetch.fcgi"
    params = {
        "db": "pmc",
        "id": pmcid.replace("PMC", ""),
        "retmode": "xml",
        "rettype": "full"
    }
    try:
        req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params),
                                     headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        xml_data = resp.read().decode("utf-8", errors="replace")
        # 简单提取文本（去掉XML标签）
        text = re.sub(r'<[^>]+>', ' ', xml_data)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        return None


def main():
    log = []
    success = 0
    fail = 0
    
    print(f"共有 {len(PAPERS)} 篇英文论文待处理")
    print("=" * 60)
    
    for i, paper in enumerate(PAPERS):
        doi = paper["doi"]
        title = paper["title"]
        fid = paper["id"]
        print(f"\n[{i+1}/{len(PAPERS)}] {fid}: {title[:60]}...")
        print(f"  DOI: {doi}")
        
        # 搜索PMCID
        pmid, pmcid = search_pubmed_by_doi(doi)
        
        if pmcid:
            print(f"  [OK] PMCID: {pmcid}")
            safe_name = f"{fid}_{safe_filename(title)}"
            
            # 尝试下载PDF
            pdf_path = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")
            pdf_ok, pdf_msg = download_pmc_pdf(pmcid, pdf_path)
            
            if pdf_ok:
                size = os.path.getsize(pdf_path)
                print(f"  [OK] PDF下载成功 ({size/1024:.0f} KB)")
                log.append({"id": fid, "doi": doi, "pmcid": pmcid, "status": "PDF_OK", "path": pdf_path})
                success += 1
            else:
                # PDF下载失败，尝试获取文本
                print(f"  [!] PDF获取失败 ({pdf_msg})，尝试获取全文文本...")
                text = fetch_pmc_text(pmcid)
                if text:
                    txt_path = os.path.join(OUTPUT_DIR, f"{safe_name}.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"  [OK] 全文文本下载成功 ({len(text)/1024:.0f} KB)")
                    log.append({"id": fid, "doi": doi, "pmcid": pmcid, "status": "TXT_OK", "path": txt_path})
                    success += 1
                else:
                    print(f"  [FAIL] 全文获取失败")
                    log.append({"id": fid, "doi": doi, "pmcid": pmcid, "status": "FAILED"})
                    fail += 1
        else:
            print(f"  [FAIL] 未找到PMCID (PMID: {pmid})")
            log.append({"id": fid, "doi": doi, "status": "NO_PMCID"})
            fail += 1
        
        # 避免请求过快
        if i < len(PAPERS) - 1:
            time.sleep(0.5)
    
    # 输出汇总
    print("\n" + "=" * 60)
    print(f"下载完成! [OK] {success}, [FAIL] {fail}")
    
    # 保存日志
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "下载日志.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"日志已保存: {log_path}")


if __name__ == "__main__":
    main()
