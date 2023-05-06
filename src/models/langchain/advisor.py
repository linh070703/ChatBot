import os
import sys

sys.path.append("/home/thaiminhpv/Workspace/Code/FUNiX-ChatGPT-Hackathon/Chatbot/Chatbot/")

from dotenv import load_dotenv
load_dotenv()
from langchain.agents import load_tools, initialize_agent, Tool, AgentType
from langchain.llms import OpenAI
from langchain.chains import LLMMathChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from typing import List, Dict, Any, Union, Literal, Tuple, Optional
from src.stocks import portfolios
from src.models import translator

llm = OpenAI(
    temperature=0,
    model_name="text-davinci-003",
    openai_api_key=os.getenv("OPENAI_API_KEYS").split(',')[0],
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

# @tool("CompareStock", return_direct=True)
# def compare_stock(stocks: List[str]) -> str:
#     """Useful for comparing stocks between different companies."""
#     stocks : List[str] = eval(stocks)
#     return stocks

@tool("Get Top Portfolios", return_direct=True)
def get_top_portfolios(top_trending: str) -> str:
    """Useful for getting current top portfolios."""
    return 'Get Top Portfolios', portfolios.get_top_portfolios(top=10)

# @tool("Get Top Stocks", return_direct=True)
# def get_top_stocks() -> str:
#     """Useful for getting current top stocks."""
#     return "top stocks"

# tools.append(compare_stock)
tools.append(get_top_portfolios)
# tools.append(get_top_stocks)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5,
)

print(agent.agent.llm_chain.prompt.template)

def ask(messages: List[Dict[str, str]]) -> str:
    question = messages[-1]['content']
    print(f"Question: {question}")
    answer = agent.run(question)
    print(f"Type of answer: {type(answer)}")
    if isinstance(answer, tuple) and len(answer) > 0 and answer[0] is not None and answer[0] == 'Get Top Portfolios':
        print(f"Returning top portfolios: ...")
        title = "These are some portfolios of stocks that I think best suited for a short term play with the stock market"
        if translator.detect_language_of(question) == 'VIETNAMESE':
            title = "Đây là danh sách các danh mục dựa trên khả năng sinh lời ngắn hạn mà mình tổng hợp được"
        # else:
        #     title = translator.translate(title, src='ENGLISH', dest=translator.detect_language_of(question))

        result = f"{title}\n{answer[1]}"
        return result

    return answer


if __name__ == "__main__":
    print(ask("Tôi muốn đầu tư lướt sóng, bạn có thể tư vấn cho tôi được không?"))