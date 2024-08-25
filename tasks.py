import logging
import re
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import os
from CustomSelenium import CustomSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from RPA.Robocorp.WorkItems import WorkItems

# Set up logging to capture detailed information during execution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self, search_phrase, months):
        # Initialize the Custom Selenium wrapper
        self.browser = CustomSelenium()
        self.browser.set_webdriver()  # Set up the Selenium WebDriver
        self.search_phrase = search_phrase  # Store the search phrase from the work item
        self.months = months  # Store the number of months to filter articles
        self.news_data = []  # Initialize an empty list to store scraped news data
        self.processed_titles = set()  # Track processed article titles to avoid duplicates

    def calculate_date_range(self):
        # Calculate the date range based on the 'months' parameter
        end_date = datetime.now()
        if self.months <= 1:
            start_date = end_date.replace(day=1)  # Start from the first day of the current month
        else:
            start_date = end_date - relativedelta(months=self.months - 1)
            start_date = start_date.replace(day=1)
        return start_date, end_date

    def is_within_date_range(self, date_text, start_date, end_date):
        # Check if the article's published date is within the desired date range
        try:
            date_text = date_text.split(' at ')[0]
            date_format = "%b %d, %Y"
            article_date = datetime.strptime(date_text, date_format)
            return start_date <= article_date <= end_date
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return False

    def find_and_scroll_to_date(self):
        # Locate and scroll to the article's published date element
        try:
            date_element = self.browser.find_element(By.CSS_SELECTOR, "div.date-published p.type-caption")
            self.browser.scroll_element_into_view(date_element)
            time.sleep(1)  # Wait for scrolling to complete
            date_text = date_element.text.replace("Published ", "")
            return date_text
        except Exception as e:
            logger.error(f"Error finding or scrolling to date element: {e}")
            return None

    def load_more_articles(self):
        # Click the 'Load More' button to fetch additional articles
        try:
            load_more_button = self.browser.find_element(By.CSS_SELECTOR, "button.p-button.p-component.p-button-rounded[aria-label='Load More']")
            self.browser.scroll_element_into_view(load_more_button)
            time.sleep(2)  # Ensure button is fully in view
            self.click_element_with_retry(load_more_button)
            time.sleep(5)  # Wait for new articles to load
            logger.info("Clicked 'Load More' button")
            return True
        except Exception as e:
            logger.info(f"No 'Load More' button found or couldn't click it: {e}")
            return False

    def format_for_url(self, text):
        # Format text to be URL-friendly
        formatted_text = re.sub(r'[^\w\s]', '', text).strip().lower().replace(" ", "-")
        return formatted_text

    def extract_key_words(self, title):
        # Extract key words from the article title
        words = title.split()
        key_words = [word.lower() for word in words if len(word) > 3]
        return key_words

    def are_key_words_in_url(self, key_words, current_url):
        # Check if key words are present in the article URL
        matches = [word for word in key_words if word in current_url]
        logger.info(f"Key words extracted: {key_words}")
        logger.info(f"Words found in URL: {matches}")
        match_count = len(matches)
        return match_count >= 3

    def normalize_title(self, text):
        # Normalize the title text for consistent comparison
        return re.sub(r'[^\w\s]', '', text).strip().lower()

    def retry_search(self):
        # Retry the search by reloading the search URL
        search_url = f"https://gothamist.com/search?q={self.search_phrase.replace(' ', '+')}"
        logger.info("Opening the browser.")
        self.browser.open_url(search_url)
        time.sleep(5)

    def save_article_image(self):
        # Capture and save a screenshot of the article's image
        try:
            output_directory = os.getenv("ROBOT_ARTIFACTS", "output")
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
                logger.info(f"Created output directory: {output_directory}")

            image_element = self.browser.find_element(By.XPATH, "//div[contains(@class, 'image-with-caption-image')]//img")
            self.browser.scroll_element_into_view(image_element)
            image_filename = os.path.join(output_directory, f"news_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            image_element.screenshot(image_filename)
            logger.info(f"Image saved as: {image_filename}")
            return image_filename

        except Exception as e:
            logger.warning(f"No image found or failed to save image: {e}")
            return None

    def click_element_with_retry(self, element):
        # Click an element with retries, using JavaScript as a fallback
        attempts = 0
        while attempts < 3:
            try:
                WebDriverWait(self.browser.driver, 10).until(EC.element_to_be_clickable(element))
                element.click()
                return
            except Exception as e:
                logger.warning(f"Click attempt {attempts + 1} failed: {e}")
                time.sleep(1)
                attempts += 1
        self.browser.driver.execute_script("arguments[0].click();", element)

    def start_search(self):
        # Main method to perform the search and scrape the data
        self.retry_search()
        start_date, end_date = self.calculate_date_range()
        article_index = 0  # Track the index of the current article being processed

        try:
            while True:
                articles = self.browser.find_elements(By.CSS_SELECTOR, "a.flexible-link.internal.card-title-link")
                logger.info(f"Number of articles found: {len(articles)}")

                while article_index < len(articles):
                    try:
                        article = articles[article_index]
                        title = article.text
                        normalized_title = self.normalize_title(title)
                        if normalized_title in self.processed_titles:
                            article_index += 1
                            continue  # Skip already processed articles

                        self.processed_titles.add(normalized_title)
                        formatted_title = self.format_for_url(title)

                        logger.info(f"Processing article: '{title}'")

                        self.browser.scroll_element_into_view(article)
                        time.sleep(2)

                        self.click_element_with_retry(article)
                        time.sleep(5)

                        current_url = self.browser.driver.current_url

                        key_words = self.extract_key_words(title)
                        if not self.are_key_words_in_url(key_words, current_url):
                            logger.info(f"Not enough key words in URL. Current URL: {current_url}. Retrying search...")
                            self.retry_search()
                            articles = self.browser.find_elements(By.CSS_SELECTOR, "a.flexible-link.internal.card-title-link")
                            continue

                        date_text = self.find_and_scroll_to_date()
                        logger.info(f"Published Date: {date_text}")

                        if not self.is_within_date_range(date_text, start_date, end_date):
                            logger.info("Article not within the date range. Stopping search.")
                            break

                        title = self.browser.get_text(By.CSS_SELECTOR, "h1.mt-4.mb-3.h2")
                        logger.info(f"Title: {title}")

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
                        time.sleep(15)

                        self.browser.wait_until_element_is_visible(By.CSS_SELECTOR, "a.flexible-link.internal.card-title-link", timeout=10)
                        articles = self.browser.find_elements(By.CSS_SELECTOR, "a.flexible-link.internal.card-title-link")
                        article_index += 1

                    except Exception as e:
                        logger.error(f"Error processing article: {e}")
                        self.browser.go_back()
                        time.sleep(15)
                        self.browser.wait_until_element_is_visible(By.CSS_SELECTOR, "a.flexible-link.internal.card-title-link", timeout=10)
                        articles = self.browser.find_elements(By.CSS_SELECTOR, "a.flexible-link.internal.card-title-link")
                        continue

                if not self.load_more_articles():
                    break

            logger.info(f"Total articles processed: {len(self.news_data)}")

            # Save the results to an Excel file in the /output directory
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

def load_work_item_parameters():
    """Load parameters from the Robocorp work item."""
    items = WorkItems()
    items.get_input_work_item()
    
    search_phrase = items.get("search_phrase", "Rock")  # Default to "Rock" if not provided
    months = int(items.get("months", 3))  # Default to 3 months if not provided
    
    return search_phrase, months

if __name__ == "__main__":
    search_phrase, months = load_work_item_parameters()
    scraper = NewsScraper(search_phrase=search_phrase, months=months)
    scraper.start_search()