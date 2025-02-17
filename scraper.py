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

load_dotenv()

class FacebookMarketplaceScraper:
    def __init__(self):
        self._initialize_driver()
        self.is_logged_in = False
        
    def _initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def random_delay(self):
        time.sleep(random.uniform(1, 3))
    def ensure_logged_in(self):
        if not self.is_logged_in:
            self.is_logged_in = self.login_flow()
        return self.is_logged_in
        
    def save_cookies(self):
        with open('facebook_cookies.pkl', 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)
        print("Session saved")
            
    def load_cookies(self):
        if os.path.exists('facebook_cookies.pkl'):
            self.driver.get('https://facebook.com')
            with open('facebook_cookies.pkl', 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            return True
        return False

    def verify_login(self):
        try:
            self.driver.get('https://facebook.com')
            # Wait for and check for an element that only exists when logged in
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Facebook"]')))
            return True
        except Exception as e:
            return False

    def manual_login(self):
        print("Please log in manually")
        self.driver.get('https://facebook.com')
        input("Press Enter after you've logged in completely (including 2FA if needed)...")
        self.save_cookies()
        
    def login_flow(self):
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
            print(f"Error during login: {str(e)}")
            return False

    def get_marketplace_item(self, item_url):
        if not self.ensure_logged_in():
            raise Exception("Failed to log in")
        try:
            self.driver.get(item_url)
            time.sleep(2)

            # Get title from browser title and clean it
            title = self.driver.title
            title = title.replace("Marketplace - ", "")
            print(f"Page title: {title}")

            # Try to click "See more" if it exists
            try:
                see_more = self.driver.find_element(By.XPATH, "//span[contains(text(), 'See more')]")
                see_more.click()
                time.sleep(1)  # Wait for text to expand
            except:
                print("No 'See more' button found or couldn't click it")

            # Get the rest of the data
            price_selector = 'div[role="main"] span[class*="x193iq5w"][dir="auto"]'
            price_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, price_selector))
            )
            
            all_texts = [elem.text for elem in price_elements]
            
            # Price is the text that starts with $
            price = next((text for text in all_texts if text.startswith('$')), "Price not found")
            
            # Location - find text with 'OH' and clean it
            location_text = next((text for text in all_texts if "OH" in text), "Location not found")
            if "in " in location_text:
                location = location_text.split("in ")[-1].strip()
            else:
                location = location_text.split("OH")[0].strip() + ", OH"
            
            # Get mileage - look for text containing "miles"
            mileage = next((text for text in all_texts if "miles" in text.lower()), "Mileage not found")
            
            # Description is the longest text (now should include expanded content)
            description = max(all_texts, key=len)
            
            item_data = {
                'title': title,
                'price': price,
                'location': location,
                'mileage': mileage,
                'description': description,
                'url': item_url
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
        try:
            self.driver.quit()
        except:
            pass