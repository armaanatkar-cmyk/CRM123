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

class SearchResponse(BaseModel):
    agencies: List[SearchResult]
    people: List[SearchResult]
    company_people: List[SearchResult]
    parsed_intent: ParsedIntent
