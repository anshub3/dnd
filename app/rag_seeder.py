# seed_rag.py
from app.core.rag_setup import ingest_documents
import os

def main():
    # Path to your official D&D documentation
    pdf_path = "./data/docs/dnd_srd_5.1.pdf"
    
    if os.path.exists(pdf_path):
        # HERE IS THE INVOCATION
        ingest_documents(pdf_path)
        print("Successfully indexed official rules into ChromaDB.")
    else:
        print(f"Error: Could not find PDF at {pdf_path}. Please add it to your project.")

if __name__ == "__main__":
    main()