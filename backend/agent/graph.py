from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import router_node, vector_search_node, postgres_query_node, external_tool_node, llm_response_node

def create_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("vector_search", vector_search_node)
    graph.add_node("postgres_query", postgres_query_node)
    graph.add_node("external_tool", external_tool_node)
    graph.add_node("llm_response", llm_response_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        lambda x: x["next"],
        {
            "vector_search": "vector_search",
            "postgres_query": "postgres_query",
            "external_tool": "external_tool",
            "llm_response": "llm_response",
            "__end__": END
        }
    )

    # After tool nodes, go back to LLM to format response
    graph.add_edge("vector_search", "llm_response")
    graph.add_edge("postgres_query", "llm_response")
    graph.add_edge("external_tool", "llm_response")
    graph.add_edge("llm_response", END)

    return graph.compile()