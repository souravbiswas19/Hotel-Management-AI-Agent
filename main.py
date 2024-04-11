"""This is the FastAPI module for creating api endpoints"""
# Libraries imported 
import os
import jwt
import json
from uuid import uuid4
from title_generator import generate_title
from Authentication.configure import JWT_SECRET_KEY
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from file_handler import process_pdf, process_csv, process_txt, process_docx
from config import OPENAI_API_KEY
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
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
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=1, api_key=OPENAI_API_KEY)
# Initialization of Google Gemini Embeddings
class CustomOpenAIEmbeddings(OpenAIEmbeddings):

    def __init__(self, openai_api_key, *args, **kwargs):
        super().__init__(openai_api_key=openai_api_key, *args, **kwargs)
        
    def _embed_documents(self, texts):
        return super().embed_documents(texts)  # <--- use OpenAIEmbedding's embedding function

    def __call__(self, input):
        return self._embed_documents(input)   

embeddings = CustomOpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
chat_history = []
agent_executer = None



@app.post("/register",response_model=schemas.UserRegister ,
            tags=["users data"],
            status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Email already registered")
    encrypted_password =get_hashed_password(user.password)
    new_user = models.User(username=user.username, email=user.email, password=encrypted_password )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return schemas.UserRegister(message="User created successfully")

@app.post('/login' ,response_model=schemas.TokenSchema, 
            tags=["users action"],
            status_code=status.HTTP_202_ACCEPTED)
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
    return schemas.TokenSchema(message="Successful login",access_token=access)

@app.post('/logout', response_model=schemas.UserLogout,
            tags=["users action"],
            status_code=status.HTTP_202_ACCEPTED)
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
    try:
        # Decode the JWT token
        payload = jwt.decode(dependencies, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('sub')

        # Check if the user exists
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Delete the access token from the database
        db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id).delete()
        db.commit()
        return schemas.UserLogout(message="Logout successful")
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.InvalidTokenError, ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")




# API End point to accept the PDF file from the user
@app.post("/upload", dependencies=[Depends(JWTBearer())],
            tags=["admin service"],
            status_code=status.HTTP_202_ACCEPTED)
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
            raise HTTPException(status_code=400, 
                                detail="Only PDF, CSV, TXT and DOCX files are allowed")
        # Function called to store the documents into the database
        chroma_db = store_to_chromadb(documents=documents, embeddings=embeddings)
        
        # Removes the file from the local storage so that memory is not occupied
        os.remove(file.filename)
        return {'Message': 'File Stored successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e





@app.post("/ask_query", status_code=status.HTTP_202_ACCEPTED,
          tags=["users service"],
          response_model=schemas.QueryResponse)
async def get_reply( question: str, 
                    session_id: str=None, 
                    db: Session = Depends(get_session), 
                    dependencies=Depends(JWTBearer())):
    """Function to get a reply"""
    global agent_executer
    try:
        try:
            payload = jwt.decode(dependencies, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('sub')
            
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
            user = db.query(User).filter(
                User.id == user_id).first()
            
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        
        except (jwt.InvalidTokenError, ValueError, AttributeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        
        if session_id is None:
            session_id = str(uuid4())

        # Retrieve chat history for the session
        chroma_db = load_from_chromadb(embeddings=embeddings)
        retriever = chroma_db.as_retriever()
        tools = build_tools(retriever=retriever, llm=llm)
        if agent_executer is None:
            agent_executer = build_agent(llm=llm, tools=tools)
            print("Agent Successfully initialized")
        output = agent_executer.invoke({"input":question,"chat_history": chat_history})
        chat_history.append({'question': question, 'response': output["output"]})
        # Check if session exists for the user
        title = generate_title(output["output"])
        user_session = db.query(models.ChatHistory).filter(
            models.ChatHistory.user_id == user.id, 
            models.ChatHistory.session_id == session_id).first()
        
        
        if not user_session:
            # Create a new session entry
            session_entry = models.ChatHistory(
                user_id=user.id, 
                session_id=session_id, 
                question=question, 
                response=output["output"])
            db.add(session_entry)
            db.commit()
            db.refresh(session_entry)
            # Inside your API endpoint function after generating the title
            new_title_entry = models.Title(
                user_id=user.id, 
                session_id=session_id, 
                title=title)
            db.add(new_title_entry)
            db.commit()
        else:
            new_chat_entry = models.ChatHistory(
                user_id=user.id, 
                session_id=session_id, 
                question=question, 
                response=output["output"])
            db.add(new_chat_entry)
            db.commit()

        session_chat_history = db.query(models.ChatHistory).filter(
            models.ChatHistory.user_id == user.id, 
            models.ChatHistory.session_id == session_id).all()


        chat_history_entries = [{"user_id": chat_entry.user_id, "question": chat_entry.question, 
                                 "id": chat_entry.id, "response": chat_entry.response, 
                                 "session_id": chat_entry.session_id} for chat_entry in session_chat_history]
    
        # return {'Title':title, 'Chat History':session_chat_history, 'Message': output["output"]}
        return schemas.QueryResponse(Title=title, 
                                     ChatHistory=chat_history_entries, 
                                     Message=output["output"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@app.get('/get_chat_by_session_id/c/{session_id}',
            tags=["users service"],
            response_model=schemas.SessionChatResponse, 
            status_code=status.HTTP_202_ACCEPTED)

def get_chat_by_id(session_id: str,
                   session: Session = Depends(get_session), 
                   dependencies=Depends(JWTBearer())):
    try:
        payload = jwt.decode(dependencies, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        session_chat_history = session.query(models.ChatHistory).filter(
            models.ChatHistory.user_id == user.id,
            models.ChatHistory.session_id == session_id).all()
        
        title_session = session.query(models.Title).filter(
            models.Title.session_id == session_id, 
            models.Title.user_id==user.id).all()
        title_name = title_session[0].title

        chat_history_entries = [{"user_id": chat_entry.user_id, "question": chat_entry.question, 
                                 "id": chat_entry.id, "response": chat_entry.response, 
                                 "session_id": chat_entry.session_id} 
                                 for chat_entry in session_chat_history]

        # return {"Title": title_name, "ChatHistory": session_chat_history}
        return schemas.SessionChatResponse(Title=title_name, ChatHistory=chat_history_entries)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.InvalidTokenError, ValueError, AttributeError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))




@app.get('/get_all_chat', 
            tags=["users service"],
            response_model=schemas.TitleListResponse, 
            status_code=status.HTTP_202_ACCEPTED)

def get_all_chat(db: Session = Depends(get_session),
                 dependencies=Depends(JWTBearer())):

    try:
        payload = jwt.decode(dependencies, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('sub')
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        
        title_session = db.query(models.Title.session_id, models.Title.title).filter(
            models.Title.user_id == user.id).all()
        
        session_titles = [{"session_id": entry[0], "title": entry[1]} for entry in title_session]
        return schemas.TitleListResponse(titles=session_titles)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.InvalidTokenError, ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")