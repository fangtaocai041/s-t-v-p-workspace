# Task Spec: C项目引擎功能完整性验证

## Goal
验证 `c项目引擎集成分析.md` 中引用的 cognitive-search-engine 三大子系统
是否仍然存在且可用：
1. EvolutionExecutor (7触发器)
2. InferenceEngine (推断/缺口检测)
3. Hypothesis Generation (涌现/矛盾检测)

## Scope
- 检查 cognitive-search-engine/src/ 下对应源文件是否存在
- 检查每个模块的类/函数签名是否完整
- 检查是否有 import 错误或缺失依赖
- 对照 c项目引擎集成分析.md 的引用一一核实

## Non-goals
- 不修复发现的缺失功能（仅报告）
- 不检查其他项目

## Success Criteria
- [ ] EvolutionExecutor 7个触发器（T1-T7）可导入
- [ ] InferenceEngine 可导入且含 gap detection
- [ ] Hypothesis Generation / EmergenceMonitor 可导入
- [ ] 所有依赖链完整（无 ImportError）
