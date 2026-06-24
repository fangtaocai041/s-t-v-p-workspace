import yaml

with open(r'D:\Reasonix\.github\workflows\rule-checks.yml', encoding='utf-8') as f:
    d = yaml.safe_load(f)

print('YAML OK')
print('on:', list(d.get('on',{}).keys()) if isinstance(d.get('on'), dict) else d.get('on'))
for name, job in d.get('jobs',{}).items():
    print('  job', name, 'runs-on:', job.get('runs-on'), 'continue-on-error:', job.get('continue-on-error'))
