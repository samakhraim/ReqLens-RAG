import os
from utils import chunk_text, get_embedding, save_json

DATA_FOLDER = "data"
STORE_PATH = "vector_store/store.json"


def ingest_documents():
    all_chunks = []

    for root, dirs, files in os.walk(DATA_FOLDER):
        for filename in files:
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(root, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            if not text.strip():
                continue

            project_name = os.path.basename(root)
            relative_path = os.path.relpath(file_path, DATA_FOLDER)

            chunks = chunk_text(text)

            for index, chunk in enumerate(chunks):
                print(f"Embedding {relative_path} chunk {index + 1}/{len(chunks)}")

                embedding = get_embedding(chunk)

                all_chunks.append({
                    "project": project_name,
                    "source": relative_path,
                    "chunk_index": index,
                    "text": chunk,
                    "embedding": embedding
                })

    save_json(STORE_PATH, all_chunks)

    print(f"\nDone. Saved {len(all_chunks)} chunks to {STORE_PATH}")


if __name__ == "__main__":
    ingest_documents()