import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from time import sleep

# Define the source URL and the number of pages to scrape
source = "https://us.shein.com/super-deals"
max_pages = 5

# Set up Selenium WebDriver in headless mode
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Run in headless mode
browser = webdriver.Chrome(options=options)

# Open the super-deals page
browser.get(source)

# Initialize an empty list to store product details
products = []

# Loop through the pages
for i in range(1, max_pages + 1):
    # Pause to let the page load
    sleep(5)

    # Get the HTML source and parse it with BeautifulSoup
    response = browser.page_source
    soup = BeautifulSoup(response, 'lxml')

    # Find all product sections
    try:
        product_list = soup.find('div', {'class': 'thrifty-find-products'}).find_all('section')
    except AttributeError:
        print("Product list not found. Exiting.")
        break

    # Extract product details
    for section in product_list:
        try:
            # Extract product name
            name = section['aria-label']
            
            # Extract product URL
            url = section.a['href']
            
            # Extract product price
            price = section.find('span', {'class': 'product-item__camecase-price'}).text
            
            # Extract product image URL
            img_tag = section.find('img')  # Locate the <img> tag
            image_url = img_tag['src'] if img_tag else "No image available"  # Get the src attribute

            # Fix relative image URLs
            full_image_url = "https:" + image_url if image_url.startswith("//") else image_url

            # Append the details to the products list
            products.append({
                "Name": name,
                "Price": price.strip(),
                "URL": urljoin("https://shein.com", url),
                "Image": full_image_url  # Use the full image URL here
            })
        except Exception as e:
            print(f"Error extracting product details: {e}")
            continue

    print(f"Page {i}: Extracted {len(product_list)} products.")

    # Navigate to the next page
    if i < max_pages:
        try:
            next_button = browser.find_element(
                By.XPATH,
                f"//span[@class='sui-pagination__inner sui-pagination__hover' and contains(text(),'{i + 1}')]"
            )
            next_button.click()
        except Exception as e:
            print(f"Error navigating to the next page: {e}")
            break

# Close the browser
browser.quit()

# Save the products to a JSON file
with open("shein.json", 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=4, ensure_ascii=False)

print(f"Scraped data saved to shein.json")
