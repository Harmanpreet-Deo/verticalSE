import warnings
import logging
import urllib3
from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
from config import ES_URL, ES_API_KEY

# Suppress Python and library warnings
warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging for Waitress and Flask
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)

app = Flask(__name__)

es = Elasticsearch(
    ES_URL,
    api_key=ES_API_KEY,  
    verify_certs=True   
)

# Home route to render the search UI
@app.route("/")
def home():
    app.logger.info("Rendering home page")
    return render_template("index.html")

# Route for favicon to suppress missing file logs
@app.route('/favicon.ico')
def favicon():
    return "", 204  # Return a blank response

# Search route to query Elasticsearch
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    size = 6  # Limit to 6 results per page
    start = (page - 1) * size  # Calculate the starting index

    app.logger.info(f"Search requested for query: '{query}', page: {page}")

    try:
        # Elasticsearch query to fetch the total matching documents
        total_response = es.search(index="climate_data", body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content", "meta_description"]
                }
            }
        })
        total = total_response["hits"]["total"]["value"]

        # Handle cases where the start index exceeds the total results
        if start >= total:
            app.logger.info(f"No results for page {page}, query: '{query}'")
            return jsonify({
                "results": [],
                "total": total,
                "page": page,
                "size": size
            })

        # Elasticsearch query to fetch results for the specific page
        body = {
            "from": start,
            "size": size,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content", "meta_description"]
                }
            }
        }

        response = es.search(index="climate_data", body=body)

        # Extract results with safe handling for null values
        results = []
        for hit in response["hits"]["hits"]:
            results.append({
                "title": hit["_source"].get("title", "No Title"),
                "url": hit["_source"].get("url", "#"),
                "meta_description": hit["_source"].get("meta_description", "No Description"),  # Handle nulls here
                "score": hit["_score"]
            })

        app.logger.info(f"Returned {len(results)} results for query: '{query}', page: {page}")
        return jsonify({
            "results": results,
            "total": total,
            "page": page,
            "size": size
        })

    except Exception as e:
        app.logger.error(f"Error during search: {e}")
        return jsonify({"error": str(e)}), 500

# New route for auto-suggestions
@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("q", "").strip()
    app.logger.info(f"Suggestions requested for query: '{query}'")

    if not query:
        return jsonify({"suggestions": []})  # Return empty list for empty query

    # Extract the last word from the query
    words = query.split()
    last_word = words[-1] if words else ""

    if not last_word:
        return jsonify({"suggestions": []})  # No last word to suggest for

    try:
        # Use `prefix` query for the last word
        body = {
            "query": {
                "prefix": {
                    "autocomplete": {
                        "value": last_word.lower()  # Match prefix case-insensitively
                    }
                }
            },
            "_source": ["autocomplete"],  # Fetch only the `autocomplete` field
            "size": 5  # Limit to 5 suggestions
        }

        response = es.search(index="climate_data", body=body)
        suggestions = []

        # Extract suggestions for the last word
        for hit in response["hits"]["hits"]:
            autocomplete_list = hit["_source"]["autocomplete"]
            for word in autocomplete_list:
                if word.lower().startswith(last_word.lower()) and word not in suggestions:
                    suggestions.append(word)

        app.logger.info(f"Returned {len(suggestions)} suggestions for query: '{query}'")
        return jsonify({"suggestions": suggestions})

    except Exception as e:
        app.logger.error(f"Error during auto-suggest: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run Waitress with logging enabled
    from waitress import serve
    logger.info("Starting the Waitress server...")
    serve(app, host="127.0.0.1", port=5000)
