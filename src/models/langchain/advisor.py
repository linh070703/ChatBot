from dotenv import load_dotenv
load_dotenv()

from langchain.agents import load_tools, initialize_agent, Tool, AgentType
from langchain.llms import OpenAI
from langchain.chains import LLMMathChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from typing import List, Dict, Any, Union, Literal, Tuple, Optional
from src.stocks import portfolios

llm = OpenAI(
    temperature=0,
    model_name="text-davinci-003",
)

tools = load_tools(["serpapi", "llm-math"], llm=llm)

# llm_chain = LLMChain(llm=llm, prompt=PromptTemplate(
#     input_variables=["query"],
#     template="{query}"
# ))
# # initialize the LLM tool
# llm_tool = Tool(
#     name='Language Model',
#     func=llm_chain.run,
#     description='use this tool for general purpose queries and logic'
# )

@tool("CompareStock", return_direct=True)
def compare_stock(stocks: List[str]) -> str:
    """Useful for comparing stocks between different companies."""
    stocks : List[str] = eval(stocks)
    return stocks

@tool("Get Top Portfolios", return_direct=True)
def get_top_portfolios() -> str:
    """Useful for getting current top portfolios."""
    return portfolios.get_top_portfolios()

# @tool("Get Top Stocks", return_direct=True)
# def get_top_stocks() -> str:
#     """Useful for getting current top stocks."""
#     return "top stocks"

tools.append(compare_stock)
# tools.append(get_top_portfolios)
# tools.append(get_top_stocks)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5,
)

# print(agent.agent.llm_chain.prompt.template)

def ask(question: str) -> str:
    return agent.run(question)

if __name__ == "__main__":
    print(ask("Compare Apple and Google"))