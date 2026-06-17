# ═══════════════════════════════════════════════════════════════
# 短颌鲚 (Coilia brachygnathus) 物种知识库
# ═══════════════════════════════════════════════════════════════
# 课题组: 淡水渔业研究中心 刘凯研究员
# 相关物种: 刀鲚 (C. nasus) — 曾被认为是刀鲚的同物异名
# 分类地位: 鲱形目 > 鳀科 > 鲚属

species:
  id: "Coilia_brachygnathus"
  chinese: "短颌鲚"
  common_names: ["毛花鱼", "毛刀鱼", "短颌"]
  scientific: "Coilia brachygnathus"
  family: "鳀科 (Engraulidae)"
  order: "鲱形目 (Clupeiformes)"
  genus: "Coilia"

  # 分类争议
  taxonomy:
    note: "曾被认为是刀鲚(Coilia nasus)的同物异名，现基于形态和分子证据确认为独立物种"
    key_differences:
      - "上颌骨较短，不达胸鳍基部"
      - "鳃耙数较少"
      - "淡水定居，不作长距离洄游"
    genetic_evidence: "COI + 微卫星标记支持物种独立性"

  # IUCN 与保护 status
  conservation:
    iucn: "未评估(NE)"
    china_red_list: "未列入"
    protection_level: "无"
    note: "资源量相对稳定，分布范围广"

  # 生物学特征
  biology:
    max_length: "~25 cm"
    common_length: "12-20 cm"
    habitat: "淡水定居 — 终生生活在淡水环境"
    spawning_season: "4-6月"
    spawning_grounds: "长江中下游干流及附属湖泊"
    feeding: "浮游动物、小型甲壳类、水生昆虫幼虫"
    migration_type: "淡水定居 (freshwater resident)"

  # 分布
  distribution:
    primary: "长江中下游干流"
    lakes: ["洞庭湖", "鄱阳湖", "巢湖"]
    note: "分布范围与刀鲚淡水群体重叠"

  # 经济价值
  economic:
    fishery: "长江中下游重要经济鱼类"
    gear: "流刺网、拖网"
    market_value: "中等 (低于刀鲚)"
    annual_catch: "数据待补全"

  # 研究现状
  research:
    key_topics:
      - "物种界定与分类争议 (vs. C. nasus)"
      - "群体遗传结构"
      - "淡水适应性进化"
    knowledge_gaps:
      - "精确资源量评估"
      - "食性生态详细研究"
      - "与刀鲚的生态位分化"
