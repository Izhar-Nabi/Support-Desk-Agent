from typing import TypedDict, Annotated, List, Literal
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    next: Literal["vector_search", "postgres_query", "external_tool", "llm_response", "__end__"]