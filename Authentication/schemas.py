from pydantic import BaseModel, EmailStr, Field
import datetime
class UserCreate(BaseModel):
    username: str =  Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

class Logindetails(BaseModel):
    email: EmailStr = Field(default=None)
    password:str = Field(default=None)
        
class TokenSchema(BaseModel):
    access_token: str = Field(default=None)
    #refresh_token: str = Field(default=None)

# class changepassword(BaseModel):
#     email: EmailStr = Field(default=None)
#     old_password:str = Field(default=None)
#     new_password:str = Field(default=None)

class TokenCreate(BaseModel):
    user_id:str = Field(default=None)
    access_token:str = Field(default=None)
    refresh_token:str = Field(default=None)
    created_date:datetime.datetime

class Link(BaseModel):
    link:str = Field(default=None)

class Question(BaseModel):
    question:str = Field(default=None)

class ChatHistory(BaseModel):
    id: int
    user_id: int
    question: str
    response: str