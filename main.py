"""This is the FastAPI module for creating api endpoints"""
# Libraries imported 
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pdf_handler import process_pdf
from config import GOOGLE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from vector_database import store_to_chromadb
from tools_builder import build_tools
from agent import build_agent

# Initialization of FastAPI
app = FastAPI()
# Initialization of Google Gemini
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.5)
# Initialization of Google Gemini Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

agent_executer = None

# API End point to accept the PDF file from the user
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Function to upload a file"""
    global agent_executer
    try:
        # Check if the file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        # Save the uploaded PDF file
        with open(file.filename, "wb") as buffer:
            buffer.write(await file.read())
        # Documents are being read from the pdf
        documents = process_pdf(filename=file.filename)
        # Function called to store the documents into the database
        chroma_db = store_to_chromadb(documents=documents, embeddings=embeddings)
        retriever = chroma_db.as_retriever()
        tools = build_tools(retriever=retriever, llm=llm)
        agent_executer = build_agent(llm=llm, tools=tools)
        return {'Message': 'File Stored successfully and Agent Successfully initialized'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/askquery/")
async def get_reply(question: str):
    """Function to get a reply"""
    global agent_executer
    try:
        if agent_executer is None:
            raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Agent not initialized")
        output = agent_executer.invoke({"input":question})
        return {'Message': output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))