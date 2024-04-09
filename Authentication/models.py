from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Authentication.database import Base
import datetime
# Define the User model

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50),  nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    # Add a relationship with chat history
    chat_history = relationship("ChatHistory", back_populates="user")


class TokenTable(Base):
    __tablename__ = "token"
    user_id = Column(Integer)
    access_token = Column(String(450), primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.now)


# Define the ChatHistory model
class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String)
    question = Column(String)
    response = Column(String)
    
    # Define the relationship with User
    user = relationship("User", back_populates="chat_history")
