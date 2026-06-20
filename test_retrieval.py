import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "consultation_knowledge"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main():
    query = input("Ask a question: ")

    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_embedding = embedding_model.encode(query).tolist()

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    print("\nTop retrieved chunks:")
    print("=" * 80)

    for index, document in enumerate(results["documents"][0], start=1):
        metadata = results["metadatas"][0][index - 1]
        distance = results["distances"][0][index - 1]

        print(f"\nResult {index}")
        print(f"Source: {metadata['source']}")
        print(f"Distance: {distance}")
        print("Content:")
        print(document)


if __name__ == "__main__":
    main()