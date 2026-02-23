from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .tools import vector_search_tool, postgres_query_tool, external_api_tool
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()  # loads environment variables from .env

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY is not set in the environment or .env file!")

os.environ["OPENAI_API_KEY"] = api_key



llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a routing assistant. Classify the user query into one category:
    - vector_search: for FAQs, support articles, how-to guides
    - postgres_query: for customer info, orders, tickets, account status
    - external_tool: for weather, crypto prices, real-time data
    - llm_response: for general chat, greetings, opinions
    
    Only respond with one of: vector_search, postgres_query, external_tool, llm_response"""),
    MessagesPlaceholder(variable_name="messages")
])

router = router_prompt | llm.bind_tools(
    tools=[vector_search_tool, postgres_query_tool, external_api_tool],
    tool_choice="required"
)

def router_node(state):
    response = router.invoke(state["messages"])
    # next_step = response.tool_calls[0].name if response.tool_calls else "llm_response"
    next_step = response.tool_calls[0]["name"] if response.tool_calls else "llm_response"

    mapping = {
        "vector_search_tool": "vector_search",
        "postgres_query_tool": "postgres_query",
        "external_api_tool": "external_tool"
    }
    return {"next": mapping.get(next_step, next_step)}

def vector_search_node(state):
    result = vector_search_tool.invoke(state["messages"][-1].content)
    return {"messages": [{"role": "assistant", "content": result}]}

def postgres_query_node(state):
    result = postgres_query_tool.invoke(state["messages"][-1].content)
    return {"messages": [{"role": "assistant", "content": result}]}

def external_tool_node(state):
    result = external_api_tool.invoke(state["messages"][-1].content)
    return {"messages": [{"role": "assistant", "content": result}]}

def llm_response_node(state):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}