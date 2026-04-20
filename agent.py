# agent.py

import os
from typing import TypedDict
from langgraph.graph import StateGraph




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

    # Embedding model
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # Knowledge base
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

    # Groq LLM (working model)
    llm = ChatGroq(model="llama-3.1-8b-instant")


# -----------------------------
# STATE
# -----------------------------
class AgentState(TypedDict):
    question: str
    retrieved: str
    answer: str
    route: str


# -----------------------------
# NODES
# -----------------------------

# 1. ROUTER
def router_node(state):
    question = state["question"].lower()

    # Tool queries
    if any(word in question for word in ["calculate", "sum", "add", "multiply", "+", "-", "*", "/"]):
        state["route"] = "tool"

    # Default: use retrieval for MOST queries
    elif len(question.split()) > 2:
        state["route"] = "retrieve"

    else:
        state["route"] = "fallback"

    return state


# 2. RETRIEVAL (RAG)
def retrieval_node(state):
    query_embedding = embedder.encode([state["question"]]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )

    state["retrieved"] = "\n".join(results["documents"][0])
    return state


# 3. TOOL (Calculator)
def tool_node(state):
    try:
        result = eval(state["question"])
        state["answer"] = f"Calculated result: {result}"
    except:
        state["answer"] = "Tool could not process the query."

    return state


# 4. ANSWER GENERATION
def answer_node(state):
    context = state.get("retrieved", "")
    question = state["question"]

    # Only check if context exists
    if not context.strip():
        state["answer"] = "This question is outside the course knowledge base."
        return state

    prompt = f"""
You are an AI assistant.

Answer ONLY from the given context.
If the answer is not present, say:
"This question is outside the course knowledge base."

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)
    state["answer"] = response.content.strip()

    return state

# -----------------------------
# BUILD GRAPH
# -----------------------------
def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("router", router_node)
    builder.add_node("retrieve", retrieval_node)
    builder.add_node("tool", tool_node)
    builder.add_node("answer", answer_node)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "retrieve": "retrieve",
            "tool": "tool",
            "fallback": "answer"
        }
    )

    builder.add_edge("retrieve", "answer")

    return builder.compile()


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def ask_agent(question: str):
    initialize_system()

    graph = build_graph()

    result = graph.invoke({
        "question": question
    })

    return result["answer"]

if __name__ == "__main__":
    print(ask_agent("What is LangGraph?"))
    print(ask_agent("2 + 2"))
    print(ask_agent("Who is Messi?"))
