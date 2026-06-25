"""Verify C-project engine modules are importable."""
import sys, importlib.util
from pathlib import Path

ROOT = Path(r'D:\Reasonix')

def load_mod(proj_dir, rel_path, name):
    spec = importlib.util.spec_from_file_location(name, str(ROOT / proj_dir / rel_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Test 1: EvolutionExecutor (7 triggers T1-T7)
ee = load_mod('cognitive-search-engine', 'src/evolution_executor.py', 'ee_mod')
from ee_mod import EvolutionExecutor, TRIGGERS
print(f'[OK] EvolutionExecutor: {len(TRIGGERS)} triggers: {[t.id for t in TRIGGERS]}')

# Test 2: InferenceEngine (gap detection + contradictions)
ie_mod = load_mod('cognitive-search-engine', 'src/inference_engine.py', 'ie_mod')
from ie_mod import InferenceEngine
ie = InferenceEngine()
print(f'[OK] InferenceEngine: detect_gaps={hasattr(ie, "_detect_gaps")}, detect_contradictions={hasattr(ie, "_detect_contradictions")}')

# Test 3: EmergenceMonitor
em = load_mod('infrastructure', 'unified_emergence.py', 'em_mod')
from em_mod import EmergenceMonitor, DimensionalLevel
print(f'[OK] EmergenceMonitor + DimensionalLevel')

# Test 4: Hypothesis Generation (via inference engine)
from ie_mod import InferenceEngine
ie2 = InferenceEngine()
test_papers = [
    {"title": "Test A", "year": 2026, "source": "pubmed"},
    {"title": "Test B", "year": 2025, "source": "cnki"},
]
result = ie2.infer(test_papers, "test_species", ["genetics", "ecology"])
print(f'[OK] InferenceEngine.infer() returned: gaps={len(result.knowledge_gaps)}, contradictions={result.contradictions_found}')

print()
print('=== ALL C-PROJECT ENGINE MODULES VERIFIED INTACT ===')
