"""
FILE: ai/seed_knowledge.py
─────────────────────────────────────────────────────────────────────────────
Baseline Knowledge Seeder — Phase 1 of the RAG pipeline setup.

Run once (or whenever you want to refresh the baseline corpus):
    cd main-lms-backend
    python -m ai.seed_knowledge

This script embeds curated MoSPI-domain reference text into ChromaDB so Gyan
can answer domain questions immediately even before any documents are uploaded.

Covers:
  • iGOT FRAC Framework
  • NSSTA training programmes
  • National Accounts & GDP (SNA 2008)
  • Consumer Price Index (CPI)
  • Periodic Labour Force Survey (PLFS)
  • Survey methodology & sampling techniques
  • MoSPI organisational overview
─────────────────────────────────────────────────────────────────────────────
"""

import logging
import sys
import os

# Allow running as `python -m ai.seed_knowledge` from the backend dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ── Baseline knowledge corpus ─────────────────────────────────────────────────

KNOWLEDGE_BASE: list[dict] = [
    {
        "source": "iGOT_FRAC_Framework",
        "text": """
iGOT Karmayogi FRAC Framework (Framework for Roles, Activities and Competencies)

The FRAC framework is the core competency architecture of the Government of India's 
Mission Karmayogi initiative, implemented through the iGOT Karmayogi online learning 
platform. It provides a unified language for describing government roles and skills.

FRAC Three-Layer Architecture:
1. ROLES: Specific job positions held by civil servants, e.g., Deputy Director (National 
   Accounts), Field Investigator (NSSO), Statistical Officer, Director General (CSO).
2. ACTIVITIES: Key functions and responsibilities performed in a given role. Each role has 
   between 5 and 15 defined activities.
3. COMPETENCIES: The skills, knowledge, and behaviours needed to perform activities 
   effectively. Competencies are categorised as:
   - Behavioural (B): Teamwork, communication, leadership, integrity
   - Domain (D): Subject-matter expertise, e.g., national accounts, price statistics
   - Functional (F): Cross-cutting technical skills, e.g. data analysis, report writing

FRAC Competency Levels (1 to 5):
Level 1 — Awareness: Basic familiarity with concepts.
Level 2 — Foundation: Can apply with guidance.
Level 3 — Intermediate: Can apply independently.
Level 4 — Advanced: Can mentor others; leads in this domain.
Level 5 — Expert: Nationally recognised expertise; shapes policy.

FRAC Dictionary Integration with iGOT:
All courses on iGOT Karmayogi are tagged to specific FRAC competencies and levels.
When a learner completes a course, their FRAC competency level is updated accordingly.
The iGOT platform uses the FRAC dictionary to generate personalised learning pathways,
ensuring every official has a clear, structured route from their current competency level
to the target level required for their role.

Role-specific FRAC Mapping (Statistical Cadre):
For Deputy Director (National Accounts Division), the typical target competency levels are:
- National Accounts Framework (SNA 2008): Level 4
- Survey Methodology: Level 4
- Price Statistics & CPI Construction: Level 3
- Data Analysis with Python & R: Level 4
- Machine Learning for Statistics: Level 3
""",
    },
    {
        "source": "NSSTA_Training_Programmes",
        "text": """
National Statistical Systems Training Academy (NSSTA) — Training Programmes

NSSTA is the apex training institution of MoSPI, located in Greater Noida, Uttar Pradesh.
It provides in-service training to officers of the Indian Statistical Service (ISS) and
other statistical personnel across central and state governments.

Core Training Programmes offered by NSSTA:

1. Foundation Course for ISS Probationers (8 weeks)
   Topics: Official statistics framework, national accounts, sampling theory, economic 
   statistics, computer applications in data analysis.

2. Advanced Programme on National Accounts Statistics (3 weeks)
   Topics: SNA 2008, GDP compilation methods (expenditure, production, income), 
   quarterly estimates, supply-use tables, input-output framework, India-specific 
   adjustments (informal sector, agriculture).

3. Workshop on Price Statistics (2 weeks)
   Topics: CPI and WPI compilation, Laspeyres index formula, basket composition, 
   base year revision, international price comparison (ICP programme).

4. Programme on Survey Design and Analysis (2 weeks)
   Topics: NSSO survey design, stratified multi-stage sampling, sample size determination, 
   design effects, analysis using SAS/SPSS/R, weighting and estimation procedures.

5. Data Dissemination and SDGs (1 week)
   Topics: SDMX data standards, open data portals, mapping official statistics to 
   UN Sustainable Development Goals (SDGs) indicators.

6. Advanced Course on Econometrics and Time Series Analysis (2 weeks)
   Topics: Regression analysis, ARIMA models, seasonal adjustment (X-13), panel data, 
   index number theory, nowcasting techniques.

NSSTA also collaborates with international agencies including IMF, World Bank, and 
UN Statistics Division for specialised training and capacity building programmes.
""",
    },
    {
        "source": "National_Accounts_GDP_SNA2008",
        "text": """
National Accounts Statistics — India (SNA 2008 Framework)

The National Statistical Office (NSO), under MoSPI, compiles India's national accounts 
following the System of National Accounts 2008 (SNA 2008), the international standard 
jointly developed by the UN, IMF, World Bank, OECD, and Eurostat.

GDP Compilation Methods (all three must yield identical results in theory):

1. EXPENDITURE METHOD (most common for quarterly): 
   GDP = C + I + G + (X − M)
   C = Private Final Consumption Expenditure (PFCE)
   I = Gross Fixed Capital Formation (GFCF) + Change in Stocks
   G = Government Final Consumption Expenditure (GFCE)
   X = Exports of goods and services
   M = Imports of goods and services

2. PRODUCTION METHOD (Value-Added Approach):
   GDP = Sum of Gross Value Added (GVA) across all industries + Product taxes − Subsidies
   GVA is computed for 8 broad sectors:
   Agriculture, forestry & fishing; Mining & quarrying; Manufacturing; Electricity, gas 
   & water supply; Construction; Trade, hotels, transport; Financial & real estate; 
   Public administration & defence.
   GDP at Market Prices = GVA at Basic Prices + Taxes on products − Subsidies on products

3. INCOME METHOD:
   GDP = Compensation of Employees (CoE) + Gross Operating Surplus (GOS) + 
         Gross Mixed Income (GMI) + Taxes on production and imports − Subsidies

Key India-specific data and concepts:
- Current base year: 2011-12 (revised from 2004-05 in 2015)
- Advance Estimates (AE): January each year
- First Revised Estimate (FRE): January following year
- Second Revised Estimate (SRE): January two years later
- Quarterly GDP estimates: released by NSO within 60 days of quarter end

Informal Sector Treatment:
India's large informal sector is estimated using enterprise surveys, PLFS data, 
and ratio estimation. The informal sector accounts for approximately 45-50% of GVA.

Base Year Revision Process:
India follows a practice of periodic base year revisions (every 7-10 years) to reflect 
structural changes in the economy. The 2011-12 base revision introduced MCA21 data, 
new price indices, and improved informal sector coverage.
""",
    },
    {
        "source": "CPI_Price_Statistics",
        "text": """
Consumer Price Index (CPI) — India

The Consumer Price Index (CPI) measures the average change in prices paid by consumers 
for a basket of goods and services over time.

India's Current CPI Series:
- Compiled by: NSO (National Statistical Office) under MoSPI
- Base Year: 2012 = 100 (introduced January 2015, replacing 2010=100 series)
- Release Frequency: Monthly (around 12th of each month for the previous month)
- Three sub-indices: CPI-Combined (rural + urban), CPI-Rural, CPI-Urban

Index Formula — Laspeyres Price Index:
CPI_t = Σ (W_i × P_it/P_i0) × 100
where:
  W_i = weight of item i in the basket (fixed at base-year expenditure shares)
  P_it = price of item i in period t
  P_i0 = price of item i in base year 2012

Item Coverage: 299 items across 6 major groups:
1. Food and Beverages (weight: 45.86%)
2. Pan, Tobacco and Intoxicants (2.38%)
3. Clothing and Footwear (6.53%)
4. Housing (10.07% — urban only; imputed rural)
5. Fuel and Light (6.84%)
6. Miscellaneous (28.32%) — includes health, education, transport, recreation

Price Data Collection:
- Urban: Price Monitoring Cell (PMC) in selected markets across 1,181 towns
- Rural: From villages in 1,181 Price Collection Centres (PCCs)

RBI Inflation Targeting:
The RBI Act (amended 2016) mandates RBI to maintain CPI inflation at 4% (±2%).
CPI is thus the official "headline inflation" benchmark in India's monetary policy.

WPI vs CPI distinction:
- WPI (Wholesale Price Index): Compiled by DPIIT (Ministry of Commerce), base 2011-12.
  Measures prices at the wholesale/producer level. Does NOT cover services.
- CPI: Measures prices at the consumer/retail level. Covers both goods and services.
""",
    },
    {
        "source": "PLFS_Employment_Survey",
        "text": """
Periodic Labour Force Survey (PLFS) — MoSPI/NSSO

The Periodic Labour Force Survey (PLFS) is one of India's most important household surveys,
conducted by the National Statistical Office (NSSO wing of MoSPI) since 2017-18.
It replaced the older Employment-Unemployment Survey (EUS) which was conducted quinquennially.

Objectives of PLFS:
1. Estimate key employment and unemployment indicators at national and state level.
2. Generate quarterly estimates of labour market indicators for urban areas.
3. Track changes in the labour market in a more timely manner.

Key Employment Concepts Measured:
- Usual Principal Status (UPS): Activity status for major part of the year (reference: 365 days)
- Usual Subsidiary Status (USS): Secondary economic activity
- Current Weekly Status (CWS): Activity status in preceding 7 days
- Current Daily Status (CDS): Activity status for each day in preceding 7 days

Key Indicators Derived from PLFS:
- LFPR: Labour Force Participation Rate = (Employed + Unemployed) / Working Age Population
- WPR: Worker Population Ratio = Employed / Working Age Population
- UR: Unemployment Rate = Unemployed / Labour Force
- Self-employment, regular wage/salaried employment, casual labour breakdown

Survey Design:
- Sample: ~1 lakh households (combined rural + urban)
- Sampling: Stratified multi-stage random sampling
- Rotation Panel: Urban areas use a rotating panel (4 visits per household over a year)
- Reference period for annual report: July–June

PLFS and Policy:
PLFS data feeds into India's national accounts (GDP from income side), social protection 
policy, and the SDG monitoring framework (particularly SDG Goal 8: Decent Work).
""",
    },
    {
        "source": "Survey_Sampling_Methodology",
        "text": """
Survey Methodology and Sampling Techniques — Official Statistics

Sampling theory underpins all of NSSO's large-scale surveys (PLFS, HCES, ASI, MSME survey).
Understanding these methods is essential for all statistical officers.

Types of Probability Sampling used by NSSO:

1. Simple Random Sampling (SRS):
   Every unit in the population has an equal probability of selection.
   Types: With Replacement (SRSWR) and Without Replacement (SRSWOR).
   Used when the population is homogeneous.

2. Stratified Random Sampling:
   Population is divided into non-overlapping, homogeneous strata (e.g., rural/urban, 
   state-wise, industry-size class). Random samples are drawn from each stratum.
   Benefit: Reduces sampling variance by ensuring representation of all subgroups.
   Used in PLFS, HCES, ASI for state/rural-urban breakdowns.

3. Cluster Sampling:
   Population is divided into clusters (villages, census enumeration blocks).
   Entire clusters are selected randomly, then all units within selected clusters are surveyed.
   Benefit: Reduces cost when population is geographically dispersed.

4. Multi-Stage Sampling:
   Sampling in multiple stages: e.g., Stage 1: Select districts; Stage 2: Select blocks/villages; 
   Stage 3: Select households. Used in PLFS, HCES.
   First Stage Units (FSU): villages (rural) / Urban Frame Survey (UFS) blocks (urban).
   Second Stage Units (SSU): households.

5. Systematic Sampling:
   Select every k-th unit after a random start. Used for listing operations.

Important Sampling Concepts:
- Sampling Frame: The complete list of all units from which the sample is drawn.
  NSSO uses the Census House Listing as the rural sampling frame.
- Design Effect (DEFF): Ratio of actual variance to SRS variance. DEFF > 1 in cluster sampling.
- Probability Proportional to Size (PPS): Larger units get higher selection probability.
  Used in ASI for large establishments.
- Weighting: Survey weights are the inverse of selection probability, adjusted for non-response.
- Non-sampling errors: Measurement errors, response errors, processing errors — often larger 
  than sampling errors in practice.
""",
    },
    {
        "source": "MoSPI_Organisational_Overview",
        "text": """
Ministry of Statistics and Programme Implementation (MoSPI) — Overview

MoSPI is the nodal ministry of the Government of India responsible for:
1. Collecting, compiling, and disseminating official statistics.
2. Coordinating the statistical activities of central and state governments.
3. Monitoring the implementation of government programmes.

Two Main Wings:
A. Statistics Wing (MoSPI Statistics):
   - National Statistical Office (NSO): Merged body of CSO + NSSO (2019 merger)
   - Central Statistics Office (CSO): National accounts, CPI, IIP, economic census
   - National Sample Survey Office (NSSO): Household surveys (PLFS, HCES, etc.)
   - Computer Centre: IT infrastructure for data processing
   - Indian Statistical Service (ISS): The dedicated cadre of statistical officers

B. Programme Implementation Wing:
   - Monitors flagship government programmes (MGNREGS, PM-KISAN, Smart Cities, etc.)
   - Twenty-Point Programme (TPP) monitoring
   - Infrastructure monitoring

Key Publications by MoSPI:
- National Accounts Statistics (annual): GDP, savings, capital formation
- Annual Survey of Industries (ASI): Factory-level manufacturing data
- Consumer Price Index (CPI): Monthly inflation release
- Index of Industrial Production (IIP): Monthly industrial output
- Economic Census: Coverage of all non-agricultural establishments
- Household Consumption Expenditure Survey (HCES)
- Periodic Labour Force Survey (PLFS)

iGOT Karmayogi Integration:
All MoSPI statistical officers are required to maintain competency levels mapped to the 
FRAC framework on iGOT Karmayogi. The MoSPI Skill Intelligence Platform (this system) 
uses the FRAC competency dictionary to compute skill gaps and generate personalised 
learning pathways from the iGOT course catalog.

NSSTA (National Statistical Systems Training Academy):
Located in Greater Noida, NSSTA is the apex training institution under MoSPI providing 
in-service training, research, and consultancy on official statistical methods.
""",
    },
]


def seed():
    """Embeds all baseline knowledge into ChromaDB."""
    from ai.vector_store import add_text_to_store, get_store_stats

    logger.info("Starting baseline knowledge seeding...")
    total_chunks = 0

    for item in KNOWLEDGE_BASE:
        source = item["source"]
        text = item["text"].strip()
        try:
            count = add_text_to_store(text, metadata={"source": source, "type": "baseline"})
            total_chunks += count
            logger.info("  ✓ Seeded '%s' → %d chunks", source, count)
        except Exception as exc:
            logger.error("  ✗ Failed to seed '%s': %s", source, exc)

    stats = get_store_stats()
    logger.info("\n=== Seeding Complete ===")
    logger.info("Total chunks added this run : %d", total_chunks)
    logger.info("Total chunks in DB          : %s", stats.get("document_chunks", "?"))
    logger.info("ChromaDB path               : %s", stats.get("db_path", "?"))
    logger.info("Embedding model             : %s", stats.get("embed_model", "?"))


if __name__ == "__main__":
    seed()
