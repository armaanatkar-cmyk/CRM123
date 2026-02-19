import re
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
}


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def search_duckduckgo(query: str, max_results: int = 15) -> list[SearchResult]:
    """Return web results from DuckDuckGo HTML endpoint."""
    response = requests.post(
        DUCKDUCKGO_HTML_URL,
        data={"q": query},
        headers=DEFAULT_HEADERS,
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: list[SearchResult] = []

    for result in soup.select("div.result"):
        anchor = result.select_one("a.result__a")
        snippet_tag = result.select_one("a.result__snippet") or result.select_one(
            "div.result__snippet"
        )
        if not anchor:
            continue

        title = anchor.get_text(strip=True)
        url = anchor.get("href", "").strip()
        snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""

        if not url:
            continue

        results.append(SearchResult(title=title, url=url, snippet=snippet))
        if len(results) >= max_results:
            break

    return results


def is_linkedin_company(url: str) -> bool:
    return bool(re.search(r"linkedin\.com/company/", url, flags=re.IGNORECASE))


def is_linkedin_profile(url: str) -> bool:
    return bool(re.search(r"linkedin\.com/in/", url, flags=re.IGNORECASE))


def dedupe_by_url(results: Iterable[SearchResult]) -> list[SearchResult]:
    seen: set[str] = set()
    deduped: list[SearchResult] = []
    for item in results:
        canonical = item.url.split("?")[0].rstrip("/")
        if canonical in seen:
            continue
        seen.add(canonical)
        deduped.append(item)
    return deduped


def find_agencies(startup: str, icp: str, region: str, max_agencies: int) -> list[SearchResult]:
    tier_queries = [
        (
            f'site:linkedin.com/company (agency OR consultancy OR studio) "{icp}" '
            f'"{region}" "{startup}"'
        ),
        (
            f'site:linkedin.com/company (agency OR consultancy OR studio) "{icp}" '
            f'"{region}"'
        ),
        (
            f'site:linkedin.com/company (agency OR consultancy OR studio) "{icp}" '
            f'"{startup}"'
        ),
        f'site:linkedin.com/company (agency OR consultancy OR studio OR marketing OR growth) "{icp}"',
    ]

    companies: list[SearchResult] = []
    for query in tier_queries:
        results = search_duckduckgo(query=query, max_results=max_agencies * 3)
        companies.extend(result for result in results if is_linkedin_company(result.url))
        if companies:
            break

    return dedupe_by_url(companies)[:max_agencies]


def find_people_for_agency(
    agency_name: str,
    icp: str,
    region: str,
    max_people: int,
) -> list[SearchResult]:
    base_roles = '(founder OR ceo OR "head of growth" OR "business development")'
    broad_roles = (
        '(founder OR ceo OR owner OR principal OR partner OR '
        '"head of growth" OR "growth lead" OR "business development" OR "account director")'
    )
    tier_queries = [
        f'site:linkedin.com/in "{agency_name}" {base_roles} "{icp}" "{region}"',
        f'site:linkedin.com/in "{agency_name}" {base_roles} "{icp}"',
        f'site:linkedin.com/in "{agency_name}" {base_roles} "{region}"',
        f'site:linkedin.com/in "{agency_name}" {broad_roles} "{icp}"',
    ]

    people: list[SearchResult] = []
    for query in tier_queries:
        results = search_duckduckgo(query=query, max_results=max_people * 3)
        people.extend(result for result in results if is_linkedin_profile(result.url))
        if people:
            break

    return dedupe_by_url(people)[:max_people]


def results_to_dataframe(results: list[SearchResult], kind: str) -> pd.DataFrame:
    rows = []
    for entry in results:
        rows.append(
            {
                "type": kind,
                "title": entry.title,
                "url": entry.url,
                "snippet": entry.snippet,
                "connect_link": entry.url,
            }
        )
    return pd.DataFrame(rows)


def parse_agency_name(title: str) -> str:
    # Typical format: "Agency Name | LinkedIn"
    if "|" in title:
        return title.split("|")[0].strip()
    return title.strip()


def main() -> None:
    st.set_page_config(page_title="Curava ICP Finder", page_icon="🎯", layout="wide")
    st.title("🎯 Curava ICP Finder")
    st.caption(
        "Discover agency ICP targets and likely employees with public web search links in a couple clicks."
    )

    with st.sidebar:
        st.header("Search Inputs")
        startup = st.text_input("Startup Name", value="Curava")
        icp = st.text_input("Target ICP", value="healthcare marketing")
        region = st.text_input("Region", value="United States")
        max_agencies = st.slider("Max agencies", 5, 50, 15)
        max_people = st.slider("Max employees per agency", 2, 15, 5)

    if "agencies_df" not in st.session_state:
        st.session_state.agencies_df = pd.DataFrame()
    if "people_df" not in st.session_state:
        st.session_state.people_df = pd.DataFrame()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("1) Find Target Agencies", type="primary", use_container_width=True):
            with st.spinner("Searching for agencies..."):
                agency_results = find_agencies(startup, icp, region, max_agencies)
                st.session_state.agencies_df = results_to_dataframe(agency_results, "agency")
            st.success(f"Found {len(st.session_state.agencies_df)} agency links")

    with col2:
        if st.button("2) Find Employees for Listed Agencies", use_container_width=True):
            if st.session_state.agencies_df.empty:
                st.warning("Run step 1 first so we know which agencies to enrich.")
            else:
                with st.spinner("Searching employee profiles..."):
                    people: list[SearchResult] = []
                    for agency_title in st.session_state.agencies_df["title"].tolist():
                        agency_name = parse_agency_name(agency_title)
                        people.extend(
                            find_people_for_agency(
                                agency_name=agency_name,
                                icp=icp,
                                region=region,
                                max_people=max_people,
                            )
                        )
                    st.session_state.people_df = results_to_dataframe(
                        dedupe_by_url(people), "person"
                    )
                st.success(f"Found {len(st.session_state.people_df)} employee profile links")

    st.divider()
    st.subheader("Agency Results")
    st.dataframe(st.session_state.agencies_df, use_container_width=True)

    st.subheader("Employee Results")
    st.dataframe(st.session_state.people_df, use_container_width=True)

    if not st.session_state.agencies_df.empty or not st.session_state.people_df.empty:
        combined = pd.concat(
            [st.session_state.agencies_df, st.session_state.people_df],
            ignore_index=True,
        )
        st.download_button(
            "Download CSV",
            data=combined.to_csv(index=False).encode("utf-8"),
            file_name="curava_icp_targets.csv",
            mime="text/csv",
        )

    st.info(
        "This tool uses public search-result links only. Respect each platform's Terms of Service and privacy laws before outreach."
    )


if __name__ == "__main__":
    main()
