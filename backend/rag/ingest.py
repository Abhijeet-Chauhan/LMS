import os
from qdrant_client import QdrantClient, models
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# --- UPDATED: Qdrant Configuration for Cloud ---
# Get your credentials from environment variables for deployment
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = "lms_collection"

# --- UPDATED: Connect to Qdrant Cloud ---
# This now uses your API Key for authentication
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# Embedding Model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Ingest Function
def ingest_file(file_path: str):
    """Ingest PDF or TXT file into Qdrant."""
    # Load document
    if file_path.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.lower().endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Use PDF or TXT.")

    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Generate embeddings
    vectors = embedder.encode([chunk.page_content for chunk in chunks])

    # Check if the collection exists, if not, create it.
    # This is a safer check than getting all collections.
    try:
        client.get_collection(collection_name=QDRANT_COLLECTION)
    except Exception:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=vectors.shape[1],  
                distance=models.Distance.COSINE
            )
        )

    # Upload to Qdrant
    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=models.Batch(
            ids=[i for i in range(len(chunks))], 
            vectors=vectors.tolist(),
            payloads=[{"page_content": chunk.page_content, "metadata": chunk.metadata} for chunk in chunks]
        ),
        wait=True
    )

    return f"Ingested {len(chunks)} chunks into Qdrant collection: {QDRANT_COLLECTION}"


def query_textbook(query: str, top_k: int = 3):
    """Search Qdrant and return most relevant chunks."""
    query_vector = embedder.encode(query).tolist()
    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k
    )

    return [hit.payload["page_content"] for hit in results]

