import warnings
import urllib3
import logging
from elasticsearch import Elasticsearch
from config import ES_URL, ES_API_KEY

# Suppress Python warnings
warnings.filterwarnings("ignore")

# Suppress urllib3-specific warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Suppress Elasticsearch library warnings
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

es = Elasticsearch(
    ES_URL,
    api_key=ES_API_KEY,  
    verify_certs=True    # Ensure SSL certificates are verified
)

# Main function to test the connection
def main():
    try:
        # Test the connection to Elasticsearch
        if es.ping():
            print("Connected to Elasticsearch successfully!")
        else:
            print("Failed to connect to Elasticsearch.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
