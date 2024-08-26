# Pedro Teixeira Brito - Thoughtful Automation Challenge

Welcome to my submission for the Thoughtful Automation Challenge! This project is designed to automate the extraction of data from a news website using Robocorp and Selenium. Below, you'll find an overview of the project, the process workflow, setup instructions, and additional details.

## 📖 Project Overview

The goal of this project is to automate the process of extracting news data from a specified news website based on certain parameters provided via a Robocorp work item. The bot searches for articles related to a specific search phrase, within a defined time range, and extracts relevant details such as the article title, date, description, and more.

## 🚀 Process Workflow

### 1. Initialize and Set Parameters:
- The process starts by reading parameters (`search_phrase` and `months`) from the Robocorp work item.

### 2. Open News Website:
- The bot opens the specified news website and enters the search phrase into the search field.

### 3. Filter and Scrape Articles:
- The bot navigates through the articles, filtering them based on the date range specified by the `months` parameter.
- For each article, the bot extracts the title, date, description, counts the occurrence of the search phrase, checks for monetary amounts, and captures a screenshot of the article image.

### 4. Save Data:
- The extracted data is saved into an Excel file in the `/output` directory, with details such as the title, date, description, image filename, and other metadata.

### 5. Handle Errors and Resilience:
- The bot is equipped with error handling and retries for robustness, ensuring that it can handle unexpected issues and complete the process successfully.

## 🛠️ Work Item Configuration

To run the bot, you need to set up the work item with the following parameters in JSON format:

### JSON Structure:
```json
{
    "search_phrase": "rock",
    "months": 3
}
```

### Expected Outcome:

For the example work item with `search_phrase = "rock"` and `months = 3`, the bot is expected to process approximately 12 articles. The expected outcome includes the following:

- **Search for Articles**: The bot will find articles related to the term "rock".
- **Date Range Filtering**: The bot will filter articles published within the last 3 months.
- **Title Extraction**: The bot will extract the title of each article.
- **Date Extraction**: The bot will capture the published date of each article.
- **Description Extraction**: The bot will extract the main body or description of the article.
- **Search Phrase Count**: The bot will count how many times the term "rock" appears in the title and description of each article.
- **Monetary Amount Detection**: The bot will check if any monetary values are mentioned in the articles.
- **Image Capture**: Screenshots of the article images will be saved.
- **Data Saving**: All the extracted data (title, date, description, image filename, search phrase count, and monetary amount detection) will be saved into an Excel file located in the `/output` directory.
- **Processing Time**: Each article takes around 1 minute to ensure all the information is retrieved accurately.

This example is designed to demonstrate all the functionalities of the bot, providing a comprehensive overview of how it processes and extracts data from the news articles.


