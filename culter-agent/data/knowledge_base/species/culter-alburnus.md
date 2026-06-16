# ═══════════════════════════════════════════════════════════════
# 翘嘴鲌 (Culter alburnus) 物种知识库
# ═══════════════════════════════════════════════════════════════
# 鲌属模式种 — 鲌类专研 Agent (P₃) 核心知识条目
# 相关物种: 蒙古鲌 (C. mongolicus)、尖头鲌 (C. oxycephalus)、红鳍原鲌 (Chanodichthys erythropterus)

species:
  id: "Culter_alburnus"
  chinese: "翘嘴鲌"
  common_names: ["翘嘴", "白鱼", "大白鱼", "翘壳", "topmouth culter", "white culter"]
  scientific: "Culter alburnus"
  family: "鲤科 (Cyprinidae)"
  subfamily: "鲌亚科 (Cultrinae)"
  order: "鲤形目 (Cypriniformes)"
  genus: "Culter (鲌属)"

  # IUCN 与保护状态
  conservation:
    iucn: "未评估 (NE) / 部分水域种群下降"
    china_status: "重要经济鱼类，长江禁捕范围内"
    yangtze_fishing_ban: "2021年起长江干流及重要支流全面禁捕"
    concerns: "过度捕捞 + 栖息地破碎化 + 水利工程阻隔产卵洄游"

  # 生物学特征
  biology:
    max_length: "105 cm"
    common_length: "30-60 cm"
    max_weight: "15 kg"
    common_weight: "0.5-3 kg"
    lifespan: "15-20 年"
    growth_rate: "中等偏快 — 1龄达 15-25 cm，3龄达 30-45 cm"
    feeding:
      type: "凶猛肉食性 (piscivorous)"
      juvenile_diet: "浮游动物 + 水生昆虫"
      adult_diet: "小型鱼类 (餐条、鰟鮍等) + 虾类"
      feeding_habit: "中上层掠食，视觉捕食为主"

  # 繁殖生物学
  reproduction:
    maturity_age: "♀ 3-4 龄, ♂ 2-3 龄"
    spawning_season: "5-7月 (水温 20-28°C)"
    spawning_type: "分批产卵 (batch spawner)"
    spawning_habitat: "静水或缓流、有水生植物的浅水区"
    fecundity: "5-60万粒 (体长依赖性)"
    egg_type: "粘性卵，附着于水草或基质"
    incubation: "2-4天 (水温相关)"

  # 栖息地与分布
  habitat:
    water_body_types: ["湖泊", "水库", "河流缓流段", "通江湖泊"]
    depth_preference: "中上层 (0-5m)，夜间可至表层"
    temperature_range: "4-32°C (最适 22-28°C)"
    distribution_native:
      - "长江水系 (中下游及附属湖泊)"
      - "珠江水系"
      - "黑龙江水系"
      - "东南沿海诸河"
    introduced_areas:
      - "云南高原湖泊 (滇池、洱海等)"
      - "海南岛"
      - "台湾 (少数水域)"

  # 渔业资源
  fishery:
    historical_importance: "长江中下游重要经济鱼类，太湖'三白'之一"
    catch_trend: "野生资源量显著下降（鄱阳湖、洞庭湖尤为明显）"
    aquaculture: "规模化人工养殖已成功，苗种人工繁殖技术成熟"
    management:
      - "长江流域: 禁捕 (2021年起)"
      - "湖区: 限额捕捞 + 增殖放流"
      - "水库: 增殖放流以维持种群"

  # ═══════════════════════════════════════════════════════════
  # 基因组学
  # ═══════════════════════════════════════════════════════════
  genomics:
    genome_size: "~1.0-1.2 Gb (估算，基于近缘鲤科鱼类)"
    chromosome_number: "2n = 48 (鲤科典型)"
    sequencing_status: "已有简化基因组 (RAD-seq/GBS) 和线粒体全基因组数据"
    whole_genome_status: "全基因组组装尚未公开报道 (截至 2025)"
    mitogenome:
      size: "~16.6 kb (典型脊椎动物线粒体基因组)"
      genes: "13 PCGs + 22 tRNA + 2 rRNA + D-loop"
      available_for: ["Culter alburnus", "Culter mongolicus", "Chanodichthys erythropterus"]
    genomic_resources:
      - "RAD-seq: 群体遗传结构、适应性分化扫描"
      - "GBS (Genotyping-by-Sequencing): SNP 标记开发"
      - "转录组: 生长、免疫、繁殖相关基因挖掘"
      - "微卫星 (SSR): 已开发多组多态性引物"
    key_questions:
      - "鲌亚科 (Cultrinae) 系统发育基因组位置不明确"
      - "Culter 与 Chanodichthys 属间界限的基因组证据"
      - "适应性进化: 肉食性 vs 杂食性近缘种的基因家族收缩/扩张"
      - "不同水系群体局部适应 (local adaptation) 的基因组印记"

  # ═══════════════════════════════════════════════════════════
  # 稳定同位素生态学
  # ═══════════════════════════════════════════════════════════
  stable_isotopes:
    commonly_used:
      - isotope: "δ¹³C"
        tissue: "肌肉 (白肌)"
        turnover: "数月 (慢转换组织)"
        interpretation: "碳源示踪 — 沿岸带 (高δ¹³C) vs 湖心带 (低δ¹³C) 饵料贡献比例"
      - isotope: "δ¹⁵N"
        tissue: "肌肉 (白肌)"
        turnover: "数月"
        interpretation: "营养级估算 — 每升高 1 营养级 δ¹⁵N 富集 2.5-3.4‰"
      - isotope: "δ³⁴S"
        tissue: "肌肉"
        interpretation: "区分淡水/海水来源 (辅助洄游研究)"
    baseline_organisms:
      - "初级消费者: 螺类 (Bellamya) — 沿岸带基线"
      - "初级消费者: 蚌类 (Corbicula) — 湖心带基线"
    analytical_methods:
      - "EA-IRMS: 元素分析仪-同位素比质谱"
      - "MixSIAR: 贝叶斯混合模型 (R 包) — 多源饵料贡献比例估算"
      - "SIAR/SIBER: 稳定同位素贝叶斯椭球 — 生态位宽度量化"
    typical_values:
      culter_alburnus_δ13C: "-24‰ ~ -20‰ (淡水湖泊)"
      culter_alburnus_δ15N: "12‰ ~ 16‰ (对应营养级 3.5-4.5)"
      trophic_position: "3.5-4.5 (次级消费者→顶级捕食者，视水体而异)"
    ontogenetic_shift: "体长 > 30 cm 后 δ¹⁵N 显著升高，反映食性由昆虫/浮游向纯鱼类转换"

  # ═══════════════════════════════════════════════════════════
  # 营养生态位
  # ═══════════════════════════════════════════════════════════
  trophic_niche:
    feeding_guild: "顶级捕食者 (apex predator in lacustrine food webs)"
    prey_spectrum:
      fish:
        - "餐条 (Hemiculter leucisculus)"
        - "鰟鮍 (Rhodeus spp.)"
        - "麦穗鱼 (Pseudorasbora parva)"
        - "棒花鱼 (Abbottina rivularis)"
        - "虾虎鱼 (Rhinogobius spp.)"
      crustaceans:
        - "日本沼虾 (Macrobrachium nipponense)"
        - "秀丽白虾 (Exopalaemon modestus)"
      insects: "水生昆虫幼虫 (蜻蜓目/蜉蝣目) — 幼鱼阶段主要饵料"
    niche_metrics:
      levin_index: "0.3-0.6 (中等食性宽度，不同水体差异大)"
      pianka_overlap: "与蒙古鲌重叠 0.5-0.7 (同域分布时)"
    dietary_shift:
      stage_1: "仔鱼期 (< 2 cm): 轮虫 + 枝角类"
      stage_2: "稚鱼期 (2-10 cm): 桡足类 + 水生昆虫幼虫"
      stage_3: "幼鱼期 (10-30 cm): 虾类 + 小型鱼类"
      stage_4: "成鱼期 (> 30 cm): 纯鱼类为主"
    seasonal_variation: "春季摄食强度高 (繁殖前能量积累)，冬季摄食降低但不停食"

  # ═══════════════════════════════════════════════════════════
  # 同域共存与生态位分化
  # ═══════════════════════════════════════════════════════════
  sympatric_coexistence:
    co_occurring_culter_species:
      - pair: "翘嘴鲌 (C. alburnus) ↔ 蒙古鲌 (C. mongolicus)"
        water_bodies: ["洞庭湖", "鄱阳湖", "太湖", "梁子湖"]
        coexistence_mechanisms:
          - "空间生态位分化: 翘嘴鲌偏好开阔水域中上层，蒙古鲌偏好近岸带中下层"
          - "饵料大小分化: 翘嘴鲌捕食较大体型鱼类 (体长 > 8 cm)，蒙古鲌偏好较小个体 (< 6 cm)"
          - "摄食时间分化: 翘嘴鲌晨昏活动高峰，蒙古鲌昼夜均有摄食"
      - pair: "翘嘴鲌 (C. alburnus) ↔ 尖头鲌 (C. oxycephalus)"
        water_bodies: ["长江中上游干支流"]
        coexistence_mechanisms:
          - "微生境分区: 翘嘴鲌占据主流，尖头鲌偏好回流区"
          - "体型差异导致饵料谱分化"
      - pair: "翘嘴鲌 (C. alburnus) ↔ 红鳍原鲌 (Ch. erythropterus)"
        water_bodies: ["长江中下游", "珠江"]
        coexistence_mechanisms:
          - "红鳍原鲌食性更广 (杂食偏动物性)，营养级略低于翘嘴鲌"
          - "红鳍原鲌对低氧耐受更强，可利用翘嘴鲌回避的缺氧区"
    niche_partitioning_axes:
      - axis: "空间 (spatial)"
        description: "垂直分层 (上层 vs 中下层)、水平分布 (开阔区 vs 近岸带)"
        evidence_strength: "强 — 多篇胃含物 + 同位素联合研究支持"
      - axis: "食性 (dietary)"
        description: "饵料大小选择、鱼类 vs 虾类比例、δ¹³C 碳源差异"
        evidence_strength: "强 — 稳定同位素 + 胃含物双验证"
      - axis: "时间 (temporal)"
        description: "摄食节律差异、繁殖期错峰"
        evidence_strength: "中等 — 行为观察数据有限，需水下声学/摄像验证"
    research_gaps:
      - "多物种共存 (>3 种鲌类) 的生态位网络尚不清楚"
      - "环境变化 (水位调控、富营养化) 如何改变共存格局缺乏长期数据"
      - "幼鱼阶段 (体长 < 10 cm) 种间竞争与生态位分化几乎未知"
      - "需要野外原位实验 (enclosure/exclosure) 验证竞争排除假说"

  # 关键研究主题
  key_research_themes:
    - "年龄与生长: 鳞片/耳石/脊椎骨轮纹鉴定，von Bertalanffy 生长方程"
    - "繁殖生物学: 繁殖力、产卵场特征、早期发育"
    - "基因组学: 全基因组组装、比较基因组、适应性进化扫描"
    - "谱系地理与群体遗传: 水系间遗传分化、种群历史动态、基因流"
    - "稳定同位素生态学: δ¹³C/δ¹⁵N 营养级重建、MixSIAR 饵料贡献"
    - "同域共存: 生态位分化、资源分割、种间竞争机制"
    - "资源评估: CPUE 趋势、YPR 模型、参考点估算"
    - "栖息地适宜性: 水位波动影响、产卵场面积变化"
    - "人工养殖: 亲鱼培育、苗种规模化生产、配合饲料开发"

