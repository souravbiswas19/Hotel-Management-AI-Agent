from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from config import OPENAI_API_KEY

def generate_title(content):
    template = "Generate a title inless than 6 to 8 words for the following text:\n{text}\nTitle:"
    prompt = PromptTemplate.from_template(template)
    llm = OpenAI()
    llm = OpenAI(openai_api_key=OPENAI_API_KEY)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    generated_title = llm_chain.run(content)
    return generated_title