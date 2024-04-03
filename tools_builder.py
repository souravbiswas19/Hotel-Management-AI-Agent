import json
import requests
from config import GOOGLE_API_KEY
from langchain.agents import Tool
from langchain.chains import LLMMathChain, LLMRequestsChain, LLMChain
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

def api_get_rates(query):
    url = 'https://private-anon-6c36a59c69-tshapiv20.apiary-mock.com/hotels/get_rates/'
    response = requests.get(url)
    return json.dumps(response.json())
search_api_rates = Tool.from_function(name="Search Rates",
                                 func=api_get_rates,
                                 description="Useful for searching Hotel Rates")

def api_get_info(query):
    url = 'https://private-anon-9e7f4fb9c1-tshapiv20.apiary-mock.com/hotels/get_detailed_info/'
    response = requests.get(url)
    return json.dumps(response.json())
search_api_info = Tool.from_function(name="Search Detailed Information",
                                 func=api_get_info,
                                 description="Useful for searching Hotel Details or Information about the hotel")

def api_get_checkout_data(query):
    url = 'https://private-anon-9e7f4fb9c1-tshapiv20.apiary-mock.com/hotels/get_checkout_data/'
    response = requests.get(url)
    return json.dumps(response.json())
search_api_checkout_data = Tool.from_function(name="Search Checkout Details",
                                 func=api_get_checkout_data,
                                 description="Useful for searching Hotel checkout details")

def search_on_google(query):
    template = """Between >>> and <<< are the raw search result text from google.
    Extract the answer to the question '{query}' or say "not found" if the information is not contained.
    Use the format
    Extracted:<answer or "not found">
    >>> {requests_result} <<<
    Extracted:"""

    PROMPT = PromptTemplate(
        input_variables=["query", "requests_result"],
        template=template,
    )
    search_chain = LLMRequestsChain(llm_chain=LLMChain(llm=GoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.5), prompt=PROMPT))
    inputs = {
        "query": query,
        "url": "https://www.google.com/search?q=" + query.replace(" ", "+"),
    }
    return search_chain(inputs)

def build_tools(retriever, llm):
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="hotel_search",
        description="Greet the user and search for information about Hotel check-in, check out, types of rooms, price of rooms, water activities. \
            For any questions on the above topics, you must use this tool!",
    )
    problem_chain = LLMMathChain.from_llm(llm=llm)
    math_tool = Tool.from_function(name="Calculator",
                func=problem_chain.run,
                 description="Useful for when you need to answer questions \
    about math. This tool is only for math questions and nothing else for the price calculation of hotel rooms.")
    search_tool = Tool.from_function(name="Google Search",
                                 func=search_on_google,
                                 description="Useful for searching query for searching query on Internet or when question cannot be answered from the given source. ")
    
    tools = [retriever_tool,math_tool,search_tool,search_api_rates,search_api_info, search_api_checkout_data]
    return tools