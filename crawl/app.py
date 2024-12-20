from flask import Flask, request, render_template
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

app = Flask(__name__)

# Open the Whoosh index
index = open_dir("index")

# Homepage with search functionality
@app.route("/", methods=["GET", "POST"])
def search():
    results = []
    query_string = ""

    if request.method == "POST":
        query_string = request.form.get("query")
        with index.searcher() as searcher:
            query = QueryParser("name", index.schema).parse(query_string)
            results = searcher.search(query, limit=10)

    return render_template("search.html", results=results, query=query_string)

if __name__ == "__main__":
    app.run(debug=True)
