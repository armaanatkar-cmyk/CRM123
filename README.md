# Curava ICP Finder (LinkedIn Link Discovery)

A lightweight Streamlit app that helps Curava discover target agencies (ICP-fit) and likely employee profiles in a couple clicks.

## What it does

1. Finds LinkedIn **agency/company** URLs using public web search.
2. Enriches each agency with likely **employee/profile** URLs.
3. Provides direct profile links and CSV export for outreach workflows.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Usage

- Step 1: Click **Find Target Agencies**.
- Step 2: Click **Find Employees for Listed Agencies**.
- Export via **Download CSV**.

## Notes

- This app uses public search-result links and does not log in to LinkedIn.
- You are responsible for complying with platform Terms of Service and local privacy/outreach regulations.
