"""CNKI 作者检索 - 搜索刘凯的中文论文
使用知网研学 Cookie 直连 CNKI API"""
import json, urllib.request, urllib.parse, re, time

COOKIE_FILE = r"D:\Reasonix\cognitive-search-engine\config\cnki_cookies.json"
OUTPUT_DIR = r"D:\Reasonix\课题组-刘凯\01_文献数据库"

# 加载Cookie
with open(COOKIE_FILE, 'r') as f:
    data = json.load(f)
cookie_str = data['cookies']

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": cookie_str,
    "Referer": "https://kns.cnki.net/",
}

def search_author(author="刘凯", inst="淡水渔业研究中心", max_results=100):
    """通过CNKI高级搜索查找作者论文"""
    base_url = "https://kns.cnki.net/kns8/defaultresult/index"
    
    # CNKI 使用 POST 方式的查询
    params = {
        "dbcode": "CJFQ",  # 期刊
        "kw": author,
        "kwField": "AU",   # 作者字段
        "code": "",
        "pageno": 1,
        "pagesize": max_results,
    }
    
    url = base_url + "?" + urllib.parse.urlencode(params, encoding='utf-8')
    
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        html = resp.read().decode('utf-8', errors='replace')
        
        # 从HTML中提取论文信息
        papers = []
        
        # 匹配论文标题和链接
        title_pattern = re.compile(r'<a[^>]*class="[^"]*title[^"]*"[^>]*href="([^"]+)"[^>]*title="([^"]*)"')
        for m in title_pattern.finditer(html):
            papers.append({"title": m.group(2), "link": m.group(1)})
        
        # 匹配作者
        author_pattern = re.compile(r'<p[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)</p>')
        
        # 匹配期刊名
        journal_pattern = re.compile(r'<span[^>]*class="[^"]*journal[^"]*"[^>]*>([^<]+)</span>')
        
        # 匹配年份
        year_pattern = re.compile(r'<span[^>]*class="[^"]*year[^"]*"[^>]*>([^<]+)</span>')
        
        # 统计
        total_match = re.search(r'找到\s*(\d[\d,]*)\s*条结果', html)
        total = total_match.group(1) if total_match else "未知"
        
        print(f"找到约 {total} 条结果")
        print(f"提取到 {len(papers)} 个标题")
        
        # 显示部分结果
        for i, p in enumerate(papers[:10]):
            print(f"  {i+1}. {p['title'][:60]}")
            print(f"     链接: {p['link'][:80]}")
        
        return papers, html
        
    except Exception as e:
        print(f"请求失败: {e}")
        # Try to read the response anyway
        import traceback
        traceback.print_exc()
        return [], ""

# 搜索作者
print("=" * 60)
print("CNKI 作者检索: 刘凯")
print("=" * 60)
papers, html = search_author()

# 如果第一种方式没结果，尝试普通关键词搜索
if len(papers) == 0:
    print("\n尝试普通搜索方式...")
    alt_url = "https://kns.cnki.net/kns8/defaultresult/index?kwd=%E5%88%98%E5%87%AF&dbcode=CJFQ"
    req = urllib.request.Request(alt_url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        html = resp.read().decode('utf-8', errors='replace')
        
        # 检查页面中是否提到结果数量
        for kw in ['找到', '条结果', 'total', 'count', 'error']:
            idx = html.find(kw)
            if idx >= 0:
                s = max(0, idx-20)
                e = min(len(html), idx+60)
                print(f"  [{kw}]: ...{html[s:e]}...")
        
        # 检查是否有JSON数据
        json_match = re.search(r'var\s+searchResult\s*=\s*(\{.+?\});', html, re.DOTALL)
        if json_match:
            print(f"找到JSON数据: {json_match.group(1)[:200]}")
        
        print(f"页面大小: {len(html)} bytes")
        
    except Exception as e:
        print(f"备用搜索也失败: {e}")

print("\n完成")
