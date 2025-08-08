from rag.ingest import query_textbook

if __name__ == "__main__":
    query = "Explain Newton's third law"
    matches = query_textbook(query)

    print("=== Top Chunks ===")
    for i, chunk in enumerate(matches, 1):
        print(f"{i}. {chunk}\n")
