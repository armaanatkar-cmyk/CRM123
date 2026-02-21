import re
import html
from urllib.parse import parse_qs, unquote, urlparse
from typing import List, Iterable
from ddgs import DDGS
from .models import SearchResult, ParsedIntent, SearchResponse

ROLE_KW = [
    "ceo", "cto", "cfo", "coo", "cmo", "vp", "svp", "evp",
    "director", "head", "manager", "lead", "founder", "co-founder",
    "partner", "principal", "strategist", "consultant", "analyst",
    "coordinator", "specialist", "executive",
    "marketing", "sales", "growth", "product", "engineering",
    "finance", "hr", "operations", "design", "data",
    "business development", "account executive", "sdr", "bdr",
]

INDUSTRY_KW = {
    "healthcare": ["healthcare", "health", "medical", "pharma", "biotech", "healthtech"],
    "fintech": ["fintech", "finance", "banking", "payments", "defi", "neobank"],
    "saas": ["saas", "software", "b2b", "enterprise software"],
    "ecommerce": ["ecommerce", "e-commerce", "retail", "dtc", "shopify"],
    "ai": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "llm"],
    "crypto": ["crypto", "blockchain", "web3", "nft"],
    "edtech": ["edtech", "education", "learning"],
    "real estate": ["real estate", "proptech", "property"],
    "cybersecurity": ["cybersecurity", "security", "infosec"],
    "cleantech": ["cleantech", "climate", "sustainability", "green"],
    "martech": ["martech", "adtech", "advertising"],
    "logistics": ["logistics", "supply chain", "shipping", "freight"],
}

REGION_KW = {
    "United States": ["us", "usa", "united states", "america"],
    "California": ["california", "ca", "sf", "san francisco", "bay area", "la", "los angeles", "silicon valley"],
    "New York": ["new york", "ny", "nyc", "manhattan"],
    "Texas": ["texas", "tx", "austin", "dallas", "houston"],
    "Europe": ["europe", "eu", "european"],
    "United Kingdom": ["uk", "united kingdom", "london", "england", "britain"],
    "Canada": ["canada", "toronto", "vancouver"],
    "Australia": ["australia", "sydney", "melbourne"],
    "India": ["india", "bangalore", "mumbai", "delhi"],
    "Germany": ["germany", "berlin", "munich"],
    "Remote": ["remote", "worldwide", "global", "anywhere"],
}

def parse_user_prompt(prompt: str) -> ParsedIntent:
    low = prompt.lower()
    found = [kw for kw in ROLE_KW if kw in low]
    icp = " ".join(dict.fromkeys(found[:4])) if found else ""
    
    industry = ""
    for canon, syns in INDUSTRY_KW.items():
        if any(s in low for s in syns):
            industry = canon
            break
    if not industry:
        match = re.search(r"\b(?:at|in|for)\s+(\w+(?:\s+\w+)?)\s+(?:companies|startups|agencies|firms)", low)
        if match:
            industry = match.group(1)
            
    region = ""
    for canon, syns in REGION_KW.items():
        if any(s in low for s in syns):
            region = canon
            break
            
    agency_words = {"agency", "agencies", "company", "companies", "firm", "firms", "startup", "startups"}
    people_words = {"people", "person", "profile", "profiles", "employee", "employees",
                    "leader", "leaders", "founder", "founders", "who", "someone"}
    tokens = set(low.split())
    has_agency = bool(agency_words & tokens)
    has_people = bool(people_words & tokens)
    search_type = "agencies" if has_agency and not has_people else ("people" if has_people and not has_agency else "both")
    
    return ParsedIntent(
        icp=icp or "technology",
        industry=industry or "technology",
        region=region or "United States",
        search_type=search_type,
        raw_prompt=prompt,
    )

def _clean_url(raw: str) -> str:
    if "bing.com/aclick" in raw or "duckduckgo.com/l/" in raw:
        parsed = parse_qs(urlparse(raw).query)
        for key in ("u", "uddg", "r"):
            if key in parsed:
                return unquote(parsed[key][0])
    return raw

