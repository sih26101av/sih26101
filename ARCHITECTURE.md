# System Architecture: AI-Enabled Skill Intelligence & LMS (MoSPI)

## 1. Project Context & Objectives
This project is a high-fidelity prototype for the Smart India Hackathon (SIH), built for the Ministry of Statistics and Programme Implementation (MoSPI). 

**The Problem:** Government officials require continuous upskilling in Official Statistics (e.g., Survey Design, National Accounts) and modern tech (AI/ML, Python). While the "iGOT Karmayogi" platform hosts courses, there is no intelligent mechanism to perform skill-gap assessments and recommend personalized learning pathways.

**The Solution:** An AI-driven Learning Management System (LMS) that maps an official's current competencies against their Job Role benchmark, calculates explicit skill gaps, and uses AI (Semantic Search & RAG) to recommend courses and generate dynamic assessments from MoSPI training documents.

---

## 2. Technology Stack
*   **Frontend:** React (Functional components, Hooks), Tailwind CSS, Lucide React (Icons).
*   **Backend API:** Python FastAPI (RESTful JSON APIs).
*   **Database:** MySQL (Relational) via SQLAlchemy ORM.
*   **AI/ML Layer:** Python-based GenAI workflows (LangChain, vector embeddings, LLM integrations for RAG).

---

## 3. Core Domain Model (Strict Constraints)
The entire database schema, class structures, and object relationships **MUST strictly adhere** to the UML class diagram defined in the accompanying file:
👉 **`mospi-competency-platform.mermaid`**

### Key Structural Rules (Derived from Mermaid):
*   **Composition vs. Aggregation:** 
    *   An `Official` *owns* a `CompetencyProfile` (Strict Composition). 
    *   An `Official` *holds* a `JobRole` (Aggregation).
*   **Dictionary Independence:** The `Competency` table acts as a master dictionary. `UserCompetency`, `RoleRequirement`, and `CourseSkillMapping` all act as junction tables pointing back to `Competency`.
*   **Data Models:** The backend SQLAlchemy models and frontend TypeScript interfaces must map exactly to the entities in the Mermaid file.

---

## 4. Software Design Patterns & SOLID Principles
The system must be highly decoupled and modular. The codebase must implement the following design patterns:

### A. The Adapter Pattern (External Integrations)
To comply with the **Dependency Inversion Principle (DIP)**, the system must not hardcode API calls to iGOT Karmayogi.
*   Implement interfaces: `ICatalogSync` (Read) and `IScorePublisher` (Write) following the **Interface Segregation Principle (ISP)**.
*   Implement concrete classes: `MockIgotPlatformAdapter` (for SIH execution) and `LiveSunbirdAdapter` (for future production).

### B. The Strategy Pattern (AI Algorithms)
AI Recommendation logic must be pluggable.
*   Implement an `IRecommendationStrategy` interface.
*   Implement concrete strategies: `VectorSearchStrategy` (Semantic embedding matching) and a fallback `SkillGapRuleStrategy` (Tag/Rule-based matching).

### C. Factory & Builder Patterns (GenAI RAG Engine)
For the Document-to-Assessment feature:
*   Use a `DocumentParserFactory` to dynamically instantiate `PdfParser`, `PptParser`, or `TextParser` based on the uploaded file type.
*   Use an `AssessmentBuilder` to safely construct the complex, nested JSON objects (Assessments containing Questions with AI Explanations) returned by the Large Language Model.

### D. Transactional Outbox & Observer Pattern (Event Syncing)
To ensure system resilience when syncing data to government servers:
*   When a user passes an assessment, emit an `AssessmentPassedEvent`.
*   Use synchronous listeners for local DB updates (e.g., `LocalProfileUpdater`).
*   Use a Transactional Outbox table (`OutboxEntry`) for external syncing. An async worker will safely push the updated score to the external iGOT adapter, ensuring a failed external API call does not crash the local grading transaction.

---

## 5. Core System Workflows

### Flow 1: Skill Gap Calculation Engine
1.  System retrieves the user's `CompetencyProfile`.
2.  System retrieves the `RoleRequirement` for the user's assigned `JobRole`.
3.  The `SkillGapEngine` compares `UserCompetency.currentLevel` against `RoleRequirement.requiredLevel`.
4.  Outputs a normalized JSON `SkillGapReport` to the frontend dashboard.

### Flow 2: AI Course Recommendation
1.  The system identifies the user's skill gaps.
2.  The `RecommendationEngine` utilizes the `HybridRecommendationStrategy`.
3.  Queries the `VectorStore` matching the gap text against `Course.syllabusVectorEmbedding`.
4.  Returns a personalized learning pathway ranked by relevance.

### Flow 3: RAG Document-to-Assessment
1.  MoSPI Administrator uploads a PDF training manual via the UI.
2.  `DocumentParserFactory` extracts the text.
3.  The text is chunked and passed to the LLM via an engineered prompt to generate Objective Type Questions (MCQs).
4.  `AssessmentBuilder` structures the output and saves it to the database, making the quiz instantly available to learners.

---

## 6. Execution Guidelines for AI Agents
When generating code for this project, follow this order of operations:
1.  **Read `mospi-competency-platform.mermaid`** completely to understand the domain.
2.  **Scaffold the Database:** Generate SQLAlchemy models (`models.py`) mapping strictly to the domain.
3.  **Scaffold the API:** Build FastAPI routes utilizing dummy JSON data that reflects the relationships.
4.  **Scaffold the UI:** Build the React frontend using Tailwind, creating the Learner and Admin dashboards to consume the API.
5.  **Implement Logic:** Build out the design pattern interfaces (Adapters, Strategies) and connect the AI logic.