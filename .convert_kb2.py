"""Regenerate species profiles."""
import yaml, os
from datetime import date

KB = 'fish-ecology-assistant/config/fish_species_kb.yaml'
PROFILES = 'fish-ecology-assistant/config/knowledge_base/species'
INDEX = 'fish-ecology-assistant/config/fish_species_index.yaml'

with open(KB, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

today = date.today().isoformat()
species_list = data['species']

index_data = {'metadata': {'title': '鱼类物种知识库索引', 'version': '3.0',
    'last_updated': today, 'total_species': len(species_list),
    'note': '详细档案位于 config/knowledge_base/species/'}, 'species': []}

for sp in species_list:
    sid = sp['id']
    sci = sp.get('scientific', '')
    cn = sp.get('name', '')
    basins = sp.get('distribution', {}).get('basins', []) if isinstance(sp.get('distribution'), dict) else []

    index_data['species'].append({'id': sid, 'name': cn, 'scientific': sci,
        'family': sp.get('family',''), 'basins': basins,
        'profile': f'knowledge_base/species/{sid}.md'})

    fm = {'id': sid, 'scientific': sci, 'name': cn, 'family': sp.get('family',''),
        'last_updated': today}
    for f in ['order','conservation','status','category','ecology','economic_value']:
        if sp.get(f): fm[f] = sp[f]
    if sp.get('aliases'): fm['aliases'] = sp['aliases']
    if basins: fm['basins'] = basins
    if sp.get('literature'): fm['literature'] = sp['literature']
    
    md = ['---']
    md.append(yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120).strip())
    md.append('---')
    md.append('')
    if sp.get('ecology'):
        md.append(f'## 生态描述\n\n{sp[\"ecology\"]}\n')
    if sp.get('economic_value'):
        md.append(f'## 经济价值\n\n{sp[\"economic_value\"]}\n')
    
    profile_path = os.path.join(PROFILES, f'{sid}.md')
    with open(profile_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    print(f'  {sid}')

with open(INDEX, 'w', encoding='utf-8') as f:
    yaml.dump(index_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120)

print(f'\n✅ Done: {len(species_list)} profiles')
