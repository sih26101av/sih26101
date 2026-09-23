"""
Static, hand-written domain content: the MoSPI competency families that extend
the original 40-competency catalogue to a full FRAC-scale dictionary.

Everything here is SYNTHETIC. It is shaped like the MoSPI slice of the FRAC
dictionary (the real FRAC runs to several hundred competencies across
ministries) so the platform can be demonstrated at realistic scale. It is not
an export of any real system.

Each entry is a tuple:

    (id, name, competencyType, decayClass, shortName, description, topics,
     gsbpm, overlap, depth)

  competencyType  "Domain" | "Functional" | "Behavioural"  (FRAC category)
  decayClass      "accuracy"   - methods/tools that go stale fast
                  "procedural" - practised routines and behaviours
  shortName       the subject as it reads inside a course title
  topics          >= 5 syllabus topics; course titles, course descriptions and
                  the item bank all draw from these
  gsbpm           GSBPM v5.1 sub-processes where the competency is exercised
  overlap         competencies a course on this one may legitimately also
                  teach (the only pairs allowed to carry a secondary tag)
  depth           catalogue depth (see domain.CATALOG_DEPTH):
                  "standard" - 1-3 courses per level, full L1-L5 ladder
                  "thin"     - 1-2 courses per level, niche subject whose
                               ladder may stop short of L5

Ids continue the original numbering (comp_*_041 onwards) so the first 40
catalogue ids stay exactly as they were.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# Family 1 - subject-matter statistics (what the statistical system publishes)
# ─────────────────────────────────────────────────────────────────────────────
SUBJECT_MATTER = [
    ("comp_labour_stats_041", "Labour Force & Employment Statistics", "Domain", "accuracy",
     "Labour Force Statistics",
     "Measuring employment, unemployment and labour force participation from the Periodic Labour Force "
     "Survey: ICLS activity-status concepts, worker-population ratios and quarterly urban estimates.",
     ["ICLS activity status concepts", "usual status and current weekly status", "worker population ratio and LFPR",
      "unemployment rate estimation", "quarterly urban labour estimates", "labour underutilisation indicators",
      "employment by industry and occupation"],
     ["2.2", "5.2", "5.7", "6.1", "6.3"],
     ["comp_survey_design_002", "comp_informal_sector_043", "comp_wage_stats_042"], "standard"),

    ("comp_wage_stats_042", "Wage, Earnings & Labour Cost Statistics", "Domain", "accuracy",
     "Wage and Earnings Statistics",
     "Compiling wage, earnings and labour-cost statistics: earnings distributions from surveys and "
     "administrative payrolls, real wage indices and gender wage gaps.",
     ["earnings distributions from survey data", "administrative payroll sources", "real wage indices",
      "gender and sectoral wage gaps", "labour cost per unit of output", "minimum wage compliance statistics"],
     ["5.5", "5.7", "6.1", "6.3"],
     ["comp_labour_stats_041", "comp_poverty_014"], "thin"),

    ("comp_informal_sector_043", "Informal Sector & Unincorporated Enterprise Statistics", "Domain", "accuracy",
     "Informal Sector Statistics",
     "Measuring the informal sector and unincorporated enterprises: survey concepts, enterprise listing "
     "without a register, own-account enterprises and informal employment.",
     ["informal sector and informal employment concepts", "unincorporated enterprise survey design",
      "listing enterprises without a register", "own-account enterprises and establishments",
      "gross value added of the informal sector", "seasonality in informal activity"],
     ["2.4", "4.1", "4.3", "5.7", "6.1"],
     ["comp_labour_stats_041", "comp_msme_stats_061", "comp_survey_design_002"], "standard"),

    ("comp_education_stats_044", "Education Statistics & Learning Indicators", "Domain", "accuracy",
     "Education Statistics",
     "Education statistics from administrative systems and surveys: enrolment and attendance ratios, "
     "out-of-school children, learning-outcome indicators and education expenditure.",
     ["gross and net enrolment ratios", "attendance and dropout measurement", "out-of-school children estimates",
      "learning outcome indicators", "household expenditure on education", "teacher and school infrastructure data",
      "school administrative data quality"],
     ["1.5", "5.1", "6.1", "6.3"],
     ["comp_social_consumption_075", "comp_sdg_monitor_015", "comp_admin_data_125"], "standard"),

    ("comp_health_stats_045", "Health Statistics & Disease Burden Indicators", "Domain", "accuracy",
     "Health Statistics",
     "Health statistics for policy: morbidity and health-service utilisation from surveys, out-of-pocket "
     "expenditure, health accounts and disease-burden indicators.",
     ["morbidity and health service utilisation", "out-of-pocket health expenditure",
      "national health accounts", "immunisation and maternal health indicators",
      "disease burden and mortality indicators", "health insurance coverage statistics"],
     ["1.5", "5.1", "6.1", "6.3"],
     ["comp_social_consumption_075", "comp_nutrition_stats_046", "comp_civil_reg_076"], "standard"),

    ("comp_nutrition_stats_046", "Nutrition & Food Security Statistics", "Domain", "accuracy",
     "Nutrition Statistics",
     "Measuring nutrition and food security: calorie and nutrient intake from consumption surveys, "
     "anthropometric indicators, dietary diversity and the prevalence of undernourishment.",
     ["calorie and nutrient intake from consumption data", "anthropometric indicators",
      "dietary diversity scores", "prevalence of undernourishment", "food consumption and PDS uptake",
      "food balance sheets"],
     ["5.5", "5.7", "6.1"],
     ["comp_health_stats_045", "comp_poverty_014", "comp_agri_stats_009"], "thin"),

    ("comp_gender_stats_047", "Gender Statistics & Women's Empowerment Indicators", "Domain", "procedural",
     "Gender Statistics",
     "Producing gender statistics: sex-disaggregated indicators, gender gaps in work and earnings, unpaid "
     "care work, women's agency indicators and the gender statistics compendium.",
     ["sex-disaggregated indicator design", "gender gaps in work and earnings", "unpaid care and domestic work",
      "women's agency and decision-making indicators", "violence against women statistics",
      "gender statistics compendium production"],
     ["1.3", "5.5", "6.1", "7.2"],
     ["comp_timeuse_stats_074", "comp_sdg_monitor_015", "comp_inclusion_198"], "standard"),

    ("comp_child_stats_048", "Child & Youth Statistics", "Domain", "accuracy",
     "Child and Youth Statistics",
     "Statistics on children and youth: child work and schooling, youth transitions to employment, "
     "NEET rates and child well-being indicators.",
     ["child work and schooling indicators", "youth NEET rate", "transition from school to work",
      "child well-being composite indicators", "child mortality and nutrition indicators",
      "youth aspirations and skilling data"],
     ["5.5", "6.1", "6.3"],
     ["comp_education_stats_044", "comp_labour_stats_041"], "thin"),

    ("comp_disability_stats_049", "Disability Statistics & Inclusion Measurement", "Domain", "accuracy",
     "Disability Statistics",
     "Measuring disability and inclusion: the Washington Group short set, functional-difficulty questions, "
     "prevalence estimation and accessibility indicators.",
     ["Washington Group short set questions", "functional difficulty measurement",
      "disability prevalence estimation", "accessibility and participation indicators",
      "disaggregation by disability status", "survey adaptations for respondents with disability"],
     ["2.2", "5.5", "6.1"],
     ["comp_inclusion_198", "comp_sdg_monitor_015"], "thin"),

    ("comp_elderly_stats_050", "Ageing & Elderly Population Statistics", "Domain", "accuracy",
     "Elderly Population Statistics",
     "Statistics on ageing: elderly dependency ratios, living arrangements, morbidity and care needs, and "
     "old-age income security indicators.",
     ["old-age dependency ratios", "living arrangements of the elderly", "elderly morbidity and care needs",
      "pension and income security coverage", "elderly labour force participation",
      "projections of the elderly population"],
     ["5.5", "6.1", "6.3"],
     ["comp_dem_analysis_008", "comp_health_stats_045"], "thin"),

    ("comp_housing_stats_051", "Housing, Slum & Urban Statistics", "Domain", "accuracy",
     "Urban and Housing Statistics",
     "Urban and housing statistics: housing condition surveys, slum definitions and enumeration, urban "
     "amenities, and city-level indicator frameworks.",
     ["housing condition survey design", "slum definitions and enumeration", "urban amenity indicators",
      "rent and housing cost measurement", "city-level indicator frameworks", "urban sprawl and land-use data"],
     ["2.3", "4.3", "5.7", "6.1"],
     ["comp_housing_price_091", "comp_spatial_stat_012", "comp_water_sanitation_052"], "thin"),

    ("comp_water_sanitation_052", "Water, Sanitation & Hygiene Statistics", "Domain", "accuracy",
     "WASH Statistics",
     "Water, sanitation and hygiene statistics: access to drinking water and sanitation, service-level "
     "ladders, water quality indicators and WASH-related SDG reporting.",
     ["drinking water access indicators", "sanitation service ladders", "hygiene practice measurement",
      "water quality indicators", "WASH indicators in the SDG framework", "rural and urban WASH comparisons"],
     ["5.5", "6.1", "7.2"],
     ["comp_sdg_monitor_015", "comp_housing_stats_051"], "thin"),

    ("comp_energy_stats_053", "Energy Statistics & Energy Balances", "Domain", "accuracy",
     "Energy Statistics",
     "Compiling energy statistics: production, trade and consumption by fuel, energy balance tables, "
     "energy intensity and access-to-electricity indicators.",
     ["energy production and consumption by fuel", "energy balance tables", "energy intensity of GDP",
      "renewable energy share indicators", "household energy access", "energy price and subsidy data"],
     ["5.1", "5.7", "6.1", "6.2"],
     ["comp_environment_stats_054", "comp_industry_stats_010", "comp_climate_stats_055"], "standard"),

    ("comp_environment_stats_054", "Environment Statistics & SEEA Accounting", "Domain", "accuracy",
     "Environment Statistics",
     "Environment statistics and environmental-economic accounting: the SEEA central framework, asset and "
     "flow accounts, emission inventories and the EnviStats compilation.",
     ["SEEA central framework", "natural resource asset accounts", "air emission accounts",
      "waste and material flow accounts", "framework for the development of environment statistics",
      "EnviStats compilation workflow"],
     ["1.4", "5.1", "5.7", "6.1", "OA.SM"],
     ["comp_climate_stats_055", "comp_forest_stats_056", "comp_nat_accounts_001"], "standard"),

    ("comp_climate_stats_055", "Climate Change & Disaster Statistics", "Domain", "accuracy",
     "Climate and Disaster Statistics",
     "Climate change and disaster-related statistics: the global set of climate change statistics, "
     "disaster loss databases, exposure and vulnerability indicators and adaptation spending.",
     ["global set of climate change statistics", "disaster loss and damage databases",
      "exposure and vulnerability indicators", "greenhouse gas inventory basics",
      "climate adaptation expenditure tracking", "extreme event frequency indicators"],
     ["1.5", "5.1", "6.1", "6.3"],
     ["comp_environment_stats_054", "comp_disaster_mgmt_190"], "thin"),

    ("comp_forest_stats_056", "Forest, Biodiversity & Natural Resource Statistics", "Domain", "accuracy",
     "Forest and Biodiversity Statistics",
     "Statistics on forests, biodiversity and natural resources: forest cover assessment, ecosystem extent "
     "and condition accounts, and resource depletion estimates.",
     ["forest cover and canopy density assessment", "ecosystem extent and condition accounts",
      "biodiversity indicators", "natural resource depletion estimates", "land degradation indicators",
      "remote sensing for forest monitoring"],
     ["5.1", "5.7", "6.1"],
     ["comp_environment_stats_054", "comp_spatial_stat_012"], "thin"),

    ("comp_transport_stats_057", "Transport & Logistics Statistics", "Domain", "accuracy",
     "Transport Statistics",
     "Transport and logistics statistics: freight and passenger volumes by mode, vehicle registration data, "
     "road accident statistics and logistics performance indicators.",
     ["freight and passenger volumes by mode", "vehicle registration administrative data",
      "road accident statistics", "logistics cost and performance indicators", "transport infrastructure inventory",
      "modal share and traffic surveys"],
     ["5.1", "5.7", "6.1"],
     ["comp_admin_data_125", "comp_services_stats_060"], "thin"),

    ("comp_tourism_stats_058", "Tourism Statistics & Tourism Satellite Account", "Domain", "accuracy",
     "Tourism Statistics",
     "Tourism statistics and the Tourism Satellite Account: visitor arrivals and expenditure, domestic "
     "tourism surveys, tourism direct GVA and employment in tourism industries.",
     ["visitor arrival and expenditure statistics", "domestic tourism survey design",
      "tourism satellite account structure", "tourism direct gross value added", "employment in tourism industries",
      "tourism price and occupancy indicators"],
     ["5.1", "5.7", "6.1"],
     ["comp_satellite_acct_087", "comp_services_stats_060"], "thin"),

    ("comp_trade_stats_059", "External Trade Statistics & HS Classification", "Domain", "accuracy",
     "External Trade Statistics",
     "Merchandise and services trade statistics: customs data processing, the Harmonised System, unit value "
     "indices, trade in value added and partner-country asymmetries.",
     ["customs data processing", "Harmonised System classification", "merchandise trade unit value indices",
      "trade in services measurement", "partner country asymmetries", "trade in value added concepts"],
     ["5.1", "5.2", "5.7", "6.2"],
     ["comp_bop_081", "comp_classification_122", "comp_index_numbers_004"], "standard"),

    ("comp_services_stats_060", "Services Sector Statistics", "Domain", "accuracy",
     "Services Sector Statistics",
     "Measuring the services sector: the annual survey of service sector enterprises, output and price "
     "measurement for services, and the services contribution to GVA.",
     ["annual survey of service sector enterprises", "output measurement for services",
      "services price and volume measurement", "services contribution to GVA", "professional and business services",
      "coverage of digitally delivered services"],
     ["2.4", "4.3", "5.7", "6.1"],
     ["comp_service_price_092", "comp_nat_accounts_001", "comp_business_register_079"], "standard"),

    ("comp_msme_stats_061", "MSME & Entrepreneurship Statistics", "Domain", "accuracy",
     "MSME Statistics",
     "Statistics on micro, small and medium enterprises: MSME definitions and registers, enterprise "
     "demography, credit access indicators and entrepreneurship rates.",
     ["MSME definitions and thresholds", "enterprise demography and birth-death rates",
      "enterprise registration data quality", "credit access indicators for enterprises", "entrepreneurship rates",
      "employment in micro enterprises"],
     ["4.1", "5.1", "5.7", "6.1"],
     ["comp_informal_sector_043", "comp_business_register_079", "comp_econ_census_007"], "standard"),

    ("comp_construction_stats_062", "Construction & Infrastructure Statistics", "Domain", "accuracy",
     "Construction Statistics",
     "Construction sector statistics: measuring construction output by the commodity-flow approach, "
     "construction cost indices, and infrastructure asset inventories.",
     ["commodity flow approach for construction", "construction cost indices",
      "building material production data", "infrastructure asset inventories", "construction employment estimates",
      "real estate and housing starts data"],
     ["5.1", "5.5", "5.7", "6.1"],
     ["comp_nat_accounts_001", "comp_housing_price_091", "comp_project_monitor_100"], "thin"),

    ("comp_mining_stats_063", "Mining & Mineral Statistics", "Domain", "accuracy",
     "Mining Statistics",
     "Mining and mineral statistics: mineral production and value, royalty and administrative returns, "
     "the mining component of the IIP and resource accounting for minerals.",
     ["mineral production and value statistics", "royalty and administrative returns",
      "mining component of the IIP", "mineral resource accounts", "employment and safety statistics in mining",
      "unreported extraction indicators"],
     ["5.1", "5.3", "5.7"],
     ["comp_industry_stats_010", "comp_environment_stats_054"], "thin"),

    ("comp_banking_stats_064", "Banking, Money & Financial Statistics", "Domain", "accuracy",
     "Banking and Money Statistics",
     "Monetary and financial statistics: monetary aggregates, credit and deposit statistics, financial "
     "soundness indicators and financial inclusion measurement.",
     ["monetary aggregates and their components", "credit and deposit statistics",
      "financial soundness indicators", "financial inclusion measurement", "interest rate statistics",
      "sectoral deployment of bank credit"],
     ["5.1", "5.7", "6.1"],
     ["comp_flow_funds_082", "comp_gfs_080"], "thin"),

    ("comp_insurance_stats_065", "Insurance & Pension Statistics", "Domain", "accuracy",
     "Insurance and Pension Statistics",
     "Insurance and pension statistics: premium and claims data, insurance penetration and density, pension "
     "fund coverage and the treatment of insurance in the national accounts.",
     ["premium and claims statistics", "insurance penetration and density",
      "pension fund coverage statistics", "insurance output in national accounts", "actuarial reserves data",
      "social insurance scheme statistics"],
     ["5.1", "5.5", "6.1"],
     ["comp_nat_accounts_001", "comp_banking_stats_064"], "thin"),

    ("comp_capital_mkt_066", "Capital Market & Corporate Sector Statistics", "Domain", "accuracy",
     "Corporate Sector Statistics",
     "Corporate and capital market statistics: company financial statements as a statistical source, "
     "corporate savings and investment, market capitalisation and the company returns database.",
     ["company financial statements as a source", "company returns database structure",
      "corporate savings and investment estimates", "market capitalisation statistics",
      "private corporate sector GVA", "data validation of company returns"],
     ["5.1", "5.3", "5.7", "6.2"],
     ["comp_nat_accounts_001", "comp_admin_data_125"], "thin"),

    ("comp_telecom_stats_067", "Telecom & Digital Connectivity Statistics", "Domain", "accuracy",
     "Telecom Statistics",
     "Telecom and connectivity statistics: subscriber and teledensity indicators, broadband penetration, "
     "data usage and the digital divide across states and social groups.",
     ["subscriber and teledensity indicators", "broadband penetration measurement",
      "mobile data usage statistics", "digital divide indicators", "telecom tariff and revenue data",
      "quality of service indicators"],
     ["5.1", "5.7", "6.1"],
     ["comp_ict_stats_068", "comp_admin_data_125"], "thin"),

    ("comp_ict_stats_068", "ICT Usage & Digital Economy Statistics", "Domain", "accuracy",
     "Digital Economy Statistics",
     "Measuring ICT use and the digital economy: household and enterprise ICT modules, digital skills "
     "indicators, and the digital economy satellite account.",
     ["household ICT use modules", "enterprise ICT and e-business modules", "digital skills indicators",
      "digital economy satellite account", "measuring digitally ordered transactions",
      "internet use and access statistics"],
     ["2.2", "5.7", "6.1"],
     ["comp_ecommerce_stats_069", "comp_satellite_acct_087", "comp_telecom_stats_067"], "standard"),

    ("comp_ecommerce_stats_069", "E-commerce & Platform Economy Measurement", "Domain", "accuracy",
     "E-commerce Measurement",
     "Measuring e-commerce and platform work: transaction volumes from platform data, gig and platform "
     "employment, cross-border digital trade and the treatment of platforms in the accounts.",
     ["e-commerce transaction measurement", "gig and platform employment", "platform data as a source",
      "cross-border digital trade", "treatment of platforms in national accounts",
      "price measurement for online retail"],
     ["1.5", "5.1", "5.7"],
     ["comp_ict_stats_068", "comp_web_scraping_158", "comp_informal_sector_043"], "thin"),

    ("comp_rnd_stats_070", "Research, Development & Innovation Statistics", "Domain", "accuracy",
     "R&D and Innovation Statistics",
     "R&D and innovation statistics: the Frascati and Oslo manual concepts, R&D expenditure and personnel, "
     "patent statistics and innovation survey design.",
     ["Frascati manual R&D concepts", "R&D expenditure and personnel statistics", "Oslo manual innovation concepts",
      "innovation survey design", "patent and bibliometric statistics", "R&D in the national accounts"],
     ["1.4", "5.7", "6.1"],
     ["comp_nat_accounts_001", "comp_survey_design_002"], "thin"),

    ("comp_crime_stats_071", "Crime & Justice Statistics", "Domain", "accuracy",
     "Crime and Justice Statistics",
     "Crime and justice statistics: the international classification of crime, police and court "
     "administrative data, victimisation surveys and case-disposal indicators.",
     ["international classification of crime for statistical purposes", "police administrative records",
      "court and case disposal indicators", "victimisation survey design", "under-reporting of offences",
      "prison and correctional statistics"],
     ["5.2", "5.3", "6.1"],
     ["comp_governance_stats_072", "comp_admin_data_125"], "thin"),

    ("comp_governance_stats_072", "Governance & Public Administration Statistics", "Domain", "accuracy",
     "Governance Statistics",
     "Governance statistics: the Praia handbook domains, service-delivery and corruption-perception "
     "measurement, and citizen experience surveys.",
     ["Praia handbook governance domains", "service delivery experience surveys",
      "corruption and integrity perception measurement", "access to justice indicators",
      "civic participation indicators", "governance indicators in the SDG framework"],
     ["1.3", "5.7", "6.1"],
     ["comp_crime_stats_071", "comp_sdg_monitor_015", "comp_citizen_039"], "thin"),

    ("comp_migration_stats_073", "Migration & Mobility Statistics", "Domain", "accuracy",
     "Migration Statistics",
     "Migration statistics: internal and international migration concepts, migration modules in household "
     "surveys, remittance measurement and circular-migration estimation.",
     ["internal and international migration concepts", "migration modules in household surveys",
      "remittance flow measurement", "circular and seasonal migration estimation",
      "migrant worker living conditions", "administrative sources on migration"],
     ["2.2", "5.5", "6.1"],
     ["comp_dem_analysis_008", "comp_labour_stats_041"], "thin"),

    ("comp_timeuse_stats_074", "Time Use Survey Methodology", "Domain", "accuracy",
     "Time Use Surveys",
     "Time use survey methodology: activity classification, diary design and recall, simultaneous "
     "activities, and valuing unpaid care and domestic work.",
     ["time use activity classification", "time diary design and recall periods", "simultaneous activity coding",
      "valuing unpaid care and domestic work", "time use estimates by sex and age",
      "quality checks on diary data"],
     ["2.2", "2.3", "5.2", "6.1"],
     ["comp_gender_stats_047", "comp_satellite_acct_087", "comp_survey_design_002"], "standard"),

    ("comp_social_consumption_075", "Social Consumption Surveys (Health & Education)", "Domain", "accuracy",
     "Social Consumption Surveys",
     "Designing and analysing social consumption surveys on health and education: schedule structure, "
     "recall periods for ailments and expenses, and estimating utilisation and spending.",
     ["social consumption schedule structure", "recall periods for ailments and expenses",
      "estimating service utilisation", "household expenditure on health and education",
      "hospitalisation episode measurement", "comparability across survey rounds"],
     ["2.3", "4.3", "5.7", "6.1"],
     ["comp_health_stats_045", "comp_education_stats_044", "comp_survey_design_002"], "standard"),

    ("comp_civil_reg_076", "Civil Registration & Vital Statistics", "Domain", "procedural",
     "Civil Registration and Vital Statistics",
     "Civil registration and vital statistics: birth and death registration completeness, cause-of-death "
     "certification, and deriving vital rates from registration data.",
     ["birth and death registration completeness", "medical certification of cause of death",
      "vital rates from registration data", "registration reporting flows",
      "linkage of registration with health systems", "quality assessment of registration data"],
     ["4.3", "5.1", "5.3", "6.1"],
     ["comp_sample_reg_077", "comp_dem_analysis_008"], "thin"),

    ("comp_sample_reg_077", "Sample Registration System & Vital Rates", "Domain", "accuracy",
     "Sample Registration System",
     "The Sample Registration System: dual-record design, half-yearly surveys and matching, estimation of "
     "birth, death and infant mortality rates, and bias assessment.",
     ["dual record system design", "half-yearly survey and matching", "birth and death rate estimation",
      "infant and maternal mortality rate estimation", "sampling error of vital rates",
      "under-registration bias assessment"],
     ["2.4", "4.3", "5.5", "6.2"],
     ["comp_civil_reg_076", "comp_dem_analysis_008", "comp_survey_design_002"], "thin"),

    ("comp_census_pop_078", "Population Census Operations", "Domain", "procedural",
     "Population Census Operations",
     "Population census operations: house listing, enumeration block formation, field hierarchy and "
     "training, census schedules, and post-enumeration evaluation.",
     ["house listing and enumeration blocks", "census field hierarchy and training", "census schedule design",
      "digital census data capture", "post-enumeration survey", "census tabulation and dissemination plan"],
     ["2.3", "4.1", "4.2", "4.3", "4.4"],
     ["comp_econ_census_007", "comp_dem_analysis_008", "comp_pes_121"], "standard"),

    ("comp_business_register_079", "Statistical Business Register Management", "Domain", "procedural",
     "Business Register",
     "Building and maintaining a statistical business register: unit models, administrative source "
     "integration, deduplication, profiling of large enterprises and frame quality.",
     ["statistical unit models", "integrating tax and company administrative sources",
      "deduplication and matching", "profiling of large enterprise groups", "register coverage and churn",
      "frame quality indicators"],
     ["4.1", "5.1", "OA.DM", "OA.QM"],
     ["comp_frame_maintenance_119", "comp_msme_stats_061", "comp_admin_data_125"], "standard"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Family 2 - macroeconomic accounts and price statistics specialisations
# ─────────────────────────────────────────────────────────────────────────────
MACRO_ACCOUNTS = [
    ("comp_gfs_080", "Government Finance Statistics & COFOG", "Domain", "accuracy",
     "Government Finance Statistics",
     "Government finance statistics: revenue and expense classification, the COFOG functional "
     "classification, general government coverage and fiscal balances.",
     ["government finance statistics framework", "revenue and expense classification",
      "COFOG functional classification", "general government sector coverage", "fiscal balance and debt statistics",
      "bridging budget documents to GFS"],
     ["5.1", "5.2", "5.7", "6.1"],
     ["comp_public_fin_025", "comp_nat_accounts_001", "comp_flow_funds_082"], "standard"),

    ("comp_bop_081", "Balance of Payments & External Sector Statistics", "Domain", "accuracy",
     "Balance of Payments",
     "Balance of payments and external sector statistics: current and financial accounts, the international "
     "investment position, and reconciliation with trade statistics.",
     ["balance of payments framework", "current account compilation", "financial account and investment position",
      "reconciliation with merchandise trade", "external debt statistics", "errors and omissions analysis"],
     ["5.1", "5.7", "6.2"],
     ["comp_trade_stats_059", "comp_nat_accounts_001"], "thin"),

    ("comp_flow_funds_082", "Flow of Funds & Financial Accounts", "Domain", "accuracy",
     "Flow of Funds",
     "Flow of funds and financial accounts: institutional sector financial balance sheets, from-whom-to-whom "
     "matrices, household saving in financial assets and sector net lending.",
     ["institutional sector financial accounts", "from-whom-to-whom matrices",
      "household financial saving estimation", "net lending and borrowing by sector",
      "financial balance sheet compilation", "reconciling flows and stocks"],
     ["5.1", "5.5", "5.7"],
     ["comp_nat_accounts_001", "comp_banking_stats_064", "comp_gfs_080"], "thin"),

    ("comp_io_tables_083", "Input-Output & Supply-Use Table Compilation", "Domain", "accuracy",
     "Supply-Use and Input-Output Tables",
     "Compiling supply-use and input-output tables: product and industry balancing, valuation layers, "
     "technology assumptions and deriving symmetric input-output tables.",
     ["supply and use balancing", "valuation layers and trade-transport margins",
      "industry and product technology assumptions", "symmetric input-output derivation",
      "import matrix construction", "multiplier analysis from input-output tables"],
     ["5.1", "5.5", "5.7", "6.2"],
     ["comp_nat_accounts_001", "comp_deflators_088", "comp_industry_stats_010"], "standard"),

    ("comp_capital_stock_084", "Capital Stock, PIM & Fixed Capital Consumption", "Domain", "accuracy",
     "Capital Stock Estimation",
     "Estimating capital stock and consumption of fixed capital: the perpetual inventory method, asset "
     "service lives, depreciation patterns and net versus gross stock.",
     ["perpetual inventory method", "asset service lives and retirement patterns",
      "depreciation and consumption of fixed capital", "net and gross capital stock",
      "capital formation by asset type", "capital services and productivity measures"],
     ["5.5", "5.7", "6.1"],
     ["comp_nat_accounts_001", "comp_deflators_088"], "thin"),

    ("comp_regional_accounts_085", "State & District Domestic Product Estimation", "Domain", "accuracy",
     "Regional Accounts",
     "Regional accounts: state and district domestic product, allocation of supra-regional activity, and "
     "coordination with state directorates of economics and statistics.",
     ["state domestic product methodology", "allocation of supra-regional activity",
      "district domestic product estimation", "regional deflators and price adjustments",
      "coordination with state statistical directorates", "regional accounts consistency checks"],
     ["5.5", "5.7", "6.2", "OA.SM"],
     ["comp_nat_accounts_001", "comp_stat_coordination_135"], "standard"),

    ("comp_qna_086", "Quarterly National Accounts Compilation", "Domain", "accuracy",
     "Quarterly National Accounts",
     "Quarterly national accounts: indicator-based extrapolation, benchmarking quarterly to annual, "
     "seasonal adjustment of quarterly series and revision practice.",
     ["indicator based quarterly extrapolation", "benchmarking quarterly series to annual",
      "seasonal adjustment of quarterly accounts", "quarterly GVA by economic activity",
      "quarterly revision practice", "advance and provisional estimates"],
     ["5.5", "5.7", "6.1", "6.5"],
     ["comp_nat_accounts_001", "comp_benchmarking_113", "comp_time_series_013"], "standard"),

    ("comp_satellite_acct_087", "Satellite Accounts (Tourism, Environment, Unpaid Work)", "Domain", "accuracy",
     "Satellite Accounts",
     "Building satellite accounts alongside the core accounts: scope and boundary decisions, linking to the "
     "supply-use framework, and tourism, environmental and unpaid-work satellite accounts.",
     ["satellite account scope and boundaries", "linking satellites to supply-use tables",
      "tourism satellite account", "environmental economic accounts", "unpaid household work account",
      "health and education satellite accounts"],
     ["5.1", "5.7", "6.1", "OA.SM"],
     ["comp_nat_accounts_001", "comp_tourism_stats_058", "comp_timeuse_stats_074"], "thin"),

    ("comp_deflators_088", "Deflators & Constant-Price Estimation", "Domain", "accuracy",
     "Deflators and Constant Prices",
     "Deflation and volume measurement: choosing deflators, single and double deflation, chain-linking at "
     "constant prices and handling quality change in volume measures.",
     ["choosing appropriate deflators", "single and double deflation",
      "chain linking volume measures", "quality change in volume measurement",
      "implicit price deflators", "constant price series at the industry level"],
     ["5.5", "5.7", "6.2"],
     ["comp_index_numbers_004", "comp_nat_accounts_001", "comp_price_stats_003"], "standard"),

    ("comp_ppp_089", "Purchasing Power Parity & International Comparisons", "Domain", "accuracy",
     "Purchasing Power Parity",
     "Purchasing power parities and the International Comparison Programme: basic heading parities, price "
     "collection for global comparison, and real expenditure comparisons across countries.",
     ["international comparison programme price collection", "basic heading parity estimation",
      "aggregation methods for parities", "real expenditure comparisons",
      "productivity comparisons using parities", "spatial price indices within the country"],
     ["4.3", "5.7", "6.2"],
     ["comp_price_stats_003", "comp_index_numbers_004"], "thin"),

    ("comp_producer_price_090", "Producer & Wholesale Price Index Compilation", "Domain", "accuracy",
     "Producer Price Statistics",
     "Compiling producer and wholesale price indices: transaction price concepts, sampling establishments "
     "and products, weight derivation from supply-use tables and index maintenance.",
     ["transaction price concepts", "establishment and product sampling for producer prices",
      "weights from supply-use tables", "quality adjustment for producer prices",
      "wholesale price index maintenance", "producer price indices as deflators"],
     ["2.4", "4.3", "5.7", "6.2"],
     ["comp_price_stats_003", "comp_index_numbers_004", "comp_deflators_088"], "standard"),

    ("comp_housing_price_091", "Housing & Asset Price Indices", "Domain", "accuracy",
     "Housing Price Indices",
     "Residential property and asset price indices: hedonic and repeat-sales methods, registration data as "
     "a source, owner-occupied housing treatment and rental equivalence.",
     ["hedonic regression for house prices", "repeat sales indices", "property registration data as a source",
      "owner occupied housing in the CPI", "rental equivalence approach", "commercial property price indicators"],
     ["5.1", "5.5", "5.7"],
     ["comp_price_stats_003", "comp_housing_stats_051"], "thin"),

    ("comp_service_price_092", "Services Price Index Development", "Domain", "accuracy",
     "Services Price Indices",
     "Developing services producer price indices: pricing methods for services, model pricing and contract "
     "pricing, and coverage of transport, telecom and business services.",
     ["pricing methods for services", "model and contract pricing", "unit value proxies for services",
      "services producer price index coverage", "quality change in services", "experimental services indices"],
     ["2.2", "4.3", "5.7"],
     ["comp_producer_price_090", "comp_services_stats_060"], "thin"),

    ("comp_cost_living_093", "Consumer Expenditure & Cost of Living Analysis", "Domain", "accuracy",
     "Consumer Expenditure Analysis",
     "Analysing household consumption expenditure: recall methods, expenditure classification, equivalence "
     "scales and cost-of-living comparisons across regions.",
     ["modified mixed and uniform recall methods", "consumption expenditure classification",
      "equivalence scales and adult equivalents", "regional cost of living comparisons",
      "Engel curves and budget shares", "comparability across survey rounds"],
     ["2.3", "5.5", "5.7", "6.1"],
     ["comp_poverty_014", "comp_price_stats_003", "comp_survey_design_002"], "standard"),

    ("comp_agri_census_094", "Agricultural Census & Input Survey", "Domain", "procedural",
     "Agricultural Census",
     "The agricultural census and input survey: operational holdings, land records as a frame, holding-size "
     "classification and input use estimation.",
     ["operational holding concepts", "land records as a census frame", "holding size classification",
      "input use estimation", "phased agricultural census operations", "tabulation of holding characteristics"],
     ["4.1", "4.3", "5.7", "6.1"],
     ["comp_agri_stats_009", "comp_irrigation_stats_097", "comp_econ_census_007"], "thin"),

    ("comp_livestock_stats_095", "Livestock, Fisheries & Allied Sector Statistics", "Domain", "accuracy",
     "Livestock and Fisheries Statistics",
     "Livestock, dairy and fisheries statistics: the livestock census, production estimation for milk, eggs "
     "and meat, fish landing data and allied-sector value added.",
     ["livestock census operations", "milk and egg production estimation", "meat production statistics",
      "marine and inland fish landing data", "allied sector gross value added", "integrated sample survey design"],
     ["4.3", "5.5", "5.7", "6.1"],
     ["comp_agri_stats_009", "comp_nat_accounts_001"], "thin"),

    ("comp_horticulture_096", "Horticulture & Crop Diversification Statistics", "Domain", "accuracy",
     "Horticulture Statistics",
     "Horticulture statistics: area and production estimation for fruits and vegetables, post-harvest loss "
     "assessment and crop diversification indicators.",
     ["horticulture area and production estimation", "post harvest loss assessment",
      "crop diversification indicators", "market arrival data as an indicator", "protected cultivation statistics",
      "remote sensing for horticulture"],
     ["4.3", "5.5", "5.7"],
     ["comp_agri_stats_009", "comp_spatial_stat_012"], "thin"),

    ("comp_irrigation_stats_097", "Irrigation, Land Use & Water Resource Statistics", "Domain", "accuracy",
     "Land Use and Irrigation Statistics",
     "Land use and irrigation statistics: the nine-fold land use classification, irrigated area by source, "
     "groundwater assessment and land records digitisation.",
     ["nine fold land use classification", "irrigated area by source",
      "groundwater resource assessment", "land records digitisation quality", "cropping intensity measures",
      "watershed level water accounting"],
     ["4.3", "5.1", "5.7"],
     ["comp_agri_stats_009", "comp_spatial_stat_012", "comp_environment_stats_054"], "thin"),

    ("comp_rural_dev_098", "Rural Development Programme Statistics", "Domain", "procedural",
     "Rural Development Statistics",
     "Statistics for rural development programmes: scheme MIS data, beneficiary coverage, asset creation "
     "indicators and village-level infrastructure data.",
     ["programme MIS as a statistical source", "beneficiary coverage and leakage indicators",
      "asset creation and durability indicators", "village infrastructure statistics",
      "person-days of employment generated", "convergence across rural schemes"],
     ["5.1", "5.3", "6.1"],
     ["comp_scheme_eval_187", "comp_admin_data_125", "comp_poverty_014"], "thin"),

    ("comp_mplads_099", "MPLADS Monitoring & Fund Utilisation Statistics", "Domain", "procedural",
     "MPLADS Monitoring",
     "Monitoring the Member of Parliament Local Area Development Scheme: sanction and utilisation reporting, "
     "work completion tracking, and state-wise fund release analysis.",
     ["MPLADS guidelines and reporting flow", "sanction and utilisation certificates",
      "work completion tracking", "state wise fund release analysis", "audit of MPLADS works",
      "geo-tagging of completed works"],
     ["5.1", "5.3", "6.1", "OA.FM"],
     ["comp_project_monitor_100", "comp_public_fin_025", "comp_audit_response_176"], "thin"),

    ("comp_project_monitor_100", "Infrastructure Project Monitoring", "Domain", "procedural",
     "Infrastructure Project Monitoring",
     "Monitoring central sector infrastructure projects: cost and time overrun analysis, the online project "
     "monitoring system, flash reports and reasons-for-delay classification.",
     ["cost and time overrun analysis", "online project monitoring system data",
      "flash report preparation", "reasons for delay classification", "project cost revision tracking",
      "sector wise project performance review"],
     ["5.1", "5.3", "6.1", "OA.PM"],
     ["comp_project_mgmt_024", "comp_mplads_099", "comp_construction_stats_062"], "standard"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Family 3 - statistical methodology and survey operations
# ─────────────────────────────────────────────────────────────────────────────
METHODOLOGY = [
    ("comp_small_area_101", "Small Area Estimation", "Domain", "accuracy",
     "Small Area Estimation",
     "Producing reliable estimates for domains the sample was not designed for: direct versus model-based "
     "estimators, Fay-Herriot area models, unit-level models and validating small-area estimates.",
     ["direct and synthetic estimators", "Fay-Herriot area level models", "unit level nested error models",
      "auxiliary data for small areas", "mean squared error estimation for small areas",
      "validating and benchmarking small area estimates"],
     ["2.5", "5.5", "6.1", "6.2"],
     ["comp_survey_design_002", "comp_bayesian_107", "comp_spatial_stat_012"], "standard"),

    ("comp_calibration_102", "Calibration, Weighting & Non-response Adjustment", "Domain", "accuracy",
     "Survey Weighting and Calibration",
     "Turning a sample into a population estimate: base weights, non-response adjustment classes, "
     "calibration to known totals, trimming extreme weights and their variance cost.",
     ["base weights and design weights", "non-response adjustment classes", "calibration to known totals",
      "raking and post-stratification", "trimming extreme weights", "variance cost of weighting"],
     ["5.6", "6.1", "6.2"],
     ["comp_survey_design_002", "comp_var_estimation_106", "comp_nonsampling_120"], "standard"),

    ("comp_imputation_103", "Editing & Imputation Methodology", "Domain", "accuracy",
     "Editing and Imputation",
     "Editing and imputing survey and administrative data: edit rules and the Fellegi-Holt principle, "
     "donor and model-based imputation, and measuring the effect of imputation on estimates.",
     ["edit rules and the Fellegi-Holt principle", "hot deck and donor imputation",
      "model based and multiple imputation", "imputation flags and audit trails",
      "measuring the effect of imputation", "selective editing and score functions"],
     ["5.3", "5.4", "6.2"],
     ["comp_outlier_114", "comp_ml_stats_005", "comp_data_gov_016"], "standard"),

    ("comp_record_linkage_104", "Record Linkage & Entity Resolution", "Domain", "accuracy",
     "Record Linkage",
     "Linking records across sources without a common key: blocking, deterministic and probabilistic "
     "linkage, the Fellegi-Sunter model, clerical review and linkage-error effects.",
     ["blocking and candidate generation", "deterministic linkage rules",
      "the Fellegi-Sunter probabilistic model", "clerical review workflows",
      "linkage error and its effect on estimates", "privacy preserving record linkage"],
     ["5.1", "OA.DM", "OA.QM"],
     ["comp_big_data_006", "comp_admin_data_125", "comp_db_design_029"], "standard"),

    ("comp_disclosure_105", "Statistical Disclosure Control", "Domain", "accuracy",
     "Statistical Disclosure Control",
     "Protecting confidentiality in published statistics: re-identification risk, cell suppression, "
     "perturbation and rounding, microdata anonymisation and the risk-utility trade-off.",
     ["re-identification risk assessment", "cell suppression in tables", "perturbation and controlled rounding",
      "microdata anonymisation techniques", "risk-utility trade-off", "disclosure rules for small cells"],
     ["6.4", "5.8", "OA.QM"],
     ["comp_data_privacy_026", "comp_dp_161", "comp_microdata_release_131"], "standard"),

    ("comp_var_estimation_106", "Variance Estimation & Resampling Methods", "Domain", "accuracy",
     "Variance Estimation",
     "Estimating sampling error for complex designs: Taylor linearisation, jackknife and bootstrap "
     "replication, design effects and reporting reliability thresholds.",
     ["Taylor series linearisation", "jackknife replication", "bootstrap for complex designs",
      "design effects and effective sample size", "variance of ratios and differences",
      "reliability thresholds for publication"],
     ["5.6", "6.1", "6.2"],
     ["comp_survey_design_002", "comp_calibration_102", "comp_r_analytics_018"], "standard"),

    ("comp_bayesian_107", "Bayesian Methods for Official Statistics", "Domain", "accuracy",
     "Bayesian Methods",
     "Bayesian inference in statistical production: priors and posteriors, hierarchical models, MCMC "
     "computation, and communicating credible intervals.",
     ["priors, likelihood and posteriors", "hierarchical and multilevel models",
      "MCMC and posterior computation", "credible intervals and their interpretation",
      "Bayesian small area models", "prior sensitivity analysis"],
     ["2.5", "5.5", "6.1"],
     ["comp_small_area_101", "comp_r_analytics_018", "comp_econometrics_111"], "thin"),

    ("comp_causal_inf_108", "Causal Inference & Programme Evaluation", "Domain", "accuracy",
     "Causal Inference",
     "Estimating programme effects from observational data: potential outcomes, matching and propensity "
     "scores, difference-in-differences, instrumental variables and regression discontinuity.",
     ["potential outcomes framework", "matching and propensity score methods",
      "difference-in-differences designs", "instrumental variables", "regression discontinuity designs",
      "sensitivity to unobserved confounding"],
     ["6.1", "6.3", "8.2"],
     ["comp_econometrics_111", "comp_exp_design_109", "comp_scheme_eval_187"], "standard"),

    ("comp_exp_design_109", "Experimental Design & Randomised Evaluations", "Domain", "accuracy",
     "Experimental Design",
     "Designing experiments and randomised evaluations: randomisation units, power calculations, "
     "stratified and cluster randomisation, pre-analysis plans and embedded survey experiments.",
     ["randomisation units and allocation", "power calculations and minimum detectable effects",
      "cluster and stratified randomisation", "pre-analysis plans", "embedded survey experiments",
      "attrition and compliance in trials"],
     ["2.3", "3.6", "8.2"],
     ["comp_causal_inf_108", "comp_survey_design_002"], "thin"),

    ("comp_multivariate_110", "Multivariate Analysis & Dimension Reduction", "Domain", "accuracy",
     "Multivariate Analysis",
     "Multivariate techniques for statistical analysis: principal components, factor analysis, cluster "
     "analysis, discriminant methods and composite index construction.",
     ["principal component analysis", "factor analysis and latent constructs", "cluster analysis and typologies",
      "discriminant and classification methods", "composite index construction", "scaling and normalisation choices"],
     ["5.5", "6.1", "6.3"],
     ["comp_ml_stats_005", "comp_r_analytics_018", "comp_econometrics_111"], "standard"),

    ("comp_econometrics_111", "Applied Econometrics for Policy Analysis", "Domain", "accuracy",
     "Applied Econometrics",
     "Econometrics applied to official data: linear and limited dependent variable models, panel "
     "estimators, endogeneity, robust standard errors and interpreting results for policy.",
     ["linear regression diagnostics", "limited dependent variable models", "panel data estimators",
      "endogeneity and identification", "robust and clustered standard errors",
      "interpreting coefficients for policy"],
     ["6.1", "6.3"],
     ["comp_causal_inf_108", "comp_stata_164", "comp_r_analytics_018"], "standard"),

    ("comp_forecasting_112", "Forecasting & Scenario Modelling", "Domain", "accuracy",
     "Forecasting and Scenario Modelling",
     "Forecasting official indicators and building scenarios: benchmark models, forecast combination, "
     "evaluation metrics, judgemental adjustment and scenario design.",
     ["benchmark forecasting models", "forecast combination and averaging",
      "forecast evaluation metrics", "judgemental adjustment of forecasts", "scenario design and stress cases",
      "communicating forecast uncertainty"],
     ["6.1", "6.3", "1.5"],
     ["comp_time_series_013", "comp_gdp_nowcast_011", "comp_decision_037"], "standard"),

    ("comp_benchmarking_113", "Benchmarking, Temporal Disaggregation & Reconciliation", "Domain", "accuracy",
     "Benchmarking and Reconciliation",
     "Reconciling series of different frequencies and sources: Denton and Chow-Lin methods, temporal "
     "disaggregation, balancing across dimensions and revision-consistent benchmarking.",
     ["Denton benchmarking method", "Chow-Lin temporal disaggregation", "balancing across dimensions",
      "reconciling annual and sub-annual series", "revision consistent benchmarking",
      "constrained optimisation for reconciliation"],
     ["5.5", "5.7", "6.2"],
     ["comp_qna_086", "comp_time_series_013", "comp_nat_accounts_001"], "thin"),

    ("comp_outlier_114", "Outlier Detection & Validation Rules", "Domain", "accuracy",
     "Outlier Detection and Validation",
     "Finding and treating suspicious values: univariate and multivariate outlier rules, influence on "
     "estimates, validation rule design and managing false positives in editing.",
     ["univariate outlier rules", "multivariate and robust outlier detection",
      "influence of outliers on estimates", "validation rule design", "false positives in editing",
      "winsorising and robust estimation"],
     ["5.3", "5.4", "6.2", "OA.QM"],
     ["comp_imputation_103", "comp_data_gov_016", "comp_data_scrutiny_129"], "standard"),

    ("comp_questionnaire_115", "Questionnaire Design & Cognitive Testing", "Domain", "accuracy",
     "Questionnaire Design",
     "Designing survey instruments that measure what they claim: question wording, response formats, "
     "recall and reference periods, cognitive interviewing and pre-testing.",
     ["question wording and comprehension", "response formats and scales",
      "recall and reference period design", "cognitive interviewing", "pre-testing and pilot analysis",
      "translation and local adaptation of schedules"],
     ["2.2", "2.3", "3.1", "3.6"],
     ["comp_survey_design_002", "comp_interview_skills_128", "comp_nonsampling_120"], "standard"),

    ("comp_capi_116", "CAPI/CATI Instrument Development", "Domain", "accuracy",
     "CAPI Instrument Development",
     "Building computer-assisted interview instruments: questionnaire logic and skip patterns, in-field "
     "validation rules, offline sync, device management and paradata capture.",
     ["questionnaire logic and skip patterns", "in-field validation rules", "offline data capture and sync",
      "device and case management", "paradata capture and use", "instrument testing before the round"],
     ["3.1", "3.5", "4.2", "4.3"],
     ["comp_questionnaire_115", "comp_mobile_dev_149", "comp_survey_ops_126"], "standard"),

    ("comp_mixed_mode_117", "Mixed-Mode & Adaptive Survey Design", "Domain", "accuracy",
     "Mixed-Mode Survey Design",
     "Designing surveys across modes: mode effects and measurement differences, responsive and adaptive "
     "designs, contact strategies and cost-quality trade-offs.",
     ["mode effects on measurement", "responsive and adaptive designs", "contact and follow-up strategies",
      "cost-quality trade-offs across modes", "web push and self-completion", "mode calibration adjustments"],
     ["2.3", "4.2", "4.3", "8.2"],
     ["comp_survey_design_002", "comp_nonsampling_120", "comp_capi_116"], "thin"),

    ("comp_panel_survey_118", "Longitudinal & Panel Survey Methods", "Domain", "accuracy",
     "Panel Survey Methods",
     "Running longitudinal and rotational panel surveys: panel rotation schemes, attrition and tracking, "
     "longitudinal weights and estimating change over time.",
     ["panel rotation schemes", "attrition and respondent tracking", "longitudinal weighting",
      "estimating gross and net change", "panel conditioning effects", "linking waves and identifiers"],
     ["2.4", "4.1", "5.6", "6.1"],
     ["comp_survey_design_002", "comp_labour_stats_041", "comp_calibration_102"], "thin"),

    ("comp_frame_maintenance_119", "Sampling Frame Construction & Maintenance", "Domain", "procedural",
     "Sampling Frames",
     "Building and maintaining sampling frames: frame sources and coverage errors, updating between "
     "censuses, duplicate and out-of-scope units, and frame documentation.",
     ["frame sources and their coverage", "under- and over-coverage errors", "updating frames between censuses",
      "duplicates and out-of-scope units", "frame documentation and versioning", "urban frame survey blocks"],
     ["4.1", "OA.DM", "OA.QM"],
     ["comp_business_register_079", "comp_survey_design_002", "comp_spatial_stat_012"], "standard"),

    ("comp_nonsampling_120", "Non-sampling Error Assessment", "Domain", "accuracy",
     "Non-sampling Error",
     "Assessing errors that sample size cannot fix: coverage, non-response, measurement and processing "
     "error, the total survey error framework and quality indicators for each component.",
     ["total survey error framework", "coverage error assessment", "non-response bias analysis",
      "measurement and interviewer error", "processing error indicators", "reporting quality to users"],
     ["8.1", "8.2", "OA.QM"],
     ["comp_data_gov_016", "comp_calibration_102", "comp_pes_121"], "standard"),

    ("comp_pes_121", "Post-Enumeration & Coverage Evaluation Surveys", "Domain", "accuracy",
     "Coverage Evaluation Surveys",
     "Evaluating coverage after a census or large survey: independent re-enumeration, dual-system "
     "estimation, matching rules and adjusting published counts.",
     ["independent re-enumeration design", "dual system estimation", "matching rules and clerical resolution",
      "erroneous inclusion and omission rates", "adjusting published counts", "reporting coverage results"],
     ["4.4", "8.1", "8.2"],
     ["comp_census_pop_078", "comp_econ_census_007", "comp_nonsampling_120"], "thin"),

    ("comp_classification_122", "Statistical Classifications (NIC, NCO, COICOP)", "Domain", "procedural",
     "Statistical Classifications",
     "Using and maintaining statistical classifications: industrial, occupational and consumption "
     "classifications, coding rules, correspondence tables and classification revisions.",
     ["industrial classification structure", "occupational classification structure",
      "consumption classification for expenditure", "coding rules and index files",
      "correspondence tables between versions", "managing a classification revision"],
     ["5.2", "OA.MM", "OA.SM"],
     ["comp_metadata_sdmx_123", "comp_ml_stats_005", "comp_trade_stats_059"], "standard"),

    ("comp_metadata_sdmx_123", "SDMX & Statistical Metadata Modelling", "Functional", "accuracy",
     "SDMX and Statistical Metadata",
     "Modelling and exchanging statistical metadata: data structure definitions, code lists and concept "
     "schemes, reference metadata, and SDMX-based exchange with international bodies.",
     ["data structure definitions", "code lists and concept schemes", "reference metadata standards",
      "SDMX exchange with international bodies", "metadata driven dissemination",
      "versioning of structural metadata"],
     ["OA.MM", "7.1", "7.2", "3.3"],
     ["comp_data_gov_016", "comp_api_int_028", "comp_classification_122"], "standard"),

    ("comp_data_ethics_124", "Data Ethics & Responsible Use of New Data", "Functional", "procedural",
     "Data Ethics",
     "Ethical use of data in official statistics: consent and proportionality for new data sources, "
     "fairness in algorithmic processing, ethical review and transparency with respondents.",
     ["consent and proportionality", "ethical review of new data sources", "fairness in algorithmic processing",
      "transparency with respondents", "ethics of data sharing agreements", "public trust and social licence"],
     ["OA.QM", "OA.DM", "1.2"],
     ["comp_integrity_034", "comp_ai_governance_156", "comp_data_privacy_026"], "standard"),

    ("comp_admin_data_125", "Administrative Data Acquisition & Quality", "Domain", "accuracy",
     "Administrative Data",
     "Bringing administrative data into statistical production: data-sharing agreements, metadata and "
     "concept alignment, quality frameworks for secondary data and change management at the source.",
     ["data sharing agreements with source agencies", "concept alignment between admin and statistical units",
      "quality frameworks for secondary data", "stability and change at the source system",
      "coverage and timeliness assessment", "documenting administrative data provenance"],
     ["1.5", "5.1", "OA.DM", "OA.QM"],
     ["comp_big_data_006", "comp_record_linkage_104", "comp_data_gov_016"], "standard"),

    ("comp_survey_ops_126", "Survey Field Operations Management", "Domain", "procedural",
     "Survey Field Operations",
     "Running a survey round in the field: workload allocation, field staff deployment, progress "
     "monitoring, logistics and cost control across sub-rounds.",
     ["workload allocation and sub-rounds", "field staff deployment", "progress monitoring dashboards",
      "field logistics and travel planning", "cost control during a round", "handling field level exceptions"],
     ["4.2", "4.3", "4.4", "OA.PM"],
     ["comp_field_supervision_127", "comp_project_mgmt_024", "comp_capi_116"], "standard"),

    ("comp_field_supervision_127", "Field Supervision & Data Quality Monitoring", "Domain", "procedural",
     "Field Supervision",
     "Supervising field work and monitoring data quality in real time: supervisory checks and re-visits, "
     "paradata-based quality indicators, interviewer feedback and fabrication detection.",
     ["supervisory checks and re-interviews", "paradata based quality indicators",
      "interview duration and pattern checks", "feedback to interviewers", "detecting fabricated interviews",
      "sample substitution rules"],
     ["4.3", "4.4", "5.3", "OA.QM"],
     ["comp_survey_ops_126", "comp_interview_skills_128", "comp_nonsampling_120"], "standard"),

    ("comp_interview_skills_128", "Interviewing Technique & Respondent Engagement", "Domain", "procedural",
     "Survey Interviewing",
     "Conducting survey interviews well: standardised interviewing, probing without leading, gaining "
     "cooperation, handling refusals and interviewing in sensitive situations.",
     ["standardised interviewing technique", "probing without leading", "gaining respondent cooperation",
      "handling refusals and call-backs", "interviewing on sensitive topics", "recording answers accurately"],
     ["4.3", "4.4"],
     ["comp_questionnaire_115", "comp_field_supervision_127", "comp_comm_032"], "standard"),

    ("comp_data_scrutiny_129", "Schedule Scrutiny & Manual Editing", "Domain", "procedural",
     "Schedule Scrutiny",
     "Scrutinising filled survey schedules: consistency checks between blocks, arithmetic and unit checks, "
     "referral back to the field and documenting corrections.",
     ["consistency checks between schedule blocks", "arithmetic and unit of measure checks",
      "referral back to the field", "documenting manual corrections", "scrutiny checklists by schedule type",
      "common enumeration errors"],
     ["5.3", "5.4", "OA.QM"],
     ["comp_outlier_114", "comp_field_supervision_127", "comp_imputation_103"], "standard"),

    ("comp_tabulation_130", "Tabulation Plan Design & Table Production", "Domain", "procedural",
     "Tabulation and Table Production",
     "Turning microdata into published tables: tabulation plan design, domain definitions, table checking "
     "and consistency, and production of the standard report table set.",
     ["tabulation plan design", "domain and sub-domain definitions", "table consistency checks",
      "presentation standards for tables", "automating the standard table set", "footnotes and quality markers"],
     ["6.1", "6.5", "7.2"],
     ["comp_statistical_sw_030", "comp_report_writing_020", "comp_disclosure_105"], "standard"),

    ("comp_microdata_release_131", "Microdata Dissemination & Data Access", "Functional", "procedural",
     "Microdata Dissemination",
     "Releasing unit-level data responsibly: public use files, licensing and access tiers, secure data "
     "enclaves, documentation for users and tracking downstream use.",
     ["public use file preparation", "licensing and access tiers", "secure data enclaves and remote access",
      "user documentation and data dictionaries", "tracking downstream use", "terms of use enforcement"],
     ["6.4", "7.2", "7.5", "OA.DM"],
     ["comp_disclosure_105", "comp_open_data_151", "comp_data_privacy_026"], "standard"),

    ("comp_revision_policy_132", "Revision Policy & Release Calendars", "Functional", "procedural",
     "Revision Policy and Release Calendars",
     "Managing releases and revisions: advance release calendars, revision policy and revision analysis, "
     "embargo handling and communicating revisions to users.",
     ["advance release calendar management", "revision policy design", "revision analysis and bias tests",
      "embargo procedures", "communicating revisions to users", "documenting methodological changes"],
     ["6.5", "7.3", "8.1"],
     ["comp_integrity_034", "comp_comm_032", "comp_time_series_013"], "standard"),

    ("comp_intl_standards_133", "International Statistical Standards & Reporting", "Functional", "procedural",
     "International Statistical Standards",
     "Working with international statistical standards and reporting obligations: UN Fundamental "
     "Principles, global manuals, data reporting to international agencies and peer review processes.",
     ["UN Fundamental Principles in practice", "global statistical manuals and their adoption",
      "reporting to international agencies", "peer review and assessment missions",
      "comparability across countries", "national adaptation of global standards"],
     ["OA.SM", "7.2", "8.2"],
     ["comp_integrity_034", "comp_intl_coop_180", "comp_metadata_sdmx_123"], "standard"),

    ("comp_statistical_law_134", "Statistical Legislation & Collection of Statistics Act", "Functional", "procedural",
     "Statistical Legislation",
     "The legal basis of official statistics: the Collection of Statistics Act and rules, powers to collect, "
     "confidentiality obligations, penalties and notification of statistical surveys.",
     ["Collection of Statistics Act provisions", "powers to collect and notify surveys",
      "confidentiality obligations in law", "penalties and enforcement", "legal basis for administrative access",
      "interaction with data protection law"],
     ["OA.SM", "OA.QM", "1.6"],
     ["comp_data_privacy_026", "comp_integrity_034", "comp_court_cases_177"], "standard"),

    ("comp_stat_coordination_135", "Coordination with State Statistical Systems", "Functional", "procedural",
     "State Statistical Coordination",
     "Coordinating the national statistical system: working with state directorates, common minimum "
     "standards, capacity support to states and harmonising state and central estimates.",
     ["working with state statistical directorates", "common minimum standards for states",
      "capacity support and hand-holding", "harmonising state and central estimates",
      "state statistical strengthening schemes", "conference of central and state statistical organisations"],
     ["OA.SM", "OA.PM", "1.2"],
     ["comp_regional_accounts_085", "comp_collab_036", "comp_intl_standards_133"], "standard"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Family 4 - data engineering, platforms and applied AI
# ─────────────────────────────────────────────────────────────────────────────
TECHNOLOGY = [
    ("comp_data_eng_136", "Data Engineering & ETL Pipelines", "Functional", "accuracy",
     "Data Engineering",
     "Building the pipelines statistical production runs on: ingestion, transformation and load patterns, "
     "orchestration and scheduling, idempotent reruns and pipeline observability.",
     ["ingestion and staging patterns", "transformation and load design", "pipeline orchestration and scheduling",
      "idempotent and restartable jobs", "data lineage and pipeline observability", "handling late arriving data"],
     ["3.2", "3.4", "5.1", "5.8"],
     ["comp_db_design_029", "comp_python_stats_017", "comp_dwh_139"], "standard"),

    ("comp_spark_137", "Distributed Processing with Spark", "Functional", "accuracy",
     "Distributed Data Processing",
     "Processing data too large for one machine: the Spark execution model, partitioning and shuffles, "
     "joins at scale, tuning memory and cost, and when distribution is not worth it.",
     ["Spark execution model", "partitioning and shuffle behaviour", "joins and aggregations at scale",
      "memory and executor tuning", "cost of distribution versus single node", "structured streaming basics"],
     ["3.2", "5.1", "5.7"],
     ["comp_big_data_006", "comp_data_eng_136", "comp_cloud_infra_027"], "thin"),

    ("comp_data_lake_138", "Data Lake & Lakehouse Architecture", "Functional", "accuracy",
     "Data Lake Architecture",
     "Designing a data lake for statistical data: zones and file layout, open table formats, schema "
     "evolution, cataloguing and governed access to raw and curated layers.",
     ["lake zones and file layout", "open table formats", "schema evolution and compatibility",
      "cataloguing lake datasets", "governed access to raw and curated layers", "partitioning and file sizing"],
     ["3.2", "5.1", "5.8", "OA.DM"],
     ["comp_data_eng_136", "comp_cloud_infra_027", "comp_dwh_139"], "thin"),

    ("comp_dwh_139", "Data Warehousing & Dimensional Modelling", "Functional", "accuracy",
     "Data Warehousing",
     "Modelling a statistical data warehouse: facts and dimensions, slowly changing dimensions, conformed "
     "dimensions across surveys, and query performance for analytical workloads.",
     ["facts and dimensions", "slowly changing dimensions", "conformed dimensions across surveys",
      "aggregate tables and materialised views", "query performance for analytics",
      "loading strategies and refresh windows"],
     ["3.2", "5.8", "7.1", "OA.DM"],
     ["comp_db_design_029", "comp_data_eng_136", "comp_bi_tools_162"], "standard"),

    ("comp_nosql_140", "NoSQL & Document Data Stores", "Functional", "accuracy",
     "NoSQL Data Stores",
     "Using non-relational stores where they fit: document and key-value models, denormalisation, "
     "consistency trade-offs, indexing and when a relational database is still the right answer.",
     ["document and key-value data models", "denormalisation trade-offs", "consistency and availability choices",
      "indexing in document stores", "aggregation pipelines", "choosing between NoSQL and relational"],
     ["3.2", "5.8", "OA.DM"],
     ["comp_db_design_029", "comp_data_eng_136"], "thin"),

    ("comp_version_ctrl_141", "Version Control & Collaborative Development", "Functional", "procedural",
     "Version Control with Git",
     "Working with version control in a team: branching and merging, reviewing changes, resolving "
     "conflicts, tagging releases and keeping analysis code reproducible over years.",
     ["branching and merging strategies", "code review workflows", "resolving merge conflicts",
      "tagging and releasing versions", "keeping analysis code reproducible", "repository structure for statistics"],
     ["3.2", "3.7", "OA.DM"],
     ["comp_reproducible_166", "comp_python_stats_017", "comp_devops_142"], "standard"),

    ("comp_devops_142", "DevOps & CI/CD for Statistical Systems", "Functional", "accuracy",
     "DevOps and CI/CD",
     "Automating build, test and deployment for statistical systems: pipelines, environment promotion, "
     "configuration management, rollback and release safety in a government setting.",
     ["continuous integration pipelines", "automated deployment and promotion",
      "configuration and secrets management", "rollback and release safety", "environment parity",
      "change control in government IT"],
     ["3.4", "3.5", "3.7"],
     ["comp_containers_143", "comp_version_ctrl_141", "comp_testing_qa_167"], "standard"),

    ("comp_containers_143", "Containerisation & Orchestration", "Functional", "accuracy",
     "Containers and Orchestration",
     "Packaging and running services in containers: images and layers, container registries, orchestration "
     "concepts, resource limits and reproducible runtime environments.",
     ["container images and layers", "registries and image provenance", "orchestration concepts",
      "resource requests and limits", "reproducible runtime environments", "container security basics"],
     ["3.4", "3.5", "3.7"],
     ["comp_cloud_infra_027", "comp_devops_142", "comp_sre_152"], "standard"),

    ("comp_linux_144", "Linux & Shell Scripting for Data Work", "Functional", "procedural",
     "Linux and Shell Scripting",
     "Getting work done on a server: the file system and permissions, text processing at the command line, "
     "shell scripting, scheduled jobs and diagnosing a slow or full machine.",
     ["file system and permissions", "text processing at the command line", "shell scripting basics",
      "scheduled jobs and cron", "diagnosing disk and memory problems", "secure remote access"],
     ["3.4", "3.5", "5.1"],
     ["comp_devops_142", "comp_network_145", "comp_data_eng_136"], "standard"),

    ("comp_network_145", "Networking & Systems Administration", "Functional", "accuracy",
     "Networking and Systems Administration",
     "Running the infrastructure statistical systems sit on: addressing and routing basics, firewalls and "
     "proxies, certificates, backups and capacity planning.",
     ["addressing and routing basics", "firewalls and network policy", "proxies and reverse proxies",
      "certificates and transport security", "backup and restore procedures", "capacity planning for servers"],
     ["3.4", "3.7", "OA.DM"],
     ["comp_cybersecurity_ops_146", "comp_linux_144", "comp_cloud_infra_027"], "thin"),

    ("comp_cybersecurity_ops_146", "Cybersecurity Operations & Incident Response", "Functional", "accuracy",
     "Cybersecurity Operations",
     "Defending government data systems: threat and vulnerability management, logging and monitoring, "
     "incident response and reporting, phishing defence and CERT-In style advisories.",
     ["vulnerability management", "security logging and monitoring", "incident response and escalation",
      "phishing and social engineering defence", "security advisories and patch cycles",
      "audit trails for sensitive data access"],
     ["3.5", "3.7", "OA.DM"],
     ["comp_data_privacy_026", "comp_identity_mgmt_147", "comp_network_145"], "standard"),

    ("comp_identity_mgmt_147", "Identity, Access Management & e-Authentication", "Functional", "accuracy",
     "Identity and Access Management",
     "Controlling who can reach what: role-based access, single sign-on and federation, multi-factor "
     "authentication, privileged access review and joiner-mover-leaver processes.",
     ["role based access control", "single sign-on and federation", "multi-factor authentication",
      "privileged access review", "joiner mover leaver processes", "access logging and certification"],
     ["3.4", "3.7", "OA.DM"],
     ["comp_cybersecurity_ops_146", "comp_e_gov_023", "comp_data_privacy_026"], "standard"),

    ("comp_web_dev_148", "Web Application Development for Data Portals", "Functional", "accuracy",
     "Web Development for Data Portals",
     "Building the web front ends statistical data is published through: page structure and accessibility, "
     "client-server interaction, rendering large tables and charts, and performance on weak connections.",
     ["page structure and accessibility", "client-server interaction patterns",
      "rendering large tables and charts", "performance on weak connections", "internationalisation of interfaces",
      "progressive enhancement"],
     ["3.3", "7.1", "7.2"],
     ["comp_ux_design_150", "comp_open_data_151", "comp_api_int_028"], "standard"),

    ("comp_mobile_dev_149", "Mobile Application Development for Field Surveys", "Functional", "accuracy",
     "Mobile Development for Surveys",
     "Building and maintaining the mobile apps enumerators use: offline-first storage, sync and conflict "
     "handling, GPS and media capture, battery and data use, and device fleet updates.",
     ["offline-first local storage", "sync and conflict handling", "GPS and media capture",
      "battery and data use optimisation", "device fleet updates", "crash reporting from the field"],
     ["3.1", "3.5", "4.3"],
     ["comp_capi_116", "comp_web_dev_148", "comp_spatial_stat_012"], "thin"),

    ("comp_ux_design_150", "User Experience Design for Statistical Products", "Functional", "procedural",
     "UX Design for Statistical Products",
     "Designing statistical products around their users: user research and personas, information "
     "architecture, usability testing, accessibility standards and design for low digital literacy.",
     ["user research and personas", "information architecture for data sites", "usability testing",
      "accessibility standards compliance", "designing for low digital literacy", "design systems and consistency"],
     ["2.1", "3.3", "7.2", "7.5"],
     ["comp_data_viz_019", "comp_web_dev_148", "comp_citizen_039"], "standard"),

    ("comp_open_data_151", "Open Data Platforms & Portal Management", "Functional", "procedural",
     "Open Data Platforms",
     "Running an open data portal: dataset publication workflow, machine-readable formats, open licensing, "
     "harvesting and catalogue standards, and measuring reuse.",
     ["dataset publication workflow", "machine readable formats", "open licensing and attribution",
      "catalogue standards and harvesting", "measuring dataset reuse", "data request and feedback handling"],
     ["7.1", "7.2", "7.4", "OA.MM"],
     ["comp_microdata_release_131", "comp_metadata_sdmx_123", "comp_e_gov_023"], "standard"),

    ("comp_sre_152", "Service Reliability & Systems Monitoring", "Functional", "accuracy",
     "Service Reliability",
     "Keeping statistical services up: service level objectives, health checks and alerting, capacity and "
     "load testing, incident review and reducing repeat failures.",
     ["service level objectives", "health checks and alerting", "load and capacity testing",
      "incident review and postmortems", "reducing repeat failures", "observability dashboards"],
     ["3.5", "3.7", "7.1"],
     ["comp_devops_142", "comp_containers_143", "comp_network_145"], "thin"),

    ("comp_nlp_153", "Natural Language Processing for Text Data", "Functional", "accuracy",
     "NLP for Text Data",
     "Turning free text into statistics: text cleaning and tokenisation, automatic coding of verbatim "
     "responses, topic and sentiment extraction, and evaluating text models honestly.",
     ["text cleaning and tokenisation", "automatic coding of verbatim responses",
      "topic modelling for open responses", "sentiment and stance extraction", "evaluating text classifiers",
      "multilingual text processing"],
     ["5.2", "5.4", "6.3"],
     ["comp_ml_stats_005", "comp_classification_122", "comp_python_stats_017"], "standard"),

    ("comp_cv_satellite_154", "Computer Vision & Satellite Imagery Analytics", "Functional", "accuracy",
     "Satellite Imagery Analytics",
     "Extracting statistics from imagery: image preprocessing, land-cover classification, change detection, "
     "night-lights and built-up indicators, and validating imagery-derived estimates against ground truth.",
     ["image preprocessing and mosaicking", "land cover classification", "change detection methods",
      "night lights and built-up indicators", "ground truth validation", "resolution and mixed pixel issues"],
     ["4.3", "5.1", "5.5"],
     ["comp_spatial_stat_012", "comp_agri_stats_009", "comp_ml_stats_005"], "standard"),

    ("comp_mlops_155", "MLOps & Model Lifecycle Management", "Functional", "accuracy",
     "MLOps",
     "Running models in production: experiment tracking, model registry and versioning, deployment "
     "patterns, drift monitoring and scheduled retraining with audit trails.",
     ["experiment tracking", "model registry and versioning", "deployment patterns for models",
      "data and concept drift monitoring", "scheduled retraining", "audit trails for model decisions"],
     ["3.2", "3.5", "5.4"],
     ["comp_ml_stats_005", "comp_devops_142", "comp_ai_governance_156"], "standard"),

    ("comp_ai_governance_156", "AI Governance, Fairness & Explainability", "Functional", "procedural",
     "AI Governance",
     "Governing AI use in government: model documentation and model cards, fairness testing across groups, "
     "explainability requirements, human oversight and recourse for affected people.",
     ["model documentation and model cards", "fairness testing across groups", "explainability techniques",
      "human oversight and escalation", "recourse for affected people", "risk classification of AI use cases"],
     ["OA.QM", "OA.DM", "8.2"],
     ["comp_data_ethics_124", "comp_mlops_155", "comp_ml_stats_005"], "standard"),

    ("comp_genai_157", "Generative AI Applications in Government", "Functional", "accuracy",
     "Generative AI in Government",
     "Using generative AI responsibly in public administration: prompt and retrieval patterns, grounding "
     "answers in official sources, evaluating outputs, cost control and where not to use it.",
     ["prompting and retrieval patterns", "grounding answers in official sources",
      "evaluating generated outputs", "hallucination risk and mitigation", "cost and latency control",
      "tasks unsuited to generative AI"],
     ["3.2", "7.5", "OA.PM"],
     ["comp_nlp_153", "comp_ai_governance_156", "comp_e_gov_023"], "standard"),

    ("comp_web_scraping_158", "Web Scraping & Alternative Data Acquisition", "Functional", "accuracy",
     "Web Scraping",
     "Collecting data from the web for statistics: scraping design and politeness, page structure change "
     "resilience, legal and ethical limits, and quality assessment of scraped series.",
     ["scraping design and rate limiting", "resilience to page structure change", "legal and ethical limits",
      "deduplication of scraped records", "quality assessment of scraped series",
      "scraped prices as a CPI input"],
     ["4.3", "5.1", "OA.QM"],
     ["comp_big_data_006", "comp_price_stats_003", "comp_python_stats_017"], "standard"),

    ("comp_mobile_data_159", "Mobile Network & Sensor Data for Statistics", "Functional", "accuracy",
     "Mobile and Sensor Data",
     "Using mobile network and sensor data: call detail record aggregates, mobility indicators, sensor and "
     "IoT streams, representativeness of device-based populations and privacy safeguards.",
     ["call detail record aggregates", "mobility and presence indicators", "sensor and IoT data streams",
      "representativeness of device populations", "privacy safeguards for telecom data",
      "combining sensor data with surveys"],
     ["1.5", "4.3", "5.1"],
     ["comp_big_data_006", "comp_migration_stats_073", "comp_dp_161"], "thin"),

    ("comp_synthetic_data_160", "Synthetic Data Generation for Testing & Release", "Functional", "accuracy",
     "Synthetic Data Generation",
     "Generating synthetic datasets: fully and partially synthetic microdata, preserving joint "
     "distributions, utility measurement, residual disclosure risk and honest labelling.",
     ["fully and partially synthetic microdata", "preserving joint distributions", "utility measurement",
      "residual disclosure risk", "synthetic data for system testing", "labelling synthetic outputs honestly"],
     ["5.8", "6.4", "3.6"],
     ["comp_disclosure_105", "comp_dp_161", "comp_ml_stats_005"], "thin"),

    ("comp_dp_161", "Differential Privacy & Privacy-Preserving Analytics", "Functional", "accuracy",
     "Differential Privacy",
     "Formal privacy for statistical outputs: the differential privacy definition and budget, noise "
     "mechanisms, suppression of small cells, and the accuracy cost of formal guarantees.",
     ["differential privacy definition and budget", "Laplace and Gaussian mechanisms",
      "suppressing small cells", "accuracy cost of formal privacy", "secure multiparty computation basics",
      "communicating privacy guarantees to users"],
     ["6.4", "OA.DM", "OA.QM"],
     ["comp_disclosure_105", "comp_data_privacy_026", "comp_synthetic_data_160"], "thin"),

    ("comp_bi_tools_162", "Business Intelligence Tools", "Functional", "accuracy",
     "Business Intelligence Tools",
     "Building reports and dashboards in BI tools: data models and measures, drill-down design, refresh "
     "scheduling, row-level security and publishing to an audience.",
     ["data models and calculated measures", "drill-down and filter design", "scheduled refresh and gateways",
      "row level security", "publishing and sharing workspaces", "performance of large visuals"],
     ["7.1", "7.2", "6.3"],
     ["comp_data_viz_019", "comp_dwh_139", "comp_db_design_029"], "standard"),

    ("comp_excel_adv_163", "Advanced Spreadsheet Analytics", "Functional", "procedural",
     "Advanced Spreadsheets",
     "Using spreadsheets well for official work: lookup and array formulas, pivot analysis, data "
     "validation, auditing formulas and knowing when to move to a real database.",
     ["lookup and array formulas", "pivot tables and grouping", "data validation and input control",
      "auditing and tracing formulas", "spreadsheet error risk", "moving from spreadsheets to databases"],
     ["5.7", "6.1"],
     ["comp_tabulation_130", "comp_db_design_029"], "standard"),

    ("comp_stata_164", "Stata for Econometric Analysis", "Functional", "accuracy",
     "Stata",
     "Working in Stata: data management and reshaping, survey estimation commands, panel and time-series "
     "estimators, do-files and reproducible logs.",
     ["data management and reshaping", "survey estimation commands", "panel data estimators",
      "programming do-files", "reproducible logs and version control", "exporting publication tables"],
     ["5.4", "5.6", "6.1"],
     ["comp_statistical_sw_030", "comp_econometrics_111", "comp_r_analytics_018"], "thin"),

    ("comp_julia_matlab_165", "Scientific Computing for Statistical Models", "Functional", "accuracy",
     "Scientific Computing",
     "Numerical computing for heavy statistical models: matrix computation, optimisation and solvers, "
     "numerical stability, profiling and speeding up simulation-heavy work.",
     ["matrix computation and linear algebra", "optimisation and solvers", "numerical stability and precision",
      "profiling and vectorisation", "simulation and Monte Carlo runs", "interfacing with compiled code"],
     ["3.2", "5.5"],
     ["comp_python_stats_017", "comp_bayesian_107"], "thin"),

    ("comp_reproducible_166", "Reproducible Research & Workflow Automation", "Functional", "procedural",
     "Reproducible Research",
     "Making statistical work repeatable: project structure, environment pinning, parameterised reports, "
     "automated end-to-end runs and archiving an analysis so it can be re-run years later.",
     ["project structure conventions", "pinning environments and dependencies",
      "parameterised and literate reports", "automated end-to-end runs", "archiving analyses for re-execution",
      "documenting data provenance"],
     ["3.2", "3.7", "OA.MM"],
     ["comp_version_ctrl_141", "comp_python_stats_017", "comp_r_analytics_018"], "standard"),

    ("comp_testing_qa_167", "Software Testing & Quality Assurance", "Functional", "accuracy",
     "Software Testing",
     "Testing statistical software and systems: unit and integration tests, test data design, regression "
     "testing of estimates, user acceptance testing and defect triage.",
     ["unit and integration tests", "test data design", "regression testing of published estimates",
      "user acceptance testing", "defect triage and severity", "test coverage and its limits"],
     ["3.5", "3.6", "OA.QM"],
     ["comp_devops_142", "comp_req_analysis_168", "comp_data_gov_016"], "standard"),

    ("comp_req_analysis_168", "Requirements Analysis & Functional Specification", "Functional", "procedural",
     "Requirements Analysis",
     "Turning a statistical need into a buildable specification: eliciting requirements, user stories and "
     "acceptance criteria, scope control, and traceability from need to delivered feature.",
     ["eliciting requirements from users", "user stories and acceptance criteria", "functional specification writing",
      "scope control and change requests", "traceability from need to feature", "prioritising a backlog"],
     ["1.1", "1.3", "2.6", "3.6"],
     ["comp_project_mgmt_024", "comp_testing_qa_167", "comp_ux_design_150"], "standard"),

    ("comp_it_procurement_169", "IT Procurement & Vendor Management", "Functional", "procedural",
     "IT Procurement and Vendor Management",
     "Buying and running IT services in government: writing technical specifications, evaluating bids on "
     "technical merit, service level agreements, vendor performance review and exit planning.",
     ["writing technical specifications", "technical evaluation of bids", "service level agreements",
      "vendor performance review", "exit and transition planning", "avoiding vendor lock-in"],
     ["OA.FM", "3.7", "OA.PM"],
     ["comp_procurement_021", "comp_enterprise_arch_170", "comp_project_mgmt_024"], "standard"),

    ("comp_enterprise_arch_170", "Enterprise Architecture & Interoperability Frameworks", "Functional", "accuracy",
     "Enterprise Architecture",
     "Designing the shape of a government IT estate: architecture layers and principles, interoperability "
     "frameworks, shared services and reference data, and managing technical debt across systems.",
     ["architecture layers and principles", "government interoperability frameworks",
      "shared services and reference data", "application portfolio rationalisation", "managing technical debt",
      "architecture review boards"],
     ["2.6", "3.3", "3.7", "OA.PM"],
     ["comp_api_int_028", "comp_e_gov_023", "comp_it_procurement_169"], "thin"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Family 5 - public administration, law and programme management
# ─────────────────────────────────────────────────────────────────────────────
ADMINISTRATION = [
    ("comp_parliament_171", "Parliament Questions & Legislative Business", "Functional", "procedural",
     "Parliament Work",
     "Handling parliamentary business: starred and unstarred questions, deadlines and vetting, assurances "
     "and their implementation, and briefing material for the House.",
     ["starred and unstarred questions", "question vetting and deadlines", "drafting replies with data",
      "parliamentary assurances and follow-up", "standing committee material", "briefing notes for the House"],
     ["7.5", "OA.PM"],
     ["comp_report_writing_020", "comp_comm_032", "comp_records_mgmt_179"], "standard"),

    ("comp_rajbhasha_172", "Official Language Implementation", "Functional", "procedural",
     "Official Language Implementation",
     "Implementing the official language policy: bilingual correspondence and publications, translation "
     "quality, official language committee work and annual targets.",
     ["bilingual correspondence requirements", "translation of statistical terms",
      "official language committee work", "annual programme targets", "bilingual publication checks",
      "terminology glossaries for statistics"],
     ["7.2", "OA.PM"],
     ["comp_report_writing_020", "comp_comm_032"], "thin"),

    ("comp_vigilance_173", "Vigilance, Conduct Rules & Disciplinary Proceedings", "Functional", "procedural",
     "Vigilance and Conduct",
     "Vigilance administration: conduct rules, preliminary enquiry and charge sheets, disciplinary "
     "proceedings, preventive vigilance and handling complaints.",
     ["conduct rules for government servants", "preliminary enquiry and charge sheets",
      "disciplinary proceeding stages", "preventive vigilance measures", "complaint handling and confidentiality",
      "role of the vigilance officer"],
     ["OA.PM", "OA.QM"],
     ["comp_integrity_034", "comp_estab_rules_174", "comp_court_cases_177"], "standard"),

    ("comp_estab_rules_174", "Establishment, Service Rules & Cadre Management", "Functional", "procedural",
     "Establishment and Service Rules",
     "Establishment work: recruitment rules, seniority and promotion, leave and transfer rules, cadre "
     "review and the service records of a statistical cadre.",
     ["recruitment and service rules", "seniority and promotion procedures", "leave and transfer rules",
      "cadre review and restructuring", "service book and record maintenance", "reservation roster maintenance"],
     ["OA.PM"],
     ["comp_pension_175", "comp_vigilance_173", "comp_records_mgmt_179"], "standard"),

    ("comp_pension_175", "Pension, Retirement Benefits & HR Records", "Functional", "procedural",
     "Pension and Retirement Benefits",
     "Retirement and pension processing: pension eligibility and calculation, the national pension system, "
     "gratuity and commutation, and timely settlement of retirement dues.",
     ["pension eligibility and calculation", "national pension system accounts", "gratuity and commutation",
      "pension papers and timelines", "family pension cases", "retirement records and verification"],
     ["OA.PM", "OA.FM"],
     ["comp_estab_rules_174", "comp_public_fin_025"], "thin"),

    ("comp_audit_response_176", "Audit Paras, Compliance & Accountability", "Functional", "procedural",
     "Audit Compliance",
     "Handling audit: inspection reports and audit paras, action taken notes, public accounts committee "
     "material, and closing observations through systemic fixes.",
     ["inspection reports and audit paras", "action taken notes", "public accounts committee material",
      "settling long pending paras", "internal audit arrangements", "systemic fixes after audit findings"],
     ["OA.FM", "OA.QM", "8.3"],
     ["comp_public_fin_025", "comp_procurement_021", "comp_integrity_034"], "standard"),

    ("comp_court_cases_177", "Court Cases & Litigation Management", "Functional", "procedural",
     "Litigation Management",
     "Managing litigation: tracking cases and hearing dates, preparing parawise comments and counter "
     "affidavits, coordinating with counsel and implementing court orders.",
     ["case tracking and hearing dates", "parawise comments and counter affidavits",
      "coordination with government counsel", "implementation of court orders", "contempt risk management",
      "records required for litigation"],
     ["OA.PM", "7.5"],
     ["comp_statistical_law_134", "comp_rtt_022", "comp_records_mgmt_179"], "standard"),

    ("comp_grievance_178", "Public Grievance Redress", "Functional", "procedural",
     "Public Grievance Redress",
     "Redressing public grievances: intake and categorisation, timelines and escalation, quality of "
     "disposal, appeals and root-cause analysis of repeat grievances.",
     ["grievance intake and categorisation", "disposal timelines and escalation", "quality of redress",
      "appeal handling", "root cause analysis of repeat grievances", "feedback to the complainant"],
     ["7.5", "8.1"],
     ["comp_citizen_039", "comp_rtt_022", "comp_comm_032"], "standard"),

    ("comp_records_mgmt_179", "Records Management, e-Office & Archival Policy", "Functional", "procedural",
     "Records Management",
     "Managing official records end to end: file numbering and noting, e-Office workflows, record "
     "retention schedules, weeding and transfer to the archives.",
     ["file numbering and noting practice", "e-Office file workflows", "record retention schedules",
      "weeding and appraisal of records", "transfer to the national archives", "digitisation of legacy records"],
     ["OA.DM", "OA.PM"],
     ["comp_e_gov_023", "comp_rtt_022", "comp_data_gov_016"], "standard"),

    ("comp_intl_coop_180", "International Cooperation & Multilateral Engagement", "Functional", "procedural",
     "International Cooperation",
     "Working with international bodies: statistical commission and working group participation, country "
     "briefs and positions, technical cooperation and hosting international delegations.",
     ["statistical commission participation", "country briefs and positions",
      "technical cooperation agreements", "hosting international delegations", "south-south statistical cooperation",
      "reporting commitments to global bodies"],
     ["OA.SM", "OA.PM", "1.2"],
     ["comp_intl_standards_133", "comp_comm_032", "comp_sdg_monitor_015"], "standard"),

    ("comp_training_design_181", "Training Design, Delivery & Evaluation", "Functional", "procedural",
     "Training Design and Delivery",
     "Designing and running training for officials: needs analysis, learning objectives and session "
     "design, facilitation, and evaluating training beyond satisfaction scores.",
     ["training needs analysis", "learning objectives and session design", "facilitation techniques",
      "blended and online delivery", "evaluating training outcomes", "trainer development and certification"],
     ["OA.PM", "8.1", "8.2"],
     ["comp_knowledge_mgmt_182", "comp_coaching_196", "comp_comm_032"], "standard"),

    ("comp_knowledge_mgmt_182", "Knowledge Management & Institutional Memory", "Functional", "procedural",
     "Knowledge Management",
     "Keeping what the organisation knows: documenting methods and decisions, handover on transfer, "
     "communities of practice, and making past work findable.",
     ["documenting methods and decisions", "handover notes on transfer", "communities of practice",
      "making past work findable", "lessons learned reviews", "succession of critical know-how"],
     ["OA.MM", "OA.PM", "8.3"],
     ["comp_training_design_181", "comp_records_mgmt_179", "comp_change_mgmt_035"], "standard"),

    ("comp_event_mgmt_183", "Conference & Event Management", "Functional", "procedural",
     "Event Management",
     "Organising official conferences and events: planning and budgeting, invitations and protocol, "
     "logistics, hybrid delivery and post-event reporting.",
     ["event planning and budgeting", "invitations and protocol", "venue and logistics management",
      "hybrid and virtual delivery", "post-event reporting", "statistics day and outreach events"],
     ["7.4", "OA.PM", "OA.FM"],
     ["comp_project_mgmt_024", "comp_comm_032"], "thin"),

    ("comp_media_relations_184", "Media Relations & Press Briefing", "Functional", "procedural",
     "Media Relations",
     "Working with the media on statistics: press notes, briefing journalists on methodology, correcting "
     "misinterpretation, and preparing spokespeople for difficult questions.",
     ["press notes for data releases", "briefing journalists on methodology",
      "correcting misinterpretation of statistics", "preparing spokespeople", "embargo handling with media",
      "responding to critical coverage"],
     ["7.3", "7.4", "7.5"],
     ["comp_comm_032", "comp_report_writing_020", "comp_revision_policy_132"], "standard"),

    ("comp_social_media_185", "Social Media & Digital Outreach", "Functional", "procedural",
     "Digital Outreach",
     "Reaching data users online: content planning for statistical releases, accessible visual assets, "
     "community responses, misinformation correction and measuring reach.",
     ["content planning for releases", "accessible visual assets", "responding to online queries",
      "correcting misinformation online", "measuring reach and engagement", "tone and voice for official accounts"],
     ["7.4", "7.5"],
     ["comp_data_viz_019", "comp_media_relations_184", "comp_citizen_039"], "thin"),

    ("comp_gender_budget_186", "Gender Budgeting & Inclusive Policy Analysis", "Functional", "procedural",
     "Gender Budgeting",
     "Applying a gender and equity lens to public finance: gender budget statements, incidence analysis of "
     "spending, equity-disaggregated outcome indicators and reporting.",
     ["gender budget statement preparation", "incidence analysis of public spending",
      "equity disaggregated outcome indicators", "scheme level gender tagging", "reporting on inclusive outcomes",
      "linking budgets to gender statistics"],
     ["1.3", "6.1", "OA.FM"],
     ["comp_gender_stats_047", "comp_public_fin_025", "comp_scheme_eval_187"], "thin"),

    ("comp_scheme_eval_187", "Scheme Monitoring & Evaluation", "Functional", "procedural",
     "Scheme Monitoring and Evaluation",
     "Monitoring and evaluating government schemes: results frameworks and indicators, baseline and "
     "endline design, process evaluation, and using evaluation findings in the next cycle.",
     ["results frameworks and indicators", "baseline and endline design", "process evaluation methods",
      "output outcome monitoring frameworks", "using findings in the next cycle", "third party evaluation management"],
     ["8.1", "8.2", "8.3"],
     ["comp_causal_inf_108", "comp_policy_analysis_188", "comp_rural_dev_098"], "standard"),

    ("comp_policy_analysis_188", "Policy Analysis & Evidence-Based Policymaking", "Functional", "procedural",
     "Policy Analysis",
     "Turning evidence into policy advice: framing the policy question, options appraisal, cost-benefit "
     "reasoning, distributional impact and writing advice ministers can act on.",
     ["framing the policy question", "options appraisal", "cost-benefit reasoning",
      "distributional impact analysis", "writing actionable policy advice", "using statistics in cabinet notes"],
     ["1.1", "1.3", "6.3", "8.3"],
     ["comp_scheme_eval_187", "comp_decision_037", "comp_strategic_031"], "standard"),

    ("comp_risk_mgmt_189", "Risk Management & Business Continuity", "Functional", "procedural",
     "Risk Management",
     "Managing risk to statistical production: risk identification and registers, controls and mitigation "
     "owners, business continuity and disaster recovery for critical releases.",
     ["risk identification and registers", "controls and mitigation owners", "risk appetite and escalation",
      "business continuity planning", "disaster recovery for critical releases", "post-incident risk review"],
     ["OA.PM", "OA.QM", "3.7"],
     ["comp_project_mgmt_024", "comp_disaster_mgmt_190", "comp_sre_152"], "standard"),

    ("comp_disaster_mgmt_190", "Disaster Preparedness & Emergency Statistics", "Functional", "procedural",
     "Disaster Preparedness",
     "Statistical work under emergency conditions: rapid assessment surveys, damage and loss reporting, "
     "continuity of field operations during a disaster and coordination with response agencies.",
     ["rapid assessment survey design", "damage and loss reporting", "continuity of field operations",
      "coordination with response agencies", "emergency data sharing protocols", "post-disaster needs assessment"],
     ["4.2", "4.3", "6.1"],
     ["comp_climate_stats_055", "comp_risk_mgmt_189", "comp_survey_ops_126"], "thin"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Family 6 - behavioural competencies (FRAC behavioural pillar)
# ─────────────────────────────────────────────────────────────────────────────
BEHAVIOURAL = [
    ("comp_emotional_int_191", "Emotional Intelligence & Self-Awareness", "Behavioural", "procedural",
     "Emotional Intelligence",
     "Recognising and managing emotions at work: self-awareness, self-regulation under pressure, empathy "
     "for colleagues and respondents, and reading a room before reacting.",
     ["self-awareness of triggers", "self-regulation under pressure", "empathy in workplace interactions",
      "reading social cues in meetings", "managing emotions during conflict", "seeking and using self-insight"],
     ["OA.PM", "1.2"],
     ["comp_resilience_194", "comp_collab_036", "comp_conflict_res_197"], "standard"),

    ("comp_negotiation_192", "Negotiation & Influencing", "Behavioural", "procedural",
     "Negotiation and Influencing",
     "Reaching agreement without authority: preparing positions and interests, building a case with "
     "evidence, trading concessions, and influencing across departments.",
     ["preparing positions and interests", "building a case with evidence", "trading concessions",
      "influencing without authority", "negotiating data sharing arrangements", "closing and recording agreements"],
     ["1.2", "OA.PM", "OA.FM"],
     ["comp_comm_032", "comp_collab_036", "comp_stat_coordination_135"], "standard"),

    ("comp_time_mgmt_193", "Time Management & Personal Productivity", "Behavioural", "procedural",
     "Time Management",
     "Managing your own workload: prioritising against deadlines, planning the week, protecting focused "
     "time, delegating routine work and saying no to low-value demands.",
     ["prioritising against deadlines", "weekly and daily planning", "protecting focused time",
      "delegating routine work", "managing interruptions", "handling competing demands"],
     ["OA.PM"],
     ["comp_accountability_199", "comp_project_mgmt_024"], "standard"),

    ("comp_resilience_194", "Resilience & Stress Management", "Behavioural", "procedural",
     "Resilience",
     "Staying effective under sustained pressure: recognising stress signals, recovery habits, perspective "
     "after setbacks, and supporting a team through a demanding survey round.",
     ["recognising stress signals", "recovery and rest habits", "perspective after setbacks",
      "supporting a team under pressure", "sustainable working during peak rounds", "seeking support early"],
     ["OA.PM", "4.3"],
     ["comp_emotional_int_191", "comp_change_mgmt_035"], "standard"),

    ("comp_learning_agility_195", "Learning Agility & Continuous Development", "Behavioural", "procedural",
     "Learning Agility",
     "Learning fast in a changing environment: seeking feedback, unlearning outdated practice, applying "
     "new methods quickly and building a personal development habit.",
     ["seeking and acting on feedback", "unlearning outdated practice", "applying new methods quickly",
      "personal development planning", "learning from other divisions", "reflective practice"],
     ["8.3", "OA.PM"],
     ["comp_feedback_205", "comp_innov_038", "comp_digital_mindset_202"], "standard"),

    ("comp_coaching_196", "Coaching & Mentoring", "Behavioural", "procedural",
     "Coaching and Mentoring",
     "Developing other people: coaching conversations, setting development goals, mentoring junior "
     "officers, and giving people stretch work with support.",
     ["coaching conversation structure", "setting development goals with staff",
      "mentoring junior officers", "assigning stretch work with support", "recognising potential",
      "handing over expertise before transfer"],
     ["OA.PM"],
     ["comp_leadership_032", "comp_feedback_205", "comp_training_design_181"], "standard"),

    ("comp_conflict_res_197", "Conflict Resolution", "Behavioural", "procedural",
     "Conflict Resolution",
     "Resolving disagreement constructively: surfacing the real issue, separating people from positions, "
     "mediating between teams and repairing working relationships.",
     ["surfacing the real issue", "separating people from positions", "mediating between teams",
      "de-escalating heated discussions", "repairing working relationships", "escalating appropriately"],
     ["OA.PM", "1.2"],
     ["comp_emotional_int_191", "comp_collab_036", "comp_negotiation_192"], "standard"),

    ("comp_inclusion_198", "Diversity, Equity & Inclusion", "Behavioural", "procedural",
     "Diversity and Inclusion",
     "Building an inclusive workplace and inclusive statistics: fair treatment and access, inclusive "
     "meetings and language, accessibility, and awareness of bias in data and decisions.",
     ["fair treatment and access at work", "inclusive meetings and language", "accessibility in the workplace",
      "awareness of bias in data", "supporting colleagues with different needs", "inclusive recruitment practice"],
     ["OA.PM", "7.5"],
     ["comp_gender_stats_047", "comp_collab_036", "comp_disability_stats_049"], "standard"),

    ("comp_accountability_199", "Accountability & Ownership", "Behavioural", "procedural",
     "Accountability and Ownership",
     "Owning outcomes rather than tasks: committing to deliverables, flagging slippage early, following "
     "through without reminders and taking responsibility for mistakes.",
     ["committing to clear deliverables", "flagging slippage early", "following through without reminders",
      "taking responsibility for mistakes", "closing the loop with stakeholders", "ownership across handovers"],
     ["OA.PM", "OA.QM"],
     ["comp_integrity_034", "comp_time_mgmt_193"], "standard"),

    ("comp_attention_detail_200", "Attention to Detail & Accuracy Orientation", "Behavioural", "procedural",
     "Attention to Detail",
     "Getting the numbers right: systematic checking habits, cross-verifying before release, spotting "
     "inconsistencies, and resisting time pressure that invites shortcuts.",
     ["systematic checking habits", "cross-verification before release", "spotting inconsistencies in tables",
      "resisting shortcuts under deadline", "double-checking published figures", "maintaining a correction log"],
     ["5.3", "6.2", "OA.QM"],
     ["comp_integrity_034", "comp_data_scrutiny_129", "comp_prob_solve_033"], "standard"),

    ("comp_systems_think_201", "Systems Thinking", "Behavioural", "procedural",
     "Systems Thinking",
     "Seeing the whole system: mapping how parts of the statistical process affect each other, "
     "anticipating second-order effects and avoiding local fixes that break something downstream.",
     ["mapping interdependencies", "anticipating second-order effects", "avoiding local fixes with global cost",
      "feedback loops in processes", "end-to-end process thinking", "trade-offs across the value chain"],
     ["2.6", "8.2", "OA.SM"],
     ["comp_strategic_031", "comp_prob_solve_033", "comp_change_mgmt_035"], "standard"),

    ("comp_digital_mindset_202", "Digital Mindset & Technology Adoption", "Behavioural", "procedural",
     "Digital Mindset",
     "Adopting new digital ways of working: willingness to move off manual routines, basic digital "
     "confidence, encouraging the team onto new tools and questioning tools that add no value.",
     ["moving off manual routines", "basic digital confidence", "encouraging team adoption of tools",
      "questioning tools that add no value", "learning new systems quickly", "digital collaboration habits"],
     ["3.6", "8.3", "OA.PM"],
     ["comp_change_mgmt_035", "comp_learning_agility_195", "comp_e_gov_023"], "standard"),

    ("comp_public_speaking_203", "Public Speaking & Presentation", "Behavioural", "procedural",
     "Public Speaking",
     "Presenting with confidence: structuring a talk, presenting statistics to non-specialists, handling "
     "questions and speaking at conferences and review meetings.",
     ["structuring a talk", "presenting statistics to non-specialists", "handling questions on the spot",
      "using slides and visuals well", "speaking at review meetings", "managing nerves before speaking"],
     ["7.4", "1.2"],
     ["comp_comm_032", "comp_data_viz_019", "comp_media_relations_184"], "standard"),

    ("comp_teamwork_remote_204", "Cross-Functional & Distributed Teamwork", "Behavioural", "procedural",
     "Distributed Teamwork",
     "Working well across divisions and locations: shared working agreements, asynchronous updates, "
     "including field and regional colleagues, and building trust without face time.",
     ["shared working agreements", "asynchronous updates and handovers", "including field and regional colleagues",
      "building trust at a distance", "running effective virtual meetings", "coordinating across time zones"],
     ["1.2", "4.2", "OA.PM"],
     ["comp_collab_036", "comp_comm_032"], "standard"),

    ("comp_feedback_205", "Giving & Receiving Feedback", "Behavioural", "procedural",
     "Feedback",
     "Making feedback useful: specific and timely observations, separating behaviour from person, "
     "receiving criticism without defensiveness, and APAR conversations that change something.",
     ["specific and timely observations", "separating behaviour from person", "receiving criticism openly",
      "appraisal conversations that land", "asking for feedback proactively", "following up after feedback"],
     ["OA.PM", "8.3"],
     ["comp_coaching_196", "comp_emotional_int_191", "comp_leadership_032"], "standard"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Everything, in id order.
# ─────────────────────────────────────────────────────────────────────────────
EXTRA_COMPETENCIES = (SUBJECT_MATTER + MACRO_ACCOUNTS + METHODOLOGY
                      + TECHNOLOGY + ADMINISTRATION + BEHAVIOURAL)
