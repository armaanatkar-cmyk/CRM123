"""
LinkedIn Profile Scraper Module
Handles authenticated LinkedIn scraping and profile extraction
"""

import time
import re
from typing import Optional, List, Dict
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd


class LinkedInScraper:
    """Handles LinkedIn login and profile scraping"""

    def __init__(self, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.logged_in = False

    def init_driver(self) -> webdriver.Chrome:
        """Initialize Chrome WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver

    def login(self, email: str, password: str, timeout: int = 30) -> bool:
        """
        Login to LinkedIn
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            timeout: Max time to wait for login (seconds)
            
        Returns:
            bool: True if login successful
        """
        if not self.driver:
            self.init_driver()

        try:
            self.driver.get("https://www.linkedin.com/login")
            wait = WebDriverWait(self.driver, timeout)

            # Enter email
            email_field = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)

            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)

            # Click login
            login_button = self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Sign in']"
            )
            login_button.click()

            # Wait for page to load after login
            time.sleep(5)
            
            # Check if we're logged in by looking for the feed or home element
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-test-id='home-logo']")
                    )
                )
                self.logged_in = True
                return True
            except:
                st.error("Login verification failed. Please check your credentials.")
                return False

        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return False

    def search_profiles(
        self,
        keywords: str,
        location: str = "",
        current_company: str = "",
        max_results: int = 50,
    ) -> List[Dict]:
        """
        Search for LinkedIn profiles matching criteria
        
        Args:
            keywords: Search keywords (skills, interests, etc.)
            location: Geographic location filter
            current_company: Company filter
            max_results: Maximum profiles to return
            
        Returns:
            List of profile dictionaries with extracted data
        """
        if not self.logged_in:
            st.error("Not logged in. Please login first.")
            return []

        profiles = []
        try:
            # Build search URL
            search_query = keywords
            if location:
                search_query += f" in {location}"
            if current_company:
                search_query += f" at {current_company}"

            # LinkedIn search URL
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            self.driver.get(search_url)
            time.sleep(3)

            # Scroll and extract profiles
            results_count = 0
            while results_count < max_results:
                # Extract profile elements
                profile_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.base-search-card"
                )

                for element in profile_elements:
                    if results_count >= max_results:
                        break

                    try:
                        profile_data = self._extract_profile_data(element)
                        if profile_data:
                            profiles.append(profile_data)
                            results_count += 1
                    except Exception as e:
                        continue

                # Scroll to load more
                if results_count < max_results:
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(2)

        except Exception as e:
            st.error(f"Error searching profiles: {str(e)}")

        return profiles

    def _extract_profile_data(self, element) -> Optional[Dict]:
        """Extract profile information from a profile card element"""
        try:
            # Extract name
            name_elem = element.find_element(By.CSS_SELECTOR, "span.name")
            name = name_elem.text if name_elem else "N/A"

            # Extract headline/title
            headline_elem = element.find_element(By.CSS_SELECTOR, "p.headline")
            headline = headline_elem.text if headline_elem else "N/A"

            # Extract subheadline (company)
            subheadline_elem = element.find_element(
                By.CSS_SELECTOR, "p.subline-level-1"
            )
            company = subheadline_elem.text if subheadline_elem else "N/A"

            # Extract profile URL
            link_elem = element.find_element(By.CSS_SELECTOR, "a.app-aware-link")
            profile_url = link_elem.get_attribute("href") if link_elem else "N/A"

            return {
                "name": name,
                "title": headline,
                "company": company,
                "url": profile_url,
                "snippet": f"{headline} at {company}",
            }

        except Exception as e:
            return None

    def get_profile_details(self, profile_url: str) -> Optional[Dict]:
        """
        Get detailed information from a profile page
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            Dictionary with profile details
        """
        if not self.logged_in:
            st.error("Not logged in.")
            return None

        try:
            self.driver.get(profile_url)
            time.sleep(3)

            details = {}

            # Extract name
            try:
                name = self.driver.find_element(
                    By.CSS_SELECTOR, "h1.text-heading-xlarge"
                ).text
                details["name"] = name
            except:
                details["name"] = "N/A"

            # Extract headline
            try:
                headline = self.driver.find_element(
                    By.CSS_SELECTOR, "div.text-body-medium"
                ).text
                details["headline"] = headline
            except:
                details["headline"] = "N/A"

            # Extract location
            try:
                location = self.driver.find_element(
                    By.CSS_SELECTOR, "span.text-body-small.inline"
                ).text
                details["location"] = location
            except:
                details["location"] = "N/A"

            # Extract about
            try:
                about = self.driver.find_element(
                    By.CSS_SELECTOR, "section.summary"
                ).text
                details["about"] = about[:500]  # Limit to 500 chars
            except:
                details["about"] = "N/A"

            details["url"] = profile_url

            return details

        except Exception as e:
            st.error(f"Error getting profile details: {str(e)}")
            return None

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.logged_in = False

    def __enter__(self):
        self.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def scrape_linkedin_profiles(
    email: str,
    password: str,
    keywords: str,
    location: str = "",
    company: str = "",
    max_results: int = 30,
) -> pd.DataFrame:
    """
    Convenience function to scrape LinkedIn profiles
    
    Returns a DataFrame with profile information
    """
    scraper = LinkedInScraper(headless=True)

    try:
        with st.spinner("Logging into LinkedIn..."):
            if not scraper.login(email, password):
                return pd.DataFrame()

        with st.spinner(f"Searching for profiles matching '{keywords}'..."):
            profiles = scraper.search_profiles(
                keywords=keywords,
                location=location,
                current_company=company,
                max_results=max_results,
            )

        if profiles:
            return pd.DataFrame(profiles)
        else:
            return pd.DataFrame()

    finally:
        scraper.close()
