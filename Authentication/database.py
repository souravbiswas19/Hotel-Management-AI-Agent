from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from Authentication.configure import DATABASE_URL
engine = create_engine(DATABASE_URL,echo=True,pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()