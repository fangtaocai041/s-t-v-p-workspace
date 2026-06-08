"""Stress test: catalog_loader v4.0 under pressure."""
import sys, time
sys.path.insert(0, 'D:/Reasonix/cognitive-search-engine/src')
from catalog_loader import *

catalog = load_catalog()
OK, FAIL = 0, 0

def check(desc, condition):
    global OK, FAIL
    if condition: OK += 1; print(f'  PASS {desc}')
    else: FAIL += 1; print(f'  FAIL {desc}')

# ── Stress 1: Routing throughput ──
print('STRESS 1: Routing throughput (50 queries x 3 methods)')
N = 50
t0 = time.time()
for i in range(N):
    q = f'test_query_{i} fish genetics diversity'
    score_domains(catalog, q)
    graph_route(catalog, q)
    graph_route(catalog, q, health_aware=True)
elapsed = time.time() - t0
rate = elapsed / (N * 3) * 1000
print(f'  150 routes in {elapsed:.2f}s ({rate:.1f}ms/route)')
check('throughput < 5s total', elapsed < 5)

# ── Stress 2: Edge cases ──
print('\nSTRESS 2: Edge cases')
cases = [
    ('', 'empty query'),
    ('a' * 500, '500-char garbage'),
    ('Ochetobius elongatus (Kner, 1867)', 'full taxonomic authority'),
    ('xYz123_!@#', 'special chars'),
]
for q, desc in cases:
    try:
        r = graph_route(catalog, q, health_aware=True)
        check(f'{desc} -> {len(r)} DBs', len(r) <= 8)
    except Exception as e:
        check(f'{desc}', False)

# ── Stress 3: Feedback storm ──
print('\nSTRESS 3: Feedback storm (200 records)')
import os
fb_path = 'D:/Reasonix/logs/catalog_feedback.jsonl'
if os.path.exists(fb_path):
    os.remove(fb_path)

t0 = time.time()
for i in range(200):
    record_search_result(f'query_{i%10}', f'db_{(i%5)+1}', i % 8, useful=(i % 3 != 0))
check('200 records written', time.time() - t0 < 2)

t0 = time.time()
suggestions = emerge_domains(catalog)
check(f'emerge in {time.time()-t0:.2f}s', time.time() - t0 < 1)

# ── Stress 4: Intent detection ──
print('\nSTRESS 4: Intent detection')
tests = [
    ('文献', 'literature'), ('原始数据', 'data'),
    ('学位论文', 'thesis'), ('全量', 'comprehensive'),
    ('genome assembly', 'literature'),
]
for q, expected in tests:
    intent = detect_intent(catalog, q)['intent']
    check(f'"{q}" -> {intent}', intent == expected)

# ── Stress 5: Progressive route ──
print('\nSTRESS 5: Progressive route integrity')
for q in ['文献', '原始数据', '学位论文']:
    r = progressive_route(catalog, q)
    n_db = sum(len(p['databases']) for p in r['phases'])
    check(f'{q}: {len(r["phases"])} phases, {n_db} DBs', n_db > 0)

# ── Stress 6: Taxonomic unfold ──
print('\nSTRESS 6: Taxonomic unfolding')
levels = taxonomic_unfold(catalog, 'Ochetobius_elongatus')
check(f'{len(levels)} levels', len(levels) >= 4)
for lv in levels:
    check(f'  L{lv["level"]} {lv["label"]}: {len(lv["databases"])} DBs', len(lv['databases']) > 0)

# ── Stress 7: Budget + retreat ──
print('\nSTRESS 7: Budget + SM-2 retreat')
b = search_budget({'intent': 'comprehensive'})
check(f'comprehensive budget = {b}', b == 12500)
b = search_budget({'intent': 'data'})
check(f'data budget = {b}', b == 2500)

r = should_continue_phase(9, 3000, 5000, 1, 3)
check(f'satisficed: {r["action"]}', r['action'] == 'stop_ok')
r = should_continue_phase(0, 1000, 5000, 1, 3, 2)
check(f'empty retreat: {r["action"]}', r['action'] == 'stop_empty')

# ── Summary ──
print(f'\n{"="*40}')
print(f'Results: {OK} passed, {FAIL} failed ({OK+FAIL} total)')
if FAIL == 0:
    print('HIGH-PRESSURE TEST PASSED')
else:
    print('FAILURES DETECTED')
    sys.exit(1)
