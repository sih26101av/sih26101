"""
Static, hand-written domain content for the mock-data generator.

Nothing here is random: competency descriptions, topic vocabularies, office
structure, GSBPM sub-processes and designations are curated text. The
generator (generate_mock_data.py) draws from these with a seeded RNG.

Everything built from this module is SYNTHETIC. It is shaped like MoSPI /
iGOT Karmayogi data so the platform can be demonstrated end-to-end; it is not
an export of any real system.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# FRAC competencies (ids / names / types are the catalogue ids the rest of the
# platform already uses — keep them stable).
#   decay: "accuracy"   — knowledge that goes stale fast (methods, tools)
#          "procedural" — practised routines / behaviours, slower decay
# ─────────────────────────────────────────────────────────────────────────────
COMPETENCIES = [
    # id, name, type, decay, description, topics
    ("comp_nat_accounts_001", "National Accounts Framework (SNA 2008)", "Domain", "accuracy",
     "Compiling and interpreting national accounts under the System of National Accounts 2008: "
     "GDP and GVA by production, income and expenditure approaches, supply-use tables, "
     "institutional sector accounts and base-year revisions.",
     ["GDP and GVA by the production approach", "supply and use tables", "institutional sector accounts",
      "base-year revision and back-series", "quarterly GDP compilation", "expenditure-side GDP and PFCE",
      "capital formation and fixed capital stock", "deflators for real GDP"]),
    ("comp_survey_design_002", "Survey Design & Sampling Methodology", "Domain", "accuracy",
     "Designing household and enterprise surveys: sampling frames, stratified multi-stage sampling, "
     "sample size and allocation, estimation with design weights, and variance estimation.",
     ["sampling frames and first-stage units", "stratified multi-stage sampling", "sample size and allocation",
      "design weights and estimation", "variance estimation and standard errors",
      "non-response adjustment", "questionnaire design and pre-testing", "rotational panel designs"]),
    ("comp_price_stats_003", "Price Statistics & CPI Construction", "Domain", "accuracy",
     "Building consumer and producer price indices: CPI basket and weights, price collection and "
     "quote validation, elementary aggregates, quality adjustment, item substitution and rebasing.",
     ["CPI basket and weights", "price collection and quote validation", "elementary aggregates",
      "quality adjustment and item substitution", "seasonal items in the CPI", "rebasing and linking CPI series",
      "housing in the CPI", "wholesale and producer price indices"]),
    ("comp_index_numbers_004", "Index Number Theory & Practice", "Domain", "accuracy",
     "Index number formulas and their properties: Laspeyres, Paasche, Fisher and chain indices, "
     "axiomatic tests, weights, linking and splicing of index series.",
     ["Laspeyres, Paasche and Fisher indices", "chain-linked indices", "axiomatic and economic index tests",
      "weights and weight reference periods", "splicing and linking index series",
      "index of industrial production", "unit value and volume indices"]),
    ("comp_ml_stats_005", "Machine Learning for Official Statistics", "Domain", "accuracy",
     "Applying machine learning to official statistics: supervised classification and coding, "
     "imputation, nowcasting with alternative data, model validation and responsible use.",
     ["automatic classification and coding with ML", "ML-based imputation", "model validation and cross-validation",
      "gradient boosting and random forests", "text classification of survey responses",
      "bias, explainability and responsible ML", "ML pipelines for survey processing"]),
    ("comp_big_data_006", "Big Data Integration in NSS Surveys", "Domain", "accuracy",
     "Integrating big data and administrative sources with NSS surveys: web-scraped prices, "
     "mobile and satellite data, record linkage, representativeness and quality assessment.",
     ["administrative data integration", "web-scraped prices", "record linkage", "satellite and mobile data",
      "representativeness and coverage bias", "big data quality frameworks", "distributed data processing"]),
    ("comp_econ_census_007", "Economic Census Planning & Execution", "Domain", "procedural",
     "Planning and running the Economic Census: establishment listing, enumeration blocks, field "
     "organisation, digital data capture, supervision and results tabulation.",
     ["establishment listing and enumeration blocks", "field organisation and supervision",
      "digital data capture for the census", "coverage checks and post-enumeration survey",
      "census results tabulation", "business register from the census"]),
    ("comp_dem_analysis_008", "Demographic Analysis & Population Estimation", "Domain", "accuracy",
     "Demographic methods for population statistics: fertility, mortality and life tables, "
     "population projections, and small-area population estimation.",
     ["fertility measures", "mortality and life tables", "population projections (cohort component)",
      "migration estimation", "small-area population estimates", "sample registration system data"]),
    ("comp_agri_stats_009", "Agricultural Statistics & Crop Forecasting", "Domain", "accuracy",
     "Agricultural statistics: land use and crop area, crop cutting experiments, yield estimation, "
     "crop forecasting with remote sensing, and livestock statistics.",
     ["crop area estimation", "crop cutting experiments and yield", "crop forecasting with remote sensing",
      "land use statistics", "livestock census", "agricultural price and cost of cultivation data"]),
    ("comp_industry_stats_010", "Industrial Statistics & ASI Methodology", "Domain", "accuracy",
     "Annual Survey of Industries methodology: frame from the factory register, census and sample "
     "sectors, NIC classification, scrutiny of returns and ASI tabulation.",
     ["ASI frame and factory register", "census and sample sectors of the ASI", "NIC industrial classification",
      "scrutiny and validation of ASI returns", "ASI estimation and tabulation",
      "index of industrial production linkages"]),
    ("comp_gdp_nowcast_011", "GDP Nowcasting Techniques", "Domain", "accuracy",
     "Nowcasting GDP from high-frequency indicators: bridge equations, dynamic factor models, "
     "mixed-frequency regressions and evaluating nowcast accuracy.",
     ["high-frequency indicators for GDP", "bridge equations", "dynamic factor models",
      "mixed-frequency (MIDAS) regressions", "nowcast evaluation and revisions"]),
    ("comp_spatial_stat_012", "Spatial Statistics & GIS for Surveys", "Domain", "procedural",
     "Using GIS and spatial statistics in surveys: geocoded frames, area sampling, spatial "
     "interpolation, mapping survey estimates and small-area geography.",
     ["GIS basics for statisticians", "geocoded sampling frames", "area sampling with maps",
      "spatial interpolation and kriging", "mapping survey estimates", "spatial autocorrelation"]),
    ("comp_time_series_013", "Time Series Analysis & Seasonal Adjustment", "Domain", "accuracy",
     "Time series methods for official statistics: decomposition, X-13ARIMA-SEATS seasonal "
     "adjustment, ARIMA modelling, trading-day effects and revision analysis.",
     ["time series decomposition", "X-13ARIMA-SEATS seasonal adjustment", "ARIMA modelling",
      "trading-day and festival effects", "revision analysis", "forecasting monthly indicators"]),
    ("comp_poverty_014", "Poverty Measurement & Welfare Indicators", "Domain", "accuracy",
     "Measuring poverty and welfare from consumption surveys: poverty lines, headcount and gap "
     "indices, inequality measures and multidimensional poverty.",
     ["consumption expenditure surveys", "poverty lines and headcount ratios", "poverty gap and severity",
      "inequality: Gini and Lorenz curves", "multidimensional poverty index", "welfare aggregates"]),
    ("comp_sdg_monitor_015", "SDG Monitoring & Voluntary National Review", "Domain", "procedural",
     "Monitoring the Sustainable Development Goals: the national indicator framework, indicator "
     "metadata, data flows from ministries and preparing the Voluntary National Review.",
     ["the SDG national indicator framework", "SDG indicator metadata", "data flows from line ministries",
      "SDG progress reports and dashboards", "the Voluntary National Review", "disaggregation for leaving no one behind"]),
    ("comp_data_gov_016", "Data Governance & Quality Assurance", "Functional", "procedural",
     "Governing statistical data and assuring quality: quality frameworks (NQAF), metadata "
     "standards, data validation rules, audits and quality reporting.",
     ["national quality assurance framework", "data validation rules", "metadata standards (SDMX, DDI)",
      "quality reports and indicators", "statistical audits", "data stewardship roles"]),
    ("comp_python_stats_017", "Python for Statistical Computing", "Functional", "accuracy",
     "Python for statistical work: pandas data wrangling, NumPy, statistical modelling with "
     "statsmodels, reproducible notebooks and automating survey processing.",
     ["pandas data wrangling", "NumPy and vectorised computation", "statsmodels regression",
      "reproducible Jupyter notebooks", "automating survey tabulation in Python", "Python packaging and testing"]),
    ("comp_r_analytics_018", "R for Advanced Analytics", "Functional", "accuracy",
     "R for analysis of survey and administrative data: tidyverse, the survey package for design-based "
     "estimation, modelling and reproducible reporting with R Markdown.",
     ["tidyverse data manipulation", "the survey package for weighted estimates", "regression modelling in R",
      "R Markdown reporting", "ggplot2 graphics", "writing R functions and packages"]),
    ("comp_data_viz_019", "Data Visualization & Dashboard Design", "Functional", "procedural",
     "Visualising statistics and designing dashboards: chart choice, visual encoding, accessible "
     "colour, interactive dashboards and communicating uncertainty.",
     ["choosing the right chart", "visual encoding and perception", "accessible colour and design",
      "interactive dashboards", "communicating uncertainty visually", "dashboard design for decision makers"]),
    ("comp_report_writing_020", "Report Writing for Statistical Publications", "Functional", "procedural",
     "Writing statistical reports and releases: key findings, plain-language explanation of "
     "estimates, tables and footnotes, metadata notes and editorial review.",
     ["writing key findings", "plain-language statistical writing", "tables, footnotes and notes",
      "press releases for statistical data", "editorial review of publications"]),
    ("comp_procurement_021", "Government Procurement & GFR Compliance", "Functional", "procedural",
     "Public procurement under the General Financial Rules: GeM procurement, tendering, bid "
     "evaluation, contract management and audit compliance.",
     ["General Financial Rules for procurement", "procurement on GeM", "tender documents and bid evaluation",
      "contract management", "procurement audit and compliance"]),
    ("comp_rtt_022", "Right to Information & Transparency", "Functional", "procedural",
     "Handling Right to Information requests and proactive disclosure: RTI Act provisions, "
     "exemptions, first appeals and transparency obligations of statistical offices.",
     ["RTI Act provisions", "handling RTI applications", "exemptions and third-party information",
      "first appeals and CIC orders", "proactive disclosure under section 4"]),
    ("comp_e_gov_023", "e-Governance Platforms & Digital Services", "Functional", "procedural",
     "Running digital public services: e-Office, digital platforms of the government, service "
     "design, digital identity and adoption of e-governance systems.",
     ["e-Office file management", "digital public infrastructure", "service design for citizens",
      "digital identity and authentication", "managing e-governance projects"]),
    ("comp_project_mgmt_024", "Project Management in Government Context", "Functional", "procedural",
     "Managing government projects and survey operations: planning, scheduling, risk registers, "
     "monitoring milestones and stakeholder reporting.",
     ["project planning and work breakdown", "scheduling and critical path", "risk registers",
      "monitoring milestones", "stakeholder reporting for projects"]),
    ("comp_public_fin_025", "Public Financial Management & Budget Analysis", "Functional", "procedural",
     "Public financial management: budget formulation, outcome budgets, expenditure tracking and "
     "analysis of government finance statistics.",
     ["budget formulation", "outcome budgeting", "expenditure tracking and PFMS",
      "government finance statistics", "fiscal indicators analysis"]),
    ("comp_data_privacy_026", "Data Privacy, Security & IT Act Compliance", "Functional", "accuracy",
     "Protecting confidential statistical data: the DPDP and IT Acts, anonymisation and disclosure "
     "control, secure data access and information security practice.",
     ["the Digital Personal Data Protection Act", "IT Act compliance", "anonymisation of microdata",
      "statistical disclosure control", "secure data access and information security"]),
    ("comp_cloud_infra_027", "Cloud Infrastructure for Statistical Systems", "Functional", "accuracy",
     "Cloud infrastructure for statistical production: MeghRaj government cloud, virtual machines "
     "and storage, containers, cost management and security in the cloud.",
     ["government cloud (MeghRaj) services", "virtual machines and storage", "containers and orchestration",
      "cloud cost management", "cloud security for statistical data"]),
    ("comp_api_int_028", "API Integration & Interoperability Standards", "Functional", "accuracy",
     "Integrating statistical systems through APIs: REST design, SDMX web services, data exchange "
     "standards and interoperability between ministries.",
     ["REST API basics", "SDMX web services", "data exchange standards", "API security and versioning",
      "interoperability between government systems"]),
    ("comp_db_design_029", "Database Design & SQL for Statistical Databases", "Functional", "accuracy",
     "Designing and querying statistical databases: relational modelling, SQL, indexing, data "
     "warehouses for survey microdata and query performance.",
     ["relational data modelling", "SQL queries and joins", "indexing and query performance",
      "data warehouses for survey microdata", "database administration basics"]),
    ("comp_statistical_sw_030", "Statistical Software Proficiency (SPSS / SAS)", "Functional", "accuracy",
     "Statistical packages for survey analysis: SPSS and SAS data steps, weighted tabulation, "
     "procedures for regression and complex-survey estimation.",
     ["SPSS data preparation", "SAS data steps and procedures", "weighted tabulation in SPSS and SAS",
      "complex-survey procedures", "automating output with syntax"]),
    ("comp_strategic_031", "Strategic Thinking", "Behavioural", "procedural",
     "Thinking strategically about the statistical system: long-term vision, priorities, "
     "anticipating user needs and aligning programmes with national goals.",
     ["long-term vision for the statistical system", "setting priorities", "anticipating data user needs",
      "strategic planning for statistical programmes", "scenario thinking"]),
    ("comp_leadership_032", "Leadership & Team Management", "Behavioural", "procedural",
     "Leading teams in statistical offices: setting direction, delegating, performance "
     "conversations, motivating field teams and developing people.",
     ["leading statistical teams", "delegation and accountability", "performance conversations",
      "motivating field teams", "developing and mentoring people"]),
    ("comp_comm_032", "Effective Communication & Stakeholder Engagement", "Behavioural", "procedural",
     "Communicating with colleagues, data users and stakeholders: briefings, presentations, "
     "user consultations and handling media questions about statistics.",
     ["briefing senior officers", "presentations on statistics", "user consultations",
      "handling media questions on data releases", "writing clear official notes"]),
    ("comp_prob_solve_033", "Problem Solving & Critical Analysis", "Behavioural", "procedural",
     "Structured problem solving: defining problems, root-cause analysis, weighing evidence and "
     "critically reviewing statistical results.",
     ["defining the problem", "root-cause analysis", "weighing evidence", "critical review of statistical results",
      "structured problem-solving tools"]),
    ("comp_integrity_034", "Integrity, Ethics & Public Service Values", "Behavioural", "procedural",
     "Integrity in official statistics: the Fundamental Principles of Official Statistics, "
     "professional independence, conflicts of interest and public service values.",
     ["Fundamental Principles of Official Statistics", "professional independence", "conflicts of interest",
      "conduct rules and public service values", "ethical handling of confidential data"]),
    ("comp_change_mgmt_035", "Change Management & Adaptability", "Behavioural", "procedural",
     "Leading and adapting to change: modernising statistical production, managing resistance, "
     "communicating change and sustaining new ways of working.",
     ["modernising statistical production", "managing resistance to change", "communicating change",
      "sustaining new processes", "personal adaptability"]),
    ("comp_collab_036", "Collaboration & Interpersonal Effectiveness", "Behavioural", "procedural",
     "Working across divisions, ministries and states: collaboration, coordination meetings, "
     "negotiating data sharing and resolving conflict.",
     ["working across divisions", "coordination with state statistical bureaus", "negotiating data sharing",
      "resolving conflict", "effective meetings"]),
    ("comp_decision_037", "Decision Making Under Uncertainty", "Behavioural", "procedural",
     "Deciding with incomplete information: using estimates with uncertainty, risk assessment, "
     "evidence-based options and documenting decisions.",
     ["decisions with uncertain estimates", "risk assessment", "evidence-based options analysis",
      "documenting decisions", "cognitive biases in decisions"]),
    ("comp_innov_038", "Innovation & Creative Problem Solving", "Behavioural", "procedural",
     "Innovating in statistical production: idea generation, pilots and experiments, adopting new "
     "data sources and scaling what works.",
     ["idea generation", "pilots and experiments", "adopting new data sources", "scaling innovations",
      "design thinking"]),
    ("comp_citizen_039", "Citizen-Centric Service Delivery", "Behavioural", "procedural",
     "Serving citizens and data users: user-centred dissemination, grievance handling, "
     "accessibility and feedback on statistical services.",
     ["user-centred dissemination", "grievance handling", "accessible statistical services",
      "collecting user feedback", "service standards for data users"]),
]

# FRAC proficiency descriptors — one template per level per competency type.
LEVEL_TEMPLATES = {
    "Domain": [
        "Knows the basic concepts and terminology of {short}; follows established procedures with close guidance.",
        "Applies {short} methods to routine tasks under supervision and spots obvious errors.",
        "Independently carries out {short} work end to end and interprets the results.",
        "Leads {short} work, reviews others' methodology and mentors junior officers.",
        "Recognised expert in {short}; sets methodology and advises on national and international standards.",
    ],
    "Functional": [
        "Aware of {short} tools and processes; needs significant guidance.",
        "Uses {short} for standard tasks with occasional support.",
        "Proficient in {short}; handles complex cases independently.",
        "Advanced practitioner of {short}; trains peers and improves processes.",
        "Subject-matter expert in {short}; defines organisational standards.",
    ],
    "Behavioural": [
        "Shows basic awareness of {short} in day-to-day work.",
        "Applies {short} in familiar, structured situations.",
        "Consistently demonstrates {short} across varied and ambiguous situations.",
        "Role-models {short} and coaches others to develop it.",
        "Institutionalises {short}; shapes organisational culture and strategy.",
    ],
}

# Level wording for course titles (A2: Intro/Fundamentals → L1–L2,
# Practitioner/Applied → L3, Advanced/Expert/Masterclass → L4–L5).
LEVEL_TITLE_WORDS = {
    1: ["Introduction to", "Basics of", "Getting Started with"],
    2: ["Fundamentals of", "Essentials of", "Foundations of"],
    3: ["Applied", "Practitioner Course in", "Hands-on"],
    4: ["Advanced", "Advanced Methods in", "Advanced Practice in"],
    5: ["Expert Masterclass:", "Masterclass in", "Leading Practice in"],
}
LEVEL_AUDIENCE = {
    1: "officers new to the subject",
    2: "officers who apply it in routine work",
    3: "practitioners who work on it independently",
    4: "senior practitioners who lead and review this work",
    5: "experts who set methodology and standards",
}

# Content overlap between competencies — the ONLY pairs allowed to carry a
# secondary tag (a course on A that genuinely teaches part of B).
OVERLAP = {
    "comp_nat_accounts_001": ["comp_price_stats_003", "comp_gdp_nowcast_011", "comp_industry_stats_010"],
    "comp_survey_design_002": ["comp_statistical_sw_030", "comp_r_analytics_018", "comp_poverty_014"],
    "comp_price_stats_003": ["comp_index_numbers_004", "comp_nat_accounts_001"],
    "comp_index_numbers_004": ["comp_price_stats_003", "comp_industry_stats_010"],
    "comp_ml_stats_005": ["comp_python_stats_017", "comp_big_data_006"],
    "comp_big_data_006": ["comp_db_design_029", "comp_cloud_infra_027", "comp_ml_stats_005"],
    "comp_econ_census_007": ["comp_survey_design_002", "comp_project_mgmt_024"],
    "comp_dem_analysis_008": ["comp_survey_design_002"],
    "comp_agri_stats_009": ["comp_spatial_stat_012", "comp_survey_design_002"],
    "comp_industry_stats_010": ["comp_index_numbers_004", "comp_survey_design_002"],
    "comp_gdp_nowcast_011": ["comp_time_series_013", "comp_nat_accounts_001"],
    "comp_spatial_stat_012": ["comp_agri_stats_009", "comp_data_viz_019"],
    "comp_time_series_013": ["comp_r_analytics_018", "comp_gdp_nowcast_011"],
    "comp_poverty_014": ["comp_survey_design_002", "comp_sdg_monitor_015"],
    "comp_sdg_monitor_015": ["comp_poverty_014", "comp_data_viz_019"],
    "comp_data_gov_016": ["comp_data_privacy_026"],
    "comp_python_stats_017": ["comp_ml_stats_005", "comp_data_viz_019"],
    "comp_r_analytics_018": ["comp_time_series_013", "comp_data_viz_019"],
    "comp_data_viz_019": ["comp_report_writing_020", "comp_python_stats_017"],
    "comp_report_writing_020": ["comp_comm_032", "comp_data_viz_019"],
    "comp_procurement_021": ["comp_public_fin_025"],
    "comp_rtt_022": ["comp_citizen_039"],
    "comp_e_gov_023": ["comp_api_int_028", "comp_citizen_039"],
    "comp_project_mgmt_024": ["comp_leadership_032"],
    "comp_public_fin_025": ["comp_procurement_021"],
    "comp_data_privacy_026": ["comp_data_gov_016"],
    "comp_cloud_infra_027": ["comp_big_data_006"],
    "comp_api_int_028": ["comp_e_gov_023"],
    "comp_db_design_029": ["comp_big_data_006"],
    "comp_statistical_sw_030": ["comp_survey_design_002"],
    "comp_strategic_031": ["comp_decision_037"],
    "comp_leadership_032": ["comp_change_mgmt_035", "comp_collab_036"],
    "comp_comm_032": ["comp_collab_036", "comp_citizen_039"],
    "comp_prob_solve_033": ["comp_innov_038", "comp_decision_037"],
    "comp_integrity_034": [],
    "comp_change_mgmt_035": ["comp_leadership_032"],
    "comp_collab_036": ["comp_comm_032"],
    "comp_decision_037": ["comp_strategic_031", "comp_prob_solve_033"],
    "comp_innov_038": ["comp_prob_solve_033"],
    "comp_citizen_039": ["comp_comm_032"],
}

# Deliberate catalogue holes (A2) — kept so stretch steps and the coverage-gap
# detector can be demonstrated. Documented in data/README.md.
LADDER_HOLES = {
    "comp_gdp_nowcast_011":  [5],
    "comp_rtt_022":          [5],
    "comp_cloud_infra_027":  [5],
    "comp_citizen_039":      [5],
    "comp_spatial_stat_012": [3],
    "comp_procurement_021":  [3],
}

# ─────────────────────────────────────────────────────────────────────────────
# Course formats (A3). Hours ranges by format; higher levels lean longer.
# ─────────────────────────────────────────────────────────────────────────────
FORMATS = {
    #  name                 hours       modality options (weights)
    "micro_learning":    ((0.5, 2.0),  {"self_paced": 1.0}),
    "self_paced_course": ((2.0, 8.0),  {"self_paced": 1.0}),
    "nssta_workshop":    ((6.0, 16.0), {"virtual_lab": 0.6, "classroom": 0.4}),
    "tpac_programme":    ((20.0, 60.0), {"classroom": 0.8, "virtual_lab": 0.2}),
}
# P(format | level)
FORMAT_BY_LEVEL = {
    1: {"micro_learning": 0.45, "self_paced_course": 0.50, "nssta_workshop": 0.05},
    2: {"micro_learning": 0.20, "self_paced_course": 0.65, "nssta_workshop": 0.15},
    3: {"micro_learning": 0.08, "self_paced_course": 0.56, "nssta_workshop": 0.30, "tpac_programme": 0.06},
    4: {"self_paced_course": 0.43, "nssta_workshop": 0.35, "tpac_programme": 0.22},
    5: {"self_paced_course": 0.25, "nssta_workshop": 0.35, "tpac_programme": 0.40},
}
FORMAT_LABEL = {
    "micro_learning": "micro-learning module",
    "self_paced_course": "self-paced iGOT course",
    "nssta_workshop": "NSSTA workshop",
    "tpac_programme": "NSSTA TPAC certification programme",
}

NSSTA_CREATOR = "National Statistical Systems Training Academy (NSSTA)"
IGOT_PROVIDERS = [
    ("Ministry of Statistics and Programme Implementation", "igot-mdo-mospi-01"),
    ("iGOT Karmayogi Platform", "igot-mdo-karmayogi-00"),
    ("Department of Personnel and Training", "igot-mdo-dopt-04"),
    ("Institute of Secretariat Training and Management", "igot-mdo-istm-05"),
]

# ─────────────────────────────────────────────────────────────────────────────
# GSBPM v5.1 sub-processes (the user asked for "GSBPM 5.2"; v5.1 (2019) is the
# latest version whose sub-process list could be confirmed — see the decisions
# log). "OA.*" are overarching processes GSBPM describes but does not number.
# ─────────────────────────────────────────────────────────────────────────────
GSBPM_PHASES = {
    "1": "Specify Needs", "2": "Design", "3": "Build", "4": "Collect",
    "5": "Process", "6": "Analyse", "7": "Disseminate", "8": "Evaluate",
    "OA": "Overarching processes",
}
GSBPM_SUBPROCESSES = {
    "1.1": "Identify needs", "1.2": "Consult and confirm needs", "1.3": "Establish output objectives",
    "1.4": "Identify concepts", "1.5": "Check data availability", "1.6": "Prepare and submit business case",
    "2.1": "Design outputs", "2.2": "Design variable descriptions", "2.3": "Design collection",
    "2.4": "Design frame and sample", "2.5": "Design processing and analysis",
    "2.6": "Design production systems and workflow",
    "3.1": "Reuse or build collection instruments", "3.2": "Reuse or build processing and analysis components",
    "3.3": "Reuse or build dissemination components", "3.4": "Configure workflows",
    "3.5": "Test production systems", "3.6": "Test statistical business process", "3.7": "Finalise production systems",
    "4.1": "Create frame and select sample", "4.2": "Set up collection", "4.3": "Run collection",
    "4.4": "Finalise collection",
    "5.1": "Integrate data", "5.2": "Classify and code", "5.3": "Review and validate", "5.4": "Edit and impute",
    "5.5": "Derive new variables and units", "5.6": "Calculate weights", "5.7": "Calculate aggregates",
    "5.8": "Finalise data files",
    "6.1": "Prepare draft outputs", "6.2": "Validate outputs", "6.3": "Interpret and explain outputs",
    "6.4": "Apply disclosure control", "6.5": "Finalise outputs",
    "7.1": "Update output systems", "7.2": "Produce dissemination products",
    "7.3": "Manage release of dissemination products", "7.4": "Promote dissemination products",
    "7.5": "Manage user support",
    "8.1": "Gather evaluation inputs", "8.2": "Conduct evaluation", "8.3": "Agree an action plan",
    "OA.QM": "Quality management", "OA.MM": "Metadata management", "OA.DM": "Data management",
    "OA.PM": "Strategic, people and programme management", "OA.FM": "Financial and procurement management",
    "OA.SM": "Statistical framework management",
}

# FRAC competency → GSBPM sub-processes where the competency is exercised.
GSBPM_MAP = {
    "comp_nat_accounts_001":  ["1.4", "5.1", "5.5", "5.7", "6.1", "6.2", "6.3", "OA.SM"],
    "comp_survey_design_002": ["2.3", "2.4", "4.1", "5.6", "6.2"],
    "comp_price_stats_003":   ["2.4", "4.3", "5.3", "5.7", "6.1", "6.2"],
    "comp_index_numbers_004": ["2.5", "5.5", "5.7", "6.2"],
    "comp_ml_stats_005":      ["3.2", "5.2", "5.4"],
    "comp_big_data_006":      ["1.5", "4.3", "5.1"],
    "comp_econ_census_007":   ["2.3", "4.1", "4.2", "4.3", "4.4"],
    "comp_dem_analysis_008":  ["5.5", "6.1", "6.3"],
    "comp_agri_stats_009":    ["4.3", "5.7", "6.1"],
    "comp_industry_stats_010": ["2.4", "4.3", "5.3", "5.7", "6.1"],
    "comp_gdp_nowcast_011":   ["5.7", "6.1", "6.3"],
    "comp_spatial_stat_012":  ["2.4", "4.1", "7.2"],
    "comp_time_series_013":   ["5.5", "6.2", "6.3"],
    "comp_poverty_014":       ["5.5", "6.1", "6.3"],
    "comp_sdg_monitor_015":   ["1.1", "1.5", "6.1", "7.2"],
    "comp_data_gov_016":      ["5.3", "8.2", "OA.QM", "OA.MM", "OA.DM"],
    "comp_python_stats_017":  ["3.2", "5.3", "5.4", "5.7"],
    "comp_r_analytics_018":   ["5.4", "5.6", "6.1"],
    "comp_data_viz_019":      ["7.2", "6.3"],
    "comp_report_writing_020": ["6.5", "7.2"],
    "comp_procurement_021":   ["OA.FM"],
    "comp_rtt_022":           ["7.5"],
    "comp_e_gov_023":         ["3.3", "7.1"],
    "comp_project_mgmt_024":  ["1.6", "2.6", "4.2", "OA.PM"],
    "comp_public_fin_025":    ["1.6", "OA.FM"],
    "comp_data_privacy_026":  ["6.4", "5.8", "OA.DM"],
    "comp_cloud_infra_027":   ["3.4", "3.5", "3.7"],
    "comp_api_int_028":       ["3.3", "7.1"],
    "comp_db_design_029":     ["3.2", "5.8", "OA.DM"],
    "comp_statistical_sw_030": ["5.4", "5.6", "5.7"],
    "comp_strategic_031":     ["1.1", "1.3", "8.3", "OA.PM"],
    "comp_leadership_032":    ["4.3", "OA.PM"],
    "comp_comm_032":          ["1.2", "7.4", "7.5"],
    "comp_prob_solve_033":    ["5.3", "6.2", "8.2"],
    "comp_integrity_034":     ["6.4", "7.3", "OA.QM"],
    "comp_change_mgmt_035":   ["3.6", "8.3", "OA.PM"],
    "comp_collab_036":        ["1.2", "4.2", "5.1"],
    "comp_decision_037":      ["1.6", "6.5", "8.3"],
    "comp_innov_038":         ["1.5", "3.2", "8.2"],
    "comp_citizen_039":       ["7.4", "7.5"],
}

# ─────────────────────────────────────────────────────────────────────────────
# Offices (B1/B2). officer-hour profile per sub-process this cycle is drawn
# around these relative weights. `products` are statistical products (B8).
# ─────────────────────────────────────────────────────────────────────────────
OFFICES = [
    # id, division name, location, legacy departments that map here, products,
    # {sub-process: relative weight}, core domain competencies (weight)
    ("off_nad", "National Accounts Division", "New Delhi",
     ["National Statistical Office (NSO)"], ["NAS"],
     {"1.4": 2, "1.5": 3, "5.1": 10, "5.5": 8, "5.7": 14, "6.1": 10, "6.2": 8, "6.3": 7, "6.5": 4,
      "7.2": 3, "OA.SM": 4, "OA.PM": 3, "OA.QM": 2},
     {"comp_nat_accounts_001": 5, "comp_gdp_nowcast_011": 3, "comp_price_stats_003": 2,
      "comp_time_series_013": 2, "comp_index_numbers_004": 1, "comp_industry_stats_010": 1}),
    ("off_psd", "Price Statistics Division", "New Delhi",
     ["Price Statistics Division"], ["CPI"],
     {"2.4": 3, "4.2": 3, "4.3": 9, "5.3": 12, "5.7": 12, "6.1": 8, "6.2": 7, "7.2": 4, "7.3": 3,
      "OA.QM": 3, "OA.PM": 2, "1.5": 2},
     {"comp_price_stats_003": 5, "comp_index_numbers_004": 4, "comp_big_data_006": 2,
      "comp_time_series_013": 1, "comp_survey_design_002": 1}),
    ("off_esd", "Economic Statistics Division", "New Delhi",
     ["Economic Statistics Division", "Central Statistics Office (CSO)"], ["IIP", "Economic Census"],
     {"2.3": 4, "4.1": 5, "4.2": 5, "4.3": 8, "4.4": 4, "5.3": 7, "5.7": 9, "6.1": 7, "6.2": 5,
      "7.2": 3, "OA.PM": 3, "OA.QM": 2},
     {"comp_econ_census_007": 4, "comp_index_numbers_004": 3, "comp_industry_stats_010": 2,
      "comp_survey_design_002": 2, "comp_time_series_013": 1}),
    ("off_isw", "Industrial Statistics Wing (ASI)", "Kolkata",
     ["Industrial Statistics Division"], ["ASI"],
     {"2.4": 3, "4.1": 5, "4.3": 10, "4.4": 5, "5.3": 12, "5.4": 8, "5.7": 9, "6.1": 6, "6.2": 4,
      "7.2": 2, "OA.QM": 3, "OA.PM": 2},
     {"comp_industry_stats_010": 5, "comp_survey_design_002": 2, "comp_statistical_sw_030": 2,
      "comp_index_numbers_004": 1, "comp_econ_census_007": 1}),
    ("off_ssd", "Social Statistics Division", "New Delhi",
     ["Social Statistics Division"], ["SDG-NIF", "EnviStats"],
     {"1.1": 4, "1.2": 3, "1.5": 6, "5.1": 7, "5.5": 6, "6.1": 10, "6.3": 8, "7.2": 9, "7.4": 3,
      "OA.MM": 3, "OA.PM": 2},
     {"comp_sdg_monitor_015": 5, "comp_poverty_014": 3, "comp_dem_analysis_008": 3,
      "comp_data_viz_019": 1}),
    ("off_sdrd", "Survey Design & Research Division", "Kolkata",
     ["National Sample Survey Office (NSSO)"], ["PLFS", "HCES"],
     {"1.4": 3, "2.1": 4, "2.2": 5, "2.3": 8, "2.4": 11, "2.5": 7, "3.1": 5, "5.6": 8, "6.2": 5,
      "6.3": 4, "8.2": 3, "OA.MM": 2},
     {"comp_survey_design_002": 5, "comp_poverty_014": 2, "comp_statistical_sw_030": 2,
      "comp_r_analytics_018": 2, "comp_agri_stats_009": 1}),
    ("off_fod_north", "Field Operations Division (Northern Zone)", "Lucknow",
     ["National Sample Survey Office (NSSO)"], ["PLFS", "HCES", "ASI"],
     {"4.1": 6, "4.2": 10, "4.3": 30, "4.4": 10, "5.3": 6, "OA.PM": 4, "OA.QM": 3},
     {"comp_survey_design_002": 4, "comp_econ_census_007": 2, "comp_agri_stats_009": 2,
      "comp_spatial_stat_012": 1}),
    ("off_fod_east", "Field Operations Division (Eastern Zone)", "Patna",
     ["National Sample Survey Office (NSSO)"], ["PLFS", "HCES", "CPI"],
     {"4.1": 6, "4.2": 10, "4.3": 30, "4.4": 10, "5.3": 6, "OA.PM": 4, "OA.QM": 3},
     {"comp_survey_design_002": 4, "comp_econ_census_007": 2, "comp_price_stats_003": 1,
      "comp_spatial_stat_012": 2}),
    ("off_dpd", "Data Processing & IT Division", "New Delhi",
     ["IT & Data Management Division"], ["PLFS", "HCES", "ASI"],
     {"3.1": 5, "3.2": 10, "3.4": 5, "3.5": 5, "3.7": 3, "5.1": 8, "5.2": 7, "5.4": 6, "5.8": 7,
      "7.1": 5, "OA.DM": 6},
     {"comp_big_data_006": 3, "comp_ml_stats_005": 3, "comp_survey_design_002": 1}),
    ("off_capd", "Coordination & Publication Division", "New Delhi",
     ["Ministry of Statistics and Programme Implementation (MoSPI)"], ["NAS", "SDG-NIF"],
     {"1.1": 3, "1.2": 4, "6.5": 6, "7.2": 12, "7.3": 8, "7.4": 7, "7.5": 9, "OA.PM": 5, "OA.FM": 4},
     {"comp_sdg_monitor_015": 2, "comp_nat_accounts_001": 1}),
    ("off_dqad", "Data Quality Assurance Division", "New Delhi",
     ["Ministry of Statistics and Programme Implementation (MoSPI)", "Central Statistics Office (CSO)"],
     ["PLFS", "CPI", "ASI"],
     {"5.3": 12, "6.2": 10, "8.1": 7, "8.2": 10, "8.3": 5, "OA.QM": 10, "OA.MM": 5},
     {"comp_survey_design_002": 3, "comp_price_stats_003": 1, "comp_industry_stats_010": 1}),
    ("off_nssta", "National Statistical Systems Training Academy", "Greater Noida",
     ["Training & Capacity Building Division"], [],
     {"1.1": 3, "1.3": 3, "8.1": 6, "8.2": 8, "8.3": 4, "OA.PM": 12, "OA.FM": 3, "7.5": 3},
     {"comp_survey_design_002": 2, "comp_nat_accounts_001": 1, "comp_price_stats_003": 1,
      "comp_sdg_monitor_015": 1}),
]

# Functional competencies an office leans on (in addition to the tier pools).
OFFICE_FUNCTIONAL = {
    "off_nad": ["comp_r_analytics_018", "comp_statistical_sw_030", "comp_report_writing_020", "comp_data_gov_016"],
    "off_psd": ["comp_python_stats_017", "comp_db_design_029", "comp_report_writing_020", "comp_data_gov_016"],
    "off_esd": ["comp_statistical_sw_030", "comp_project_mgmt_024", "comp_report_writing_020", "comp_db_design_029"],
    "off_isw": ["comp_statistical_sw_030", "comp_db_design_029", "comp_data_gov_016", "comp_python_stats_017"],
    "off_ssd": ["comp_data_viz_019", "comp_report_writing_020", "comp_r_analytics_018", "comp_data_gov_016"],
    "off_sdrd": ["comp_r_analytics_018", "comp_statistical_sw_030", "comp_python_stats_017", "comp_data_gov_016"],
    "off_fod_north": ["comp_project_mgmt_024", "comp_e_gov_023", "comp_data_privacy_026", "comp_procurement_021"],
    "off_fod_east": ["comp_project_mgmt_024", "comp_e_gov_023", "comp_data_privacy_026", "comp_procurement_021"],
    "off_dpd": ["comp_python_stats_017", "comp_db_design_029", "comp_cloud_infra_027", "comp_api_int_028",
                "comp_data_privacy_026"],
    "off_capd": ["comp_report_writing_020", "comp_data_viz_019", "comp_rtt_022", "comp_public_fin_025",
                 "comp_e_gov_023"],
    "off_dqad": ["comp_data_gov_016", "comp_statistical_sw_030", "comp_data_privacy_026", "comp_report_writing_020"],
    "off_nssta": ["comp_project_mgmt_024", "comp_public_fin_025", "comp_procurement_021", "comp_e_gov_023"],
}

BEHAVIOURAL_BY_TIER = {
    "TIER4_JUNIOR": ["comp_collab_036", "comp_comm_032", "comp_integrity_034", "comp_prob_solve_033",
                     "comp_citizen_039"],
    "TIER3_MID":    ["comp_prob_solve_033", "comp_comm_032", "comp_collab_036", "comp_integrity_034",
                     "comp_decision_037", "comp_innov_038"],
    "TIER2_SENIOR": ["comp_leadership_032", "comp_decision_037", "comp_change_mgmt_035", "comp_comm_032",
                     "comp_innov_038"],
    "TIER1_APEX":   ["comp_strategic_031", "comp_leadership_032", "comp_change_mgmt_035", "comp_decision_037"],
}

# Designations by tier (ISS / SSS cadres).
DESIGNATIONS = {
    "TIER1_APEX":   ["Additional Director General", "Deputy Director General"],
    "TIER2_SENIOR": ["Director", "Joint Director"],
    "TIER3_MID":    ["Deputy Director", "Assistant Director", "Senior Statistical Officer"],
    "TIER4_JUNIOR": ["Junior Statistical Officer", "Statistical Investigator Grade-I"],
}

# P(requiredLevel | tier) — A1: junior mostly L2–L3, senior L3–L5.
REQUIRED_LEVEL_BY_TIER = {
    "TIER4_JUNIOR": {2: 0.55, 3: 0.40, 1: 0.05},
    "TIER3_MID":    {3: 0.55, 2: 0.20, 4: 0.25},
    "TIER2_SENIOR": {4: 0.55, 3: 0.25, 5: 0.20},
    "TIER1_APEX":   {4: 0.45, 5: 0.45, 3: 0.10},
}

# Statistical products (B8 capability risk).
PRODUCTS = {
    "NAS": "National Accounts Statistics (GDP)",
    "CPI": "Consumer Price Index",
    "IIP": "Index of Industrial Production",
    "ASI": "Annual Survey of Industries",
    "PLFS": "Periodic Labour Force Survey",
    "HCES": "Household Consumption Expenditure Survey",
    "SDG-NIF": "SDG National Indicator Framework progress report",
    "EnviStats": "EnviStats India",
    "Economic Census": "Economic Census",
}
# Competencies critical to producing each product (B8).
PRODUCT_CRITICAL = {
    "NAS": ["comp_nat_accounts_001", "comp_gdp_nowcast_011", "comp_index_numbers_004"],
    "CPI": ["comp_price_stats_003", "comp_index_numbers_004"],
    "IIP": ["comp_index_numbers_004", "comp_industry_stats_010"],
    "ASI": ["comp_industry_stats_010", "comp_survey_design_002"],
    "PLFS": ["comp_survey_design_002", "comp_statistical_sw_030"],
    "HCES": ["comp_survey_design_002", "comp_poverty_014"],
    "SDG-NIF": ["comp_sdg_monitor_015", "comp_data_viz_019"],
    "EnviStats": ["comp_sdg_monitor_015"],
    "Economic Census": ["comp_econ_census_007", "comp_survey_design_002"],
}

# Short subject names used in course titles.
SHORT_NAMES = {
    "comp_nat_accounts_001": "National Accounts", "comp_survey_design_002": "Survey Sampling",
    "comp_price_stats_003": "Price Statistics", "comp_index_numbers_004": "Index Numbers",
    "comp_ml_stats_005": "Machine Learning for Official Statistics",
    "comp_big_data_006": "Big Data for Official Statistics", "comp_econ_census_007": "Economic Census Operations",
    "comp_dem_analysis_008": "Demographic Analysis", "comp_agri_stats_009": "Agricultural Statistics",
    "comp_industry_stats_010": "Industrial Statistics (ASI)", "comp_gdp_nowcast_011": "GDP Nowcasting",
    "comp_spatial_stat_012": "GIS for Surveys", "comp_time_series_013": "Time Series and Seasonal Adjustment",
    "comp_poverty_014": "Poverty Measurement", "comp_sdg_monitor_015": "SDG Monitoring",
    "comp_data_gov_016": "Data Governance and Quality", "comp_python_stats_017": "Python for Statistics",
    "comp_r_analytics_018": "R for Statistical Analysis", "comp_data_viz_019": "Data Visualisation",
    "comp_report_writing_020": "Statistical Report Writing", "comp_procurement_021": "Public Procurement (GFR)",
    "comp_rtt_022": "Right to Information", "comp_e_gov_023": "e-Governance",
    "comp_project_mgmt_024": "Project Management", "comp_public_fin_025": "Public Financial Management",
    "comp_data_privacy_026": "Data Privacy and Security", "comp_cloud_infra_027": "Cloud for Statistical Systems",
    "comp_api_int_028": "APIs and Interoperability", "comp_db_design_029": "SQL and Database Design",
    "comp_statistical_sw_030": "SPSS and SAS", "comp_strategic_031": "Strategic Thinking",
    "comp_leadership_032": "Leadership", "comp_comm_032": "Communication and Stakeholder Engagement",
    "comp_prob_solve_033": "Problem Solving", "comp_integrity_034": "Integrity and Ethics",
    "comp_change_mgmt_035": "Change Management", "comp_collab_036": "Collaboration",
    "comp_decision_037": "Decision Making", "comp_innov_038": "Innovation",
    "comp_citizen_039": "Citizen-Centric Service",
}

# Crosswalk rules: iGOT dictionary competency name (competencies.json, CID ids)
# → catalogue FRAC id. First match wins. These are keyword rules, NOT human
# confirmations, so every mapping is written with confirmed=false.
CROSSWALK_RULES = [
    (r"national account|\bgdp\b|gross domestic", "comp_nat_accounts_001"),
    (r"nowcast", "comp_gdp_nowcast_011"),
    (r"index number", "comp_index_numbers_004"),
    (r"\bprice|inflation", "comp_price_stats_003"),
    (r"sampl|survey", "comp_survey_design_002"),
    (r"machine learning|artificial intelligence|\bai\b|deep learning", "comp_ml_stats_005"),
    (r"big data", "comp_big_data_006"),
    (r"census", "comp_econ_census_007"),
    (r"demograph|population", "comp_dem_analysis_008"),
    (r"agricultur|\bcrop|farm|horticult|livestock", "comp_agri_stats_009"),
    (r"industrial statist|\bindustr", "comp_industry_stats_010"),
    (r"\bgis\b|geospatial|spatial|remote sensing|geographic", "comp_spatial_stat_012"),
    (r"time series|seasonal", "comp_time_series_013"),
    (r"poverty|welfare|inequalit", "comp_poverty_014"),
    (r"sustainable development|\bsdg", "comp_sdg_monitor_015"),
    (r"data governance|data quality|quality assurance|data management|metadata", "comp_data_gov_016"),
    (r"python|programming|coding", "comp_python_stats_017"),
    (r"statistical analysis|data analy|analytics|econometric", "comp_r_analytics_018"),
    (r"visuali|dashboard", "comp_data_viz_019"),
    (r"report writing|drafting|noting|writing", "comp_report_writing_020"),
    (r"procurement|tender|contract|\bgem\b|purchase", "comp_procurement_021"),
    (r"right to information|\brti\b|transparen", "comp_rtt_022"),
    (r"e-governance|e-office|digital|e-gov", "comp_e_gov_023"),
    (r"project management|programme management|project", "comp_project_mgmt_024"),
    (r"budget|financial management|public finance|fiscal|finance", "comp_public_fin_025"),
    (r"privacy|cyber|information security|data protection", "comp_data_privacy_026"),
    (r"cloud", "comp_cloud_infra_027"),
    (r"\bapi\b|interoperab|integration", "comp_api_int_028"),
    (r"database|\bsql\b", "comp_db_design_029"),
    (r"\bspss\b|\bsas\b|statistical software|\bstata\b", "comp_statistical_sw_030"),
    (r"strateg|vision", "comp_strategic_031"),
    (r"leadership|team management|people management|leading", "comp_leadership_032"),
    (r"communicat|stakeholder|presentation|public speaking", "comp_comm_032"),
    (r"problem solving|critical thinking|analytical thinking|reasoning", "comp_prob_solve_033"),
    (r"integrity|ethic|values|probity", "comp_integrity_034"),
    (r"change management|adaptab|agility", "comp_change_mgmt_035"),
    (r"collaborat|teamwork|interpersonal|networking|coordination", "comp_collab_036"),
    (r"decision", "comp_decision_037"),
    (r"innovat|creativ|design thinking", "comp_innov_038"),
    (r"citizen|service delivery|grievance|customer", "comp_citizen_039"),
]
