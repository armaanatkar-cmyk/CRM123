import sys
import types

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    pandas_stub.DataFrame = object
    sys.modules["pandas"] = pandas_stub

if "streamlit" not in sys.modules:
    streamlit_stub = types.ModuleType("streamlit")
    sys.modules["streamlit"] = streamlit_stub

if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")
    def _unused_post(*args, **kwargs):
        raise RuntimeError("requests.post should be monkeypatched in tests")
    requests_stub.post = _unused_post
    sys.modules["requests"] = requests_stub

if "bs4" not in sys.modules:
    bs4_stub = types.ModuleType("bs4")
    class _DummySoup:
        def __init__(self, *args, **kwargs):
            pass
    bs4_stub.BeautifulSoup = _DummySoup
    sys.modules["bs4"] = bs4_stub

from app import (
    SearchResult,
    dedupe_by_url,
    find_agencies,
    find_people_for_agency,
    is_linkedin_company,
    is_linkedin_profile,
    parse_agency_name,
)


def test_linkedin_url_detection():
    assert is_linkedin_company("https://www.linkedin.com/company/acme/")
    assert not is_linkedin_company("https://www.linkedin.com/in/someone/")
    assert is_linkedin_profile("https://linkedin.com/in/jane-doe")
    assert not is_linkedin_profile("https://example.com")


def test_dedupe_by_url_removes_query_duplicates():
    results = [
        SearchResult(title="A", url="https://linkedin.com/in/x?trk=abc", snippet=""),
        SearchResult(title="A2", url="https://linkedin.com/in/x", snippet=""),
    ]
    deduped = dedupe_by_url(results)
    assert len(deduped) == 1


def test_parse_agency_name():
    assert parse_agency_name("Acme Agency | LinkedIn") == "Acme Agency"
    assert parse_agency_name("JustName") == "JustName"


def test_find_agencies_runs_fallback_tiers_and_dedupes(monkeypatch):
    seen_queries = []

    responses = {
        'site:linkedin.com/company (agency OR consultancy OR studio) "healthcare" "US" "Curava"': [],
        'site:linkedin.com/company (agency OR consultancy OR studio) "healthcare" "US"': [],
        'site:linkedin.com/company (agency OR consultancy OR studio) "healthcare" "Curava"': [
            SearchResult("A", "https://linkedin.com/company/acme/?trk=1", ""),
            SearchResult("B", "https://linkedin.com/company/acme/", ""),
            SearchResult("C", "https://linkedin.com/company/beta/", ""),
            SearchResult("X", "https://example.com/not-linkedin", ""),
        ],
        'site:linkedin.com/company (agency OR consultancy OR studio OR marketing OR growth) "healthcare"': [
            SearchResult("D", "https://linkedin.com/company/gamma/", "")
        ],
    }

    def fake_search(query, max_results):
        seen_queries.append(query)
        return responses[query]

    monkeypatch.setattr("app.search_duckduckgo", fake_search)

    results = find_agencies("Curava", "healthcare", "US", max_agencies=2)

    assert [r.url for r in results] == [
        "https://linkedin.com/company/acme/?trk=1",
        "https://linkedin.com/company/beta/",
    ]
    assert seen_queries == [
        'site:linkedin.com/company (agency OR consultancy OR studio) "healthcare" "US" "Curava"',
        'site:linkedin.com/company (agency OR consultancy OR studio) "healthcare" "US"',
        'site:linkedin.com/company (agency OR consultancy OR studio) "healthcare" "Curava"',
    ]


def test_find_people_runs_fallback_tiers_and_dedupes(monkeypatch):
    seen_queries = []

    responses = {
        'site:linkedin.com/in "Acme" (founder OR ceo OR "head of growth" OR "business development") "healthcare" "US"': [],
        'site:linkedin.com/in "Acme" (founder OR ceo OR "head of growth" OR "business development") "healthcare"': [],
        'site:linkedin.com/in "Acme" (founder OR ceo OR "head of growth" OR "business development") "US"': [
            SearchResult("P1", "https://linkedin.com/in/jane?trk=abc", ""),
            SearchResult("P2", "https://linkedin.com/in/jane", ""),
            SearchResult("P3", "https://linkedin.com/in/john", ""),
            SearchResult("NotProfile", "https://linkedin.com/company/acme", ""),
        ],
        'site:linkedin.com/in "Acme" (founder OR ceo OR owner OR principal OR partner OR "head of growth" OR "growth lead" OR "business development" OR "account director") "healthcare"': [
            SearchResult("P4", "https://linkedin.com/in/sam", "")
        ],
    }

    def fake_search(query, max_results):
        seen_queries.append(query)
        return responses[query]

    monkeypatch.setattr("app.search_duckduckgo", fake_search)

    results = find_people_for_agency("Acme", "healthcare", "US", max_people=2)

    assert [r.url for r in results] == [
        "https://linkedin.com/in/jane?trk=abc",
        "https://linkedin.com/in/john",
    ]
    assert seen_queries == [
        'site:linkedin.com/in "Acme" (founder OR ceo OR "head of growth" OR "business development") "healthcare" "US"',
        'site:linkedin.com/in "Acme" (founder OR ceo OR "head of growth" OR "business development") "healthcare"',
        'site:linkedin.com/in "Acme" (founder OR ceo OR "head of growth" OR "business development") "US"',
    ]
