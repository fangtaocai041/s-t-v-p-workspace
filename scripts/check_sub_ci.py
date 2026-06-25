import json, os, sys, urllib.request, zipfile, io

token = os.environ.get("GITHUB_TOKEN")
if not token:
    print("ERROR: GITHUB_TOKEN not set"); sys.exit(1)

# porpoise-agent - latest failure
repo = 'fangtaocai041/porpoise-agent'

req = urllib.request.Request('https://api.github.com/repos/%s/actions/runs?per_page=1&status=failure' % repo)
req.add_header('Authorization', 'token ' + token)
req.add_header('Accept', 'application/vnd.github.v3+json')
resp = urllib.request.urlopen(req, timeout=10)
d = json.loads(resp.read())

run = d['workflow_runs'][0]
print('Latest failure #%d: %s' % (run['run_number'], run['name']))
print('Commit: ' + (run.get('head_commit') or {}).get('message', '')[:80])

# Get jobs
req2 = urllib.request.Request(run['jobs_url'])
req2.add_header('Authorization', 'token ' + token)
req2.add_header('Accept', 'application/vnd.github.v3+json')
resp2 = urllib.request.urlopen(req2, timeout=10)
jd = json.loads(resp2.read())
for j in jd.get('jobs', []):
    print('  Job: %s conclusion=%s' % (j['name'], j['conclusion']))
    for s in j.get('steps', []):
        print('    %s: %s' % (s['name'], s['conclusion']))
        if s['conclusion'] == 'failure' and s.get('annotations'):
            for a in s['annotations']:
                print('      [%s] %s' % (a['annotation_level'], a['message'][:300]))
