from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
import os
import json

# Define the schema
schema = Schema(
    name=TEXT(stored=True),
    price=TEXT(stored=True),
    url=ID(stored=True, unique=True),
    image=ID(stored=True)  # Store image URLs for product images
)

# Create or open index directory
index_dir = "index"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)
    ix = create_in(index_dir, schema)  # Create a new index if it doesn't exist
else:
    ix = open_dir(index_dir)  # Open existing index

# JSON data files to index
data_files = ["data/asos.json", "data/shein.json"]

# Index the data
with ix.writer() as writer:
    for file in data_files:
        try:
            # Open and load JSON data
            with open(file, "r", encoding="utf-8") as f:
                products = json.load(f)

                # Iterate through each product in the JSON
                for item in products:
                    try:
                        writer.add_document(
                            name=item.get("Name", "No name available"),
                            price=item.get("Price", "No price available"),
                            url=item.get("URL", ""),  # URL field is mandatory
                           image=item.get("Image", "/static/VELOURIA.png")  # Add leading slash for absolute path

 # Use a placeholder if missing
                        )
                    except Exception as e:
                        print(f"Error indexing item: {item}. Error: {e}")

        except FileNotFoundError:
            print(f"File not found: {file}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file}")

print("Indexing completed!")
