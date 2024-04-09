"""This python file implements the env variables for API coniguration"""
# .env file contains the necessary key values that need to be loaded for using models
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# End-of-file (EOF)