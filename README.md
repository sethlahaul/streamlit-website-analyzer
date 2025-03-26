# Website Analyzer Tool

A Streamlit application that analyzes websites for SEO, conversion optimization, performance, and mobile-friendliness.

## Features

- **SEO Analysis**: Examines title tags, meta descriptions, heading structure, images, and links
- **Conversion Optimization**: Analyzes buttons, forms, and calls-to-action (CTAs)
- **Performance Analysis**: Evaluates JavaScript files, CSS files, images, and page size
- **Mobile-Friendliness**: Checks viewport meta tag and responsive design elements

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application with:

```
python -m streamlit run app.py
```

Or:

```
streamlit run app.py
```

## How It Works

1. Enter a website URL (including http:// or https://)
2. Click 'Analyze' to start the analysis
3. View the results in different categories

## Requirements

- Python 3.7+
- Streamlit
- Requests
- BeautifulSoup4

## Notes

- The tool provides a basic analysis and recommendations for website improvement
- Performance analysis is based on simple metrics and does not require Lighthouse
- All analysis is done client-side without storing any data