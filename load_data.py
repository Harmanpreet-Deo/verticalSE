import json
import hashlib
import warnings
import urllib3
import logging
from urllib.parse import urlparse
from elasticsearch import Elasticsearch, helpers
from config import ES_URL, ES_API_KEY

# Suppress warnings
warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

es = Elasticsearch(
    ES_URL,
    api_key=ES_API_KEY,  # Use the API key for authentication
    verify_certs=True    # Ensure SSL certificates are verified
)

def normalize_url(url):
    """
    Normalize the URL to avoid duplicate IDs due to different formats of the same URL.
    Removes trailing slashes and query parameters.
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

def generate_id(url):
    """
    Generate a unique ID by hashing the normalized URL.
    """
    normalized_url = normalize_url(url)
    return hashlib.md5(normalized_url.encode("utf-8")).hexdigest()

def load_data(file_path, index_name):
    """
    Load preprocessed data into Elasticsearch, ensuring no duplicate IDs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        actions = []
        seen_ids = set()  # Track unique IDs to prevent overwrites

        for entry in data:
            url = entry.get("url")
            if not url:  # Skip invalid documents
                continue

            doc_id = generate_id(url)  # Generate unique ID
            if doc_id in seen_ids:
                continue  # Skip duplicate documents
            seen_ids.add(doc_id)

            actions.append({
                "_op_type": "index",
                "_index": index_name,
                "_id": doc_id,
                "_source": entry,
            })

        print(f"Prepared {len(actions)} unique actions for indexing.")

        # Track success and failure
        success_count = 0
        error_count = 0

        # Bulk indexing with error tracking
        for success, info in helpers.parallel_bulk(es, actions, raise_on_error=False):
            if success:
                success_count += 1
            else:
                error_count += 1

        es.indices.refresh(index=index_name)
        print(f"{success_count} document(s) successfully loaded into '{index_name}' index.")
        print(f"{error_count} document(s) failed to load.")

    except Exception as e:
        print(f"Error loading data to Elasticsearch: {e}")

if __name__ == "__main__":
    file_path = "processed_data.json"
    index_name = "climate_data"
    load_data(file_path, index_name)
