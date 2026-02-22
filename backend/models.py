from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    company: Optional[str] = ""

class ParsedIntent(BaseModel):
    icp: str
    industry: str
    region: str
    search_type: str
    raw_prompt: str
    extra_keywords: List[str] = []

class SearchResponse(BaseModel):
    agencies: List[SearchResult]
    people: List[SearchResult]
    company_people: List[SearchResult]
    parsed_intent: ParsedIntent

class EnrichRequest(BaseModel):
    name: str
    company: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    snippet: Optional[str] = ""
    title: Optional[str] = ""

class EnrichResponse(BaseModel):
    email: Optional[str] = ""
    email_confidence: str = "none"  # "found" | "inferred" | "none"
    cold_email_draft: Optional[str] = ""
