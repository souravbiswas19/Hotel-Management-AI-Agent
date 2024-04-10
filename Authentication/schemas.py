from pydantic import BaseModel, EmailStr, Field, UUID4
import datetime
from typing import List

class UserCreate(BaseModel):
    username: str =  Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
    class Config:
        orm_mode = True

class UserRegister(BaseModel):
    message: str = Field(default=None)

class Logindetails(BaseModel):
    email: EmailStr = Field(default=None)
    password:str = Field(default=None)
    class Config:
        orm_mode = True
        
class TokenSchema(BaseModel):
    message: str = Field(default=None)
    access_token: str = Field(default=None)

class UserLogout(BaseModel):
    message: str = Field(default=None)


class Question(BaseModel):
    question:str

class ChatHistoryResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    question: str
    response: str

    class Config:
        orm_mode = True

class QueryResponse(BaseModel):
    Title: str
    ChatHistory: List[ChatHistoryResponse]
    Message: str

class SessionChatResponse(BaseModel):
    Title: str
    ChatHistory: List[ChatHistoryResponse]

class TitleList(BaseModel):
    session_id: str
    title: str

    class Config:
        orm_mode = True

# For Getting all chat session id and title
class TitleListResponse(BaseModel):
    titles: List[TitleList]
