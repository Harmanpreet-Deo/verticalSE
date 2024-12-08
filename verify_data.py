import warnings
import urllib3
import logging
from elasticsearch import Elasticsearch
from config import ES_URL, ES_API_KEY

# Suppress Python warnings
warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Suppress Elasticsearch and urllib3 logs
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

es = Elasticsearch(
    ES_URL,
    api_key=ES_API_KEY,  # Use the API key for authentication
    verify_certs=True    # Ensure SSL certificates are verified
)

# Get the count of documents in the index
response = es.count(index="climate_data")
print(f"Total documents in the 'climate_data' index: {response['count']}")
