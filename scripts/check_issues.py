import json

d = json.load(open(r'D:\Reasonix\logs\issues.json', encoding='utf-8'))
print('共 %d 个 issues:' % len(d))
for i in d:
    labels = ', '.join([l['name'] for l in i.get('labels', [])])
    print('  #%d [%s] %s' % (i['number'], i['state'], i['title'][:80]))
    if labels:
        print('          labels: ' + labels)
    # 只看 open 的
    if i['state'] == 'open':
        print('          body: ' + (i.get('body') or '')[:200])
