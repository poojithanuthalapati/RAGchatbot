```python
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os

# Import the .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration
DATA_PATH = "data"
CHROMA_PATH = "chroma_db"

# Initialize a LOCAL embedding model
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initialize the vector store
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# Load PDF documents
loader = PyPDFDirectoryLoader(DATA_PATH)
raw_documents = loader.load()

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

# Create unique IDs
uuids = [str(uuid4()) for _ in range(len(chunks))]

# Add chunks to Chroma
vector_store.add_documents(
    documents=chunks,
    ids=uuids
)

print(f"Successfully added {len(chunks)} chunks to Chroma.")
```
