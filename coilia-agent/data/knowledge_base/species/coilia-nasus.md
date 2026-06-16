# ═══════════════════════════════════════════════════════════════
# 刀鲚 (Coilia nasus) 物种知识库
# ═══════════════════════════════════════════════════════════════
# 课题组: 淡水渔业研究中心 刘凯研究员
# 相关物种: 短颌鲚 (C. brachygnathus)、凤鲚 (C. mystus)
# 分类地位: 鲱形目 > 鳀科 > 鲚属

species:
  id: "Coilia_nasus"
  chinese: "刀鲚"
  common_names: ["长江刀鱼", "刀鱼", "长颌鲚", "tapertail anchovy"]
  scientific: "Coilia nasus"
  family: "鳀科 (Engraulidae)"
  order: "鲱形目 (Clupeiformes)"
  genus: "Coilia"

  # IUCN 与保护 status
  conservation:
    iucn: "濒危(EN)"
    china_red_list: "濒危"
    protection_level: "未列入国家重点保护名录"
    yangtze_fishing_ban: "2021年起全面禁捕"
    special_permit: "2019年起停止发放专项捕捞许可证"

  # 生物学特征
  biology:
    max_length: "41 cm"
    common_length: "18-35 cm"
    max_weight: "~200 g"
    lifespan: "4-5 年"
    habitat: "溯河洄游性 — 海洋生长，淡水繁殖"
    spawning_season: "4-6月"
    spawning_grounds: "长江中下游及附属湖泊"
    feeding: "浮游动物、小型甲壳类、仔鱼"
    migration_type: "溯河洄游 (anadromous)"

  # 洄游特征
  migration:
    upstream_period: "2-4月 (溯江而上)"
    downstream_period: "秋冬季 (幼鱼降海)"
    historical_range: "长江口至洞庭湖 (最远可达宜昌)"
    current_range: "大幅萎缩，主要集中于长江口-安徽段"
    key_barriers: ["三峡大坝", "葛洲坝", "沿江多个闸坝"]

  # 经济与文化价值
  cultural:
    nickname: "长江三鲜之首 (刀鱼、鲥鱼、河豚)"
    peak_price: "清明前刀鱼曾达 8000-10000 元/斤"
    fishing_gear: "刀鱼网 (流刺网)、滚钩"
    culinary: "清蒸刀鱼为江南名菜"

  # 近缘种
  related_species:
    - name: "短颌鲚"
      scientific: "Coilia brachygnathus"
      difference: "淡水定居型，上颌骨较短，长江流域优势种之一"
      conservation: "无保护 status"
    - name: "凤鲚"
      scientific: "Coilia mystus"
      difference: "沿海分布为主，偶入长江口"
      conservation: "无保护 status"

  # 资源变迁
  population_trend:
    historical_peak: "1973年长江刀鱼产量 3750t"
    recent_low: "2010年后年产量不足 100t，部分年份 < 50t"
    fishing_ban_effect: "2021年禁捕后资源呈恢复迹象，但尚未系统评估"
    note: "刀鲚资源量仅为历史峰值的 1-3%"

# ══════════════════════════════════════════════════════════════
# 关键研究主题
# ══════════════════════════════════════════════════════════════
research_themes:
  - theme: "耳石微化学与洄游履历"
    methods: ["LA-ICP-MS", "Sr/Ca 比分析", "电子探针"]
    key_questions:
      - "刀鲚个体洄游履历如何重建？"
      - "不同群体间洄游模式差异？"
      - "水利工程对洄游通道的阻断程度？"

  - theme: "群体遗传学与种群结构"
    methods: ["微卫星(SSR)", "线粒体DNA", "SNP", "RAD-seq"]
    key_questions:
      - "长江刀鲚是否有多群体结构？"
      - "刀鲚与短颌鲚的遗传分化程度？"
      - "禁捕后遗传多样性是否恢复？"

  - theme: "资源评估与管理"
    methods: ["CPUE标准化", "体长频率法", "Beverton-Holt模型"]
    key_questions:
      - "禁捕后刀鲚资源恢复速率？"
      - "最大可持续产量(MSY)是多少？"
      - "何时可以考虑重新开放捕捞？"

  - theme: "早期资源与补充群体"
    methods: ["仔鱼网调查", "耳石日轮分析", "产卵场调查"]
    key_questions:
      - "刀鲚产卵场现状与分布？"
      - "补充群体数量年际变化？"

  - theme: "食性与营养生态"
    methods: ["胃含物分析", "稳定同位素(δ13C/δ15N)", "DNA宏条形码"]
    key_questions:
      - "刀鲚在不同生活史阶段的食性转换？"
      - "禁捕后食物网结构变化？"

# ══════════════════════════════════════════════════════════════
# 关键研究团队与文献 (国内)
# ══════════════════════════════════════════════════════════════
key_research_groups:
  - institution: "淡水渔业研究中心"
    researchers: ["刘凯", "徐东坡", "施炜纲"]
    focus: "刀鲚资源评估、洄游生态"
  - institution: "中国水产科学研究院东海水产研究所"
    researchers: ["庄平", "赵峰"]
    focus: "刀鲚耳石微化学、洄游履历"
  - institution: "上海海洋大学"
    researchers: ["唐文乔", "刘其根"]
    focus: "刀鲚遗传学、群体结构"
  - institution: "中国科学院水生生物研究所"
    researchers: ["刘焕章", "陈毅峰"]
    focus: "长江鱼类多样性、刀鲚保护生物学"