def _company_from_url(url: str) -> str:
    match = re.search(r"linkedin\.com/company/([^/?]+)", url)
    if match:
        return match.group(1).replace("-", " ").title()
    return ""

def is_linkedin_company(url: str) -> bool:
    return "linkedin.com/company/" in url.lower()

def is_linkedin_profile(url: str) -> bool:
    return "linkedin.com/in/" in url.lower()

def dedupe_by_url(items: Iterable[SearchResult]) -> List[SearchResult]:
    seen = set()
    output = []
    for result in items:
        key = result.url.split("?")[0].rstrip("/")
        if key not in seen:
            seen.add(key)
            output.append(result)
    return output

def parse_agency_name(title: str) -> str:
    for sep in ("|", "·", "—", "-"):
        if sep in title:
            left = title.split(sep, 1)[0].strip()
            return left or title.strip()
    return title.strip()

def search_web(query: str, max_results: int = 12) -> List[SearchResult]:
    try:
        results = DDGS().text(query, region="wt-wt", max_results=max_results)
        output = []
        for result in results:
            title = result.get("title", "").strip()
            url = _clean_url(result.get("href", "").strip())
            snippet = result.get("body", "").strip()
            if url:
                output.append(SearchResult(title=title, url=url, snippet=snippet))
        if output:
            return output
    except Exception:
        pass
        
    keywords = re.sub(r'site:\S+|"', "", query).split()[:4]
    term = "+".join(keywords)
    # Return dummy results on failure if needed, or empty list
    return []

def find_agencies(icp: str, industry: str, region: str, n: int = 8) -> List[SearchResult]:
    queries = [
        f'site:linkedin.com/company "{icp}" {industry} agency "{region}"',
        f'site:linkedin.com/company {icp} {industry} agency {region}',
        f'{icp} {industry} agency {region} linkedin.com/company',
    ]
    hits = []
    for query in queries:
        if len(hits) >= n:
            break
        for result in search_web(query, n * 2):
            if is_linkedin_company(result.url):
                result.company = _company_from_url(result.url)
                hits.append(result)
    return dedupe_by_url(hits)[:n]

def find_people(icp: str, industry: str, region: str, n: int = 8) -> List[SearchResult]:
    queries = [
        f'site:linkedin.com/in "{icp}" {industry} "{region}"',
        f'site:linkedin.com/in {icp} {industry} {region}',
        f'{icp} {industry} {region} linkedin.com/in',
    ]
    hits = []
    for query in queries:
        if len(hits) >= n:
            break
        hits.extend(result for result in search_web(query, n * 2) if is_linkedin_profile(result.url))
    return dedupe_by_url(hits)[:n]

def find_people_at_companies(agencies: List[SearchResult], icp: str, per_company: int = 3) -> List[SearchResult]:
    people = []
    for agency in agencies[:6]:
        company_name = agency.company or parse_agency_name(agency.title)
        query = f'site:linkedin.com/in "{company_name}" {icp}'
        try:
            results = search_web(query, per_company * 2)
            for result in results:
                if is_linkedin_profile(result.url):
                    result.company = company_name
                    people.append(result)
                    company_count = sum(1 for person in people if person.company == company_name)
                    if company_count >= per_company:
                        break
        except Exception:
            continue
    return dedupe_by_url(people)

def run_search_logic(query: str) -> SearchResponse:
    parsed = parse_user_prompt(query)
    agencies = []
    people = []
    company_people = []
    
    if parsed.search_type in ("both", "agencies"):
        agencies = find_agencies(parsed.icp, parsed.industry, parsed.region, n=8)
        if agencies:
            company_people = find_people_at_companies(agencies, parsed.icp, per_company=3)
    if parsed.search_type in ("both", "people"):
        people = find_people(parsed.icp, parsed.industry, parsed.region, n=8)
    
    return SearchResponse(
        agencies=agencies,
        people=people,
        company_people=company_people,
        parsed_intent=parsed
    )
