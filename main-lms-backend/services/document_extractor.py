"""
FILE: main-lms-backend/services/document_extractor.py
─────────────────────────────────────────────────────────────────────────────
Offline AI pipeline to parse uploaded certificates/resumes and map them 
to FRAC competencies using a local Ollama LLM (llama3.2:3b).
Zero external API calls.
"""

import json
import requests
from typing import List, Optional
from pydantic import BaseModel, Field
from pypdf import PdfReader

# ── Structured Output Schemas ────────────────────────────────────────────────

class ExtractedCompetency(BaseModel):
    competency_id: str = Field(..., description="The exact UUID of the matched FRAC competency.")
    competency_name: str = Field(..., description="Name of the matched competency.")
    extracted_level: float = Field(..., description="Skill level (1.0 to 5.0). Beginner=2.0, Intermediate=3.0, Advanced=4.0.")
    issue_date: Optional[str] = Field(None, description="Date of issuance (YYYY-MM-DD).")
    justification: str = Field(..., description="Brief rationale explaining why this score was chosen based on document text.")

class CertificateExtractionResult(BaseModel):
    is_valid_credential: bool = Field(..., description="True if document is a valid training record or resume.")
    issuing_organization: Optional[str] = Field(None, description="Organization that issued the credential.")
    extracted_competencies: List[ExtractedCompetency]

# ── Local Extractor Service (Ollama) ─────────────────────────────────────────

class DocumentExtractorService:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "llama3.2:3b"

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            reader = PdfReader(pdf_path)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")

    def parse_document(self, text_content: str, frac_dictionary: list[dict]) -> CertificateExtractionResult:
        frac_reference = json.dumps([
            {"id": comp["id"], "name": comp["name"], "category": comp["competencyType"]}
            for comp in frac_dictionary
        ])

        system_prompt = (
            "You are an expert HR Skill Intelligence Auditor. Extract training records into JSON.\n\n"
            "RULES:\n"
            "1. ISSUER: You MUST extract the 'issuing_organization' (e.g., Coursera, Udemy, CDAC, University).\n"
            "2. SKILL MAPPING: Map the document's skills to the closest match in the provided FRAC list. "
            "For example, if the document says 'Python for Data Science', map it to 'Python for Statistical Computing'.\n"
            "3. DATES: Format issue dates as YYYY-MM-DD. If only a year is found, use YYYY-01-01.\n"
            "4. LEVELS: Assign 2.0 for beginner, 3.0 for intermediate/bootcamp, and 4.0 for advanced/expert.\n"
            "5. NO HALLUCINATIONS: If the document is not a valid certificate or resume, set is_valid_credential to false."
        )

        user_prompt = f"FRAC Dictionary Reference:\n{frac_reference}\n\nDocument Text:\n{text_content}"

        # FIX: Pydantic V2 syntax
        schema = CertificateExtractionResult.model_json_schema()

        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "format": schema,
                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            }
        )
        
        # FIX: Detailed error logging instead of a generic 404 crash
        if response.status_code != 200:
            raise ValueError(f"Ollama Error (Status {response.status_code}): {response.text}")
        
        result_json = response.json()["response"]
        
        # FIX: Pydantic V2 syntax for JSON parsing
        return CertificateExtractionResult.model_validate_json(result_json)

# ─────────────────────────────────────────────────────────────────────────────
# Verification Test Block
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    extractor = DocumentExtractorService()
    
    mock_frac = [
        {"id": "comp_data_gov_016", "name": "Data Governance & Quality Assurance", "competencyType": "Functional"},
        {"id": "comp_python_stats_017", "name": "Python for Statistical Computing", "competencyType": "Functional"}
    ]
    
    mock_pdf_text = (
        "CERTIFICATE OF COMPLETION. This certifies that Anshika Sharma has successfully "
        "completed the 'Advanced Python for Data Science and Statistical Modeling' bootcamp. "
        "Issued by Coursera on August 15, 2023."
    )
    
    print("Sending document to local Ollama (llama3.2:3b) for extraction...")
    result = extractor.parse_document(mock_pdf_text, mock_frac)
    
    print(f"\nValid Credential: {result.is_valid_credential}")
    print(f"Issuer: {result.issuing_organization}")
    
    for comp in result.extracted_competencies:
        print(f"\nMatched FRAC ID: {comp.competency_id}")
        print(f"Matched Skill Name: {comp.competency_name}")
        print(f"Granted Level: {comp.extracted_level}")
        print(f"Issue Date: {comp.issue_date}")
        print(f"Reasoning: {comp.justification}")