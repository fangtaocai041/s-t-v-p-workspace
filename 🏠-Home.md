# 🧠 Reasonix 工作区 — 首页

> 水生生态研究 · 三生万物架构 · 多智能体协作系统
> 
> `D:\Reasonix` · 1327 篇文档 · 9 个项目

---

## 🔺 三角核心 (密闭三元素)

| 角色 | 项目 | 说明 |
|------|------|------|
| **S/V0** | [[fish-ecology-assistant/README\|鱼类生态助手]] | 知识供给层 · 443+ 物种 · KB-First 搜索 |
| **V/V1** | [[cognitive-search-engine/README\|认知搜索引擎]] | 搜索验证层 · BDI+ReAct · 59 数据库编目 |
| **Coord** | [[eon-core/README\|eon-core]] | 协调内核 · 10层同心架构 |

### 三角文档

- [[fish-ecology-assistant/docs/ARCHITECTURE\|F架构文档]]
- [[cognitive-search-engine/docs/ARCHITECTURE\|C架构文档]]
- [[cognitive-search-engine/ROADMAP\|C路线图]]
- [[fish-ecology-assistant/CHEATSHEET\|F速查表]]

---

## 🌊 衍生智能体

| 项目 | 专题 | 关键能力 |
|------|------|----------|
| [[coilia-agent/README\|刀鲚智能体]] | 刀鲚 | 耳石微化学 · 洄游生态 · CPUE |
| [[culter-agent/README\|鲌类智能体]] | 翘嘴鲌/蒙古鲌 | 基因组 · 稳定同位素 · 年龄生长 |
| [[porpoise-agent/README\|江豚智能体]] | 长江江豚 | NBHF声学 · 栖息地建模 · 种群评估 |

---

## ⚖️ 基础设施

| 项目 | 说明 |
|------|------|
| [[conflict-arbiter/README\|冲突仲裁器]] | 多源保护级别冲突 · 中国优先加权 |
| [[infrastructure/README\|基础设施]] | 涌现检测 · NLP · 统一监控 |
| [[san-sheng-wanwu-core/README\|三生万物核心]] | 硅基生命体 · RCCA |
| [[workspace/README\|统一入口]] | 一键调用全部子项目 |

---

## 📊 编目数据库

> 当前版本: v2.1.0 · 15 领域 · 59 数据库

### 国际学术

| 类型 | 数据库 |
|------|--------|
| 生物医学 | NCBI PubMed · Nucleotide · SRA |
| 生态多样性 | GBIF · IUCN RedList · BHL · EOL · Dryad |
| 水生专题 | FishBase · WoRMS · FAO Fisheries |
| 预印本 | bioRxiv · arXiv (q-bio/cs/stat) |
| AI/ML | PapersWithCode · OpenReview · Semantic Scholar |
| 数学 | Project Euclid · zbMATH |
| 聚合器 | BASE · DART-Europe · NDLTD · OAIster · CORE · DOAJ |

### 大学机构知识库

| 学校 | 强项 | 覆盖领域 |
|------|------|----------|
| UBC cIRcle | 渔业资源评估 | 渔业 · 生态 |
| UW ResearchWorks | 水产与渔业科学 | 渔业 · 水生 |
| Wageningen UR | 水产养殖/生态 | 水生 · 渔业 · 生态 |
| UC eScholarship | 演化/生态/分子 | 生态 · 分子 · 毒理 |
| James Cook Uni | 珊瑚礁/热带渔业 | 水生 · 保护 · 生态 |
| MIT DSpace | 计算生物学/AI | AI · 生物信息 · 数学 |

### 中国学术

| 机构 | 类型 |
|------|------|
| 中科院水生所 (ihb.ac.cn) | 研究所 |
| 中国水产科学院 (cafs.ac.cn) | 研究所 |
| 国家科技图书文献中心 (nstl.gov.cn) | 图书馆 |
| 知网 · 维普 · 万方 | 期刊数据库 |

📁 完整编目: [[cognitive-search-engine/config/database_catalog.yaml]]

---

## 🧬 核心技术栈

| 维度 | 技术 |
|------|------|
| 架构 | BDI + ReAct + RCCA + 三角核心 |
| 搜索 | 并行多源 + Thompson Sampling + MPC 优化 |
| 验证 | Authority Scoring + AgentJudge LLM 评估 |
| 报告 | Hub-and-Spoke 分类 + Markdown 输出 |
| 进化 | 涌现检测 + 反馈闭环 + 编目权重自进化 |
| 协调 | eon-core · EventBus · 10层同心架构 |

---

## 🔗 快速链接

- [[cognitive-search-engine/CHANGELOG\|C更新日志]]
- [[cognitive-search-engine/CONTRIBUTING\|贡献指南]]
- [[fish-ecology-assistant/GUIDE\|F使用指南]]
- [[fish-ecology-assistant/SQLite_操作手册\|SQLite操作手册]]
- [[fish-ecology-assistant/HEARTBEAT\|心跳监控]]

---

## ⚙️ 工作区资源

- `.reasonix/skills/` — 28 个 AI 技能定义
- `.reasonix/memory/` — 持久记忆 · 全局规则
- `logs/` — 编目反馈日志 · 涌现检测日志

---

*最后更新: 2026-06-21 · 编目 v2.1.0 · 112 项集成测试全通过*
