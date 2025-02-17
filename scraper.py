# scraper.py

import os
import json
import random
import time
from typing import Dict, Optional

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

class FacebookMarketplaceScraper:
    def __init__(self):
        """Initialize the scraper with a Chrome driver."""
        self._initialize_driver()
        self.is_logged_in = False

    def _initialize_driver(self):
        """Initialize the Chrome driver with options and wait."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def random_delay(self):
        """Add a random delay between 1 and 3 seconds."""
        time.sleep(random.uniform(1, 3))

    def ensure_logged_in(self) -> bool:
        """Ensure the scraper is logged in."""
        if not self.is_logged_in:
            self.is_logged_in = self.login_flow()
        return self.is_logged_in

    def save_cookies(self):
        """Save the current cookies to a file."""
        with open("facebook_cookies.json", "w") as f:
            json.dump(self.driver.get_cookies(), f)
        print("Session saved")

    def load_cookies(self) -> bool:
        """Load cookies from a file if they exist."""
        if os.path.exists("facebook_cookies.json"):
            self.driver.get("https://facebook.com")
            with open("facebook_cookies.json", "r") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            return True
        return False

    def verify_login(self) -> bool:
        """Verify if the scraper is logged in."""
        try:
            self.driver.get("https://facebook.com")
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Facebook"]'))
            )
            return True
        except Exception:
            return False

    def manual_login(self):
        """Manually log in the scraper."""
        print("Please log in manually")
        self.driver.get("https://facebook.com")
        input(
            "Press Enter after you've logged in completely (including 2FA if needed)..."
        )
        self.save_cookies()

    def login_flow(self) -> bool:
        """Handle the login flow, trying to load saved cookies first."""
        if self.load_cookies() and self.verify_login():
            print("Loaded saved session")
            return True

        try:
            self.manual_login()
            if self.verify_login():
                return True
            else:
                print("Login verification failed after manual login")
                return False
        except Exception as e:
            self.log_error("Error during login", str(e))
            return False

    def get_marketplace_item(self, item_url: str) -> Optional[Dict]:
        """Retrieve data for a marketplace item."""
        if not self.ensure_logged_in():
            raise Exception("Failed to log in")
        try:
            self.driver.get(item_url)
            time.sleep(2)

            title = self.driver.title.replace("Marketplace - ", "")
            print(f"Page title: {title}")

            try:
                see_more = self.driver.find_element(By.XPATH, "//span[contains(text(), 'See more')]")
                see_more.click()
                time.sleep(1)
            except:
                print("No 'See more' button found or couldn't click it")

            price_selector = 'div[role="main"] span[class*="x193iq5w"][dir="auto"]'
            price_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, price_selector))
            )

            all_texts = [elem.text for elem in price_elements]

            price = next((text for text in all_texts if text.startswith("$")), "Price not found")
            location_text = next((text for text in all_texts if "OH" in text), "Location not found")
            location = location_text.split("in ")[-1].strip() if "in " in location_text else location_text.split("OH")[0].strip() + ", OH"
            mileage = next((text for text in all_texts if "miles" in text.lower()), "Mileage not found")
            description = max(all_texts, key=len)

            item_data = {
                "title": title,
                "price": price,
                "location": location,
                "mileage": mileage,
                "description": description,
                "url": item_url,
            }

            print("\nData retrieved:")
            for key, value in item_data.items():
                print(f"{key}: {value}")

            return item_data

        except TimeoutException:
            self.log_error("Timeout while trying to load item", item_url)
            return None
        except Exception as e:
            self.log_error("Error while getting item data", str(e))
            return None

    def cleanup(self):
        """Clean up the driver."""
        try:
            self.driver.quit()
        except Exception as e:
            self.log_error("Error during cleanup", str(e))

    def log_error(self, message: str, detail: str):
        """Log an error with a generic message."""
        print(f"ERROR: {message} - Details: {detail}")