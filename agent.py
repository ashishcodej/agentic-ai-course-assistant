# agent.py

import os
from typing import List

# 🔑 SET YOUR GROQ KEY HERE
os.environ["GROQ_API_KEY"] = "your_actual_key"

# -----------------------------
# GLOBALS (lazy load)
# -----------------------------
embedder = None
collection = None
llm = None


# -----------------------------
# INITIALIZE SYSTEM
# -----------------------------
def initialize_system():
    global embedder, collection, llm

    if embedder is not None:
        return

    import chromadb
    from sentence_transformers import SentenceTransformer
    from langchain_groq import ChatGroq

    # Embeddings
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    documents = [
        "Agentic AI systems can reason, act and use tools.",
        "ReAct framework combines reasoning and acting.",
        "Memory helps agents maintain context across turns.",
        "Embeddings convert text into vectors.",
        "ChromaDB is a vector database.",
        "LangChain helps build LLM applications.",
        "RAG retrieves context before answering.",
        "LangGraph builds workflows using nodes and edges.",
        "RAGAS evaluates AI systems.",
        "Deployment uses Streamlit or FastAPI."
    ]

    embeddings = embedder.encode(documents).tolist()

    client = chromadb.Client()
    collection = client.create_collection("course_assistant")

    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=[str(i) for i in range(len(documents))]
    )

  
    llm = ChatGroq(model="llama-3.1-8b-instant")


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def ask_agent(question: str):
    initialize_system()

    query_embedding = embedder.encode([question]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )

    context = "\n".join(results["documents"][0])

    prompt = f"""
You are an AI assistant.

Use the context to answer clearly.

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    answer = response.content.strip()

    return answer