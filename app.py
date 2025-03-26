import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time
import subprocess
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tempfile
# Remove the problematic import
# from pylighthouse import lighthouse

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

    # Lighthouse analysis is now run by default when clicking the main Analyze button

def run_lighthouse_analysis(url):
    """Runs a Lighthouse analysis on the given URL and returns the results."""
    try:
        # Check if Node.js is installed
        try:
            node_version = subprocess.run(["node", "--version"], check=True, capture_output=True, text=True)
            st.info(f"Node.js detected: {node_version.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError):
            st.error("Node.js is not installed or not in PATH. Lighthouse requires Node.js to run.")
            st.info("Please install Node.js from https://nodejs.org/ and try again.")
            return None
        
        # Check if Chrome is installed
        chrome_found = False
        chrome_path = "chrome"
        if os.name == 'nt':  # Windows
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    chrome_found = True
                    st.info(f"Chrome detected at: {path}")
                    break
        
        if not chrome_found:
            st.error("Google Chrome is not installed or not found in the standard locations.")
            st.info("Lighthouse requires Chrome to run. Please install Chrome and try again.")
            return None
            
        # Check for and manage existing Chrome processes (Windows only)
        if os.name == 'nt':
            try:
                # Check for Chrome processes running in headless mode
                st.info("Checking for existing Chrome processes...")
                chrome_processes = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/FO", "CSV"], 
                    capture_output=True, text=True, check=True
                )
                
                # Parse the output to see if Chrome is running
                chrome_running = "chrome.exe" in chrome_processes.stdout
                
                if chrome_running:
                    st.warning("Detected running Chrome instances that might interfere with Lighthouse.")
                    # Ask user if they want to terminate Chrome processes
                    if st.button("Terminate Chrome processes and continue"):
                        try:
                            # Kill Chrome processes
                            subprocess.run(
                                ["taskkill", "/F", "/IM", "chrome.exe"], 
                                capture_output=True, check=True
                            )
                            st.success("Chrome processes terminated successfully.")
                        except subprocess.SubprocessError as e:
                            st.error(f"Failed to terminate Chrome processes: {e}")
                            st.info("Please close Chrome manually and try again.")
                            return None
                    else:
                        st.info("You can manually close Chrome and try again, or click the button above to automatically terminate Chrome processes.")
                        return None
            except subprocess.SubprocessError as e:
                st.warning(f"Could not check for Chrome processes: {e}")
                # Continue anyway as this is just a precautionary check
        
        # Create a temporary directory to store the report
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Define the output file path
            output_file = os.path.join(tmp_dir, "lighthouse-report.json")
            
            # Install Lighthouse if not already installed
            st.info("Checking for Lighthouse installation...")
            try:
                # Try to run lighthouse --version to check if it's installed
                # On Windows, we need to use npx.cmd instead of npx
                npx_command = "npx.cmd" if os.name == 'nt' else "npx"
                subprocess.run([npx_command, "lighthouse", "--version"], 
                               check=True, capture_output=True, text=True)
                st.success("Lighthouse is available via npx.")
            except subprocess.SubprocessError:
                st.warning("Lighthouse not found. Attempting to install it temporarily...")
                try:
                    # On Windows, we need to use npm.cmd instead of npm
                    npm_command = "npm.cmd" if os.name == 'nt' else "npm"
                    install_process = subprocess.run(
                        [npm_command, "install", "-g", "lighthouse"], 
                        check=True, capture_output=True, text=True
                    )
                    st.success("Lighthouse installed successfully.")
                except subprocess.SubprocessError as e:
                    st.error(f"Failed to install Lighthouse: {e}")
                    st.info("You can manually install Lighthouse by running: npm install -g lighthouse")
                    return None
            
            # Run Lighthouse using the lighthouse CLI
            st.info(f"Running Lighthouse analysis on {url}...")
            # On Windows, we need to use npx.cmd instead of npx
            npx_command = "npx.cmd" if os.name == 'nt' else "npx"
            command = [
                npx_command, "lighthouse", url,
                "--output=json",
                f"--output-path={output_file}"
            ]
            
            try:
                process = subprocess.run(command, check=True, capture_output=True, text=True)
                st.success("Lighthouse analysis completed successfully!")
                
                # Clean up any remaining Chrome processes (Windows only)
                if os.name == 'nt':
                    try:
                        # Check if there are any headless Chrome processes still running
                        chrome_processes = subprocess.run(
                            ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/FO", "CSV"], 
                            capture_output=True, text=True, check=True
                        )
                        
                        # If Chrome is still running, try to clean up
                        if "chrome.exe" in chrome_processes.stdout:
                            st.info("Cleaning up Chrome processes...")
                            try:
                                # Kill Chrome processes
                                subprocess.run(
                                    ["taskkill", "/F", "/IM", "chrome.exe"], 
                                    capture_output=True, check=True
                                )
                                st.success("Chrome processes cleaned up successfully.")
                            except subprocess.SubprocessError as e:
                                st.warning(f"Could not clean up Chrome processes: {e}")
                                # Continue anyway as we already have the results
                    except subprocess.SubprocessError as e:
                        st.warning(f"Could not check for Chrome processes during cleanup: {e}")
                        # Continue anyway as we already have the results
                
                # Read the results from the output file
                try:
                    # Use UTF-8 encoding explicitly to handle non-ASCII characters
                    with open(output_file, 'r', encoding='utf-8') as f:
                        lighthouse_data = json.load(f)
                        
                    return lighthouse_data
                except UnicodeDecodeError as ude:
                    st.error(f"Encoding error when reading Lighthouse results: {ude}")
                    # Fallback to reading with error handling
                    try:
                        with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
                            lighthouse_data = json.load(f)
                        st.warning("Some characters in the Lighthouse report were replaced due to encoding issues.")
                        return lighthouse_data
                    except Exception as e:
                        st.error(f"Failed to read Lighthouse results: {e}")
                        return None
            except subprocess.SubprocessError as e:
                st.error(f"Error running Lighthouse: {e}")
                if e.stderr:
                    st.error(f"Error details: {e.stderr}")
                st.info("Make sure Chrome is not running in headless mode already or try closing other Chrome instances.")
                
                # Attempt to clean up any Chrome processes that might be stuck (Windows only)
                if os.name == 'nt':
                    try:
                        # Kill Chrome processes
                        subprocess.run(
                            ["taskkill", "/F", "/IM", "chrome.exe"], 
                            capture_output=True, check=True
                        )
                        st.info("Attempted to clean up Chrome processes after error.")
                    except subprocess.SubprocessError:
                        # Ignore errors during cleanup after failure
                        pass
                        
                return None
    except Exception as e:
        st.error(f"Failed to run Lighthouse analysis: {e}")
        return None

