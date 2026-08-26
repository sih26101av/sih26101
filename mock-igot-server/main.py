from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mock iGOT Karmayogi API", description="Standalone mock server for SIH MoSPI Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# FRAC DICTIONARY --- 15 Competencies (Framework of Roles, Activities & Competencies)
# =============================================================================
MOCK_FRAC_DICTIONARY = [
    {"competency_id": "FRAC-STAT-001", "name": "National Accounts & GDP Estimation", "type": "Domain", "description": "Understanding of SNA 2008, GDP compilation methodologies, input-output tables, and supply-use frameworks as practiced by NSO India."},
    {"competency_id": "FRAC-STAT-002", "name": "Survey Methodology & Sampling Design", "type": "Domain", "description": "Proficiency in probability sampling theory, stratified/cluster/multistage sampling, NSSO survey design, questionnaire design, and estimation under complex survey structures."},
    {"competency_id": "FRAC-STAT-003", "name": "Statistical Data Quality & Validation", "type": "Domain", "description": "Ability to apply data quality frameworks (SDMX, IMF DQAF), conduct editing and imputation, manage outliers, and validate disseminated statistical products."},
    {"competency_id": "FRAC-STAT-004", "name": "Price Statistics & Index Numbers", "type": "Domain", "description": "Understanding of CPI, WPI, PPI compilation, Laspeyres/Paasche formulas, and deflation methods."},
    {"competency_id": "FRAC-STAT-005", "name": "Econometrics & Time Series Analysis", "type": "Domain", "description": "Application of regression models, VAR, ARIMA, cointegration tests, seasonal adjustment (X-13ARIMA-SEATS), and forecasting for official economic statistics."},
    {"competency_id": "FRAC-TECH-006", "name": "Data Visualization & Dashboarding", "type": "Functional", "description": "Designing interactive charts, dashboards, and infographics using Power BI, Tableau, and Python (Matplotlib, Seaborn, Plotly) to communicate government data."},
    {"competency_id": "FRAC-TECH-007", "name": "Data Privacy, Security & Ethics", "type": "Functional", "description": "Knowledge of PDPB 2023, statistical confidentiality obligations, anonymisation techniques, data sharing agreements, and ethical use of administrative data."},
    {"competency_id": "FRAC-TECH-008", "name": "Machine Learning for Official Statistics", "type": "Functional", "description": "Application of supervised/unsupervised ML algorithms for classification, nowcasting, text mining administrative records, and automating statistical production pipelines."},
    {"competency_id": "FRAC-TECH-009", "name": "Database Management & SQL", "type": "Functional", "description": "Proficiency in relational databases (PostgreSQL, MySQL), SQL query optimisation, data warehousing, and ETL pipeline design for statistical bureaux."},
    {"competency_id": "FRAC-TECH-010", "name": "Geospatial Data Analysis & GIS", "type": "Functional", "description": "Use of GIS tools (QGIS, ArcGIS), spatial statistics, satellite imagery analysis, and integration of geographic data layers with census and survey data."},
    {"competency_id": "FRAC-GOV-011", "name": "Public Financial Management & Government Accounting", "type": "Functional", "description": "Understanding of GFR 2017, PFMS, budget preparation, appropriation accounts, and fiscal reporting under Government Accounting Standards."},
    {"competency_id": "FRAC-GOV-012", "name": "Public Procurement & Contract Management", "type": "Functional", "description": "Knowledge of GFR Chapter 6, CVC guidelines, GeM portal operations, tender evaluation, and vendor management in government procurement processes."},
    {"competency_id": "FRAC-BEHAV-013", "name": "Leadership & Team Management", "type": "Behavioural", "description": "Ability to motivate cross-functional teams, manage performance, resolve conflicts, delegate effectively, and lead change initiatives within a government ministry."},
    {"competency_id": "FRAC-BEHAV-014", "name": "Policy Analysis & Strategic Thinking", "type": "Behavioural", "description": "Capacity to analyse complex policy problems, synthesise evidence from multiple data sources, evaluate trade-offs, and formulate evidence-based recommendations for senior leadership."},
    {"competency_id": "FRAC-BEHAV-015", "name": "Communication & Report Writing", "type": "Behavioural", "description": "Drafting clear policy briefs, press notes, cabinet notes, statistical press releases, and stakeholder presentations adhering to Government of India communication standards."},
]

