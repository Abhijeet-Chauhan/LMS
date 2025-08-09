import os
from qdrant_client import QdrantClient
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, Distance, PointStruct

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = "lms_collection"

# Connect to local Qdrant
client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)

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

    #  Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Generate embeddings
    vectors = [embedder.encode(chunk.page_content).tolist() for chunk in chunks]

    # Create collection if not exists
    existing_collections = [col.name for col in client.get_collections().collections]
    if QDRANT_COLLECTION not in existing_collections:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=len(vectors[0]),
                distance=Distance.COSINE
            )
        )

    # Upload to Qdrant
    payloads = [{"page_content": chunk.page_content} for chunk in chunks]
    points = [
        PointStruct(id=i, vector=vectors[i], payload=payloads[i])
        for i in range(len(vectors))
    ]

    client.upsert(collection_name=QDRANT_COLLECTION, points=points)

    return f"Ingested {len(chunks)} chunks into Qdrant"

# Query Function
def query_textbook(query: str, top_k: int = 3):
    """Search Qdrant and return most relevant chunks."""
    query_vector = embedder.encode(query).tolist()
    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k
    )
    return [hit.payload["text"] for hit in results]

# Test Script
if __name__ == "__main__":
    pdf_path = "C:/Users/Asus/Desktop/test/LMS/book/keww106.pdf"
    print(ingest_file(pdf_path))

    query = "Explain Newton's third law"
    matches = query_textbook(query)

    print("\n=== Top Matches ===")
    for i, chunk in enumerate(matches, 1):
        print(f"{i}. {chunk}\n")