# ═══════════════════════════════════════════════════════════════
# 近缘物种速览
# ═══════════════════════════════════════════════════════════════

related_species:

  - id: "Culter_mongolicus"
    chinese: "蒙古鲌 (蒙古红鲌)"
    scientific: "Culter mongolicus"
    distinguishing: "体侧扁、吻尖、各鳍呈橙红色，体长可达 65 cm"
    distribution: "长江、珠江及北方水系"
    feeding: "肉食性 — 小型鱼类、虾类"
    reproduction: "5-7月产卵，粘性卵"
    status: "经济鱼类，部分水域种群下降"

  - id: "Culter_oxycephalus"
    chinese: "尖头鲌"
    scientific: "Culter oxycephalus"
    distinguishing: "头显著尖长，体长可达 50 cm"
    distribution: "长江中上游及附属水体"
    status: "分布较窄，关注度较低"

  - id: "Chanodichthys_erythropterus"
    chinese: "红鳍原鲌 (红鳍鲌)"
    scientific: "Chanodichthys erythropterus"
    note: "原归鲌属 (Culter)，现置于原鲌属 (Chanodichthys)"
    distinguishing: "胸鳍/腹鳍/臀鳍呈橙红色，体长可达 102 cm"
    distribution: "东亚广泛分布 (中国、俄罗斯、朝鲜半岛、越南)"
    reproduction: "6-7月产卵"
    status: "适应力强，分布广泛，经济价值中等"

  - id: "Culter_dabryi"
    chinese: "达氏鲌"
    scientific: "Culter dabryi"
    distinguishing: "体较小，体长一般 < 30 cm"
    distribution: "长江、钱塘江等水系"
    status: "小型鲌类，经济价值低于翘嘴鲌"

  - id: "Culter_oxycephaloides"
    chinese: "拟尖头鲌"
    scientific: "Culter oxycephaloides"
    distinguishing: "与尖头鲌相似，但吻稍短"
    distribution: "长江中游"
    status: "分布局限，关注度低"
