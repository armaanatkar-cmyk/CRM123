import re
import html
from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import parse_qs, unquote, urlparse
import time

import pandas as pd
import streamlit as st
from ddgs import DDGS


# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ICP Finder AI",
    page_icon="⚡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── CSS (ChatGPT Design) ─────────────────────────────────────────
_CSS = """
<style>
/* 
   ChatGPT Dark Theme Mimic
   Based on chat.openai.com dark mode appearance.
   Background: #343541
   Text: #ECECF1
   Input: #40414F
*/

@import url('https://fonts.googleapis.com/css2?family=Söhne:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Söhne', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* App Background */
.stApp {
    background-color: #343541;
    color: #ececf1;
}

/* Hide Streamlit Header/Footer */
#MainMenu, header, footer {visibility: hidden;}
div[data-testid="stToolbar"], div[data-testid="stDecoration"], .stDeployButton {display:none;}

/* Central Column - mimic ChatGPT width (text-width constraint) */
.block-container {
    max-width: 800px !important;
    padding-top: 2rem !important;
    padding-bottom: 6rem !important; /* Space for fixed input */
    margin: 0 auto !important;
}

/* 
   Chat Messages
*/
div[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.05); /* Subtle separator */
    padding: 1.5rem 0 !important;
    margin: 0 !important;
}

/* Avatar Styling */
div[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
    background-color: #19c37d !important; /* ChatGPT Green */
    color: white !important;
    border-radius: 2px !important; 
}
div[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] img {
    border-radius: 2px !important;
}
/* User Avatar Overlay (if user has no image, st uses fallback) */
div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageAvatar"] {
    background-color: #5436DA !important; /* Streamlit user purple fallback? */
}

/* Message Content */
div[data-testid="stMarkdownContainer"] p, 
div[data-testid="stMarkdownContainer"] li {
    font-size: 1rem !important;
    line-height: 1.7 !important;
    color: #ececf1 !important;
}
div[data-testid="stMarkdownContainer"] h3 {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
    color: #ececf1 !important;
}
div[data-testid="stMarkdownContainer"] a {
    color: #10a37f !important;
    text-decoration: none !important;
}
div[data-testid="stMarkdownContainer"] a:hover {
    text-decoration: underline !important;
}

/* 
   Input Field - ChatGPT Style 
   Floating at bottom, centered, rounded corners 
*/
.stChatInputContainer {
    bottom: 0 !important;
    padding-bottom: 1.5rem !important;
    padding-top: 1rem !important;
    background: linear-gradient(180deg, rgba(52,53,65,0), #343541 30%) !important;
}
.stChatInputContainer > div {
    background-color: #40414f !important; /* Input BG */
    border: 1px solid rgba(32,33,35,0.5) !important;
    border-radius: 12px !important;
    color: white !important;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
}
.stChatInputContainer > div:focus-within {
    border-color: #10a37f !important; /* Green glow on focus */
    box-shadow: 0 0 20px rgba(0,0,0,0.2) !important;
}
textarea[data-testid="stChatInputTextArea"] {
    color: white !important;
    font-size: 1rem !important;
}
/* Send Button */
button[data-testid="stChatInputSubmitButton"] {
    color: #d1d5db !important;
}
button[data-testid="stChatInputSubmitButton"]:hover {
    color: #10a37f !important;
}

/* 
   Empty State / Welcome Page 
*/
.gpt-logo-container {
    display: flex;
    justify-content: center;
    margin-bottom: 3rem;
    margin-top: 10vh;
}
.gpt-logo {
    background: white;
    padding: 2px;
    border-radius: 50%; /* Circle */
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: #343541;
    box-shadow: 0 0 20px rgba(255,255,255,0.1);
}
.welcome-header {
    text-align: center;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin-bottom: 4rem !important;
    color: #ececf1 !important;
}

/* Grid of suggestions */
.suggestion-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 2rem;
}

/* Suggestion Buttons (Custom) - Rendered as full width buttons in cols */
.stButton button {
    width: 100%;
    height: auto;
    text-align: left !important;
    background-color: transparent !important;
    border: 1px solid #565869 !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem 0.9rem !important;
    color: #d1d5db !important;
    font-size: 0.85rem !important;
    transition: background-color 0.2s, color 0.2s;
    line-height: 1.4 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    min-height: 60px;
}
.stButton button:hover {
    background-color: #40414f !important;
    color: #ececf1 !important;
    border-color: #19c37d !important; /* Green highlight border */
}
.stButton button p {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    margin-bottom: 2px !important;
    color: #e1e1e1 !important;
}
.suggestion-sub {
    font-size: 0.8rem !important;
    color: #9ca3af !important;
}

/* Results Snippet */
.result-snippet {
    color: #9ca3af;
    font-size: 0.85rem;
    margin-left: 1.4rem; /* Indent under numbered list */
    margin-bottom: 0.8rem;
    line-height: 1.5;
}

/* Download Button Styling */
div[data-testid="stHorizontalBlock"] button {
    background: #10a37f !important; /* Green primary btn */
    border: none !important;
    color: white !important;
    font-weight: 600;
}
div[data-testid="stHorizontalBlock"] button:hover {
    background: #1a7f64 !important;
}

hr {
    border-color: rgba(255,255,255,0.1) !important;
    margin: 2rem 0 !important;
}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)


# ── Data & Parsing ───────────────────────────────────────────────
@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    company: str = ""


@dataclass
class ParsedPrompt:
    icp: str
    industry: str
    region: str
    search_type: str
    raw_prompt: str = ""


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


def parse_user_prompt(prompt: str) -> ParsedPrompt:
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
    
    return ParsedPrompt(
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


def dedupe_by_url(items: Iterable[SearchResult]) -> list[SearchResult]:
    seen: set[str] = set()
    output: list[SearchResult] = []
    for result in items:
        key = result.url.split("?")[0].rstrip("/")
        if key not in seen:
            seen.add(key)
            output.append(result)
    return output


def parse_agency_name(title: str) -> str:
    # Helper for tests
    for sep in ("|", "·", "—", "-"):
        if sep in title:
            left = title.split(sep, 1)[0].strip()
            return left or title.strip()
    return title.strip()


def search_web(query: str, max_results: int = 12) -> list[SearchResult]:
    try:
        results = DDGS().text(query, region="wt-wt", max_results=max_results)
        output: list[SearchResult] = []
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
    return [
        SearchResult(
            title="LinkedIn Companies: " + " ".join(keywords),
            url="https://www.linkedin.com/search/results/companies/?keywords=" + term,
            snippet="Browse matching companies on LinkedIn",
        ),
        SearchResult(
            title="LinkedIn People: " + " ".join(keywords),
            url="https://www.linkedin.com/search/results/people/?keywords=" + term,
            snippet="Browse matching profiles on LinkedIn",
        ),
    ]


def find_agencies(icp: str, industry: str, region: str, n: int = 8) -> list[SearchResult]:
    queries = [
        f'site:linkedin.com/company "{icp}" {industry} agency "{region}"',
        f'site:linkedin.com/company {icp} {industry} agency {region}',
        f'{icp} {industry} agency {region} linkedin.com/company',
    ]
    hits: list[SearchResult] = []
    for query in queries:
        if len(hits) >= n:
            break
        for result in search_web(query, n * 2):
            if is_linkedin_company(result.url):
                result.company = _company_from_url(result.url)
                hits.append(result)
    return dedupe_by_url(hits)[:n]


def find_people(icp: str, industry: str, region: str, n: int = 8) -> list[SearchResult]:
    queries = [
        f'site:linkedin.com/in "{icp}" {industry} "{region}"',
        f'site:linkedin.com/in {icp} {industry} {region}',
        f'{icp} {industry} {region} linkedin.com/in',
    ]
    hits: list[SearchResult] = []
    for query in queries:
        if len(hits) >= n:
            break
        hits.extend(result for result in search_web(query, n * 2) if is_linkedin_profile(result.url))
    return dedupe_by_url(hits)[:n]


def find_people_at_companies(agencies: list[SearchResult], icp: str, per_company: int = 3) -> list[SearchResult]:
    people: list[SearchResult] = []
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


def _result_lines(results: list[SearchResult], heading: str) -> str:
    # Use HTML for better formatting control inside Markdown
    lines = [f"### {heading}"]
    for idx, result in enumerate(results, start=1):
        company = f" — {result.company}" if result.company else ""
        title = result.title.strip() or "LinkedIn result"
        snippet = html.escape(result.snippet[:160] + "..." if len(result.snippet) > 160 else result.snippet)
        
        # ChatGPT style list item
        lines.append(
            f"{idx}. [{title}]({result.url}){company}"
        )
        if snippet:
            lines.append(f"   <div class=\"result-snippet\">{snippet}</div>")

    return "\n".join(lines)


def build_assistant_markdown(
    parsed: ParsedPrompt,
    agencies: list[SearchResult],
    people: list[SearchResult],
    company_people: list[SearchResult],
) -> str:
    total_people = len(people) + len(company_people)
    intro = (
        f"I searched for **{parsed.icp}** in **{parsed.industry}** around **{parsed.region}**.\n\n"
        f"I found **{len(agencies)} agencies** and **{total_people} people** that match your criteria."
    )
    
    blocks = [intro]
    if agencies:
        blocks.append(_result_lines(agencies, "Agencies & Companies"))
    if company_people:
        blocks.append(_result_lines(company_people, "Key People at These Companies"))
    if people:
        blocks.append(_result_lines(people, "Profiles & Leads"))
    if not agencies and not people and not company_people:
        blocks.append("\nI couldn’t find strong matches.\n\nTry a more specific role (e.g., 'Head of Marketing'), industry, or location.")
    
    return "\n\n".join(blocks)


def run_search(prompt: str) -> dict:
    parsed = parse_user_prompt(prompt)
    agencies: list[SearchResult] = []
    people: list[SearchResult] = []
    company_people: list[SearchResult] = []
    
    if parsed.search_type in ("both", "agencies"):
        agencies = find_agencies(parsed.icp, parsed.industry, parsed.region, n=8)
        if agencies:
            company_people = find_people_at_companies(agencies, parsed.icp, per_company=3)
    if parsed.search_type in ("both", "people"):
        people = find_people(parsed.icp, parsed.industry, parsed.region, n=8)
    
    response_md = build_assistant_markdown(parsed, agencies, people, company_people)
    all_results = agencies + people + company_people
    
    # Store results in session state right away so download button works immediately
    if "all_results" not in st.session_state:
        st.session_state.all_results = []
    st.session_state.all_results.extend(all_results)
    
    return {
        "content": response_md,
        "all_results": all_results,
    }


# ── Session State ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "all_results" not in st.session_state:
    st.session_state.all_results = []


# ── Input Handling (Top of loop to catch runs) ───────────────────
prompt = st.chat_input("Message customized ICP Finder...")


# ── Render Logic ────────────────────────────────────────────────
# Empty State
if not st.session_state.messages:
    # Top Logo
    st.markdown(
        """
        <div class="gpt-logo-container">
            <div class="gpt-logo">⚡️</div>
        </div>
        <div class="welcome-header">How can I help you find leads today?</div>
        """, 
        unsafe_allow_html=True
    )
    
    # 2x2 Grid of Suggestions
    # We use a custom key mechanism to trigger search from buttons
    c1, c2 = st.columns(2)
    sug_1 = ("VP Marketing", "healthcare agencies in California")
    sug_2 = ("Growth Leads", "fintech startups in New York")
    sug_3 = ("Sales Directors", "SaaS companies in Texas")
    sug_4 = ("Founders", "AI startups in Europe")
    
    with c1:
        if st.button(f"**{sug_1[0]}**\n\n{sug_1[1]}", key="btn1", use_container_width=True):
             prompt = f"{sug_1[0]} at {sug_1[1]}"
        if st.button(f"**{sug_3[0]}**\n\n{sug_3[1]}", key="btn3", use_container_width=True):
             prompt = f"{sug_3[0]} at {sug_3[1]}"
             
    with c2:
        if st.button(f"**{sug_2[0]}**\n\n{sug_2[1]}", key="btn2", use_container_width=True):
             prompt = f"{sug_2[0]} at {sug_2[1]}"
        if st.button(f"**{sug_4[0]}**\n\n{sug_4[1]}", key="btn4", use_container_width=True):
             prompt = f"{sug_4[0]} at {sug_4[1]}"


# ── Render Chat History ──────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)


# ── Run Search if Prompt Exists ──────────────────────────────────
if prompt:
    # 1. Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 2. Append assistant placeholder & run
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = run_search(prompt)
            st.markdown(payload["content"], unsafe_allow_html=True)
    
    # 3. Save to history
    st.session_state.messages.append({"role": "assistant", "content": payload["content"]})
    
    # 4. Rerun to update state/buttons
    st.rerun()


# ── Footer / Export ──────────────────────────────────────────────
# Only show if there are results and we are not in the middle of a run
if st.session_state.all_results and st.session_state.messages:
    st.markdown("---")
    
    # Unique results
    unique = dedupe_by_url(st.session_state.all_results)
    
    # Create CSV
    result_rows = [
        {"title": r.title, "url": r.url, "snippet": r.snippet, "company": r.company}
        for r in unique
    ]
    df = pd.DataFrame(result_rows)
    csv = df.to_csv(index=False).encode("utf-8")
    
    cols = st.columns([1, 1, 3])
    with cols[0]:
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="leads.csv",
            mime="text/csv",
            help="Download all found leads in this session",
            use_container_width=True
        )
    with cols[1]:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.all_results = []
            st.rerun()

