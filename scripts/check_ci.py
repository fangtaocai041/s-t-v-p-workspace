import json, sys

with open(r'D:\Reasonix\logs\ci_runs_detail.json', encoding='utf-8') as f:
    d = json.load(f)

print(f"total_count: {d.get('total_count')}")
for r in d.get('workflow_runs', []):
    print(f"  #{r['run_number']} {r['name']} status={r['status']} conclusion={r['conclusion']} sha={r['head_sha'][:8]}")
    print(f"    jobs_url: {r['jobs_url']}")
