from elasticsearch import Elasticsearch, helpers
import json

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Load combined JSON data
with open("combined_products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

# Define the index
index_name = "products"

# Delete the index if it already exists
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

# Create the index
es.indices.create(index=index_name)

# Prepare data for bulk indexing
actions = [
    {
        "_index": index_name,
        "_source": product,
    }
    for product in products
]

# Bulk index the data
helpers.bulk(es, actions)
print(f"Indexed {len(products)} products into Elasticsearch!")
