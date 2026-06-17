"""Simple string-based fix for garbled ? chars in all README files."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

def fix_project(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    before = text.count('?')
    
    # Simple string replacements (not regex)
    reps = [
        # Arrows → in specific contexts
        (') ?DS-', ') \u2192 DS-'),
        (') ?MoE', ') \u2192 MoE'),
        (') ?P(stale)', ') \u2192 P(stale)'),
        (') ?hit-and-stop', ') \u2192 hit-and-stop'),
        (') ?full pipeline', ') \u2192 full pipeline'),
        (') ?single-step', ') \u2192 single-step'),
        (') ?focus', ') \u2192 focus'),
        (') ?compute', ') \u2192 compute'),

        # Checkmarks ✅
        ('\n| ?R 4', '\n| \u2705 R 4'),
        ('\n| ?Paddle', '\n| \u2705 Paddle'),  
        ('\n| ?Direct Zotero', '\n| \u2705 Direct Zotero'),
        ('\n| ?5-stage', '\n| \u2705 5-stage'),
        ('\n| ?One script', '\n| \u2705 One script'),
        ('\n| ?GitHub Actions', '\n| \u2705 GitHub Actions'),
        ('\n| ?18 WHEN', '\n| \u2705 18 WHEN'),
        ('\n| ?fish', '\n| \u2705 fish'),
        ('\n| ?13 IMA', '\n| \u2705 13 IMA'),
        
        # Circled numbers
        ('| \ufffd| Practice', '| \u2460 | Practice'),
        ('| \ufffd| Contradiction', '| \u2461 | Contradiction'),  
        ('| \ufffd| Phased', '| \u2462 | Phased'),
        ('| \ufffd| Concentration', '| \u2463 | Concentration'),
        ('| \ufffd| Initiative', '| \u2464 | Initiative'),
        ('| \ufffd| Differentiated', '| \u2465 | Differentiated'),
        ('| \ufffd| Multi', '| \u2466 | Multi'),
        
        # Common text fixes
        ('porpoise(P\u2081', 'porpoise(P\u2081'),  # already correct
        ('D\u00b2Plane', 'D\u00b2 Plane'),

        # "? sources" → "≥3 sources"
        ('?emergence', '\u2192 emergence'),

        # Fix double checkmark
        ('\u2705 \u2705 |', '\u2705 |'),
    ]
    
    for old, new in reps:
        text = text.replace(old, new)
    
    after = text.count('?')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return before, after

projects = ['eon-core','cognitive-search-engine','porpoise-agent','coilia-agent','culter-agent']
base = r'D:\Reasonix'

for proj in projects:
    for fname in ['README.md', 'README.zh.md']:
        path = os.path.join(base, proj, fname)
        if os.path.exists(path):
            b, a = fix_project(path)
            print(f'{proj}/{fname}: {b} -> {a} ?')
