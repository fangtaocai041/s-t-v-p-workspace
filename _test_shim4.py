"""Test approach 4: shim with proper sys.path setup"""
import shutil, os, sys

os.chdir(r"D:\Reasonix\eon-core")
sys.path.insert(0, ".")
orig = "src/rcca_core.py"
bak = orig + ".test_bak"
shutil.copy2(orig, bak)

# Approach 4: ensure '.' or project root on path first
shim = (
    '"""Redirect to canonical rcca_core.py via direct file load."""\n'
    'import importlib.util as _iu, sys as _sys, os as _os\n'
    "# Ensure project root on path\n"
    '_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))\n'
    '_canonical = r"D:\\Reasonix\\cognitive-search-engine\\src\\rcca_core.py"\n'
    '_spec = _iu.spec_from_file_location("canonical_rcca", _canonical)\n'
    '_mod = _iu.module_from_spec(_spec)\n'
    '_spec.loader.exec_module(_mod)\n'
    '# Re-export all public symbols\n'
    'for _a in dir(_mod):\n'
    '    if not _a.startswith("_"): globals()[_a] = getattr(_mod, _a)\n'
)
with open(orig, "w", encoding="utf-8") as f:
    f.write(shim)

try:
    sys.path.insert(0, ".")
    from src.rcca_core import SelfModelEngine, EmotionEngine, EmotionType
    print("APPROACH 4 OK!")
except Exception as e:
    print("APPROACH 4 FAILED:", e)

shutil.copy2(bak, orig)
os.remove(bak)
print("Original restored")
