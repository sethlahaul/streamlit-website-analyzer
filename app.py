import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time

# Set page configuration
st.set_page_config(
    page_title="Website Analyzer Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_page_content(url):
    """Fetches the page content of the given URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 404:
            st.error("Error 404: Page not found.")
            return None
        elif response.status_code == 403:
            st.error("Error 403: Access forbidden. The website may be blocking automated requests.")
            return None
        elif response.status_code == 500:
            st.error("Error 500: Internal Server Error.")
            return None
        elif response.status_code != 200:
            st.error(f"Error: Received status code {response.status_code}")
            return None
        
        response.raise_for_status()
        return response.text
    except requests.exceptions.MissingSchema:
        st.error("Invalid URL. Please make sure to include http:// or https://")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Connection Error. Please check if the URL is correct and the website is accessible.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. The website might be slow or unavailable.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the page: {e}")
        return None

def analyze_seo(url, content):
    """Analyzes the SEO aspects of a webpage."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Basic SEO elements
    title = soup.title.string if soup.title else "Missing"
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_content = meta_desc["content"] if meta_desc else "Missing"
    
    # Headings analysis
    headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    
    # Images without alt text
    images = soup.find_all("img")
    images_without_alt = sum(1 for img in images if not img.get("alt"))
    
    # Links analysis
    links = soup.find_all("a")
    internal_links = sum(1 for link in links if link.get("href") and not link.get("href").startswith("http"))
    external_links = sum(1 for link in links if link.get("href") and link.get("href").startswith("http"))
    
    # Display SEO analysis
    st.subheader("SEO Analysis", divider="rainbow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Basic SEO Elements")
        st.info(f"**Title Tag:** {title}")
        if len(title) < 50 or len(title) > 60:
            st.warning(f"⚠️ Title length: {len(title)} characters. Recommended: 50-60 characters.")
        else:
            st.success(f"✅ Title length: {len(title)} characters (Good)")
            
        st.info(f"**Meta Description:** {meta_desc_content}")
        if len(meta_desc_content) < 150 or len(meta_desc_content) > 160:
            st.warning(f"⚠️ Meta description length: {len(meta_desc_content)} characters. Recommended: 150-160 characters.")
        else:
            st.success(f"✅ Meta description length: {len(meta_desc_content)} characters (Good)")
    
    with col2:
        st.markdown("### Content Structure")
        st.info("**Heading Structure:**")
        for key, value in headings.items():
            st.text(f"{key}: {value}")
        
        if headings['h1'] == 0:
            st.warning("⚠️ No H1 tag found. Consider adding an H1 tag for better SEO.")
        elif headings['h1'] > 1:
            st.warning(f"⚠️ Multiple H1 tags found ({headings['h1']}). Consider using only one H1 tag.")
        else:
            st.success("✅ One H1 tag found (Good)")
    
    st.markdown("### Links and Images")
    col3, col4 = st.columns(2)
    
    with col3:
        st.info(f"**Total Links:** {len(links)}")
        st.text(f"Internal Links: {internal_links}")
        st.text(f"External Links: {external_links}")
    
    with col4:
        st.info(f"**Total Images:** {len(images)}")
        if images_without_alt > 0:
            st.warning(f"⚠️ {images_without_alt} images without alt text. Add alt text for better accessibility and SEO.")
        else:
            st.success("✅ All images have alt text (Good)")

def analyze_conversion(content):
    """Analyzes conversion factors like CTAs, forms, and readability."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find conversion elements
    buttons = soup.find_all("button")
    forms = soup.find_all("form")
    inputs = soup.find_all("input")
    
    # CTA analysis
    cta_texts = ["sign up", "buy now", "get started", "subscribe", "learn more", "download", "try", "join", "contact"]
    cta_count = sum(1 for button in buttons if button.get_text().strip() and any(text in button.get_text().lower() for text in cta_texts))
    
    # Form field analysis
    form_fields = {}
    for form in forms:
        form_inputs = form.find_all("input")
        form_fields[form] = len(form_inputs)
    
    # Display conversion analysis
    st.subheader("Conversion Optimization Analysis", divider="rainbow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Interactive Elements")
        st.info(f"**Buttons:** {len(buttons)}")
        st.info(f"**Forms:** {len(forms)}")
        st.info(f"**Input Fields:** {len(inputs)}")
    
    with col2:
        st.markdown("### Call to Action (CTA) Analysis")
        st.info(f"**CTAs found:** {cta_count}")
        
        if cta_count == 0:
            st.warning("⚠️ No clear CTAs found. Consider adding strong CTAs to improve conversions.")
        elif cta_count < 3:
            st.warning(f"⚠️ Only {cta_count} CTAs found. Consider adding more strategic CTAs.")
        else:
            st.success(f"✅ {cta_count} CTAs found (Good)")
    
    if len(forms) > 0:
        st.markdown("### Form Analysis")
        for i, (form, field_count) in enumerate(form_fields.items()):
            st.text(f"Form #{i+1}: {field_count} input fields")
            
            if field_count > 5:
                st.warning(f"⚠️ Form #{i+1} has {field_count} fields. Consider reducing to improve conversion.")
    elif len(forms) == 0:
        st.warning("⚠️ No forms found. Consider adding a form to capture leads.")

def analyze_performance(url, content):
    """Analyzes basic performance metrics of a webpage."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Count resources
    scripts = soup.find_all("script")
    styles = soup.find_all("link", rel="stylesheet") + soup.find_all("style")
    images = soup.find_all("img")
    
    # Estimate page size (very rough estimate)
    page_size_kb = len(content) / 1024
    
    # Count external resources
    external_scripts = sum(1 for script in scripts if script.get("src") and script.get("src").startswith("http"))
    external_styles = sum(1 for style in styles if style.get("href") and style.get("href").startswith("http"))
    
    # Display performance analysis
    st.subheader("Performance Analysis", divider="rainbow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Resource Count")
        st.info(f"**JavaScript Files:** {len(scripts)}")
        st.info(f"**CSS Files:** {len(styles)}")
        st.info(f"**Images:** {len(images)}")
        st.info(f"**Estimated Page Size:** {page_size_kb:.2f} KB")
    
    with col2:
        st.markdown("### Performance Recommendations")
        
        if external_scripts > 5:
            st.warning(f"⚠️ {external_scripts} external JavaScript files. Consider bundling or reducing.")
        
        if external_styles > 3:
            st.warning(f"⚠️ {external_styles} external CSS files. Consider bundling or reducing.")
        
        if len(images) > 10:
            st.warning(f"⚠️ {len(images)} images found. Consider optimizing or lazy loading.")
        
        if page_size_kb > 500:
            st.warning(f"⚠️ Page size ({page_size_kb:.2f} KB) is large. Consider optimizing.")

def analyze_mobile_friendliness(content):
    """Analyzes mobile-friendliness of a webpage."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Check for viewport meta tag
    viewport = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = viewport is not None
    
    # Check for responsive elements
    media_queries = len(re.findall(r'@media', content))
    
    # Display mobile-friendliness analysis
    st.subheader("Mobile-Friendliness Analysis", divider="rainbow")
    
    if has_viewport:
        st.success(f"✅ Viewport meta tag found: {viewport['content'] if viewport.get('content') else ''}")
    else:
        st.warning("⚠️ No viewport meta tag found. This is essential for mobile responsiveness.")
    
    if media_queries > 0:
        st.success(f"✅ {media_queries} media queries found, suggesting responsive design.")
    else:
        st.warning("⚠️ No media queries found. The site might not be fully responsive.")

def is_valid_url(url):
    """Validates if a URL is properly formatted."""
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def main():
    # Sidebar
    with st.sidebar:
        st.title("Website Analyzer Tool")
        st.markdown("---")
        st.markdown("This tool analyzes websites for SEO, conversion optimization, performance, and mobile-friendliness.")
        st.markdown("---")
        st.markdown("### How to use")
        st.markdown("1. Enter a website URL (including http:// or https://)")
        st.markdown("2. Click 'Analyze' to start the analysis")
        st.markdown("3. View the results in different categories")
        st.markdown("---")
        st.markdown("### Analysis Categories")
        st.markdown("- SEO Analysis")
        st.markdown("- Conversion Optimization")
        st.markdown("- Performance Analysis")
        st.markdown("- Mobile-Friendliness")
    
    # Main content
    st.title("🔍 Website Analyzer Tool")
    st.markdown("Enter a website URL to analyze its SEO, conversion optimization, performance, and mobile-friendliness.")
    
    url = st.text_input("Enter website URL (including http:// or https://):")
    
    analyze_button = st.button("Analyze", type="primary")
    
    if analyze_button:
        if not url:
            st.error("Please enter a URL.")
            return
        
        if not is_valid_url(url):
            st.error("Please enter a valid URL (including http:// or https://).")
            return
        
        with st.spinner("Analyzing website... This may take a few seconds."):
            # Show progress
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            # Step 1: Fetch content
            progress_text.text("Fetching website content...")
            content = get_page_content(url)
            progress_bar.progress(25)
            time.sleep(0.5)  # Small delay for better UX
            
            if not content:
                return
            
            # Step 2: SEO Analysis
            progress_text.text("Analyzing SEO elements...")
            analyze_seo(url, content)
            progress_bar.progress(50)
            time.sleep(0.5)  # Small delay for better UX
            
            # Step 3: Conversion Analysis
            progress_text.text("Analyzing conversion elements...")
            analyze_conversion(content)
            progress_bar.progress(75)
            time.sleep(0.5)  # Small delay for better UX
            
            # Step 4: Performance Analysis
            progress_text.text("Analyzing performance...")
            analyze_performance(url, content)
            progress_bar.progress(90)
            time.sleep(0.5)  # Small delay for better UX
            
            # Step 5: Mobile-Friendliness Analysis
            progress_text.text("Analyzing mobile-friendliness...")
            analyze_mobile_friendliness(content)
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_text.empty()
            
            st.success("Analysis complete! Scroll down to see the results.")

if __name__ == "__main__":
    main()