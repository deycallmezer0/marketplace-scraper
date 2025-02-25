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
import re
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
    def get_marketplace_images(self, item_url, save_path=None):
        """
        Extracts and saves all images from a Facebook Marketplace listing.
        Skips the first image as it's a duplicate of the second.
        
        Args:
            item_url (str): URL of the marketplace listing
            save_path (str, optional): Directory to save images. Defaults to 'images/[listing_title]'
            
        Returns:
            list: List of image URLs found on the page
        """
        try:
            # Find all image elements in the product carousel
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "img.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x5yr21d.xl1xv1r.xh8yej3")
            
            print(f"Found {len(img_elements)} images")
            image_urls = []
            
            # Create directory for saving images if it doesn't exist
            if save_path and not os.path.exists(save_path):
                os.makedirs(save_path)
                
            # Skip first image (index 0) as it's a duplicate
            for i, img in enumerate(img_elements[1:], start=1):
                try:
                    # Extract the image URL from the src attribute
                    img_url = img.get_attribute("src")
                    if img_url:
                        image_urls.append(img_url)
                        print(f"Image {i}: {img_url}")
                        
                        # Save the image if a save path is provided
                        if save_path:
                            # Create a filename based on listing and image index
                            filename = f"image_{i}.jpg"
                            file_path = os.path.join(save_path, filename)
                            
                            # Download and save the image
                            import requests
                            img_data = requests.get(img_url).content
                            with open(file_path, 'wb') as f:
                                f.write(img_data)
                            print(f"Saved image to {file_path}")
                    
                except Exception as e:
                    print(f"Error processing image {i}: {str(e)}")
            
            return image_urls
            
        except Exception as e:
            print(f"Error extracting images: {str(e)}")
            return []
    def get_marketplace_item(self, item_url, task_id=None, task_statuses=None):
        """
        Main function to retrieve data from a Facebook Marketplace item.
        Updates task_statuses as data is retrieved if provided.
        Returns the data as a dictionary or None if an error occurs.
        """
        try:
            print(f"Getting item data from: {item_url}")
            self.driver.get(item_url)
            time.sleep(5)
            
            # Get basic item details
            title = self.get_page_title()
            
            # Update task status with title
            if task_id and task_statuses:
                task_statuses[task_id]["car_data"]["title"] = title
                task_statuses[task_id]["message"] = f"Found listing: {title}"
                
            # Click "See more" if available
            self.click_see_more_button()
            
            # Extract price, location, time posted
            basic_info = self.extract_basic_info()
            
            # Update task status with basic info
            if task_id and task_statuses:
                task_statuses[task_id]["car_data"]["price"] = basic_info.get("price", "Price not found")
                task_statuses[task_id]["car_data"]["location"] = basic_info.get("location", "Location not found")
                task_statuses[task_id]["car_data"]["description"] = basic_info.get("description", "")
                task_statuses[task_id]["message"] = "Found basic car info..."
            
            # Extract "About this vehicle" data
            about_data = self.extract_about_section()
            
            # Update task status with about data
            if task_id and task_statuses:
                task_statuses[task_id]["car_data"]["about"] = about_data
                task_statuses[task_id]["message"] = "Found vehicle details..."
            
            # Combine all data
            item_data = {
                    "title": title,
                    "price": basic_info.get("price", "Price not found"),
                    "location": basic_info.get("location", "Location not found"),
                    "time_posted": basic_info.get("time_posted", "Unknown"),
                    "description": basic_info.get("description", ""),
                    "mileage": basic_info.get("mileage", ""),
                    "url": item_url,
                    "about": about_data,
                    "id": task_id
                }
            
            # Extract and save images
            if task_id and task_statuses:
                task_statuses[task_id]["message"] = "Getting images..."
            
            image_urls = self.extract_and_save_images(title, item_url)
            item_data["images"] = image_urls
            
            # Update task status with images
            if task_id and task_statuses:
                task_statuses[task_id]["car_data"]["images"] = image_urls
                task_statuses[task_id]["message"] = f"Found {len(image_urls)} images"
            
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

    def get_page_title(self):
        """Extract and format the page title"""
        title = self.driver.title.replace("Marketplace - ", "")
        title = title.replace(" | Facebook", "")
        print(f"Page title: {title}")
        return title

    def click_see_more_button(self):
        """Handle clicking the 'See more' button with fallbacks"""
        try:
            see_more = self.driver.find_element(By.XPATH, "//span[contains(text(), 'See more')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", see_more)
            time.sleep(2)
            
            try:
                see_more.click()
            except Exception as click_error:
                print(f"Regular click failed, trying JavaScript click: {click_error}")
                self.driver.execute_script("arguments[0].click();", see_more)
            
            time.sleep(1)
        except NoSuchElementException:
            print("No 'See more' button found")

    def extract_basic_info(self):
        """Extract price, location, time posted, and description"""
        basic_info = {}
        
        # Get all text elements
        price_selector = 'div[role="main"] span[class*="x193iq5w"][dir="auto"]'
        price_elements = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, price_selector))
        )
        all_texts = [elem.text for elem in price_elements]
        
        # Extract price
        basic_info["price"] = next((text for text in all_texts if text.startswith("$")), "Price not found")
        
        # Extract location and time posted
        try:
            listing_info_elem = self.driver.find_element(By.XPATH, 
                "//span[contains(text(), 'Listed') and contains(text(), ' in ')]")
            
            if listing_info_elem:
                listing_info_text = listing_info_elem.text
                print(f"Listing info: {listing_info_text}")
                
                # Extract time posted
                if "ago" in listing_info_text:
                    time_parts = listing_info_text.split(" in ")[0].split("Listed ")
                    if len(time_parts) > 1:
                        basic_info["time_posted"] = time_parts[1].strip()
                    else:
                        basic_info["time_posted"] = "Unknown"
                else:
                    basic_info["time_posted"] = "Unknown"
                    
                # Extract location
                if " in " in listing_info_text:
                    basic_info["location"] = listing_info_text.split(" in ")[1].strip()
                else:
                    basic_info["location"] = "Location not found"
                    
                print(f"Extracted time: {basic_info['time_posted']}")
                print(f"Extracted location: {basic_info['location']}")
                
        except NoSuchElementException:
            print("Could not find listing info element")
            # Fallback method for location
            location_text = next((text for text in all_texts if re.search(r'[A-Z]{2}$', text) or 
                                re.search(r', [A-Z]{2}', text)), "Location not found")
            basic_info["location"] = location_text
            basic_info["time_posted"] = "Unknown"
        
        # Extract description (longest text)
        basic_info["description"] = max(all_texts, key=len)
        
        # Extract mileage
        basic_info["mileage"] = next((text for text in all_texts if "miles" in text.lower()), "")
        
        return basic_info

    def extract_about_section(self):
        """Extract 'About this vehicle' section details"""
        about_data = {}
        
        try:
            # Find the "About this vehicle" section
            about_section_header = self.driver.find_element(By.XPATH, 
                "//h2[contains(.//span, 'About this vehicle')]")

            # Get the parent div that contains all details
            about_section = about_section_header.find_element(By.XPATH, 
                "ancestor::div[contains(@class, 'xod5an3')]")
            print("About section found")

            # Get all the detail rows
            detail_elements = about_section.find_elements(By.CSS_SELECTOR, 
                "div.x78zum5.xdj266r.x1emribx.xat24cr.x1i64zmx.x1y1aw1k.x1sxyh0.xwib8y2.xurb0ha")
            print(f"Found {len(detail_elements)} details in about section")
            
            for element in detail_elements:
                try:
                    detail_text = element.find_element(By.CSS_SELECTOR, 
                        "div.xamitd3.x1r8uery.x1iyjqo2.xs83m0k.xeuugli span").text
                    print(f"Detail: {detail_text}")
                    
                    self.categorize_detail(about_data, detail_text)
                except Exception as e:
                    print(f"Error extracting detail: {str(e)}")
        except NoSuchElementException:
            print("About section not found")
        except Exception as e:
            print(f"Error extracting about section: {str(e)}")
            
        return about_data

    def categorize_detail(self, about_data, detail_text):
        """Categorize a detail text into the appropriate category"""
        if "miles" in detail_text.lower():
            about_data["mileage"] = detail_text
        elif "transmission" in detail_text.lower():
            about_data["transmission"] = detail_text
        elif "color" in detail_text.lower():
            about_data["color"] = detail_text
        elif "safety rating" in detail_text.lower():
            about_data["safety"] = detail_text
        elif "fuel type" in detail_text.lower():
            about_data["fuel_type"] = detail_text
        elif "mpg" in detail_text.lower():
            about_data["mpg"] = detail_text
        else:
            # For any other unclassified details
            about_data[f"detail_{len(about_data)}"] = detail_text

    def extract_and_save_images(self, title, item_url):
        """Extract and save marketplace images"""
        try:
            # Create a clean folder name based on the listing title
            folder_name = "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in title)
            folder_name = folder_name.replace(' ', '_')[:50]  # Limit length
            save_path = os.path.join("images", folder_name)
            
            # Get and save images
            return self.get_marketplace_images(item_url, save_path)
        except Exception as e:
            print(f"Error saving images: {str(e)}")
            return []
    def cleanup(self):
        """
        Closes the driver.
        """
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Failed to close driver: {str(e)}")
