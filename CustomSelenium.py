
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class CustomSelenium:
    def __init__(self):
        self.driver = None

    def set_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1200")
        self.driver = webdriver.Chrome(options=chrome_options)

    def open_url(self, url, screenshot=None):
        self.driver.get(url)
        if screenshot:
            self.driver.save_screenshot(screenshot)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def click_element(self, element):
        element.click()

    def scroll_element_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def get_text(self, by, value):
        return self.driver.find_element(by, value).text

    def get_element_attribute(self, element, attribute_name):
        return element.get_attribute(attribute_name)

    def go_back(self):
        self.driver.back()

    def wait_until_element_is_visible(self, by, value, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )

    def close_browser(self):
        if self.driver:
            self.driver.quit()
