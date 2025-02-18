# scraper.py

import os
import time
import random
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import json
from selenium.common.exceptions import NoSuchElementException

load_dotenv()

class FacebookMarketplaceScraper:
    """
    A class to scrape data from Facebook Marketplace.
    """

    def __init__(self, force_visible=False):
        """
        Initializes the scraper with a Chrome driver.
        Args:
            force_visible (bool): Force browser to be visible regardless of login status
        """
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Check if cookies exist - if they don't, we'll need visible mode for login
        self.needs_visible = force_visible or not os.path.exists("facebook_cookies.json")
        
        if not self.needs_visible:
            self.chrome_options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def random_delay(self):
        """
        Adds a random delay between 1 and 3 seconds.
        """
        time.sleep(random.uniform(1, 3))

    def save_cookies(self):
        """
        Saves the current cookies to a file.
        """
        with open("facebook_cookies.json", "w") as f:
            json.dump(self.driver.get_cookies(), f)
        print("Session saved")

    def load_cookies(self):
        """
        Loads cookies from a file if they exist.
        Returns True if successful, False otherwise.
        """
        if os.path.exists("facebook_cookies.json"):
            self.driver.get("https://facebook.com")
            with open("facebook_cookies.json", "r") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            return True
        return False

    def verify_login(self):
        """
        Verifies if the user is logged in by checking for a specific element.
        Returns True if logged in, False otherwise.
        """
        try:
            self.driver.get("https://facebook.com")
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Facebook"]'))
            )
            return True
        except Exception as e:
            return False

    def manual_login(self):
        """
        Prompts the user to log in manually and saves cookies.
        """
        print("Please log in manually")
        self.driver.get("https://facebook.com")
        input(
            "Press Enter after you've logged in completely (including 2FA if needed)..."
        )
        self.save_cookies()

    def login_flow(self):
        """
        Attempts to log in using saved cookies or manual login.
        If login fails with headless mode, reopens in visible mode.
        Returns True if successful, False otherwise.
        """
        if self.load_cookies() and self.verify_login():
            print("Loaded saved session")
            return True

        # If we're in headless mode and login failed, restart in visible mode
        if not self.needs_visible:
            print("Login failed in headless mode, switching to visible mode...")
            self.driver.quit()
            self.chrome_options.remove_argument("--headless")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                        options=self.chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

        try:
            self.manual_login()
            if self.verify_login():
                return True
            else:
                print("Login verification failed after manual login")
                return False
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False

    def get_marketplace_item(self, item_url):
        """
        Retrieves data from a Facebook Marketplace item.
        Returns the data as a dictionary or None if an error occurs.
        """
        try:
            print(f"Getting item data from: {item_url}")
            self.driver.get(item_url)
            time.sleep(5)

            title = self.driver.title.replace("Marketplace - ", "")
            title = title.replace(" | Facebook", "")
            print(f"Page title: {title}")

            try:
                see_more = self.driver.find_element(By.XPATH, "//span[contains(text(), 'See more')]")
                see_more.click()
                time.sleep(1)
            except NoSuchElementException:
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
            print(f"Timeout while trying to load item: {item_url}")
            return None
        except Exception as e:
            print(f"Error while getting item data: {str(e)}")
            return None

    def cleanup(self):
        """
        Closes the driver.
        """
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Failed to close driver: {str(e)}")
