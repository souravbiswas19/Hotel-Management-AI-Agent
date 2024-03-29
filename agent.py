from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
# from langchain.memory import ConversationBufferMemory

def build_agent(llm, tools, question):
    prompt = hub.pull("hwchase17/react")
    # memory = ConversationBufferMemory(memory_key="chat_history")
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executer = AgentExecutor(agent=agent, tools=tools, verbose=True)
    output = agent_executer.invoke({"input":question})
    return output