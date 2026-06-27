import os
from dotenv import load_dotenv
from google import genai
from app.utils import get_embedding, cosine_similarity, load_json
from app.prompts import build_requirement_analysis_prompt


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

client = genai.Client(api_key=api_key)

STORE_PATH = "vector_store/store.json"


def get_retrieval_confidence(score):
    """
    Converts the best similarity score into a human-friendly confidence label.

    Important:
    This is retrieval confidence, not final answer accuracy.
    """
    if score >= 0.80:
        return "High"
    elif score >= 0.65:
        return "Medium"
    else:
        return "Low"


def retrieve_relevant_chunks(question, top_k=5):
    """
    Converts the user's question into an embedding,
    compares it with all stored document chunks,
    and returns the most relevant chunks.
    """
    store = load_json(STORE_PATH)

    if not store:
        raise ValueError("Vector store is empty. Run python ingest.py first.")

    question_embedding = get_embedding(question)

    scored_chunks = []

    for item in store:
        score = cosine_similarity(question_embedding, item["embedding"])
        similarity_percentage = round(float(score) * 100, 2)

        scored_chunks.append({
            "score": float(score),
            "similarity_percentage": similarity_percentage,
            "project": item["project"],
            "source": item["source"],
            "chunk_index": item["chunk_index"],
            "text": item["text"]
        })

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)

    return scored_chunks[:top_k]


def build_context(chunks):
    """
    Builds the context that will be sent to Gemini.
    This context contains only the top retrieved chunks.
    """
    return "\n\n".join([
        f"""
Project: {chunk['project']}
Source: {chunk['source']}
Chunk: {chunk['chunk_index']}
Retrieval Match: {chunk['similarity_percentage']}%

Content:
{chunk['text']}
"""
        for chunk in chunks
    ])


def print_retrieval_report(chunks, best_chunk, retrieval_confidence):
    """
    Prints the retrieval result after Gemini answers.
    """
    print("\n================ BEST SOURCE MATCH ================\n")
    print(f"Best source: {best_chunk['source']}")
    print(f"Project: {best_chunk['project']}")
    print(f"Chunk: {best_chunk['chunk_index']}")
    print(f"Match percentage: {best_chunk['similarity_percentage']}%")
    print(f"Retrieval confidence: {retrieval_confidence}")

    print("\n================ RETRIEVED SOURCES ================\n")

    for chunk in chunks:
        print(
            f"- {chunk['source']} | project: {chunk['project']} "
            f"| chunk {chunk['chunk_index']} | match: {chunk['similarity_percentage']}%"
        )


def answer_question(question):
    """
    Retrieves the best chunks, builds the prompt,
    sends the prompt to Gemini, and prints the answer.
    """
    chunks = retrieve_relevant_chunks(question, top_k=5)

    best_chunk = chunks[0]
    retrieval_confidence = get_retrieval_confidence(best_chunk["score"])

    context = build_context(chunks)

    prompt = build_requirement_analysis_prompt(
        context=context,
        question=question,
        retrieval_confidence=retrieval_confidence,
        best_source=best_chunk["source"],
        best_match_percentage=best_chunk["similarity_percentage"]
    )

    print("\nSending request to Gemini...")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    print("\nGemini response received.")

    print("\n================ REQLENS AI ANSWER ================\n")
    print(response.text)

    print_retrieval_report(
        chunks=chunks,
        best_chunk=best_chunk,
        retrieval_confidence=retrieval_confidence
    )


if __name__ == "__main__":
    print("ReqLens AI — RAG Assistant for Software Requirements Analysis")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("Ask about the project requirements: ")

        if question.lower().strip() == "exit":
            print("Goodbye.")
            break

        try:
            answer_question(question)
        except Exception as error:
            print("\nAn error occurred:")
            print(error)
            print("\nMake sure you already ran: python ingest.py")