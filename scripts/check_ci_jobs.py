import json

with open(r'D:\Reasonix\logs\ci_jobs_82.json', encoding='utf-8') as f:
    d = json.load(f)

for j in d.get('jobs', []):
    print(f"  Job: {j['name']} conclusion={j['conclusion']}")
    for s in j.get('steps', []):
        icon = 'X' if s['conclusion'] == 'failure' else 'OK' if s['conclusion'] == 'success' else '--'
        print(f"    {icon} {s['name']}: {s['conclusion']}")
