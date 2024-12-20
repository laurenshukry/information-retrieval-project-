import json
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, NUMERIC
import os

# Define the schema for the search index
schema = Schema(
    name=TEXT(stored=True),
    price=NUMERIC(stored=True),
    url=TEXT(stored=True),
    image=TEXT(stored=True)
)

# Create the index directory
if not os.path.exists("index"):
    os.mkdir("index")

# Create the index
index = create_in("index", schema)
writer = index.writer()

# Load data from JSON files and index them
json_files = ["asos_new_in.json", "shein.json"]
for file in json_files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            writer.add_document(
                name=item.get("Name", "No name available"),
                price=item.get("Price", 0),
                url=item.get("URL", "No URL available"),
                image=item.get("Image", "No image available")
            )

writer.commit()
print("Indexing completed!")
