# Wikipedia Scraper

## Overview
The **Wikipedia Scraper** is a Python-based tool designed to extract information from Wikipedia. It utilizes libraries like `requests` and `BeautifulSoup` to retrieve and parse HTML content, enabling users to efficiently scrape Wikipedia pages for specific data.

## Features
- Scrape content from any Wikipedia page by providing a URL.
- Extract and display the main content of the page, including paragraphs and sections.
- Easy to customize for additional scraping needs.
- Lightweight and straightforward script, suitable for quick data retrieval.

## Requirements
- Python 3.7+
- Required Python libraries:
  - `requests`
  - `BeautifulSoup4`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/membaby/wikipedia-scraper.git
   cd wikipedia-scraper
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

   If the `requirements.txt` file is not provided, you can manually install the dependencies:
   ```bash
   pip install requests beautifulsoup4
   ```

## Usage
1. Open the `Wikipedia Scraper.py` file and edit the `url` variable to point to the desired Wikipedia page.
   ```python
   url = "https://en.wikipedia.org/wiki/Example_Page"
   ```

2. Run the script:
   ```bash
   python "Wikipedia Scraper.py"
   ```

3. The scraped content will be printed to the console. You can modify the script to save the content to a file if needed.

## Code Structure
The script follows these main steps:
1. Sends an HTTP GET request to the specified Wikipedia page.
2. Parses the retrieved HTML using BeautifulSoup.
3. Extracts text content from the main sections of the page.
4. Displays the extracted information.

## Customization
- **Change target elements:**
  Modify the BeautifulSoup selectors to scrape additional elements, such as tables, images, or infobox data.

- **Save to file:**
  Add functionality to write the scraped data to a `.txt`, `.csv`, or `.json` file for further processing.

## Example Output
For the Wikipedia page `https://en.wikipedia.org/wiki/Python_(programming_language)`, the script might output:
```
Title: Python (programming language)

Content:
Python is a high-level, interpreted, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation...
```

## Contributing
Contributions are welcome! If you have suggestions for improvements or new features, feel free to:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- [Wikipedia](https://www.wikipedia.org) for providing publicly accessible information.
- The developers of `requests` and `BeautifulSoup` for their invaluable libraries.
