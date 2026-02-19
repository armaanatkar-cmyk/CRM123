from app import SearchResult, dedupe_by_url, is_linkedin_company, is_linkedin_profile, parse_agency_name


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
