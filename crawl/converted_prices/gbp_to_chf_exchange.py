import json
from forex_python.converter import CurrencyRates
import os

def convert_prices_to_chf(input_file, output_file, base_currency='GBP', target_currency='CHF'):
    """
    Converts the prices in the input JSON file from base_currency to target_currency
    and saves the updated data to the output JSON file.
    
    :param input_file: Path to the input JSON file with original prices.
    :param output_file: Path where the converted JSON will be saved.
    :param base_currency: The original currency code (default 'GBP').
    :param target_currency: The target currency code (default 'CHF').
    """
    c = CurrencyRates()
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' does not exist.")
        return
    
    try:
        # Load the product data from the input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {input_file}: {e}")
        return
    except Exception as e:
        print(f"Unexpected error reading {input_file}: {e}")
        return
    
    try:
        # Fetch the current exchange rate
        rate = c.get_rate(base_currency, target_currency)
        print(f"Current Exchange Rate: 1 {base_currency} = {rate} {target_currency}")
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return
    
    # Convert each product's price
    for product in products:
        price_str = product.get('Price', '').replace(base_currency, '').replace(',', '').strip()
        try:
            price_gbp = float(price_str)
            price_chf = round(price_gbp * rate, 2)
            product['Price'] = f"{target_currency}{price_chf}"
        except ValueError:
            print(f"Invalid price format for product '{product.get('Name', 'Unknown')}': '{product.get('Price', '')}'")
            product['Price'] = "Conversion Error"
        except Exception as e:
            print(f"Error converting price for product '{product.get('Name', 'Unknown')}': {e}")
            product['Price'] = "Conversion Error"
    
    try:
        # Write the updated data to the output JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
        print(f"Prices successfully converted and saved to '{output_file}'.")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    # Define your input and output file paths
    input_json = 'boohoo_new_in.json'         # Replace with your input JSON file name
    output_json = 'boohoo_new_in_chf.json'    # Desired output file name
    
    # Call the conversion function
    convert_prices_to_chf(input_json, output_json)
