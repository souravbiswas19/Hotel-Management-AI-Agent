from dotenv import load_dotenv
import os
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DIRECTORY_NAME = os.getenv("DIRECTORY_NAME")
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")