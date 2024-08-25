Pedro Teixeira Brito - Thoughtful Automation Challenge

Welcome to my submission for the Thoughtful Automation Challenge! This project is designed to automate the extraction of data from a news website using Robocorp and Selenium. Below, you'll find an overview of the project, the process workflow, setup instructions, and additional details.

📖 Project Overview:

The goal of this project is to automate the process of extracting news data from a specified news website based on certain parameters provided via a Robocorp work item. The bot searches for articles related to a specific search phrase, within a defined time range, and extracts relevant details such as the article title, date, description, and more.

🚀 Process Workflow:

Initialize and Set Parameters:

The process starts by reading parameters (search_phrase and months) from the Robocorp work item.
Open News Website:

The bot opens the specified news website and enters the search phrase into the search field.
Filter and Scrape Articles:

The bot navigates through the articles, filtering them based on the date range specified by the months parameter.
For each article, the bot extracts the title, date, description, counts the occurrence of the search phrase, checks for monetary amounts, and captures a screenshot of the article image.
Save Data:

The extracted data is saved into an Excel file in the /output directory, with details such as the title, date, description, image filename, and other metadata.
Handle Errors and Resilience:

The bot is equipped with error handling and retries for robustness, ensuring that it can handle unexpected issues and complete the process successfully.