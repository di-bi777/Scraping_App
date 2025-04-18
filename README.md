# Scraping App - Topic Analysis Tool

A Streamlit-based web application that performs web scraping and topic analysis using word clouds. This application can analyze content from ScrumSign's website or process data from CSV files.

## Features

- **Web Scraping**: Automatically scrapes content from ScrumSign's website
  - Blog articles
  - Customer testimonials
- **CSV Data Processing**: Ability to analyze text data from CSV files
- **Word Cloud Generation**: Creates visual representations of text data
- **Japanese Language Support**: Full support for Japanese text analysis using Janome
- **Customizable Font Options**: 
  - Manual font path input
  - Automatic font download from Google Fonts

## Requirements

- Python 3.x
- Streamlit
- pandas
- requests
- BeautifulSoup4
- wordcloud
- matplotlib
- janome

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install streamlit pandas requests beautifulsoup4 wordcloud matplotlib janome
```

## Usage

1. Run the application:
```bash
streamlit run ScrapingApp.py
```

2. Choose your analysis method:
   - Web scraping from ScrumSign website
   - CSV file upload

3. For web scraping:
   - Select content type (Blog articles or Customer testimonials)
   - Choose font settings
   - Wait for content scraping and word cloud generation

4. For CSV analysis:
   - Upload your CSV file
   - Select the text column for analysis
   - Choose font settings
   - Generate word cloud

## Features in Detail

### Web Scraping
- Automatically extracts content from ScrumSign's website
- Processes multiple pages
- Shows progress during scraping
- Handles Japanese text appropriately

### Word Cloud Generation
- Supports Japanese text analysis
- Customizable stopwords
- Adjustable word cloud parameters
- Interactive display with reset option

### Font Management
- Option to manually specify font path
- Automatic download of Noto Sans CJK JP font
- Font validation checks

## Notes

- The application includes built-in delays to prevent overwhelming the target website
- Japanese text analysis is optimized for better results
- The word cloud generation includes common Japanese stopwords

