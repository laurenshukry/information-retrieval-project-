import json
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from time import sleep
import random
import sys
import signal
from webdriver_manager.chrome import ChromeDriverManager

# ================================
# Configuration and Setup
# ================================

# Configure logging
logging.basicConfig(
    filename='boohoo_crawler.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Graceful shutdown handler
def signal_handler(sig, frame):
    logging.info("Interrupt received. Shutting down gracefully...")
    sys.exit(0)

# Register the signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def initialize_webdriver(headless=True):
    """
    Initializes the Selenium WebDriver with desired options using webdriver-manager.
    """
    options = webdriver.ChromeOptions()
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
    options.add_argument(f"user-agent={user_agent}")
    
    if headless:
        options.add_argument("--headless")
    
    # Optional: Disable images for faster loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    # Additional options to make headless mode less detectable
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Initialize the WebDriver using webdriver-manager
    try:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logging.info("WebDriver initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        sys.exit(1)
    
    # Modify navigator.webdriver to avoid detection
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        },
    )
    
    return driver

# ================================
# Data Extraction Functions
# ================================

def extract_product_details(product_section):
    """
    Extracts product details from a product section.
    """
    try:
        # Extract Product Name
        name_tag = product_section.find('h3', class_='b-product_tile-title')
        name = name_tag.get_text(strip=True) if name_tag else "No name available"
        
        # Extract Product URL
        url_tag = name_tag.find('a', href=True) if name_tag else None
        relative_url = url_tag['href'] if url_tag else ""
        full_url = urljoin("https://www.boohoo.com", relative_url)
        
        # Extract Product Image URL
        img_tag = product_section.find('img', alt=True)
        image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else "No image available"
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        elif image_url.startswith("/"):
            image_url = urljoin("https://www.boohoo.com", image_url)
        
        # Extract Current Price
        price_new_tag = product_section.find('span', class_='b-price-item m-new')
        price_new = price_new_tag.get_text(strip=True) if price_new_tag else "No price available"
        
        # Compile Product Data
        product_data = {
            "Name": name,
            "Price": price_new,
            "URL": full_url,
            "Image": image_url
        }
        
        logging.info(f"Extracted product: {product_data['Name']}")
        return product_data
    except Exception as e:
        logging.error(f"Error extracting product details: {e}")
        return None

# ================================
# Pagination Handling Functions
# ================================

def click_load_more(driver, retries=3):
    """
    Clicks the 'Load More' button to load additional products.
    Returns True if the button was clicked, False otherwise.
    Retries up to 'retries' times on failure.
    """
    for attempt in range(retries):
        try:
            # Selector for the 'Load More' button
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.js-load-more'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            sleep(1)  # Small pause before clicking
            load_more_button.click()
            logging.info("Clicked 'Load More' button.")
            return True
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} to click 'Load More' failed: {e}")
            sleep(2)  # Wait before retrying
    logging.error("Failed to click 'Load More' button after multiple attempts.")
    return False

def scroll_to_bottom(driver, pause_time=2):
    """
    Scrolls to the bottom of the page to load all products.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logging.info("Reached the bottom of the page.")
            break
        last_height = new_height

# ================================
# Main Crawler Function
# ================================

def main():
    # Define the source URL and the number of pages to scrape
    source_url = "https://www.boohoo.com/mens-promotions/mens-flash-promo"
    max_pages = 5  # Set the desired number of pages to scrape
    
    # Initialize the WebDriver
    driver = initialize_webdriver(headless=True)
    
    # Initialize an empty list to store product details and a set to track seen URLs
    products = []
    seen_urls = set()
    
    try:
        # Open the target page
        driver.get(source_url)
        logging.info(f"Accessed {source_url}")
        
        # Loop through the pages
        for page in range(1, max_pages + 1):
            logging.info(f"Scraping Page {page}...")
            try:
                # Wait for product sections to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'section.b-product_tile'))
                )
                logging.info(f"Product sections loaded for Page {page}.")
            except Exception as e:
                logging.error(f"Error loading products on page {page}: {e}")
                break
            
            # Scroll to the bottom to ensure all products are loaded
            scroll_to_bottom(driver, pause_time=random.uniform(2, 4))
            
            # Get the HTML source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # Find all product sections
            product_sections = soup.select('section.b-product_tile')
            logging.info(f"Found {len(product_sections)} products on page {page}.")
            print(f"Found {len(product_sections)} products on page {page}.")
            
            # Extract product details
            for product_section in product_sections:
                product = extract_product_details(product_section)
                if product and product["URL"] not in seen_urls:
                    products.append(product)
                    seen_urls.add(product["URL"])
                elif product:
                    logging.info(f"Duplicate product found: {product['Name']} - Skipping.")
            
            # Navigate to the next page if not the last page
            if page < max_pages:
                # Attempt to click 'Load More' button with retries
                clicked = click_load_more(driver)
                if not clicked:
                    logging.info("No 'Load More' button found or unable to click. Ending scraping.")
                    print("No 'Load More' button found or unable to click. Ending scraping.")
                    break
                # Optional: Wait for new products to load
                sleep(random.uniform(2, 4))
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the driver quits properly
        driver.quit()
        logging.info("WebDriver closed.")
        print("WebDriver closed.")
        
        # Save the products to a JSON file
        if products:
            output_file = "boohoo_new_in.json"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(products, f, indent=4, ensure_ascii=False)
                logging.info(f"Scraped data saved to {output_file}")
                print(f"Scraped data saved to {output_file}")
            except Exception as e:
                logging.error(f"Error saving data to {output_file}: {e}")
                print(f"Error saving data to {output_file}: {e}")
        else:
            logging.info("No products scraped.")
            print("No products scraped.")

# ================================
# Entry Point
# ================================

if __name__ == "__main__":
    main()
