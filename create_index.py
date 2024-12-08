import warnings
import urllib3
import logging
from elasticsearch import Elasticsearch
from config import ES_URL, ES_API_KEY

# Suppress Python warnings
warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging to suppress messages from urllib3 and elasticsearch
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

es = Elasticsearch(
    ES_URL,
    api_key=ES_API_KEY,  # Use the API key for authentication
    verify_certs=True    # Ensure SSL certificates are verified
)

# Define the refined index structure
index_config = {
    "mappings": {
        "properties": {
            "url": {"type": "keyword"},
            "title": {"type": "text"},
            "meta_description": {"type": "text"},
            "content": {
                "type": "text",
                "analyzer": "english"  # Use built-in English analyzer
            },
            "autocomplete": {
                "type": "search_as_you_type"  # Optimized for auto-suggestions
            }
        }
    }
}

def main():
    try:
        # Test the connection
        if es.ping():
            print("Connected to Elasticsearch successfully!")
        else:
            print("Failed to connect to Elasticsearch. Exiting...")
            return

        # Create the index if it doesn't exist
        if not es.indices.exists(index="climate_data"):
            es.indices.create(index="climate_data", body=index_config)
            print("Index created successfully!")
        else:
            print("Index already exists!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
