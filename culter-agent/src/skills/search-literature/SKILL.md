# Search Literature — 鲌类文献检索

> **触发**: 用户查询鲌类相关文献
> **搜索策略**: 中英双语，5引擎并行

## PREFLIGHT

1. 识别查询中的物种名: `Culter alburnus` / 翘嘴鲌 / `Culter mongolicus` / 蒙古鲌 / `Chanodichthys erythropterus` / 红鳍鲌
2. 生成 OCR 变体: `Culter alburnus` → `Culter alburnis`, `Culter alburna`, `Culter alburnas`
3. 中文变体: 翘嘴鲌 / 白鱼 / 大白鱼 / 翘壳 / 蒙古红鲌 / 红鳍原鲌
4. 确定研究方向: 年龄/生长/繁殖/遗传/资源/栖息地

## PARALLEL SEARCH

```
引擎1 (Google Scholar, priority=1):
  "Culter alburnus" growth OR age OR reproduction

引擎2 (PubMed, priority=2):
  "Culter alburnus"[Title/Abstract]

引擎3 (CNKI, priority=4):
  翘嘴鲌 OR 蒙古鲌 AND (年龄 OR 生长 OR 资源 OR 遗传)

引擎4 (万方, priority=5):
  翘嘴鲌 年龄 生长

引擎5 (百度学术, priority=3):
  site:xueshu.baidu.com 翘嘴鲌 生长 OR 资源
```

## OUTPUT

按主题分类输出:
1. 年龄鉴定与生长建模
2. 繁殖生物学
3. 种群遗传与种质资源
4. 资源评估与管理
5. 栖息地与产卵场
6. 人工养殖与增殖
