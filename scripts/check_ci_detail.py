import json, os, sys, urllib.request

token = os.environ.get("GITHUB_TOKEN")
if not token:
    print("ERROR: GITHUB_TOKEN not set"); sys.exit(1)

# fish-ecology-assistant - 最新一次失败
repos = {
    'fangtaocai041/fish-ecology-assistant': None,
    'fangtaocai041/coilia-agent': None,
    'fangtaocai041/porpoise-agent': None,
}

for repo in repos:
    # 获取最新失败run
    req = urllib.request.Request('https://api.github.com/repos/%s/actions/runs?per_page=1&status=failure' % repo)
    req.add_header('Authorization', 'token ' + token)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    resp = urllib.request.urlopen(req, timeout=10)
    d = json.loads(resp.read())
    
    if d.get('total_count', 0) == 0:
        print('=== %s === No failures' % repo)
        continue
    
    run = d['workflow_runs'][0]
    print('=== %s === #%d %s' % (repo, run['run_number'], run['name']))
    
    # 获取jobs
    req2 = urllib.request.Request(run['jobs_url'])
    req2.add_header('Authorization', 'token ' + token)
    req2.add_header('Accept', 'application/vnd.github.v3+json')
    resp2 = urllib.request.urlopen(req2, timeout=10)
    jd = json.loads(resp2.read())
    
    for j in jd.get('jobs', []):
        for s in j.get('steps', []):
            if s['conclusion'] == 'failure':
                print('  FAILED step: ' + s['name'])
                # Get annotations if available
                if s.get('annotations'):
                    for a in s['annotations']:
                        print('    ' + a['message'][:200])
    
    # Try to get logs
    import subprocess, os
    log_path = r'D:\Reasonix\logs\ci_logs_%s.zip' % repo.replace('/', '_')
    req3 = urllib.request.Request('https://api.github.com/repos/%s/actions/runs/%s/logs' % (repo, run['id']))
    req3.add_header('Authorization', 'token ' + token)
    req3.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        resp3 = urllib.request.urlopen(req3, timeout=30)
        with open(log_path, 'wb') as f:
            f.write(resp3.read())
        # List files in zip
        import zipfile
        with zipfile.ZipFile(log_path) as zf:
            names = zf.namelist()
            # Find the validate job test log
            for name in names:
                if 'test' in name.lower() or 'validate' in name.lower():
                    if name.endswith('.txt'):
                        content = zf.read(name).decode('utf-8', errors='replace')
                        # Find error lines
                        lines = content.split('\n')
                        for line in lines:
                            if 'ERROR' in line or 'FAIL' in line or 'ModuleNotFound' in line or 'Error' in line:
                                print('    LOG: ' + line[:150])
                        break
    except Exception as e:
        print('  Log fetch error: ' + str(e)[:60])
    
    print()
