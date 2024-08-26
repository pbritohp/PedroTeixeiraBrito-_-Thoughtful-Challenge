import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary
import time

class CustomSelenium:
    def __init__(self):
        self.driver = None  # Initialize the driver to None

    def set_webdriver(self):
        # This method sets up the Chrome WebDriver with various options and configurations
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode for cloud environments
            chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
            chrome_options.add_argument("--window-size=1920,1200")  # Set the window size
            chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
            chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

            # Path where ChromeDriver is expected to be located
            chrome_driver_path = os.getenv("CHROME_DRIVER_PATH", chromedriver_binary.chromedriver_filename)

            # Log the expected ChromeDriver path for debugging
            logging.info(f"Looking for ChromeDriver at: {chrome_driver_path}")

            # Check if ChromeDriver exists at the specified path
            if not os.path.exists(chrome_driver_path):
                logging.error(f"ChromeDriver not found at {chrome_driver_path}")
                raise FileNotFoundError(f"ChromeDriver not found at {chrome_driver_path}")

            # Log that ChromeDriver was found and is being used
            logging.info(f"Using ChromeDriver located at: {chrome_driver_path}")

            # Initialize the WebDriver with the ChromeDriver service
            service = Service(executable_path=chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("Chrome WebDriver initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Chrome WebDriver: {e}")
            self.driver = None  # Ensure the driver is None if initialization fails

    def open_url(self, url, screenshot=None):
        # Open a specified URL and optionally take a screenshot
        if self.driver is not None:
            try:
                self.driver.get(url)
                logging.info(f"Opened URL: {url}")
                if screenshot:
                    self.driver.save_screenshot(screenshot)
                    logging.info(f"Screenshot saved: {screenshot}")
            except Exception as e:
                logging.error(f"Failed to open URL {url}: {e}")
        else:
            logging.error("Driver not initialized.")

    def find_element(self, by, value):
        # Find a single element on the page using a locator
        try:
            return self.driver.find_element(by, value)
        except Exception as e:
            logging.error(f"Failed to find element: {e}")
            return None

    def find_elements(self, by, value):
        # Find multiple elements on the page using a locator
        try:
            return self.driver.find_elements(by, value)
        except Exception as e:
            logging.error(f"Failed to find elements: {e}")
            return []

    def click_element(self, element):
        # Click on the provided web element
        try:
            element.click()
        except Exception as e:
            logging.error(f"Failed to click element: {e}")

    def scroll_element_into_view(self, element):
        # Scroll the web element into view
        if element:
            self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def get_text(self, by, value):
        # Retrieve text content from a web element
        try:
            return self.driver.find_element(by, value).text
        except Exception as e:
            logging.error(f"Failed to get text: {e}")
            return ""

    def get_element_attribute(self, element, attribute_name):
        # Get a specific attribute from a web element
        try:
            return element.get_attribute(attribute_name)
        except Exception as e:
            logging.error(f"Failed to get element attribute: {e}")
            return ""

    def go_back(self):
        # Navigate back in the browser's history
        try:
            self.driver.back()
        except Exception as e:
            logging.error(f"Failed to go back: {e}")

    def wait_until_element_is_visible(self, by, value, timeout=10):
        # Wait until the specified element becomes visible
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        except Exception as e:
            logging.error(f"Wait until element is visible failed: {e}")

    def close_browser(self):
        # Close the browser and end the WebDriver session
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Browser closed successfully.")
            except Exception as e:
                logging.error(f"Failed to close browser: {e}")
    
    def retry_find_element(self, by, value, retries=3, delay=2):
        # Retry finding an element multiple times with a delay between attempts
        element = None
        for attempt in range(retries):
            try:
                element = self.find_element(by, value)
                if element:
                    break  # Exit loop if element is found
            except Exception as e:
                logging.warning(f"Retry {attempt + 1}/{retries}: Could not find element: {e}")
                time.sleep(delay)
        return element