# =============================================================================
# CBP CATALOG --- 35 Competency Building Products
# =============================================================================
MOCK_CBP_CATALOG = [
    # --- STATISTICAL / TECHNICAL CBPs ---
    {"igot_course_id": "CRS-IGOT-5521", "course_title": "National Accounts Statistics: SNA 2008 & GDP Estimation Methods", "provider_name": "NSSTA", "duration_minutes": 2400, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-STAT-001", "skill_name": "National Accounts & GDP Estimation", "proficiency_taught": 4}, {"external_skill_id": "FRAC-STAT-003", "skill_name": "Statistical Data Quality & Validation", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-8812", "course_title": "Survey Design and Sampling Methodologies for Large-Scale Household Surveys", "provider_name": "NSSTA", "duration_minutes": 1800, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-STAT-002", "skill_name": "Survey Methodology & Sampling Design", "proficiency_taught": 4}]},
    {"igot_course_id": "CRS-IGOT-7734", "course_title": "Applied Machine Learning for Official Statistics", "provider_name": "Capacity Building Commission", "duration_minutes": 2700, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-TECH-008", "skill_name": "Machine Learning for Official Statistics", "proficiency_taught": 3}, {"external_skill_id": "FRAC-STAT-003", "skill_name": "Statistical Data Quality & Validation", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-4422", "course_title": "Advanced Data Visualization with Python & Power BI", "provider_name": "Capacity Building Commission", "duration_minutes": 1200, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-TECH-006", "skill_name": "Data Visualization & Dashboarding", "proficiency_taught": 3}]},
    {"igot_course_id": "CRS-IGOT-3310", "course_title": "CPI & WPI Compilation: Concepts, Methodology and International Best Practices", "provider_name": "NSSTA", "duration_minutes": 960, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-STAT-004", "skill_name": "Price Statistics & Index Numbers", "proficiency_taught": 3}, {"external_skill_id": "FRAC-STAT-001", "skill_name": "National Accounts & GDP Estimation", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-6601", "course_title": "Econometrics for Policy: Regression, Panel Data & Causal Inference", "provider_name": "NSSTA", "duration_minutes": 3000, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-STAT-005", "skill_name": "Econometrics & Time Series Analysis", "proficiency_taught": 4}, {"external_skill_id": "FRAC-TECH-008", "skill_name": "Machine Learning for Official Statistics", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-6602", "course_title": "R for Official Statistics: From Data Wrangling to Production", "provider_name": "Capacity Building Commission", "duration_minutes": 1800, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-STAT-005", "skill_name": "Econometrics & Time Series Analysis", "proficiency_taught": 3}, {"external_skill_id": "FRAC-STAT-002", "skill_name": "Survey Methodology & Sampling Design", "proficiency_taught": 2}, {"external_skill_id": "FRAC-TECH-006", "skill_name": "Data Visualization & Dashboarding", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-9100", "course_title": "Data Quality Assessment and SDMX Standards for NSOs", "provider_name": "NSSTA", "duration_minutes": 1080, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-STAT-003", "skill_name": "Statistical Data Quality & Validation", "proficiency_taught": 4}]},
    {"igot_course_id": "CRS-IGOT-9200", "course_title": "Big Data & Administrative Records for Statistical Production", "provider_name": "Capacity Building Commission", "duration_minutes": 900, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-TECH-008", "skill_name": "Machine Learning for Official Statistics", "proficiency_taught": 2}, {"external_skill_id": "FRAC-TECH-009", "skill_name": "Database Management & SQL", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-9300", "course_title": "SQL & PostgreSQL for Government Data Management", "provider_name": "Capacity Building Commission", "duration_minutes": 1200, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-TECH-009", "skill_name": "Database Management & SQL", "proficiency_taught": 3}]},
    {"igot_course_id": "CRS-IGOT-9400", "course_title": "Geospatial Analysis for Poverty and Development Indicators", "provider_name": "NSSTA", "duration_minutes": 1440, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-TECH-010", "skill_name": "Geospatial Data Analysis & GIS", "proficiency_taught": 3}, {"external_skill_id": "FRAC-STAT-002", "skill_name": "Survey Methodology & Sampling Design", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-9500", "course_title": "Seasonal Adjustment of Economic Time Series Using X-13ARIMA-SEATS", "provider_name": "NSSTA", "duration_minutes": 960, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-STAT-005", "skill_name": "Econometrics & Time Series Analysis", "proficiency_taught": 4}]},
    {"igot_course_id": "CRS-IGOT-9600", "course_title": "NLP for Automating Statistical Press Releases", "provider_name": "Capacity Building Commission", "duration_minutes": 720, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-TECH-008", "skill_name": "Machine Learning for Official Statistics", "proficiency_taught": 3}, {"external_skill_id": "FRAC-BEHAV-015", "skill_name": "Communication & Report Writing", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-9700", "course_title": "Tableau for Government: Building Ministerial Performance Dashboards", "provider_name": "iGOT Karmayogi", "duration_minutes": 660, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-TECH-006", "skill_name": "Data Visualization & Dashboarding", "proficiency_taught": 4}]},
    {"igot_course_id": "CRS-IGOT-9800", "course_title": "Poverty Measurement: Methodological Frameworks and Indian Experience", "provider_name": "NSSTA", "duration_minutes": 1560, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-STAT-002", "skill_name": "Survey Methodology & Sampling Design", "proficiency_taught": 3}, {"external_skill_id": "FRAC-STAT-001", "skill_name": "National Accounts & GDP Estimation", "proficiency_taught": 2}, {"external_skill_id": "FRAC-BEHAV-014", "skill_name": "Policy Analysis & Strategic Thinking", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-9850", "course_title": "Input-Output Analysis and Supply-Use Tables for Economic Planning", "provider_name": "NSSTA", "duration_minutes": 2160, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-STAT-001", "skill_name": "National Accounts & GDP Estimation", "proficiency_taught": 5}, {"external_skill_id": "FRAC-STAT-005", "skill_name": "Econometrics & Time Series Analysis", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1017", "course_title": "Python for Beginners: Data Wrangling with Pandas for Government Analysts", "provider_name": "iGOT Karmayogi", "duration_minutes": 900, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-TECH-009", "skill_name": "Database Management & SQL", "proficiency_taught": 2}, {"external_skill_id": "FRAC-STAT-003", "skill_name": "Statistical Data Quality & Validation", "proficiency_taught": 1}]},
    {"igot_course_id": "CRS-IGOT-1018", "course_title": "Advanced GIS: Drone Surveys, Remote Sensing & Satellite-Based Census Mapping", "provider_name": "NSSTA", "duration_minutes": 1800, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-TECH-010", "skill_name": "Geospatial Data Analysis & GIS", "proficiency_taught": 5}, {"external_skill_id": "FRAC-STAT-002", "skill_name": "Survey Methodology & Sampling Design", "proficiency_taught": 2}]},
    # --- FUNCTIONAL / GOVERNANCE / BEHAVIOURAL CBPs ---
    {"igot_course_id": "CRS-IGOT-9999", "course_title": "Data Privacy, Confidentiality and the Personal Data Protection Act", "provider_name": "DoPT", "duration_minutes": 900, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-TECH-007", "skill_name": "Data Privacy, Security & Ethics", "proficiency_taught": 3}]},
    {"igot_course_id": "CRS-IGOT-1001", "course_title": "Fundamentals of Government Financial Rules (GFR 2017)", "provider_name": "ISTM", "duration_minutes": 480, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-GOV-011", "skill_name": "Public Financial Management & Government Accounting", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1002", "course_title": "Advanced Public Financial Management: PFMS, PAOs and Appropriation Accounts", "provider_name": "ISTM", "duration_minutes": 960, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-GOV-011", "skill_name": "Public Financial Management & Government Accounting", "proficiency_taught": 4}]},
    {"igot_course_id": "CRS-IGOT-1003", "course_title": "Government Procurement & GeM Portal: End-to-End Process", "provider_name": "DoPT", "duration_minutes": 600, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-GOV-012", "skill_name": "Public Procurement & Contract Management", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1004", "course_title": "CVC Guidelines & Vigilance Administration for Government Officers", "provider_name": "ISTM", "duration_minutes": 480, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-GOV-012", "skill_name": "Public Procurement & Contract Management", "proficiency_taught": 3}, {"external_skill_id": "FRAC-TECH-007", "skill_name": "Data Privacy, Security & Ethics", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1005", "course_title": "Leadership Effectiveness for Group A Officers", "provider_name": "Capacity Building Commission", "duration_minutes": 720, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-013", "skill_name": "Leadership & Team Management", "proficiency_taught": 3}]},
    {"igot_course_id": "CRS-IGOT-1006", "course_title": "Transformational Leadership and Change Management in Government", "provider_name": "Capacity Building Commission", "duration_minutes": 840, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-013", "skill_name": "Leadership & Team Management", "proficiency_taught": 4}, {"external_skill_id": "FRAC-BEHAV-014", "skill_name": "Policy Analysis & Strategic Thinking", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1007", "course_title": "Policy Design Masterclass: Evidence-Based Policymaking for Ministries", "provider_name": "Capacity Building Commission", "duration_minutes": 1200, "difficulty": "Advanced", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-014", "skill_name": "Policy Analysis & Strategic Thinking", "proficiency_taught": 4}, {"external_skill_id": "FRAC-BEHAV-015", "skill_name": "Communication & Report Writing", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1008", "course_title": "Effective Report Writing and Cabinet Note Drafting for IAS Officers", "provider_name": "ISTM", "duration_minutes": 480, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-015", "skill_name": "Communication & Report Writing", "proficiency_taught": 3}]},
    {"igot_course_id": "CRS-IGOT-1009", "course_title": "Presentation Skills: Communicating Complex Data to Non-Technical Audiences", "provider_name": "iGOT Karmayogi", "duration_minutes": 360, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-015", "skill_name": "Communication & Report Writing", "proficiency_taught": 2}, {"external_skill_id": "FRAC-TECH-006", "skill_name": "Data Visualization & Dashboarding", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1010", "course_title": "Ethics, Integrity and Anti-Corruption for Civil Servants", "provider_name": "DoPT", "duration_minutes": 360, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-TECH-007", "skill_name": "Data Privacy, Security & Ethics", "proficiency_taught": 2}, {"external_skill_id": "FRAC-GOV-012", "skill_name": "Public Procurement & Contract Management", "proficiency_taught": 1}]},
    {"igot_course_id": "CRS-IGOT-1011", "course_title": "Performance Management and Annual Performance Assessment Reports (APARs)", "provider_name": "DoPT", "duration_minutes": 300, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-013", "skill_name": "Leadership & Team Management", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1012", "course_title": "Digital India: e-Office, DARPG and Paperless Government Operations", "provider_name": "iGOT Karmayogi", "duration_minutes": 240, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-TECH-009", "skill_name": "Database Management & SQL", "proficiency_taught": 1}]},
    {"igot_course_id": "CRS-IGOT-1013", "course_title": "Cyber Security Essentials for Government Officials", "provider_name": "iGOT Karmayogi", "duration_minutes": 420, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-TECH-007", "skill_name": "Data Privacy, Security & Ethics", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1014", "course_title": "Strategic Planning and Mission-Mode Project Management", "provider_name": "Capacity Building Commission", "duration_minutes": 900, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-014", "skill_name": "Policy Analysis & Strategic Thinking", "proficiency_taught": 3}, {"external_skill_id": "FRAC-BEHAV-013", "skill_name": "Leadership & Team Management", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1015", "course_title": "Introduction to Bharat GIS and National Spatial Data Infrastructure", "provider_name": "NSSTA", "duration_minutes": 540, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-TECH-010", "skill_name": "Geospatial Data Analysis & GIS", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1016", "course_title": "Statistical Press Releases: Writing and Disseminating Official Data", "provider_name": "NSSTA", "duration_minutes": 300, "difficulty": "Beginner", "skills_covered": [{"external_skill_id": "FRAC-BEHAV-015", "skill_name": "Communication & Report Writing", "proficiency_taught": 3}, {"external_skill_id": "FRAC-STAT-003", "skill_name": "Statistical Data Quality & Validation", "proficiency_taught": 2}]},
    {"igot_course_id": "CRS-IGOT-1019", "course_title": "Contract Management and Dispute Resolution in Government Projects", "provider_name": "ISTM", "duration_minutes": 600, "difficulty": "Intermediate", "skills_covered": [{"external_skill_id": "FRAC-GOV-012", "skill_name": "Public Procurement & Contract Management", "proficiency_taught": 4}]},
]

# Alias for backward compatibility with adapter
MOCK_CATALOG = MOCK_CBP_CATALOG

# =============================================================================
# USER HISTORIES
# =============================================================================
MOCK_USER_HISTORY = {
    "EMP-8472": [
        {"igot_course_id": "CRS-IGOT-5521", "course_title": "National Accounts Statistics: SNA 2008 & GDP Estimation Methods", "status": "COMPLETED", "progress_percentage": 100, "remaining_minutes": 0, "last_accessed_at": "2025-10-12T09:00:00Z"},
        {"igot_course_id": "CRS-IGOT-8812", "course_title": "Survey Design and Sampling Methodologies", "status": "IN_PROGRESS", "progress_percentage": 45, "remaining_minutes": 990, "last_accessed_at": "2026-08-15T11:30:00Z"},
        {"igot_course_id": "CRS-IGOT-9999", "course_title": "Data Privacy, Confidentiality and the Personal Data Protection Act", "status": "IN_PROGRESS", "progress_percentage": 60, "remaining_minutes": 360, "last_accessed_at": "2026-08-20T14:00:00Z"},
        {"igot_course_id": "CRS-IGOT-1010", "course_title": "Ethics, Integrity and Anti-Corruption for Civil Servants", "status": "COMPLETED", "progress_percentage": 100, "remaining_minutes": 0, "last_accessed_at": "2026-07-10T10:00:00Z"},
    ],
    "user123": [
        {"igot_course_id": "CRS-IGOT-5521", "course_title": "National Accounts Statistics: SNA 2008 & GDP Estimation Methods", "status": "IN_PROGRESS", "progress_percentage": 65, "remaining_minutes": 840, "last_accessed_at": "2026-08-20T10:00:00Z"},
        {"igot_course_id": "CRS-IGOT-1001", "course_title": "Fundamentals of Government Financial Rules (GFR 2017)", "status": "COMPLETED", "progress_percentage": 100, "remaining_minutes": 0, "last_accessed_at": "2026-08-05T09:00:00Z"},
    ]
}

MOCK_SCORES_DB = []
MOCK_ENROLLMENTS_DB = []


# --- Pydantic Models ---
class ScoreRequest(BaseModel):
    competency_id: str
    new_level: int
    score_percentage: float
    passed: bool
    evaluated_at: str
    source: str

class EnrollRequest(BaseModel):
    igot_course_id: str
    enrolled_at: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/api/external/igot/catalog")
def get_catalog():
    return {"status": "success", "data": MOCK_CBP_CATALOG}


@app.get("/api/external/igot/frac")
def get_frac_dictionary():
    return {"status": "success", "data": MOCK_FRAC_DICTIONARY}


@app.get("/api/external/igot/users/{userId}/history")
def get_user_history(userId: str):
    history = MOCK_USER_HISTORY.get(userId, [])
    return {"status": "success", "data": history}


@app.post("/api/external/igot/users/{userId}/score", status_code=201)
def push_score(userId: str, payload: ScoreRequest):
    MOCK_SCORES_DB.append({"userId": userId, "score_data": payload.model_dump()})
    return {"status": "success", "message": "Score synced successfully to iGOT"}


@app.post("/api/external/igot/users/{userId}/enroll", status_code=201)
def enroll_user(userId: str, payload: EnrollRequest):
    MOCK_ENROLLMENTS_DB.append({"userId": userId, "enrollment_data": payload.model_dump()})
    if userId not in MOCK_USER_HISTORY:
        MOCK_USER_HISTORY[userId] = []
    course_info = next((c for c in MOCK_CBP_CATALOG if c["igot_course_id"] == payload.igot_course_id), None)
    if course_info:
        MOCK_USER_HISTORY[userId].append({
            "igot_course_id": course_info["igot_course_id"],
            "course_title": course_info["course_title"],
            "status": "NOT_STARTED",
            "progress_percentage": 0,
            "remaining_minutes": course_info["duration_minutes"],
            "last_accessed_at": payload.enrolled_at
        })
    return {"status": "success", "message": "User enrolled successfully on iGOT"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)