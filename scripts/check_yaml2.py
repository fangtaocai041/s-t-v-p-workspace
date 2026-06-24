import yaml
for f in ['rule-checks.yml', 'anti-hallucination.yml', 'cross-project-check.yml', 'gitee-sync.yml']:
    path = r'D:\Reasonix\.github\workflows\\' + f
    try:
        with open(path, encoding='utf-8') as fh:
            yaml.safe_load(fh)
        print(f + ': OK')
    except Exception as e:
        print(f + ': ERROR - ' + str(e)[:100])
