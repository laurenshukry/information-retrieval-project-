from flask import Flask, request, render_template, jsonify
from whoosh import index
from whoosh.qparser import QueryParser
import os
import json

app = Flask(__name__)

# Load the Whoosh index
INDEX_DIR = "index"
if not os.path.exists(INDEX_DIR):
    print(f"Index directory '{INDEX_DIR}' does not exist. Please run 'index.py' to create it.")
    ix = None
else:
    try:
        ix = index.open_dir(INDEX_DIR)
    except Exception as e:
        print(f"Error opening index: {e}")
        ix = None

@app.route("/", methods=["GET"])
def search():
    query_string = request.args.get("query", "").strip()
    price_filter = request.args.get("price", "").strip()
    results = []

    if ix:
        try:
            with ix.searcher() as searcher:
                parser = QueryParser("name", ix.schema)
                query = parser.parse(query_string) if query_string else parser.parse("*")
                search_results = searcher.search(query, limit=100)

                results = []
                for hit in search_results:
                    image_url = hit.get("image", "https://via.placeholder.com/150")
                    
                    # Replace Shein placeholder images with custom placeholder
                    if "bg-grey-solid-color" in image_url:
                        image_url = "{{ url_for('static', filename='VELOURIA.png') }}"

                    results.append({
                        "name": hit["name"],
                        "price": hit.get("price", "N/A"),
                        "url": hit.get("url", "#"),
                        "image": image_url,
                    })

                if price_filter:
                    results.sort(key=lambda item: float(item["price"].strip("$").replace("CHF", "")),
                                 reverse=price_filter == "high-low")
        except Exception as e:
            print(f"Error during search: {e}")

    return render_template("search.html", results=results, query=query_string, price_filter=price_filter)


@app.route("/like_product", methods=["POST"])
def like_product():
    product_id = request.form.get("product_id")
    return update_likes(product_id, like=True)

@app.route("/dislike_product", methods=["POST"])
def dislike_product():
    product_id = request.form.get("product_id")
    return update_likes(product_id, like=False)
DATA_FILES = ["data/asos.json", "data/shein.json"]  # Paths to your original data files

def update_likes(product_name, like):
    try:
        updated = False

        # Process each file independently
        for file_path in DATA_FILES:
            with open(file_path, "r", encoding="utf-8") as file:
                items = json.load(file)

            # Update the specific product's score if found
            for item in items:
                if item["Name"] == product_name:
                    item["Score"] = item.get("Score", 0) + (1 if like else -1)
                    updated = True
                    break  # Exit after updating the product

            # Save the updated file
            if updated:
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(items, file, indent=4)
                break  # Stop after updating the correct file

        if updated:
            return jsonify({"message": "Success", "product_name": product_name, "new_score": item["Score"]})
        else:
            return jsonify({"error": "Product not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/suggested", methods=["GET"])
def suggested():
    try:
        price_filter = request.args.get("price", "").strip()  # Get the price filter parameter
        unique_items = {}

        # Combine all data files into a single list
        for file_path in DATA_FILES:
            with open(file_path, "r") as file:
                items = json.load(file)
                for item in items:
                    # Use the 'Name' field as the unique key to avoid duplicates
                    if item["Name"] not in unique_items and item.get("Score", 0) > 0:
                        # Check for Shein placeholder image and replace it
                        image_url = item.get("Image", "https://via.placeholder.com/150")
                        if "bg-grey-solid-color" in image_url:
                            image_url = "{{ url_for('static', filename='VELOURIA.png') }}"
                        
                        # Update the item with the corrected image
                        unique_items[item["Name"]] = {
                            "Name": item["Name"],
                            "Price": item.get("Price", "0"),
                            "URL": item.get("URL", "#"),
                            "Image": image_url,
                            "Score": item.get("Score", 0),
                            "Category": item.get("Category", "Uncategorized")
                        }

        # Sort items with positive scores by score in descending order (default sorting)
        suggestions = sorted(unique_items.values(), key=lambda x: x["Score"], reverse=True)

        # Apply price sorting if needed
        if price_filter == "low-high":
            suggestions.sort(key=lambda x: float(x.get("Price", "0").strip("CHF").replace(",", ".")))
        elif price_filter == "high-low":
            suggestions.sort(key=lambda x: float(x.get("Price", "0").strip("CHF").replace(",", ".")), reverse=True)

    except Exception as e:
        print(f"Error: {e}")
        suggestions = []

    # Pass the price_filter back to the template for persistence
    return render_template("suggestions.html", suggestions=suggestions, price_filter=price_filter)




# List of common clothing-related words for query completion
clothing_terms = [
    "Dress", "Socks", "Shirt", "Pants", "Jacket", "Skirt", "Sweater", "Jeans",
    "Blouse", "Coat", "T-shirt", "Shorts", "Suit", "Blazer", "Hat", "Scarf",
    "Gloves", "Boots", "Sandals", "Underwear", "Belt", "Tie", "Leggings", "Trousers",
    "Cardigan", "Hoodie", "Pajamas", "Swimsuit", "Bikini", "Vest", "Gown", "Kimono",
    "Poncho", "Sneakers", "Heels", "Mittens", "Cap", "Overalls", "Bra", "Lingerie",
    "Nightgown", "Slippers", "Flip-flops", "Stockings", "Beanie", "Tunic", "Pullover",
    "Sarong", "Jumpsuit", "Tights"
]

@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "").lower().strip()
    if not query:  # Return empty suggestions for an empty query
        return jsonify([])

    # Filter clothing terms that start with the query
    suggestions = [word for word in clothing_terms if word.lower().startswith(query)]

    return jsonify(suggestions[:10])  # Return the top 10 matches





if __name__ == "__main__":
    app.run(debug=True)
