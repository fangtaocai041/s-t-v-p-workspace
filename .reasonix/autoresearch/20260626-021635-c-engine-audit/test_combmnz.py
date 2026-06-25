import sys; sys.path.insert(0, r'D:\Reasonix\cognitive-search-engine\src')
from parallel_search._shared import combmnz_fuse, fuse_results

a=[{"doi":"x","title":"A","source":"pubmed"}]
b=[{"doi":"x","title":"A","source":"crossref"},{"doi":"y","title":"B","source":"crossref"}]
c=[{"doi":"x","title":"A","source":"openalex"}]

fused = combmnz_fuse([a,b,c])
print(f"CombMNZ: {len(fused)} papers")
for p in fused:
    print(f"  {p['title']}: score={p['_mnz_score']:.3f}, sources={p['_source_count']}")

# Verify fuse_results dispatch
rrf_result = fuse_results([a,b,c], method="rrf")
mnz_result = fuse_results([a,b,c], method="combmnz")
assert len(rrf_result) == len(mnz_result) == 2
print("fuse_results dispatch: OK")
print("ALL CombMNZ TESTS PASSED")
