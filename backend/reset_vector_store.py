from qdrant_client import QdrantClient
from qdrant_client.http import models

# Configuration
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "lms_collection"
VECTOR_SIZE = 384 # size for all-MiniLM-L6-v2

client = QdrantClient(url=QDRANT_URL)

print(f"Attempting to reset collection: '{QDRANT_COLLECTION}'...")

try:
    # command deletes the entire collection including all vectors
    delete_result = client.delete_collection(collection_name=QDRANT_COLLECTION)

    if delete_result:
        print(f"Collection '{QDRANT_COLLECTION}' deleted successfully.")
    else:
        print(f"Collection '{QDRANT_COLLECTION}' did not exist, so no need to delete.")

    client.recreate_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE
        ),
    )
    print(f"Collection '{QDRANT_COLLECTION}' created again, ready for new data.")
    print("\nVector store has been reset. You can now ingest a new document.")

except Exception as e:
    print(f"An error occurred: {e}")