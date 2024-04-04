"""This is the FastAPI module for creating api endpoints"""
# Libraries imported 
import os
from typing import Optional
import jwt
from Authentication.configure import JWT_SECRET_KEY
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from file_handler import process_pdf, process_csv, process_txt, process_docx
from config import GOOGLE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from vector_database import store_to_chromadb, load_from_chromadb
from tools_builder import build_tools
from agent import build_agent
import Authentication.schemas as schemas
import Authentication.models as models
from Authentication.models import User
from Authentication.database import Base, SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException,status, Header
from Authentication.auth_bearer import JWTBearer
from Authentication.utils import create_access_token, get_hashed_password, verify_password

# Initialization of FastAPI
app = FastAPI()

Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Initialization of Google Gemini
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.5)
# Initialization of Google Gemini Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
chat_history = []
agent_executer = None


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email already registered")
    encrypted_password =get_hashed_password(user.password)
    new_user = models.User(username=user.username, email=user.email, password=encrypted_password )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message":"user created successfully"}

@app.post('/login' ,response_model=schemas.TokenSchema)
def login(request: schemas.Logindetails, db: Session = Depends(get_session), ):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )    
    access=create_access_token(user.id)
    token_db = models.TokenTable(user_id=user.id,  access_token=access)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access
    }

# API End point to accept the PDF file from the user
@app.post("/upload/", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_202_ACCEPTED)
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
        
        # Removes the file from the local storage so that memory is not occupied
        os.remove(file.filename)
        return {'Message': 'File Stored successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/ask_query/", status_code=status.HTTP_302_FOUND)
async def get_reply(session_id: int, question: str, db: Session = Depends(get_session), dependencies=Depends(JWTBearer())):
    """Function to get a reply"""
    global agent_executer
    try:
        try:
            
            payload = jwt.decode(dependencies, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('sub')
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except (jwt.InvalidTokenError, ValueError, AttributeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Check if session exists for the user
        user_session = db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user.id, models.ChatHistory.session_id == session_id).first()
        if not user_session:
            # Create a new session entry
            session_entry = models.ChatHistory(user_id=user.id, session_id=session_id, question="", response="")
            db.add(session_entry)
            db.commit()
            db.refresh(session_entry)

        # Retrieve chat history for the session
        chroma_db = load_from_chromadb(embeddings=embeddings)
        retriever = chroma_db.as_retriever()
        tools = build_tools(retriever=retriever, llm=llm)
        if agent_executer is None:
            agent_executer = build_agent(llm=llm, tools=tools)
            print("Agent Successfully initialized")
        output = agent_executer.invoke({"input":question,"chat_history": chat_history})
        new_chat_entry = models.ChatHistory(user_id=user.id, session_id=session_id, question=question, response=output["output"])
        db.add(new_chat_entry)
        db.commit()
        chat_history.append({'question': question, 'response': output["output"]})
        session_chat_history = db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user.id, models.ChatHistory.session_id == session_id).all()
        return {'Chat History':session_chat_history, 'Message': output["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/get_current_users')
def get_current_user(session_id: int,session: Session = Depends(get_session), dependencies=Depends(JWTBearer())):
    try:
        payload = jwt.decode(dependencies, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        session_chat_history = session.query(models.ChatHistory).filter(models.ChatHistory.user_id == user.id, models.ChatHistory.session_id == session_id).all()
        return session_chat_history
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.InvalidTokenError, ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
