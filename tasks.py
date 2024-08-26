from RPA.Robocorp.WorkItems import WorkItems
import logging
import re
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import os
from CustomSelenium import CustomSelenium
from selenium.webdriver.common.by import By

# Set up logging to capture detailed information during execution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self, search_phrase, months):
        self.browser = CustomSelenium()  # Initialize the custom Selenium wrapper
        self.browser.set_webdriver()  # Set up the Selenium WebDriver
        self.search_phrase = search_phrase
        self.months = months
        self.news_data = []  # List to store scraped news data
        self.processed_urls = set()  # Set to keep track of processed URLs

    def calculate_date_range(self):
        # Calculate the date range based on the number of months specified
        end_date = datetime.now()
        if self.months <= 1:
            start_date = end_date.replace(day=1)
        else:
            start_date = end_date - relativedelta(months=self.months - 1)
            start_date = start_date.replace(day=1)
        return start_date, end_date

    def is_within_date_range(self, date_text, start_date, end_date):
        # Check if the article's published date is within the calculated date range
        try:
            date_text = date_text.split(' at ')[0]
            date_format = "%b %d, %Y"
            article_date = datetime.strptime(date_text, date_format)
            return start_date <= article_date <= end_date
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return False

    def find_and_scroll_to_date(self):
        # Locate and scroll to the date element on the article page
        try:
            date_element = self.browser.find_element(By.CLASS_NAME, "date-published")
            if not date_element:
                logger.error("Date element not found.")
                return None
            self.browser.scroll_element_into_view(date_element)
            time.sleep(2)
            published_date_element = date_element.find_element(By.XPATH, ".//p[contains(text(),'Published')]")
            if not published_date_element:
                logger.error("Published date element not found.")
                return None
            date_text = published_date_element.text.replace("Published ", "")
            logger.info(f"Published Date: {date_text}")
            return date_text
        except Exception as e:
            logger.error(f"Error finding or scrolling to date element: {e}")
            return None

    def load_more_articles(self):
        # Click the "Load More" button to fetch more articles on the search results page
        try:
            load_more_button = self.browser.find_element(By.CSS_SELECTOR, "button.p-button.p-component.p-button-rounded[aria-label='Load More']")
            self.browser.scroll_element_into_view(load_more_button)
            self.browser.driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(10)
            logger.info("Clicked 'Load More' button")
            return True
        except Exception as e:
            logger.info("No 'Load More' button found, no more articles to load.")
            return False

    def save_article_image(self):
        # Save the article's image locally and return the filename
        try:
            output_directory = os.getenv("ROBOT_ARTIFACTS", "output/image_folder")
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
                logging.info(f"Created image folder: {output_directory}")
            image_element = self.browser.retry_find_element(By.CSS_SELECTOR, "div.image-with-caption-image img")
            if image_element:
                self.browser.scroll_element_into_view(image_element)
                time.sleep(5)
                image_filename = os.path.join(output_directory, f"news_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                image_element.screenshot(image_filename)
                logging.info(f"Image saved as: {image_filename}")
                return image_filename
            else:
                logging.warning("No image element found.")
                return None
        except Exception as e:
            logging.warning(f"No image found or failed to save image: {e}")
            return None

    def start_search(self):
        # Start the search process by opening the search URL
        search_url = f"https://gothamist.com/search?q={self.search_phrase.replace(' ', '+')}"
        logger.info("Opening the browser.")
        self.browser.open_url(search_url)
        time.sleep(10)
        start_date, end_date = self.calculate_date_range()
        try:
            while True:
                # Find and process each article in the search results
                articles = self.browser.find_elements(By.CSS_SELECTOR, "a.flexible-link.internal.card-title-link")
                found_urls = [article.get_attribute('href') for article in articles]
                logger.info(f"Found article URLs: {found_urls}")
                article_index = 0
                while article_index < len(found_urls):
                    article_url = found_urls[article_index]
                    if article_url in self.processed_urls:
                        logger.info(f"Skipping already processed URL: {article_url}")
                        article_index += 1
                        continue
                    logger.info(f"Navigating to article {article_index + 1}: {article_url}")
                    self.browser.open_url(article_url)
                    time.sleep(10)
                    self.processed_urls.add(article_url)
                    title = self.browser.get_text(By.CSS_SELECTOR, "h1.mt-4.mb-3.h2")
                    logger.info(f"Title: {title}")
                    date_text = self.find_and_scroll_to_date()
                    logger.info(f"Published Date: {date_text}")
                    if not self.is_within_date_range(date_text, start_date, end_date):
                        logger.info("Article not within the date range. Stopping search.")
                        break
                    try:
                        description = self.browser.get_text(By.CSS_SELECTOR, "div.streamfield.article-body div.streamfield-paragraph.rte-text")
                        logger.info(f"Description: {description}")
                    except Exception as e:
                        description = None
                        logger.error(f"Error finding description: {e}")
                    image_filename = self.save_article_image()
                    search_phrase_count = title.lower().count(self.search_phrase.lower()) + (description.lower().count(self.search_phrase.lower()) if description else 0)
                    logger.info(f"Search phrase count: {search_phrase_count}")
                    money_pattern = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?|(?:\d{1,3}(?:,\d{3})*(?:\.\d{2})? (?:dollars|USD))"
                    contains_money = bool(re.search(money_pattern, title)) or bool(re.search(money_pattern, description))
                    logger.info(f"Contains money: {contains_money}")
                    self.news_data.append({
                        "Title": title,
                        "Date": date_text,
                        "Description": description,
                        "Image Filename": image_filename,
                        "Search Phrase Count": search_phrase_count,
                        "Contains Money": contains_money
                    })
                    self.browser.go_back()
                    time.sleep(20)
                    article_index += 1
                if not self.load_more_articles():
                    break
            # Save the collected data to an Excel file
            logger.info(f"Total articles processed: {len(self.news_data)}")
            output_directory = os.getenv("ROBOT_ARTIFACTS", "output")
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            output_file = os.path.join(output_directory, "news_data.xlsx")
            df = pd.DataFrame(self.news_data)
            logger.info(df.head())
            df.to_excel(output_file, index=False)
            logger.info(f"Saved results to {output_file}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            self.browser.close_browser()

def main():
    # Initialize the WorkItems object to manage inputs and outputs
    work_items = WorkItems()
    work_items.get_input_work_item()  # Load the input work item
    for item in work_items.inputs:
        logger.info(f"Work item payload: {item.payload}")
        # Check and retrieve 'search_phrase' and 'months' from the payload
        search_phrase = item.payload.get("search_phrase")
        months = item.payload.get("months")
        if not search_phrase or months is None:
            logger.error("Key 'search_phrase' or 'months' not found in the work item payload.")
            return
        # Initialize and run the NewsScraper with the provided inputs
        scraper = NewsScraper(search_phrase=search_phrase, months=months)
        scraper.start_search()

if __name__ == "__main__":
    main()
