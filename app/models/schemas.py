from pydantic import BaseModel, constr
from typing import List, Optional, Dict, Any

Sector = constr(regex=r"^[a-zA-Z\s-]{2,50}$")

class AnalyzeResponse(BaseModel):
    sector: str
    summary: str
    markdown: str
    sources: List[str]
    # Intermediate results from each step
    intermediate_results: Dict[str, Any]