def display_lighthouse_results(lighthouse_data):
    """Displays the Lighthouse analysis results in a user-friendly format."""
    if not lighthouse_data:
        st.error("No Lighthouse data available to display.")
        return
        
    try:
        # Extract the audit results
        categories = lighthouse_data.get('categories', {})
        audits = lighthouse_data.get('audits', {})
        
        # Display the main scores
        st.subheader("Lighthouse Analysis Results", divider="rainbow")
        
        # Create a DataFrame for the main scores
        scores = {
            'Category': [],
            'Score': []
        }
        
        for category_key, category_data in categories.items():
            if category_data is None:
                continue
            scores['Category'].append(category_data.get('title', category_key))
            # Safely handle None values for score
            score_value = category_data.get('score')
            score = round((score_value or 0) * 100)  # Use 0 if score_value is None
            scores['Score'].append(score)
        
        # Only proceed if we have scores to display
        if not scores['Category']:
            st.warning("No valid Lighthouse category scores found.")
            return
            
        scores_df = pd.DataFrame(scores)
        
        # Display scores as a horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Set color based on score
        colors = []
        for score in scores_df['Score']:
            # Ensure score is not None before comparison
            if score is None:
                colors.append('gray')  # Default color for None values
            elif score >= 90:
                colors.append('green')
            elif score >= 50:
                colors.append('orange')
            else:
                colors.append('red')
        
        # Create the horizontal bar chart
        bars = ax.barh(scores_df['Category'], scores_df['Score'], color=colors)
        
        # Add score labels to the bars
        for bar in bars:
            width = bar.get_width()
            if width is not None:  # Check if width is not None
                ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width}%', 
                        ha='left', va='center', fontweight='bold')
        
        # Set chart properties
        ax.set_xlim(0, 105)  # Set x-axis limit to 0-105 to accommodate labels
        ax.set_xlabel('Score')
        ax.set_title('Lighthouse Performance Scores')
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Display the chart in Streamlit
        st.pyplot(fig)
        
        # Display detailed metrics in expandable sections
        with st.expander("Performance Metrics"):
            # Extract key performance metrics
            metrics = [
                ('First Contentful Paint', 'first-contentful-paint'),
                ('Speed Index', 'speed-index'),
                ('Largest Contentful Paint', 'largest-contentful-paint'),
                ('Time to Interactive', 'interactive'),
                ('Total Blocking Time', 'total-blocking-time'),
                ('Cumulative Layout Shift', 'cumulative-layout-shift')
            ]
            
            for metric_name, metric_key in metrics:
                if metric_key in audits and audits[metric_key] is not None:
                    metric_data = audits[metric_key]
                    display_name = metric_data.get('title', metric_name)
                    display_value = metric_data.get('displayValue', 'N/A')
                    
                    # Safely handle None values for score
                    score_value = metric_data.get('score')
                    if score_value is not None:
                        score = score_value * 100
                        
                        # Determine color based on score
                        if score >= 90:
                            color = 'green'
                        elif score >= 50:
                            color = 'orange'
                        else:
                            color = 'red'
                        
                        st.markdown(f"**{display_name}**: {display_value} "
                                    f"<span style='color:{color};font-weight:bold;'>"
                                    f"({score:.0f}%)</span>", unsafe_allow_html=True)
                    else:
                        # Display without score if score is None
                        st.markdown(f"**{display_name}**: {display_value} "
                                    f"<span style='color:gray;font-weight:bold;'>"
                                    f"(N/A)</span>", unsafe_allow_html=True)
        
        # Display opportunities for improvement
        with st.expander("Opportunities for Improvement"):
            # Extract opportunities from audits
            opportunities = []
            for audit_key, audit_data in audits.items():
                if audit_data is None:
                    continue
                    
                # Safely check score
                score_value = audit_data.get('score')
                if score_value is not None and score_value < 1 and 'details' in audit_data:
                    # Check if 'items' exists in details
                    if 'items' not in audit_data['details']:
                        continue
                        
                    opportunities.append({
                        'title': audit_data.get('title', audit_key),
                        'description': audit_data.get('description', ''),
                        'score': score_value * 100
                    })
            
            # Sort opportunities by score (lowest first) with safe key function
            def safe_score_key(x):
                return x.get('score', 0) if x.get('score') is not None else 0
                
            opportunities.sort(key=safe_score_key)
            
            # Display top 5 opportunities
            if opportunities:
                for i, opportunity in enumerate(opportunities[:5]):
                    score = opportunity.get('score')
                    score_display = f"({score:.0f}%)" if score is not None else "(N/A)"
                    color = 'gray'
                    if score is not None:
                        color = 'red' if score < 50 else 'orange'
                    
                    st.markdown(f"**{i+1}. {opportunity['title']}** "
                                f"<span style='color:{color};font-weight:bold;'>"
                                f"{score_display}</span>", unsafe_allow_html=True)
                    st.markdown(f"{opportunity['description']}")
                    st.markdown("---")
            else:
                st.info("No improvement opportunities found.")
        
        # Display best practices and SEO recommendations
        with st.expander("Best Practices & SEO Recommendations"):
            # Extract best practices and SEO audits
            best_practices = []
            seo_recommendations = []
            
            for audit_key, audit_data in audits.items():
                if audit_data is None:
                    continue
                    
                # Safely check score
                score_value = audit_data.get('score')
                if score_value is not None and score_value < 1:
                    category = audit_data.get('group', '')
                    if category is not None and 'best-practices' in category:
                        best_practices.append({
                            'title': audit_data.get('title', audit_key),
                            'description': audit_data.get('description', ''),
                            'score': score_value * 100
                        })
                    elif category is not None and 'seo' in category:
                        seo_recommendations.append({
                            'title': audit_data.get('title', audit_key),
                            'description': audit_data.get('description', ''),
                            'score': score_value * 100
                        })
            
            # Sort by score (lowest first) with safe key function
            def safe_score_key(x):
                return x.get('score', 0) if x.get('score') is not None else 0
                
            best_practices.sort(key=safe_score_key)
            seo_recommendations.sort(key=safe_score_key)
            
            # Display best practices
            st.markdown("#### Best Practices")
            if best_practices:
                for i, practice in enumerate(best_practices[:3]):
                    st.markdown(f"**{i+1}. {practice['title']}**")
                    st.markdown(f"{practice['description']}")
            else:
                st.info("No best practice recommendations found.")
            
            # Display SEO recommendations
            st.markdown("#### SEO Recommendations")
            if seo_recommendations:
                for i, recommendation in enumerate(seo_recommendations[:3]):
                    st.markdown(f"**{i+1}. {recommendation['title']}**")
                    st.markdown(f"{recommendation['description']}")
            else:
                st.info("No SEO recommendations found.")
    
    except Exception as e:
        st.error(f"Error displaying Lighthouse results: {e}")
        # Print more detailed error information for debugging
        import traceback
        st.error(f"Error details: {traceback.format_exc()}")
        st.json(lighthouse_data)  # Fallback to displaying raw JSON

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
        st.markdown("4. Run Lighthouse analysis for detailed performance metrics")
        st.markdown("---")
        st.markdown("### Analysis Categories")
        st.markdown("- SEO Analysis")
        st.markdown("- Conversion Optimization")
        st.markdown("- Performance Analysis")
        st.markdown("- Mobile-Friendliness")
        st.markdown("- Lighthouse Analysis (detailed performance)")
    
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
            progress_bar.progress(85)
            time.sleep(0.5)  # Small delay for better UX
            
            # Step 6: Lighthouse Analysis
            progress_text.text("Running Lighthouse analysis... This may take a minute or two.")
            st.info("Lighthouse analysis requires Node.js and Chrome to be installed on your system.")
            lighthouse_results = run_lighthouse_analysis(url)
            if lighthouse_results:
                display_lighthouse_results(lighthouse_results)
            else:
                st.warning("Lighthouse analysis could not be completed. Make sure Node.js and Chrome are installed.")
                st.info("""
                To run Lighthouse analysis, you need:
                1. Node.js installed (https://nodejs.org/)
                2. Google Chrome installed
                3. npm or npx available in your PATH
                
                You can also install Lighthouse globally with: npm install -g lighthouse
                """)
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_text.empty()
            
            st.success("Analysis complete! Scroll down to see the results.")

if __name__ == "__main__":
    main()