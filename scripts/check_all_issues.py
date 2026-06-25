import json, os, subprocess, sys

repos = [
    'fangtaocai041/s-t-v-p-workspace',
    'fangtaocai041/fish-ecology-assistant',
    'fangtaocai041/cognitive-search-engine',
    'fangtaocai041/eon-core',
    'fangtaocai041/coilia-agent',
    'fangtaocai041/culter-agent',
    'fangtaocai041/porpoise-agent',
    'fangtaocai041/conflict-arbiter',
    'fangtaocai041/san-sheng-wanwu-core',
]

token = os.environ.get("GITHUB_TOKEN")
if not token:
    print("ERROR: GITHUB_TOKEN environment variable not set")
    print("  Generate at: https://github.com/settings/tokens")
    print("  Then run: $env:GITHUB_TOKEN='ghp_...'; python check_all_issues.py")
    sys.exit(1)

for repo in repos:
    import urllib.request
    req = urllib.request.Request('https://api.github.com/repos/%s/issues?state=all&per_page=5' % repo)
    req.add_header('Authorization', 'token ' + token)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        d = json.loads(resp.read())
        open_issues = [i for i in d if i['state'] == 'open']
        if open_issues:
            print('=== %s ===' % repo)
            for i in open_issues:
                print('  #%d %s' % (i['number'], i['title'][:80]))
                if i.get('body'):
                    print('    ' + i['body'][:300])
    except Exception as e:
        print('=== %s === ERROR: %s' % (repo, str(e)[:60]))

print('Done.')
