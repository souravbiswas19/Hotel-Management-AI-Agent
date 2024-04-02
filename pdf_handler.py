"""This file implements the extraction of pdf content from pdf file and returns them as Document objects"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
#fucntion to accept the file name and return a Document object
def process_pdf(filename):
    """PyPDFLoader has been used to load the pdf from the specified location of the path mentioned"""
    loader = PyPDFLoader(filename)
    #file converted to document
    docs = loader.load_and_split()
    #The whole document is split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024)
    documents = text_splitter.split_documents(docs)
    return documents #return the document object