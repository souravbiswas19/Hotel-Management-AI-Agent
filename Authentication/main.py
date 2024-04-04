import Authentication.schemas as schemas
import Authentication.models as models
import jwt
from datetime import datetime 
from Authentication.models import User
from Authentication.database import Base, SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException,status, Header
from Authentication.auth_bearer import JWTBearer
from functools import wraps
from Authentication.utils import create_access_token, get_hashed_password, verify_password
from fastapi import Header
from typing import Optional
from Authentication.configure import JWT_SECRET_KEY

Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
app=FastAPI()

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
    #refresh = create_refresh_token(user.id)
    token_db = models.TokenTable(user_id=user.id,  access_token=access)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access
    }

@app.get('/getusers', dependencies=[Depends(JWTBearer())])
def get_current_user(session: Session = Depends(get_session), 
                      authorization: Optional[str] = Header(None)):
    print(authorization)
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.InvalidTokenError, ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
