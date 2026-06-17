-- ============================================================
-- Fish Trait Database Schema (v1.0)
-- SanShengWanWu Ecosystem — 三生万物 鱼类性状库
-- ============================================================

-- Morphology traits (形态性状)
CREATE TABLE IF NOT EXISTS traits_morphology (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    max_length_cm REAL,
    common_length_cm REAL,
    max_weight_kg REAL,
    body_shape TEXT,              -- 体形: fusiform/compressed/depressed/elongated/anguilliform
    mouth_position TEXT,          -- 口位: terminal/superior/inferior/subterminal
    fin_formula_dorsal TEXT,      -- 背鳍式: D. III,7
    fin_formula_anal TEXT,        -- 臀鳍式
    fin_formula_pectoral TEXT,    -- 胸鳍式
    scale_type TEXT,              -- 鳞式: cycloid/ctenoid/ganoid/placoid/none
    lateral_line_scales INTEGER,  -- 侧线鳞数
    gill_raker_count TEXT,        -- 鳃耙数
    vertebrae_count TEXT,         -- 脊椎骨数
    body_depth_ratio REAL,        -- 体高/体长比
    head_length_ratio REAL,       -- 头长/体长比
    sexual_dimorphism TEXT,       -- 性二型特征
    source TEXT DEFAULT 'FishBase',
    source_url TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3, -- 1-5
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Life history traits (生活史性状)
CREATE TABLE IF NOT EXISTS traits_life_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    lifespan_years REAL,
    age_at_maturity_male REAL,    -- 雄性性成熟年龄
    age_at_maturity_female REAL,  -- 雌性性成熟年龄
    generation_time_years REAL,   -- 世代周期
    growth_rate TEXT,             -- 生长速率描述: fast/moderate/slow
    longevity_record_years REAL,  -- 最长寿命记录
    natural_mortality_m REAL,     -- 自然死亡率 M
    source TEXT DEFAULT 'FishBase',
    source_url TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Reproduction traits (繁殖性状)
CREATE TABLE IF NOT EXISTS traits_reproduction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    spawning_type TEXT,           -- 产卵类型: batch/total/semelparous/iteroparous
    spawning_season_start TEXT,   -- 产卵季起始月: 4
    spawning_season_end TEXT,     -- 产卵季结束月: 6
    spawning_temperature_min REAL,
    spawning_temperature_max REAL,
    spawning_temperature_opt REAL,
    fecundity_min INTEGER,        -- 绝对繁殖力下限
    fecundity_max INTEGER,        -- 绝对繁殖力上限
    fecundity_unit TEXT,          -- 繁殖力单位: eggs/female
    relative_fecundity REAL,      -- 相对繁殖力: eggs/g body weight
    egg_diameter_mm REAL,         -- 卵径 (mm)
    egg_type TEXT,                -- 卵类型: pelagic/demersal/adhesive/semi-buoyant
    larval_length_at_hatch_mm REAL,
    parental_care TEXT,           -- 亲体护卫: none/male/guarding/nest_building/mouth_brooding
    spawning_substrate TEXT,      -- 产卵基质
    spawning_migration TEXT,      -- 产卵洄游: yes/no/unknown
    source TEXT DEFAULT 'FishBase',
    source_url TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Feeding & Trophic traits (食性与营养性状)
CREATE TABLE IF NOT EXISTS traits_feeding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    trophic_level REAL,           -- 营养级 (FishBase Troph)
    feeding_type TEXT,            -- 食性类型: piscivorous/planktivorous/benthivorous/omnivorous/herbivorous/detritivorous
    feeding_period TEXT,          -- 捕食时期: diurnal/nocturnal/crepuscular/continuous
    predation_strategy TEXT,      -- 捕食策略: ambush/pursuit/ suction/gulping/filter_feeding
    diet_composition_juvenile TEXT,  -- 幼鱼食谱
    diet_composition_adult TEXT,     -- 成鱼食谱
    diet_shift_stages TEXT,       -- 食性转换阶段 (e.g. "浮游动物→虾类→鱼类" 如翘嘴鲌)
    prey_size_ratio REAL,         -- 猎物/捕食者体长比
    feeding_migration TEXT,       -- 摄食洄游: yes/no
    daily_feeding_rhythm TEXT,    -- 日摄食节律
    source TEXT DEFAULT 'FishBase',
    source_url TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Stable Isotope traits (稳定同位素特征 — 长江专属)
CREATE TABLE IF NOT EXISTS traits_isotopes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    delta_13c_mean REAL,          -- δ13C 均值 (‰)
    delta_13c_range TEXT,         -- δ13C 范围
    delta_15n_mean REAL,          -- δ15N 均值 (‰)
    delta_15n_range TEXT,         -- δ15N 范围
    trophic_position_estimate REAL,  -- 营养级估算 (基于 δ15N)
    sample_location TEXT,         -- 采样地点
    sample_season TEXT,           -- 采样季节
    sample_year INTEGER,          -- 采样年份
    tissue_type TEXT,             -- 组织类型: muscle/liver/scale/otolith
    source TEXT DEFAULT 'literature',
    source_doi TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Habitat traits (栖息地性状)
CREATE TABLE IF NOT EXISTS traits_habitat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    habitat_type TEXT,            -- 生境类型: river/lake/reservoir/estuary/floodplain
    depth_range_min_m REAL,
    depth_range_max_m REAL,
    temperature_range_min_c REAL,
    temperature_range_max_c REAL,
    temperature_opt_c REAL,
    ph_min REAL,
    ph_max REAL,
    dissolved_oxygen_min_mgl REAL,
    flow_preference TEXT,         -- 流速偏好: lentic/lotic/medium/fast/slow
    substrate_preference TEXT,    -- 底质偏好: mud/sand/gravel/rock/vegetation
    water_type TEXT,              -- 水体类型: freshwater/brackish/marine
    turbidity_tolerance TEXT,     -- 浊度耐受: low/medium/high
    source TEXT DEFAULT 'FishBase',
    source_url TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Migration traits (洄游性状)
CREATE TABLE IF NOT EXISTS traits_migration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    migration_type TEXT,          -- 洄游类型: anadromous/catadromous/potamodromous/oceanodromous/non-migratory
    migration_distance_km REAL,
    migration_season_start TEXT,
    migration_season_end TEXT,
    spawning_migration_detail TEXT,  -- 产卵洄游详情
    feeding_migration_detail TEXT,   -- 摄食洄游详情
    overwintering_migration TEXT,    -- 越冬洄游
    larval_drift TEXT,            -- 仔鱼漂流
    barrier_sensitivity TEXT,     -- 障碍物敏感性: high/medium/low (水坝影响)
    source TEXT DEFAULT 'FishBase',
    source_url TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Conservation traits (保护性状)
CREATE TABLE IF NOT EXISTS traits_conservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    iucn_status TEXT,             -- IUCN: EX/EW/CR/EN/VU/NT/LC/DD/NE
    iucn_assessed_year INTEGER,
    china_red_list_status TEXT,   -- 中国红色名录
    china_red_list_year INTEGER,
    cites_appendix TEXT,          -- CITES: I/II/III/none
    provincial_protection TEXT,   -- 省级保护等级
    national_key_protection TEXT, -- 国家重点保护: 一级/二级/none
    population_trend TEXT,        -- 种群趋势: decreasing/stable/increasing/unknown
    major_threats TEXT,           -- 主要威胁
    commercial_importance TEXT,   -- 商业重要性
    aquaculture_use TEXT,         -- 养殖利用
    source TEXT DEFAULT 'IUCN',
    source_url TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 4,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Growth model traits (生长模型参数)
CREATE TABLE IF NOT EXISTS traits_growth (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id TEXT NOT NULL,
    vbgf_linf_cm REAL,            -- VBGF L∞ (cm)
    vbgf_k REAL,                  -- VBGF K (year⁻¹)
    vbgf_t0 REAL,                 -- VBGF t₀ (year)
    growth_performance_index REAL, -- φ' = log10(K) + 2*log10(L∞)
    length_weight_a REAL,         -- W = a·L^b 参数 a
    length_weight_b REAL,         -- W = a·L^b 参数 b
    sex_ratio TEXT,               -- 性别比
    condition_factor_k REAL,      -- 肥满度 K
    study_location TEXT,          -- 研究地点
    study_year INTEGER,           -- 研究年份
    source TEXT DEFAULT 'literature',
    source_doi TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    confidence INTEGER DEFAULT 3,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Data sources registry (数据来源注册表)
CREATE TABLE IF NOT EXISTS trait_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,
    source_type TEXT,             -- api/database/literature/expert/manual
    url TEXT,
    reliability INTEGER DEFAULT 3,  -- 1-5
    update_frequency TEXT,        -- 更新频率: daily/weekly/monthly/annual/irregular
    last_sync TEXT,
    notes TEXT
);

-- Insert known data sources
INSERT OR IGNORE INTO trait_sources(source_name, source_type, url, reliability, update_frequency, notes)
VALUES
  ('FishBase', 'api', 'https://fishbase.de/api/', 5, 'annual', 'Global authority on fish species data. API returns JSON.'),
  ('FISHMORPH', 'database', 'https://fishmorph.bournemouth.ac.uk/', 4, 'irregular', 'Specialized fish morphological trait database.'),
  ('IUCN Red List', 'api', 'https://apiv3.iucnredlist.org/', 5, 'annual', 'Global conservation status authority.'),
  ('CITES', 'database', 'https://cites.org/eng/app/appendices.php', 5, 'periodic', 'CITES appendices updated every 2-3 years.'),
  ('China Red List', 'database', 'http://www.mee.gov.cn/', 4, 'irregular', '中国红色名录，更新不固定。最近版本: 2023。'),
  ('Yangtze Fish Book', 'literature', '《长江鱼类》(multiple editions)', 5, 'irregular', '长江流域鱼类权威专著，无API，手工录入。'),
  ('淡水渔业研究中心', 'expert', 'FFRC, CAFS', 5, 'continuous', '刘凯研究员课题组，长江鱼类一手数据。'),
  ('水生生物学报', 'literature', 'http://ssswxb.ihb.ac.cn/', 4, 'monthly', '中文核心期刊，长江鱼类形态/生态数据丰富。'),
  ('中国水产科学', 'literature', 'http://www.fishscichina.com/', 4, 'monthly', '水产科学核心期刊。'),
  ('FAO FishStat', 'database', 'https://www.fao.org/fishery/statistics/', 4, 'annual', 'FAO全球渔业统计数据。');
