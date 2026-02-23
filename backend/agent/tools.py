from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from sqlalchemy import create_engine, text
from langchain_openai import OpenAIEmbeddings
import json
import random

@tool
def vector_search_tool(query: str) -> str:
    """Search support articles and FAQs using semantic search."""
    from backend.database.vector_store import init_vector_store
    vectorstore = init_vector_store()
    docs = vectorstore.similarity_search(query, k=2)
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def postgres_query_tool(query: str) -> str:
    """Run SQL query to fetch customer or ticket information."""
    from backend.config import settings
    engine = create_engine(settings.POSTGRES_URL)
    
    # Simple intent-based SQL generation
    query_lower = query.lower()
    if any(x in query_lower for x in ["customer", "who is", "account"]):
        name = query_lower.split("customer")[-1].strip().split()[0] if "customer" in query_lower else None
        if name:
            sql = text("SELECT * FROM customers WHERE name ILIKE :name")
            params = {"name": f"%{name}%"}
        else:
            sql = text("SELECT * FROM customers LIMIT 5")
            params = {}
    elif "ticket" in query_lower or "issue" in query_lower:
        sql = text("""
            SELECT c.name, t.issue, t.status 
            FROM tickets t 
            JOIN customers c ON t.customer_id = c.id 
            LIMIT 5
        """)
        params = {}
    else:
        sql = text("SELECT name, city FROM customers LIMIT 3")
        params = {}

    with engine.connect() as conn:
        result = conn.execute(sql, params)
        rows = result.fetchall()
        if not rows:
            return "No matching data found."
        return "\n".join([str(row) for row in rows])

@tool
def external_api_tool(query: str) -> str:
    """Mock external API for weather, crypto, or general info."""
    query_lower = query.lower()
    if "weather" in query_lower:
        cities = ["New York", "London", "Tokyo", "Sydney"]
        city = random.choice(cities)
        return f"Current weather in {city}: 18°C, partly cloudy."
    elif "crypto" in query_lower or "bitcoin" in query_lower:
        return "Bitcoin price: $92,450 USD (mock data)"
    else:
        return "This is a mock external API response for general queries."