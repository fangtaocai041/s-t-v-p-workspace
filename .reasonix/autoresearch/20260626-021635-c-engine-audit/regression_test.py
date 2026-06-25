"""Regression test: verify new parallel search architecture doesn't degrade."""
import sys
from pathlib import Path

ROOT = Path(r'D:\Reasonix')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'cognitive-search-engine' / 'src'))
sys.path.insert(0, str(ROOT / 'cognitive-search-engine'))

# Set up package context for relative imports
import parallel_search._shared as _shared_mod

# Imports work? 
from parallel_search._shared import (
    retry_call, classify_error, ErrorTier, rrf_fuse, EngineBreaker, get_engine_breaker,
    _HEADERS, _TIMEOUT_S, logger
)

# 1. Verify _deduplicate still exists (backward compat)
from parallel_search._engine import _deduplicate, ParallelSearch, SearchStats, _PROVIDERS, _CN_PROVIDERS
assert callable(_deduplicate), "_deduplicate not callable"

# 2. Test retry_call
counter = [0]
def flaky():
    counter[0] += 1
    if counter[0] < 2:
        raise TimeoutError("timed out")
    return "ok"
result = retry_call(flaky, max_retries=2)
assert result == "ok", f"retry_call failed: {result}"
print("[PASS] retry_call works")

# 3. Test classify_error
assert classify_error(TimeoutError("timed out")) == ErrorTier.RETRY
assert classify_error(Exception("429 Too Many Requests")) == ErrorTier.RATE_LIMIT
assert classify_error(Exception("403 Forbidden")) == ErrorTier.FATAL
assert classify_error(Exception("unknown error")) == ErrorTier.SUSPEND
print("[PASS] classify_error 4 tiers correct")

# 4. Test rrf_fuse
list_a = [{"doi": "10.1/a", "title": "Paper A", "source": "pubmed"}]
list_b = [{"doi": "10.1/a", "title": "Paper A", "source": "crossref"}, {"doi": "10.2/b", "title": "Paper B", "source": "crossref"}]
fused = rrf_fuse([list_a, list_b])
assert len(fused) == 2, f"RRF should fuse to 2 papers, got {len(fused)}"
assert fused[0]["_source_count"] == 2, f"Paper A should be in 2 sources, got {fused[0]['_source_count']}"
assert "_rrf_score" in fused[0], "Missing _rrf_score"
print(f"[PASS] rrf_fuse: {len(fused)} papers, top score={fused[0]['_rrf_score']:.4f}")

# 5. Test EngineBreaker
eb = EngineBreaker("test", max_failures=2, suspend_seconds=0.1)
assert eb.can_pass() == True
eb.record_failure()
assert eb.can_pass() == True
eb.record_failure()
assert eb.can_pass() == False  # suspended
import time; time.sleep(0.15)
assert eb.can_pass() == True  # probe allowed after suspend
eb.record_success()
assert eb.can_pass() == True  # recovered
print("[PASS] EngineBreaker suspend/recover cycle")

# 6. Verify SearchStats structure unchanged
s = SearchStats(total_raw=10, total_merged=8, new_papers=[], providers_succeeded=['a'], providers_failed=['b'], elapsed_s=1.0)
assert hasattr(s, 'total_raw')
assert hasattr(s, 'total_merged')
assert hasattr(s, 'new_papers')
assert hasattr(s, 'providers_succeeded')
assert hasattr(s, 'providers_failed')
assert hasattr(s, 'elapsed_s')
print("[PASS] SearchStats structure unchanged")

# 7. Verify all providers registered
assert len(_PROVIDERS) >= 9, f"Expected >=9 providers, got {len(_PROVIDERS)}"
assert len(_CN_PROVIDERS) >= 3, f"Expected >=3 CN providers, got {len(_CN_PROVIDERS)}"
print(f"[PASS] {len(_PROVIDERS)} intl + {len(_CN_PROVIDERS)} CN providers")

# 8. Verify ParallelSearch.search() signature unchanged  
import inspect
sig = inspect.signature(ParallelSearch.search)
params = list(sig.parameters.keys())
assert 'query' in params
assert 'max_per_provider' in params
print(f"[PASS] ParallelSearch.search() signature: {params}")

print("\n=== ALL 8 REGRESSION CHECKS PASSED ===")
