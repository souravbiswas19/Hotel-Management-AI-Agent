from langchain_community.vectorstores import Chroma, FAISS

def store_to_chromadb(documents, embeddings):
    """
    Store a vector store to a ChromaDB.
    """
    PERSIST_STORAGE = "./chroma_storage"
    chroma_db = Chroma.from_documents(documents=documents, embedding= embeddings, persist_directory=PERSIST_STORAGE)
    return chroma_db

def load_from_chromadb(embeddings):
    """
    Load a vector store from a ChromaDB.
    """
    PERSIST_STORAGE = "./chroma_storage"
    chroma_db = Chroma(persist_directory=PERSIST_STORAGE, embedding_function=embeddings)
    return chroma_db

def store_to_FAISS(documents, embeddings):
    """
    Store a vector store to a FAISS.
    """
    faiss_db = FAISS.from_documents(documents=documents, embedding= embeddings)
    faiss_db.save_local("faiss_store")
    return faiss_db

def load_from_FAISS(embeddings):
    """
    Load a vector store from a ChromaDB.
    """
    faiss_db = FAISS.load_local("faiss_store", embeddings=embeddings, allow_dangerous_deserialization=True)
    return faiss_db
