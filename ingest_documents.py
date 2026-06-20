import os
import chromadb
from sentence_transformers import SentenceTransformer


KNOWLEDGE_DIR = "knowledge_base"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "consultation_knowledge"

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def main():
    print("Loading embedding model...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    documents = []
    metadatas = []
    ids = []
    embeddings = []

    for filename in os.listdir(KNOWLEDGE_DIR):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(KNOWLEDGE_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks):
            chunk_id = f"{filename}_chunk_{index}"

            documents.append(chunk)
            metadatas.append({
                "source": filename,
                "chunk_index": index
            })
            ids.append(chunk_id)

            embedding = embedding_model.encode(chunk).tolist()
            embeddings.append(embedding)

    if not documents:
        print("No documents found.")
        return

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"Ingested {len(documents)} chunks into ChromaDB.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Database path: {CHROMA_DIR}")


if __name__ == "__main__":
    main()