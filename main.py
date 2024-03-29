from pdf_handler import process_pdf
from llm_embedding import load_Gemini_embeddings, load_Gemini
from vector_database import store_to_chromadb, store_to_FAISS, load_from_chromadb, load_from_FAISS
from tools_builder import build_tools
from agent import build_agent
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()
llm = load_Gemini()
embeddings = load_Gemini_embeddings()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Function to upload a file"""
    try:
        # Check if the file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        # Save the uploaded PDF file
        with open(file.filename, "wb") as buffer:
            buffer.write(await file.read())

        documents = process_pdf(filename=file.filename)
        store_to_chromadb(documents=documents, embeddings=embeddings)
        store_to_FAISS(documents=documents, embeddings=embeddings)
        return {'Message': 'File Stored successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    
@app.post("/askquery/")
async def get_reply(question: str):
    """Function to get a reply"""
    try:
        chroma_db = load_from_chromadb(embeddings)
        faiss_db = load_from_FAISS(embeddings=embeddings)
        # retriever = faiss_db.as_retriever()
        retriever = chroma_db.as_retriever()
        tools = build_tools(retriever=retriever, llm=llm)
        output = build_agent(llm=llm, tools=tools, question=question)
        return {'Message': output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))