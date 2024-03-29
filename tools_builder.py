from langchain.agents import Tool
from langchain.chains import LLMMathChain
from langchain.tools.retriever import create_retriever_tool

def build_tools(retriever, llm):
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="hotel_search",
        description="Search for information about Hotel check-in, check out, types of rooms, price of rooms, water activities. \
            For any questions on the above topics, you must use this tool!",
    )
    problem_chain = LLMMathChain.from_llm(llm=llm)
    math_tool = Tool.from_function(name="Calculator",
                func=problem_chain.run,
                 description="Useful for when you need to answer questions \
    about math. This tool is only for math questions and nothing else for the price calculation of hotel rooms.")
    tools = [retriever_tool,math_tool]
    return tools