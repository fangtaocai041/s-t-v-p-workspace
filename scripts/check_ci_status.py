import json, os, sys, urllib.request

token = os.environ.get("GITHUB_TOKEN")
if not token:
    print("ERROR: GITHUB_TOKEN not set"); sys.exit(1)
repos = [
    'fangtaocai041/fish-ecology-assistant',
    'fangtaocai041/cognitive-search-engine',
    'fangtaocai041/coilia-agent',
    'fangtaocai041/culter-agent',
    'fangtaocai041/porpoise-agent',
    'fangtaocai041/conflict-arbiter',
    'fangtaocai041/san-sheng-wanwu-core',
]

for repo in repos:
    req = urllib.request.Request('https://api.github.com/repos/%s/actions/runs?per_page=3&status=failure' % repo)
    req.add_header('Authorization', 'token ' + token)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        d = json.loads(resp.read())
        if d.get('total_count', 0) > 0:
            print('=== %s === %d failures' % (repo, d['total_count']))
            for r in d.get('workflow_runs', [])[:3]:
                msg = (r.get('head_commit') or {}).get('message', '')[:40]
                print('  #%d %s %s' % (r['run_number'], r['name'][:30], msg))
        else:
            print('=== %s === All green' % repo)
    except Exception as e:
        print('=== %s === ERROR: %s' % (repo, str(e)[:60]))
