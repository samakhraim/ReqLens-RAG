import os
from dotenv import load_dotenv
from google import genai
from utils import get_embedding, cosine_similarity, load_json

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

client = genai.Client(api_key=api_key)

STORE_PATH = "vector_store/store.json"


def retrieve_relevant_chunks(question, top_k=5):
    store = load_json(STORE_PATH)

    if not store:
        raise ValueError("Vector store is empty. Run python ingest.py first.")

    question_embedding = get_embedding(question)

    scored_chunks = []

    for item in store:
        score = cosine_similarity(question_embedding, item["embedding"])

        scored_chunks.append({
            "score": float(score),
            "project": item["project"],
            "source": item["source"],
            "chunk_index": item["chunk_index"],
            "text": item["text"]
        })

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)

    return scored_chunks[:top_k]


def answer_question(question):
    chunks = retrieve_relevant_chunks(question)

    context = "\n\n".join([
        f"Project: {chunk['project']}\nSource: {chunk['source']} | Chunk: {chunk['chunk_index']}\n{chunk['text']}"
        for chunk in chunks
    ])

    prompt = f"""
You are ReqLens AI, a software requirements analysis assistant.

Your job:
Analyze messy client requirements and convert them into clear software planning outputs.

Use only the provided context. Do not invent requirements that are not supported by the context.
If information is missing, list it under "Missing Questions".

Return the answer in this format:

Project Understanding:
...

MVP Scope:
1. ...
2. ...
3. ...

Out of Scope / Phase 2:
- ...

User Stories:
- As a ..., I want ..., so that ...

Acceptance Criteria:
- ...

Suggested Database Entities:
- ...

Suggested API Endpoints:
- ...

Risks / Ambiguities:
- ...

Missing Questions for Client:
- ...

Sources Used:
- ...

Context:
{context}

User Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    print("\n================ REQLENS AI ANSWER ================\n")
    print(response.text)

    print("\n================ RETRIEVED SOURCES ================\n")
    for chunk in chunks:
        print(f"- {chunk['source']} | chunk {chunk['chunk_index']} | similarity: {chunk['score']:.4f}")


if __name__ == "__main__":
    print("ReqLens AI — RAG Assistant for Software Requirements Analysis")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("Ask about the project requirements: ")

        if question.lower().strip() == "exit":
            break

        answer_question(question)