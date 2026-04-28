import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# a lightweight local embedding model (no API keys)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def ingest_documents(pdf_path: str):
    print(f"--- 📖 Ingesting: {pdf_path} ---")
    
    # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    # 2. Split into chunks (D&D rules need overlap so context isn't cut)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    # 3. Create/Update Vector Store
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory="./data/chroma_db"
    )
    print("--- ✅ RAG Database Ready ---")
    return vectorstore

def get_retriever():
    return Chroma(
        persist_directory="./data/chroma_db", 
        embedding_function=embeddings
    ).as_retriever(search_kwargs={"k": 3})