# SQLite 数据库操作手册
# 三生万物 · 鱼类知识库

## 打开数据库

方法1：双击打开 DB Browser for SQLite，点"打开数据库"选 species.db
方法2：文件 → 打开 → D:\Reasonix\fish-ecology-assistant\data\species.db

## 界面说明

┌─────────────┬──────────────────────────┐
│  数据库结构   │     数据表格              │
│  (左侧)      │     (右侧)               │
│             │                          │
│  所有表名    │  选中表后显示所有数据       │
│  species    │  和 Excel 几乎一样         │
│  literature │  可以直接点单元格修改！      │
│  traits_*   │                          │
│  ...        │                          │
└─────────────┴──────────────────────────┘

## 常用操作（在"执行SQL"标签页里粘贴运行）

### 查看物种列表
SELECT chinese, scientific, family, conservation FROM species ORDER BY chinese;

### 查看刀鲚的全部信息
SELECT * FROM species WHERE chinese='刀鲚';

### 查看所有性状数据
SELECT * FROM traits_feeding;
SELECT * FROM traits_migration;
SELECT * FROM traits_conservation;
SELECT * FROM traits_morphology;

### 模糊搜索（搜"鲌"相关的）
SELECT chinese, scientific FROM species WHERE chinese LIKE '%鲌%';

### 查某个物种的文献
SELECT title, year, journal FROM literature
WHERE species_id='ochetobius_elongatus' ORDER BY year DESC;

### 添加新物种
INSERT INTO species(id, scientific, chinese, family, conservation)
VALUES('新ID', '学名', '中文名', '科', '保护等级');

### 添加性状数据
INSERT INTO traits_feeding(species_id, trophic_level, feeding_type, source, confidence)
VALUES('物种ID', 3.5, 'piscivorous', '你的数据来源', 4);

### 修改数据
UPDATE species SET conservation='濒危(EN)' WHERE chinese='刀鲚';

### 删除数据（慎重！）
DELETE FROM traits_feeding WHERE id=99;

## 修改完后一定要点"保存"按钮（Ctrl+S）！

## 数据表说明

species         — 30种长江鱼类
literature      — 文献记录
aliases         — 别名
traits_feeding  — 食性（营养级/捕食策略/食谱/食性转换）
traits_migration— 洄游（类型/距离/季节/水坝敏感性）
traits_conservation— 保护（IUCN/中国红色名录/威胁）
traits_morphology— 形态（体长/口位/鳞式/鳍式）
traits_growth   — 生长（VBGF参数）
traits_reproduction— 繁殖
traits_habitat  — 栖息地
traits_isotopes — 稳定同位素
traits_life_history— 生活史
trait_sources   — 数据来源注册表
taxonomic_synonyms— 分类变更追踪
