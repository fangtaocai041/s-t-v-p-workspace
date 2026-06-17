"""Fix garbled chars in all project English README files."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    old_count = text.count('?')
    
    # === RATINGS: ⭐⭐⭐⭐? → ⭐⭐⭐⭐⭐ ===
    text = text.replace('⭐⭐⭐⭐?', '⭐⭐⭐⭐⭐')
    
    # === P1/P2/P3 subscripts ===
    text = text.replace('**P?*', '**P₁**')
    text = text.replace('| **P?* |', '| **P₁** |')
    
    # === Em dashes in context ===
    text = text.replace('?BDI +', ' \u2014 BDI +')
    text = text.replace(' ?EventBus', ' \u2014 EventBus')
    
    # === Triangulation ===
    text = text.replace('? independent projects', '\u22653 independent projects')
    text = text.replace('? sources,', '\u22653 sources,')
    text = text.replace('? sources', '\u22653 sources')
    text = text.replace('When ? independent', 'When \u22653 independent')
    
    # === Efficiency label ===
    text = text.replace('| ?Efficiency', '| \u26a1 Efficiency')
    
    # === Arrows → ===
    text = text.replace(' ?DS-1', ' \u2192 DS-1')
    text = text.replace(' ?DS-', ' \u2192 DS-')
    text = text.replace(' ?MoE', ' \u2192 MoE')
    text = text.replace(' ?P(stale)', ' \u2192 P(stale)')
    text = text.replace(' ?hit-and-stop', ' \u2192 hit-and-stop')
    text = text.replace(' ?full pipeline', ' \u2192 full pipeline')
    text = text.replace(' ?single-step', ' \u2192 single-step')
    text = text.replace(' ?focus', ' \u2192 focus')
    text = text.replace(' ?compute', ' \u2192 compute')
    text = text.replace(' ?fish(S/V0)', ' \u2192 fish(S/V0)')
    text = text.replace(' ?cognitive(V/V1)', ' \u2192 cognitive(V/V1)')
    text = text.replace(' ?eon-core(Coord)', ' \u2192 eon-core(Coord)')
    text = text.replace('interactive?2-layer', 'interactive \u2192 2-layer')
    
    # === Checkmarks in tables ===
    text = text.replace('\n| ?430', '\n| \u2705 430')
    text = text.replace('\n| ?R 4', '\n| \u2705 R 4')
    text = text.replace('\n| ?Paddle', '\n| \u2705 Paddle')
    text = text.replace('\n| ?Direct', '\n| \u2705 Direct')
    text = text.replace('\n| ?5-stage', '\n| \u2705 5-stage')
    text = text.replace('\n| ?GitHub', '\n| \u2705 GitHub')
    text = text.replace('\n| ?13 IMA', '\n| \u2705 13 IMA')
    text = text.replace('\n| ?18 WHEN', '\n| \u2705 18 WHEN')
    text = text.replace('\n| ?fish\u2194', '\n| \u2705 fish\u2194')
    text = text.replace('\n| ?Self', '\n| \u2705 Self')
    text = text.replace('\n| ?Cross', '\n| \u2705 Cross')
    text = text.replace('\n| ?Zotero', '\n| \u2705 Zotero')
    text = text.replace('\n| ?One script', '\n| \u2705 One script')
    
    # === Circled numbers ===
    text = text.replace('| ?| Practice', '| \u2460 | Practice')
    text = text.replace('| ?| Contradiction', '| \u2461 | Contradiction')
    text = text.replace('| ?| Phased', '| \u2462 | Phased')
    text = text.replace('| ?| Concentration', '| \u2463 | Concentration')
    text = text.replace('| ?| Initiative', '| \u2464 | Initiative')
    text = text.replace('| ?| Differentiated', '| \u2465 | Differentiated')
    text = text.replace('| ?| Multi', '| \u2466 | Multi')
    
    # === Misc ===
    text = text.replace('D?Plane', 'D\u00b2 Plane')
    text = text.replace('?reconstruct', ' \u2014 reconstruct')
    text = text.replace('?500+', ' \u2192 500+')
    text = text.replace('?emergence', ' \u2192 emergence')
    text = text.replace('?Dao De Jing', ' \u2014 *Dao De Jing*')
    text = text.replace('?三体', ' \u4e09 (Three)')
    text = text.replace('# 🕸?Cognitive', '# \u1f578\ufe0f Cognitive')
    
    new_count = text.count('?')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return old_count, new_count

base = r'D:\Reasonix'
projects = ['eon-core','cognitive-search-engine','porpoise-agent','coilia-agent','culter-agent']

for proj in projects:
    path = os.path.join(base, proj, 'README.md')
    if not os.path.exists(path): continue
    old, new = fix_file(path)
    print(f'{proj}/README.md: {old} -> {new} ?')
