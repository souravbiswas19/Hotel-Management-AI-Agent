"""This is the FastAPI module for creating api endpoints"""
# Libraries imported 
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from file_handler import process_pdf, process_csv, process_txt, process_docx
from config import GOOGLE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from vector_database import store_to_chromadb, load_from_chromadb
from tools_builder import build_tools
from agent import build_agent

# Initialization of FastAPI
app = FastAPI()
# Initialization of Google Gemini
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.5)
# Initialization of Google Gemini Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
chat_history = []
agent_executer = None

# API End point to accept the PDF file from the user
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Function to upload a file"""
    try:
        # Check if the file is a PDF
        # Save the uploaded PDF file
        with open(file.filename, "wb") as buffer:
            buffer.write(await file.read())
        # Documents are being read from the pdf
        if file.filename.endswith(".pdf"):
            documents = process_pdf(filename=file.filename)
        elif file.filename.endswith(".csv"):
            documents = process_csv(filename=file.filename)
        elif file.filename.endswith(".txt"):
            documents = process_txt(filename=file.filename)
        elif file.filename.endswith(".docx"):
            documents = process_docx(filename=file.filename)
        else:
            raise HTTPException(status_code=400, detail="Only PDF, CSV, TXT and DOCX files are allowed")
        # Function called to store the documents into the database
        chroma_db = store_to_chromadb(documents=documents, embeddings=embeddings)
        return {'Message': 'File Stored successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/askquery/")
async def get_reply(question: str):
    """Function to get a reply"""
    global agent_executer
    try:
        chroma_db = load_from_chromadb(embeddings=embeddings)
        retriever = chroma_db.as_retriever()
        tools = build_tools(retriever=retriever, llm=llm)
        if agent_executer is None:
            agent_executer = build_agent(llm=llm, tools=tools)
            print("Agent Successfully initialized")
        output = agent_executer.invoke({"input":question,"chat_history": chat_history})
        chat_history.append({'question': question, 'response': output})
        return {'Message': output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
