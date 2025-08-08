from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "lms_collection"

client = QdrantClient(url=QDRANT_URL)

print(f"Attempting to delete collection: '{QDRANT_COLLECTION}'...")

try:
    # Delete the collection
    operation_result = client.delete_collection(collection_name=QDRANT_COLLECTION)
    if operation_result:
        print(f"Collection '{QDRANT_COLLECTION}' deleted successfully!")
    else:
        print(f"Collection '{QDRANT_COLLECTION}' could not be deleted or did not exist.")

except UnexpectedResponse as e:
    print(f"Could not delete collection. It likely did not exist. Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")