"""
CNKI 批量检索刘凯中文论文
使用知网研学Cookie从多个API端点尝试获取
"""
import requests, json, re, time, os

COOKIE_FILE = r"D:\Reasonix\cognitive-search-engine\config\cnki_cookies.json"

with open(COOKIE_FILE) as f:
    data = json.load(f)
cookies = {}
for item in data['cookies'].split('; '):
    if '=' in item:
        k, v = item.split('=', 1)
        cookies[k] = v

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
}

results = []

# === 方法1: CNKI 高级检索 API ===
print("=" * 50)
print("方法1: CNKI高级检索API")
urls_to_try = [
    "https://kns.cnki.net/kns8/searchclassic",
    "https://kns.cnki.net/kns8/defaultresult/search",
    "https://search.cnki.net/search",
]

for base_url in urls_to_try:
    params_list = [
        {"dbcode": "CJFQ", "kw": "刘凯", "field": "au", "pageSize": 100},
        {"dbcode": "CJFQ", "au": "刘凯", "pageSize": 100, "pageNum": 1},
        {"keyword": "刘凯", "dbCode": "CJFQ", "pageSize": 100},
    ]
    for params in params_list:
        try:
            r = requests.get(base_url, params=params, cookies=cookies, headers=headers, timeout=10)
            txt = r.text
            # 检查是否返回了论文数据
            paper_count = txt.count('<tr') + txt.count('class="result"') + txt.count('"title"')
            has_liukai = '刘凯' in txt
            if has_liukai and paper_count > 5:
                print(f"  ✓ {base_url} 返回数据: {len(txt)} bytes, 论文片段: {paper_count}")
                results.append(txt)
                break
            elif '登录' in txt[:2000]:
                print(f"  ✗ {base_url}: 需登录")
            else:
                print(f"  - {base_url}: {r.status_code}, {len(txt)} bytes")
        except Exception as e:
            print(f"  ✗ {base_url}: {e}")

# === 方法2: 知网研学(CNKI Study) API ===
print("\n方法2: 知网研学API")
study_urls = [
    ("https://xue.cnki.net/search/searchresult", {"keyword": "刘凯", "pageNum": 1, "pageSize": 100}),
    ("https://xue.cnki.net/search/searchresult.ashx", {"keyword": "刘凯", "pageSize": 100}),
]
for url, params in study_urls:
    try:
        r = requests.post(url, data=params, cookies=cookies, headers=headers, timeout=10)
        print(f"  {url}: {r.status_code}, {len(r.text)}")
        if r.status_code == 200:
            try:
                j = r.json()
                total = j.get('total', j.get('count', j.get('data', {}).get('total', '?')))
                print(f"    总数: {total}")
            except:
                pass
    except Exception as e:
        print(f"  ✗ {url}: {e}")

# === 方法3: xai.cnki.net (AI增强版) API ===
print("\n方法3: xai.cnki.net API")
xai_urls = [
    "https://xai.cnki.net/api/search/paper",
    "https://xai.cnki.net/api/paper/search",
    "https://xai.cnki.net/api/search",
]
for url in xai_urls:
    try:
        r = requests.post(url, json={"keyword": "刘凯", "pageSize": 20}, cookies=cookies, 
                         headers={**headers, 'Content-Type': 'application/json'}, timeout=10)
        print(f"  {url}: {r.status_code}, {len(r.text)}")
        if r.status_code == 200:
            try:
                print(f"    内容: {r.text[:200]}")
            except:
                pass
    except Exception as e:
        print(f"  ✗ {url}: {e}")

# === 方法4: 直接解析页面的JS数据 ===
print("\n方法4: 从页面提取JS数据")
url = "https://kns.cnki.net/kns8/defaultresult/index?kwd=%E5%88%98%E5%87%AF&dbcode=CJFQ"
r = requests.get(url, cookies=cookies, headers={**headers, 'Accept': 'text/html'}, timeout=10)

# 找所有script标签中的JSON数据
for m in re.finditer(r'var\s+(\w+)\s*=\s*(\{.+?\});', r.text, re.DOTALL):
    name = m.group(1)
    if any(k in name.lower() for k in ['result', 'search', 'data', 'paper', 'record']):
        try:
            j = json.loads(m.group(2))
            print(f"  找到数据: {name} = {json.dumps(j)[:200]}")
        except:
            pass

# 找pageData/initData等
for m in re.finditer(r'(pageData|initData|searchData|resultData)\s*[:=]\s*(\{.+?\})(?:;|,|\s*\]|\s*\})', r.text, re.DOTALL):
    try:
        j = json.loads(m.group(2))
        print(f"  找到: {m.group(1)} = {json.dumps(j)[:200]}")
    except:
        pass

# 找XML/JSON内嵌数据
for m in re.finditer(r'<script[^>]*type=["\']application/json["\'][^>]*>(.+?)</script>', r.text, re.DOTALL):
    try:
        j = json.loads(m.group(1))
        print(f"  JSON script data: {type(j).__name__} {json.dumps(j)[:200]}")
    except:
        print(f"  JSON script (not parseable): {m.group(1)[:100]}")

print(f"\n总页面大小: {len(r.text)} bytes")
