import os
import gradio as gr

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHROMA_PATH = r"chroma_db"

# Use the same embedding model used during ingestion
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initiate Grok
llm = ChatOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="openai/gpt-oss-20b"
)

# Connect to ChromaDB
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# Set up vector store as retriever
num_results = 5
retriever = vector_store.as_retriever(
    search_kwargs={"k": num_results}
)


def stream_response(message, history):

    # Retrieve relevant chunks
    docs = retriever.invoke(message)

    # Add chunks to knowledge
    knowledge = ""

    for doc in docs:
        knowledge += doc.page_content + "\n\n"

    if message is not None:

        partial_message = ""

        rag_prompt = f"""
You are an assistant that answers questions based on the knowledge provided to you.

While answering, do not use your internal knowledge.
Solely use the information provided in the "Knowledge" section.

Do not mention the knowledge section to the user.

Question:
{message}

Conversation history:
{history}

Knowledge:
{knowledge}
"""

        # Stream response from Grok
        for response in llm.stream(rag_prompt):
            partial_message += response.content
            yield partial_message


# Initiate the Gradio app
chatbot = gr.ChatInterface(
    stream_response,
    textbox=gr.Textbox(
        placeholder="Send to the LLM...",
        container=False,
        autoscroll=True,
        scale=7
    ),
)

# Launch the app
chatbot.launch()