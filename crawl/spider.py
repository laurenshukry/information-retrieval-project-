import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from time import sleep
import random

# Define the source URL and the number of pages to scrape
source = "https://www.asos.com/women/new-in/cat/?cid=27108"
max_pages = 5

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
browser = webdriver.Chrome(options=options)

# Open the New In page
browser.get(source)

# Initialize an empty list to store product details
products = []

# Loop through the pages
for i in range(1, max_pages + 1):
    try:
        # Wait for product container to load
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article[class^="productTile_"]'))
        )
    except Exception as e:
        print(f"Error loading products on page {i}: {e}")
        break

    # Scroll to load lazy-loaded images
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)  # Allow time for images to load

    # Get the HTML source and parse it with BeautifulSoup
    response = browser.page_source
    soup = BeautifulSoup(response, 'lxml')

    # Find all product sections
    product_list = soup.select('article[class^="productTile_"]')  # Matches dynamic class names
    print(f"Page {i}: Found {len(product_list)} products.")

    # Extract product details
    for product in product_list:
        try:
            # Extract product name
            name_tag = product.find('p', {'class': 'productDescription_sryaw'})
            name = name_tag.text.strip() if name_tag else "No name available"

            # Extract product price
            price_tag = product.find('span', {'class': 'price__B9LP'})
            price = price_tag.text.strip() if price_tag else "No price available"

            # Extract product URL
            url_tag = product.find('a', href=True)
            url = url_tag['href'] if url_tag else "No URL available"
            full_url = urljoin("https://www.asos.com", url)

            # Extract product image URL
            img_container = product.find('div', {'class': 'productHeroContainer_dVvdX'})
            img_tag = img_container.find('img') if img_container else None
            image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else "No image available"
            full_image_url = "https:" + image_url if image_url.startswith("//") else image_url

            # Append the details to the products list
            products.append({
                "Name": name,
                "Price": price,
                "URL": full_url,
                "Image": full_image_url
            })
        except Exception as e:
            print(f"Error extracting product details: {e}")
            continue

    # Navigate to the next page
    if i < max_pages:
        clicked = False
        for _ in range(3):  # Retry clicking up to 3 times
            try:
                load_more_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-auto-id="loadMoreProducts"]'))
                )
                browser.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                sleep(1)
                load_more_button.click()
                clicked = True
                break
            except Exception as e:
                print(f"Retry clicking 'Load More' button failed: {e}")
        if not clicked:
            print("Failed to click 'Load More' after multiple attempts.")
            break

# Close the browser
browser.quit()

# Save the products to a JSON file
with open("asos_new_in.json", 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=4, ensure_ascii=False)

print(f"Scraped data saved to asos_new_in.json")
