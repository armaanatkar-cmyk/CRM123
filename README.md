# Curava ICP Finder (Enhanced LinkedIn Discovery Tool)

A powerful Streamlit app for discovering target agencies, companies, and potential leads on LinkedIn. Features both public search and authenticated scraping capabilities.

## 🎯 Features

- **Agency-Based Search**: Find target agencies and their employees based on ICP criteria
- **Keyword-Based Search**: Search for profiles matching specific keywords using public search
- **LinkedIn Direct Search**: Authenticate and scrape LinkedIn profiles directly (requires credentials)
- **CSV Export**: Download all results for your outreach workflows
- **Profile Enrichment**: Extract and organize profile data including name, title, company, and URL

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser (for LinkedIn direct search)
- LinkedIn account (for authenticated scraping)

### Installation

```bash
# Clone or navigate to project directory
cd CRM123

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Agency-Based Search (Recommended - No Login Required)
- **Step 1**: Enter your startup name, target ICP, and region
- **Step 2**: Click "Find Target Agencies" to discover relevant companies
- **Step 3**: Click "Find Employees" to discover decision-makers at those agencies
- **Step 4**: Download results as CSV

### 2. Keyword-Based Search (No Login Required)
- Select "Keyword-Based Search" mode
- Enter search keywords (e.g., "growth marketer healthcare")
- Filter by job titles and location
- Click search and download results

### 3. LinkedIn Direct Search (Requires Credentials)
- Select "LinkedIn Direct Search" mode
- ⚠️ Enter your LinkedIn email and password (secure - not stored)
- Enter search parameters (keywords, location, company filter)
- Click "Search LinkedIn Directly" to scrape profiles
- Download authenticated results

## 🔒 Security & Privacy

- **Credentials**: LinkedIn credentials are NOT stored or logged
- **Session-Based**: All data is cleared when you close the browser
- **Terms of Service**: Ensure compliance with LinkedIn ToS before using authenticated scraping
- **Rate Limiting**: Be mindful of LinkedIn's rate limits when scraping

## 🐛 Bug Fixes & Improvements

### Fixed Issues
✅ Code formatting and line break issues  
✅ Error handling for network failures  
✅ Improved data deduplication logic  
✅ Better session state management  
✅ Enhanced UI/UX with emoji indicators  

### New Features Added
✨ LinkedIn authenticated scraping capability  
✨ Dual search modes (public + private)  
✨ Profile enrichment with structured data  
✨ Flexible filtering options  
✨ Better error messages and guidance  

## 📁 Project Structure

```
CRM123/
├── app.py                    # Main Streamlit application
├── linkedin_scraper.py       # LinkedIn authentication & scraping module
├── requirements.txt          # Python dependencies
├── test_app.py              # Unit tests
├── README.md                # This file
└── .venv/                   # Virtual environment
```

## 🔧 Dependencies

- **streamlit**: Web app framework
- **pandas**: Data manipulation
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **selenium**: Browser automation for LinkedIn
- **webdriver-manager**: Automated ChromeDriver management
- **python-linkedin-api**: LinkedIn API utilities

## 📊 Output Format

Results include:
- **Name**: Profile or agency name
- **Title/Headline**: Current job title or agency type
- **Company**: Current company or agency name
- **URL**: Direct LinkedIn profile/company link
- **Snippet**: Brief description or headline

All data is exportable to CSV format for CRM integration.

## ⚠️ Important Notes

1. **LinkedIn Compliance**: This tool respects LinkedIn's public API guidelines. Ensure you comply with:
   - LinkedIn User Agreement
   - LinkedIn API Terms of Service
   - Local privacy and data protection laws (GDPR, CCPA, etc.)

2. **Rate Limiting**: LinkedIn may throttle or block excessive requests. Use reasonable search volumes.

3. **Bot Detection**: LinkedIn actively detects automated access. Use authenticated mode with valid credentials.

4. **Data Privacy**: Do not use scraped data for purposes beyond legitimate B2B outreach.

## 🆘 Troubleshooting

### "Login verification failed"
- Check credentials are correct
- LinkedIn may require additional verification (2FA, CAPTCHA)
- Try using the Keyword-Based Search mode instead

### "No profiles found"
- Try different keywords
- LinkedIn search may have limited results
- Adjust location or company filters

### "Chrome driver error"
- Ensure Chrome/Chromium is installed
- The tool will auto-download ChromeDriver
- Check for system permission issues

### "Request timeout"
- DuckDuckGo search is slow - wait for results
- Check your internet connection
- Try fewer max results

## 🔄 Workflow Example

```
1. Find agencies in healthcare marketing space
   → Use Agency-Based Search with startup="Curava", ICP="healthcare marketing"

2. Extract decision-makers from discovered agencies
   → Click "Find Employees" to get CEO, CMO, Growth Lead contacts

3. Search for additional prospects using LinkedIn
   → Switch to LinkedIn Direct Search for authenticated access
   → Search for "VP Marketing" + "healthcare" in target regions

4. Export & Organize
   → Download all results as CSV
   → Import into your CRM or email tool
   → Begin outreach campaign
```

## 📝 Notes

- This is an enhanced version of the original Curava ICP Finder
- Added LinkedIn authenticated scraping (beta)
- Improved error handling and UI/UX
- All search results point to public LinkedIn profiles
- Respect rate limits and platform guidelines

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the usage guide
3. Ensure all dependencies are installed
4. Verify Python 3.8+ is being used

---

**Last Updated**: February 18, 2026  
**Version**: 2.0 (Enhanced with LinkedIn Scraping)
